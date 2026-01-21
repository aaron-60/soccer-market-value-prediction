"""
feature_analysis.py
===================
Creates ML features and performs statistical analysis on the data.

Usage:
    python src/feature_analysis.py

This combines:
- Feature engineering for ML model
- Statistical analysis and insights
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = PROCESSED_DATA_PATH / "player_market_value.db"

# Top 5 leagues
TOP_5_LEAGUES = {
    "GB1": "Premier League",
    "ES1": "La Liga", 
    "IT1": "Serie A",
    "L1": "Bundesliga",
    "FR1": "Ligue 1"
}

# Position mapping
POSITION_GROUPS = {
    "Goalkeeper": ["Goalkeeper"],
    "Defender": ["Centre-Back", "Left-Back", "Right-Back", "Defender"],
    "Midfielder": ["Central Midfield", "Defensive Midfield", "Attacking Midfield", 
                   "Left Midfield", "Right Midfield", "Midfielder"],
    "Attacker": ["Centre-Forward", "Left Winger", "Right Winger", 
                 "Second Striker", "Attack"]
}

POSITION_TO_GROUP = {}
for group, positions in POSITION_GROUPS.items():
    for pos in positions:
        POSITION_TO_GROUP[pos] = group


def get_connection():
    """Get database connection."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE_PATH}\nRun data_pipeline.py first.")
    return sqlite3.connect(DATABASE_PATH)


def format_value(value):
    """Format market value for display."""
    if value >= 1_000_000:
        return f"€{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"€{value/1_000:.0f}K"
    return f"€{value:.0f}"


# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

def create_features():
    """Create comprehensive player features for ML model."""
    print("\n" + "="*60)
    print("CREATING ML FEATURES")
    print("="*60)
    
    conn = get_connection()
    
    # Load base player data
    query = """
    SELECT 
        p.player_id,
        p.name as player_name,
        p.position,
        p.sub_position,
        p.foot,
        p.height_cm,
        p.country_of_citizenship as nationality,
        p.date_of_birth,
        p.current_club_id,
        p.current_club_name,
        p.current_club_domestic_competition_id as league_id,
        p.market_value_in_eur as market_value,
        p.highest_market_value_in_eur as peak_market_value,
        
        c.name as club_name,
        c.total_market_value as club_total_value,
        c.squad_size as club_squad_size,
        c.average_age as club_avg_age,
        c.stadium_seats,
        
        stats.total_appearances,
        stats.total_goals,
        stats.total_assists,
        stats.total_minutes,
        stats.total_yellow_cards,
        stats.total_red_cards,
        stats.seasons_played
        
    FROM players p
    LEFT JOIN clubs c ON p.current_club_id = c.club_id
    LEFT JOIN (
        SELECT 
            player_id,
            COUNT(*) as total_appearances,
            SUM(goals) as total_goals,
            SUM(assists) as total_assists,
            SUM(minutes_played) as total_minutes,
            SUM(yellow_cards) as total_yellow_cards,
            SUM(red_cards) as total_red_cards,
            COUNT(DISTINCT strftime('%Y', date)) as seasons_played
        FROM appearances
        GROUP BY player_id
    ) stats ON p.player_id = stats.player_id
    
    WHERE p.market_value_in_eur IS NOT NULL 
      AND p.market_value_in_eur > 0
      AND p.date_of_birth IS NOT NULL
    """
    
    df = pd.read_sql_query(query, conn)
    print(f"\nLoaded {len(df):,} players with market values")
    
    # === FEATURE ENGINEERING ===
    print("\nEngineering features...")
    
    # 1. Age
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
    df['age'] = ((pd.Timestamp.now() - df['date_of_birth']).dt.days / 365.25).astype(int)
    
    df['age_group'] = pd.cut(
        df['age'], 
        bins=[0, 20, 24, 28, 32, 50],
        labels=['U21', '21-24', '25-28', '29-32', '33+']
    )
    
    # 2. Position encoding
    df['position_group'] = df['position'].map(POSITION_TO_GROUP).fillna('Unknown')
    position_map = {'Goalkeeper': 0, 'Defender': 1, 'Midfielder': 2, 'Attacker': 3, 'Unknown': 1}
    df['position_encoded'] = df['position_group'].map(position_map)
    
    # 3. League tier
    df['is_top5_league'] = df['league_id'].isin(TOP_5_LEAGUES.keys()).astype(int)
    league_tier_map = {'GB1': 1, 'ES1': 1, 'IT1': 1, 'L1': 1, 'FR1': 1}
    df['league_tier'] = df['league_id'].map(league_tier_map).fillna(2)
    
    # 4. Fill missing stats
    for col in ['total_appearances', 'total_goals', 'total_assists', 'total_minutes', 
                'total_yellow_cards', 'total_red_cards', 'seasons_played']:
        df[col] = df[col].fillna(0)
    
    # 5. Per 90 stats
    df['goals_per_90'] = np.where(df['total_minutes'] > 0, 
                                   df['total_goals'] * 90 / df['total_minutes'], 0)
    df['assists_per_90'] = np.where(df['total_minutes'] > 0,
                                     df['total_assists'] * 90 / df['total_minutes'], 0)
    df['goal_contributions_per_90'] = df['goals_per_90'] + df['assists_per_90']
    df['minutes_per_game'] = np.where(df['total_appearances'] > 0,
                                       df['total_minutes'] / df['total_appearances'], 0)
    
    # 6. Foot encoding
    foot_map = {'right': 0, 'left': 1, 'both': 2}
    df['foot_encoded'] = df['foot'].str.lower().map(foot_map).fillna(0)
    
    # 7. Height (fill missing)
    df['height_cm'] = df.groupby('position_group')['height_cm'].transform(
        lambda x: x.fillna(x.median())
    ).fillna(180)
    
    # 8. Club prestige
    df['club_total_value'] = df['club_total_value'].fillna(0)
    df['club_value_rank'] = df['club_total_value'].rank(pct=True)
    
    # 9. Nationality features
    nationality_avg = df.groupby('nationality')['market_value'].mean()
    df['nationality_avg_value'] = df['nationality'].map(nationality_avg)
    
    # 10. Club average value
    df['club_avg_player_value'] = df.groupby('current_club_id')['market_value'].transform('mean')
    
    # 11. Log transform
    df['log_market_value'] = np.log1p(df['market_value'])
    
    # 12. Composite scores
    df['productivity_score'] = df['total_goals'] * 3 + df['total_assists'] * 2 + df['total_appearances'] * 0.1
    
    # Filter valid ages
    df = df[(df['age'] >= 15) & (df['age'] <= 45)]
    
    # Save full features
    output_path = PROCESSED_DATA_PATH / 'player_features.csv'
    df.to_csv(output_path, index=False)
    print(f"✓ Saved {len(df):,} players to player_features.csv")
    
    # Create ML-ready dataset (filtered)
    df_ml = df[
        (df['market_value'] >= 100000) &
        (df['total_appearances'] >= 5) &
        (df['age'] >= 16) &
        (df['age'] <= 40)
    ].copy()
    
    ml_path = PROCESSED_DATA_PATH / 'ml_dataset.csv'
    df_ml.to_csv(ml_path, index=False)
    print(f"✓ Saved {len(df_ml):,} players to ml_dataset.csv (filtered for ML)")
    
    conn.close()
    return df


# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def analyze_overview(conn):
    """Generate overview statistics."""
    print("\n" + "="*60)
    print("📊 DATASET OVERVIEW")
    print("="*60)
    
    cursor = conn.cursor()
    
    tables = ['players', 'clubs', 'competitions', 'games', 'appearances', 'player_valuations']
    print(f"\n{'Table':<25} {'Records':>15}")
    print("-" * 42)
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:>15,}")
    
    cursor.execute("""
        SELECT COUNT(*), SUM(market_value_in_eur), AVG(market_value_in_eur)
        FROM players WHERE market_value_in_eur > 0
    """)
    count, total, avg = cursor.fetchone()
    print(f"\nPlayers with market value: {count:,}")
    print(f"Total market value: {format_value(total or 0)}")
    print(f"Average value: {format_value(avg or 0)}")


def analyze_top_players(conn):
    """Show top 15 most valuable players."""
    print("\n" + "="*60)
    print("🏆 TOP 15 MOST VALUABLE PLAYERS")
    print("="*60)
    
    query = """
    SELECT 
        name,
        position,
        CAST((julianday('now') - julianday(date_of_birth)) / 365.25 AS INTEGER) as age,
        current_club_name as club,
        market_value_in_eur / 1000000 as value_millions
    FROM players
    WHERE market_value_in_eur > 0
    ORDER BY market_value_in_eur DESC
    LIMIT 15
    """
    df = pd.read_sql_query(query, conn)
    
    print(f"\n{'#':<3} {'Player':<25} {'Position':<15} {'Age':>4} {'Club':<20} {'Value':>10}")
    print("-" * 82)
    for i, row in df.iterrows():
        print(f"{i+1:<3} {str(row['name'])[:24]:<25} {str(row['position'])[:14]:<15} "
              f"{row['age']:>4} {str(row['club'])[:19]:<20} €{row['value_millions']:>7.1f}M")


def analyze_by_position(conn):
    """Analyze values by position."""
    print("\n" + "="*60)
    print("📍 MARKET VALUE BY POSITION")
    print("="*60)
    
    query = """
    SELECT 
        position,
        COUNT(*) as players,
        AVG(market_value_in_eur) as avg_value,
        MAX(market_value_in_eur) as max_value
    FROM players
    WHERE market_value_in_eur > 0 AND position IS NOT NULL
    GROUP BY position
    ORDER BY avg_value DESC
    """
    df = pd.read_sql_query(query, conn)
    
    print(f"\n{'Position':<25} {'Players':>10} {'Avg Value':>12} {'Max Value':>12}")
    print("-" * 62)
    for _, row in df.iterrows():
        print(f"{str(row['position'])[:24]:<25} {row['players']:>10,} "
              f"{format_value(row['avg_value']):>12} {format_value(row['max_value']):>12}")


def analyze_by_age(conn):
    """Analyze values by age group."""
    print("\n" + "="*60)
    print("📅 MARKET VALUE BY AGE GROUP")
    print("="*60)
    
    query = """
    SELECT 
        CASE 
            WHEN age < 21 THEN '1. Under 21'
            WHEN age BETWEEN 21 AND 24 THEN '2. 21-24'
            WHEN age BETWEEN 25 AND 28 THEN '3. 25-28 (Prime)'
            WHEN age BETWEEN 29 AND 32 THEN '4. 29-32'
            ELSE '5. 33+'
        END as age_group,
        COUNT(*) as players,
        AVG(market_value) as avg_value,
        MAX(market_value) as max_value
    FROM (
        SELECT CAST((julianday('now') - julianday(date_of_birth)) / 365.25 AS INTEGER) as age,
               market_value_in_eur as market_value
        FROM players
        WHERE market_value_in_eur > 0 AND date_of_birth IS NOT NULL
    )
    WHERE age >= 15 AND age <= 45
    GROUP BY age_group
    ORDER BY age_group
    """
    df = pd.read_sql_query(query, conn)
    
    print(f"\n{'Age Group':<20} {'Players':>10} {'Avg Value':>12} {'Max Value':>12}")
    print("-" * 58)
    for _, row in df.iterrows():
        print(f"{row['age_group']:<20} {row['players']:>10,} "
              f"{format_value(row['avg_value']):>12} {format_value(row['max_value']):>12}")


def analyze_by_league(conn):
    """Analyze values by league."""
    print("\n" + "="*60)
    print("🏟️ TOP LEAGUES BY TOTAL VALUE")
    print("="*60)
    
    query = """
    SELECT 
        c.domestic_competition_id as league_id,
        comp.name as league_name,
        COUNT(DISTINCT p.player_id) as players,
        AVG(p.market_value_in_eur) as avg_value,
        SUM(p.market_value_in_eur) as total_value
    FROM players p
    JOIN clubs c ON p.current_club_id = c.club_id
    LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id
    WHERE p.market_value_in_eur > 0
    GROUP BY c.domestic_competition_id
    HAVING players >= 50
    ORDER BY total_value DESC
    LIMIT 12
    """
    df = pd.read_sql_query(query, conn)
    
    print(f"\n{'League':<30} {'Players':>8} {'Avg Value':>12} {'Total Value':>15}")
    print("-" * 70)
    for _, row in df.iterrows():
        league = str(row['league_name'])[:29] if row['league_name'] else row['league_id']
        print(f"{league:<30} {row['players']:>8,} "
              f"{format_value(row['avg_value']):>12} {format_value(row['total_value']):>15}")


def analyze_top_clubs(conn):
    """Analyze most valuable clubs."""
    print("\n" + "="*60)
    print("🏆 TOP 12 MOST VALUABLE SQUADS")
    print("="*60)
    
    query = """
    SELECT 
        c.name as club,
        COUNT(p.player_id) as squad,
        SUM(p.market_value_in_eur) as total_value,
        AVG(p.market_value_in_eur) as avg_value
    FROM clubs c
    JOIN players p ON c.club_id = p.current_club_id
    WHERE p.market_value_in_eur > 0
    GROUP BY c.club_id
    ORDER BY total_value DESC
    LIMIT 12
    """
    df = pd.read_sql_query(query, conn)
    
    print(f"\n{'#':<3} {'Club':<30} {'Squad':>6} {'Total Value':>15} {'Avg Value':>12}")
    print("-" * 70)
    for i, row in df.iterrows():
        print(f"{i+1:<3} {str(row['club'])[:29]:<30} {row['squad']:>6} "
              f"{format_value(row['total_value']):>15} {format_value(row['avg_value']):>12}")


def analyze_correlations():
    """Analyze feature correlations with market value."""
    print("\n" + "="*60)
    print("📈 FEATURE CORRELATIONS WITH MARKET VALUE")
    print("="*60)
    
    df = pd.read_csv(PROCESSED_DATA_PATH / 'player_features.csv')
    df = df[(df['market_value'] > 100000) & (df['total_appearances'] >= 10)]
    
    print(f"\nAnalyzing {len(df):,} players (min 10 appearances)\n")
    
    numeric_cols = ['age', 'total_appearances', 'total_goals', 'total_assists',
                    'goals_per_90', 'assists_per_90', 'height_cm', 'is_top5_league']
    
    correlations = {}
    for col in numeric_cols:
        if col in df.columns:
            corr = df['market_value'].corr(df[col])
            correlations[col] = corr
    
    sorted_corr = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
    
    print(f"{'Feature':<25} {'Correlation':>12} {'Impact':<10}")
    print("-" * 50)
    for feature, corr in sorted_corr:
        indicator = "🔺 Higher" if corr > 0.1 else "🔻 Lower" if corr < -0.1 else "➖ Weak"
        print(f"{feature:<25} {corr:>12.3f} {indicator}")


def run_analysis():
    """Run all statistical analysis."""
    print("\n" + "="*60)
    print("STATISTICAL ANALYSIS")
    print("="*60)
    
    conn = get_connection()
    
    try:
        analyze_overview(conn)
        analyze_top_players(conn)
        analyze_by_position(conn)
        analyze_by_age(conn)
        analyze_by_league(conn)
        analyze_top_clubs(conn)
    finally:
        conn.close()
    
    # Correlation analysis uses the CSV
    if (PROCESSED_DATA_PATH / 'player_features.csv').exists():
        analyze_correlations()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run feature engineering and analysis."""
    print("\n" + "="*60)
    print("⚽ SOCCER MARKET VALUE - FEATURE ENGINEERING & ANALYSIS")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create features
    create_features()
    
    # Run analysis
    run_analysis()
    
    print("\n" + "="*60)
    print("✅ FEATURE ENGINEERING & ANALYSIS COMPLETE!")
    print("="*60)
    print(f"""
Output files:
  • {PROCESSED_DATA_PATH / 'player_features.csv'}
  • {PROCESSED_DATA_PATH / 'ml_dataset.csv'}

Next step: Generate visualizations
    python src/visualizations.py
""")


if __name__ == "__main__":
    main()
