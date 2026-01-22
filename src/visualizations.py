"""
visualizations.py
=================
Generates all visualizations for the Soccer Market Value project.

Usage:
    python src/visualizations.py
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from datetime import datetime


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"
VISUALIZATIONS_PATH = PROJECT_ROOT / "visualizations"
DATABASE_PATH = PROCESSED_DATA_PATH / "player_market_value.db"

VISUALIZATIONS_PATH.mkdir(parents=True, exist_ok=True)

# Colors
COLORS = {
    "primary": "#3498db",
    "secondary": "#e74c3c", 
    "success": "#2ecc71",
    "warning": "#f39c12"
}

POSITION_COLORS = {
    "Goalkeeper": "#f39c12",
    "Defender": "#3498db",
    "Midfielder": "#2ecc71", 
    "Attacker": "#e74c3c"
}

# Position mapping
POSITION_TO_GROUP = {
    "Goalkeeper": "Goalkeeper",
    "Centre-Back": "Defender", "Left-Back": "Defender", "Right-Back": "Defender", "Defender": "Defender",
    "Central Midfield": "Midfielder", "Defensive Midfield": "Midfielder", "Attacking Midfield": "Midfielder",
    "Left Midfield": "Midfielder", "Right Midfield": "Midfielder", "Midfielder": "Midfielder",
    "Centre-Forward": "Attacker", "Left Winger": "Attacker", "Right Winger": "Attacker",
    "Second Striker": "Attacker", "Attack": "Attacker"
}

# Plot settings
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def save_plot(name):
    """Save current plot."""
    filepath = VISUALIZATIONS_PATH / f"{name}.png"
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {name}.png")


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_age_value_curve():
    """Plot how market value changes with age."""
    df = pd.read_csv(PROCESSED_DATA_PATH / 'player_features.csv')
    
    age_stats = df.groupby('age').agg({
        'market_value': ['mean', 'median', 'count']
    }).reset_index()
    age_stats.columns = ['age', 'mean_value', 'median_value', 'count']
    age_stats = age_stats[(age_stats['age'] >= 17) & (age_stats['age'] <= 38) & (age_stats['count'] >= 20)]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(age_stats['age'], age_stats['mean_value']/1e6, marker='o', linewidth=2, 
            color=COLORS['primary'], label='Mean Value')
    ax.plot(age_stats['age'], age_stats['median_value']/1e6, marker='s', linewidth=2,
            color=COLORS['secondary'], linestyle='--', label='Median Value')
    
    ax.axvspan(25, 28, alpha=0.2, color='green', label='Prime Years (25-28)')
    
    peak_age = age_stats.loc[age_stats['mean_value'].idxmax(), 'age']
    peak_value = age_stats['mean_value'].max() / 1e6
    ax.annotate(f'Peak: Age {peak_age}', xy=(peak_age, peak_value),
                xytext=(peak_age + 2, peak_value + 1),
                arrowprops=dict(arrowstyle='->', color='gray'))
    
    ax.set_xlabel('Age')
    ax.set_ylabel('Market Value (€ Millions)')
    ax.set_title('Player Market Value Curve by Age')
    ax.legend()
    
    save_plot('01_age_value_curve')


def plot_position_distribution():
    """Plot market value by position."""
    df = pd.read_csv(PROCESSED_DATA_PATH / 'player_features.csv')
    df = df[df['position_group'].notna() & (df['position_group'] != 'Unknown')]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    position_order = ['Goalkeeper', 'Defender', 'Midfielder', 'Attacker']
    colors = [POSITION_COLORS.get(p, COLORS['primary']) for p in position_order]
    
    # Box plot
    positions = [df[df['position_group'] == p]['market_value']/1e6 for p in position_order]
    bp = axes[0].boxplot(positions, labels=position_order, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    axes[0].set_ylabel('Market Value (€ Millions)')
    axes[0].set_title('Value Distribution by Position')
    axes[0].set_ylim(0, df['market_value'].quantile(0.95)/1e6)
    
    # Bar chart
    pos_avg = df.groupby('position_group')['market_value'].mean().reindex(position_order)/1e6
    bars = axes[1].bar(position_order, pos_avg, color=colors, alpha=0.7, edgecolor='black')
    axes[1].set_ylabel('Average Market Value (€ Millions)')
    axes[1].set_title('Average Value by Position')
    
    for bar, val in zip(bars, pos_avg):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'€{val:.1f}M', ha='center', va='bottom')
    
    save_plot('02_position_distribution')


def plot_league_comparison():
    """Compare top 5 leagues."""
    conn = get_connection()
    
    query = """
    SELECT 
        CASE c.domestic_competition_id
            WHEN 'GB1' THEN 'Premier League'
            WHEN 'ES1' THEN 'La Liga'
            WHEN 'IT1' THEN 'Serie A'
            WHEN 'L1' THEN 'Bundesliga'
            WHEN 'FR1' THEN 'Ligue 1'
        END as league,
        COUNT(*) as players,
        AVG(p.market_value_in_eur) as avg_value,
        SUM(p.market_value_in_eur) as total_value
    FROM players p
    JOIN clubs c ON p.current_club_id = c.club_id
    WHERE p.market_value_in_eur > 0
      AND c.domestic_competition_id IN ('GB1', 'ES1', 'IT1', 'L1', 'FR1')
    GROUP BY c.domestic_competition_id
    ORDER BY avg_value DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(df)))
    
    axes[0].barh(df['league'], df['avg_value']/1e6, color=colors)
    axes[0].set_xlabel('Average Player Value (€ Millions)')
    axes[0].set_title('Average Player Value')
    axes[0].invert_yaxis()
    
    axes[1].barh(df['league'], df['total_value']/1e9, color=colors)
    axes[1].set_xlabel('Total Value (€ Billions)')
    axes[1].set_title('Total League Value')
    axes[1].invert_yaxis()
    
    axes[2].barh(df['league'], df['players'], color=colors)
    axes[2].set_xlabel('Number of Players')
    axes[2].set_title('Player Count')
    axes[2].invert_yaxis()
    
    plt.suptitle('Top 5 European Leagues Comparison', fontsize=14, y=1.02)
    save_plot('03_league_comparison')


def plot_top_players():
    """Plot top 20 most valuable players."""
    conn = get_connection()
    
    query = """
    SELECT name, position, market_value_in_eur / 1000000 as value_millions, current_club_name as club
    FROM players
    WHERE market_value_in_eur > 0
    ORDER BY market_value_in_eur DESC
    LIMIT 20
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df['position_group'] = df['position'].map(POSITION_TO_GROUP).fillna('Unknown')
    colors = [POSITION_COLORS.get(pg, COLORS['primary']) for pg in df['position_group']]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(range(len(df)), df['value_millions'], color=colors, alpha=0.8)
    
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([f"{n[:20]} ({c[:15]})" for n, c in zip(df['name'], df['club'])])
    ax.invert_yaxis()
    ax.set_xlabel('Market Value (€ Millions)')
    ax.set_title('Top 20 Most Valuable Players')
    
    for i, (bar, val) in enumerate(zip(bars, df['value_millions'])):
        ax.text(val + 1, i, f'€{val:.0f}M', va='center', fontsize=9)
    
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=p) for p, c in POSITION_COLORS.items()]
    ax.legend(handles=legend_elements, loc='lower right', title='Position')
    
    save_plot('04_top_players')


def plot_age_position_heatmap():
    """Create heatmap of values by age and position."""
    df = pd.read_csv(PROCESSED_DATA_PATH / 'player_features.csv')
    df = df[df['position_group'].notna() & (df['position_group'] != 'Unknown')]
    
    df['age_bin'] = pd.cut(df['age'], bins=[16, 20, 24, 28, 32, 36, 45],
                           labels=['17-20', '21-24', '25-28', '29-32', '33-36', '37+'])
    
    pivot = df.pivot_table(values='market_value', index='position_group', columns='age_bin', aggfunc='mean') / 1e6
    pivot = pivot.reindex([p for p in ['Attacker', 'Midfielder', 'Defender', 'Goalkeeper'] if p in pivot.index])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(pivot.values, cmap='RdYlGn', aspect='auto')
    
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticklabels(pivot.index)
    
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            if not np.isnan(value):
                color = 'white' if value > pivot.values.mean() else 'black'
                ax.text(j, i, f'€{value:.1f}M', ha='center', va='center', color=color)
    
    ax.set_xlabel('Age Group')
    ax.set_ylabel('Position')
    ax.set_title('Average Market Value by Age and Position')
    plt.colorbar(im, label='Market Value (€ Millions)')
    
    save_plot('05_age_position_heatmap')


def plot_value_distribution():
    """Plot value distribution."""
    df = pd.read_csv(PROCESSED_DATA_PATH / 'player_features.csv')
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Log histogram
    log_values = np.log10(df['market_value'][df['market_value'] > 0])
    axes[0].hist(log_values, bins=50, color=COLORS['primary'], edgecolor='white', alpha=0.7)
    axes[0].set_xlabel('Log10(Market Value in EUR)')
    axes[0].set_ylabel('Number of Players')
    axes[0].set_title('Distribution of Player Market Values (Log Scale)')
    
    for val, label in [(5, '€100K'), (6, '€1M'), (7, '€10M'), (8, '€100M')]:
        axes[0].axvline(x=val, color='red', linestyle='--', alpha=0.5)
        axes[0].text(val, axes[0].get_ylim()[1]*0.9, label, rotation=90, va='top', ha='right')
    
    # Pie chart with legend instead of labels
    brackets = [
        ('< €1M', df['market_value'] < 1000000),
        ('€1M - €5M', (df['market_value'] >= 1000000) & (df['market_value'] < 5000000)),
        ('€5M - €20M', (df['market_value'] >= 5000000) & (df['market_value'] < 20000000)),
        ('€20M - €50M', (df['market_value'] >= 20000000) & (df['market_value'] < 50000000)),
        ('> €50M', df['market_value'] >= 50000000)
    ]
    
    labels = [b[0] for b in brackets]
    counts = [b[1].sum() for b in brackets]
    colors_pie = plt.cm.Blues(np.linspace(0.3, 0.9, len(brackets)))
    
    # Use legend instead of labels on pie to avoid overlap
    wedges, texts, autotexts = axes[1].pie(
        counts, 
        autopct='%1.1f%%', 
        colors=colors_pie, 
        startangle=90,
        pctdistance=0.6
    )
    
    # Make percentage text more readable
    for autotext in autotexts:
        autotext.set_fontsize(9)
    
    # Add legend on the side
    axes[1].legend(wedges, labels, title="Value Bracket", loc="center left", bbox_to_anchor=(1, 0.5))
    axes[1].set_title('Players by Value Bracket')
    
    plt.tight_layout()
    save_plot('06_value_distribution')


def plot_nationality_analysis():
    """Plot values by nationality."""
    conn = get_connection()
    
    query = """
    SELECT country_of_citizenship as nationality, COUNT(*) as players,
           AVG(market_value_in_eur) as avg_value, SUM(market_value_in_eur) as total_value
    FROM players
    WHERE market_value_in_eur > 0 AND country_of_citizenship IS NOT NULL
    GROUP BY country_of_citizenship
    HAVING players >= 30
    ORDER BY total_value DESC
    LIMIT 12
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(df)))[::-1]
    
    ax.barh(df['nationality'], df['total_value']/1e9, color=colors)
    ax.set_xlabel('Total Market Value (€ Billions)')
    ax.set_title('Total Player Value by Nationality (Top 12)')
    ax.invert_yaxis()
    
    save_plot('07_nationality_analysis')


def plot_club_values():
    """Plot most valuable squads."""
    conn = get_connection()
    
    query = """
    SELECT c.name as club, COUNT(p.player_id) as squad, SUM(p.market_value_in_eur) as total_value
    FROM clubs c
    JOIN players p ON c.club_id = p.current_club_id
    WHERE p.market_value_in_eur > 0
    GROUP BY c.club_id
    ORDER BY total_value DESC
    LIMIT 15
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(df)))[::-1]
    
    bars = ax.barh(range(len(df)), df['total_value']/1e9, color=colors)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([str(c)[:25] for c in df['club']])
    ax.invert_yaxis()
    ax.set_xlabel('Total Squad Value (€ Billions)')
    ax.set_title('Top 15 Most Valuable Squads')
    
    for i, (bar, val) in enumerate(zip(bars, df['total_value']/1e9)):
        ax.text(val + 0.02, i, f'€{val:.2f}B', va='center', fontsize=9)
    
    save_plot('08_club_values')


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Generate all visualizations."""
    print("\n" + "="*60)
    print("⚽ SOCCER MARKET VALUE - GENERATING VISUALIZATIONS")
    print("="*60)
    print(f"Output: {VISUALIZATIONS_PATH}\n")
    
    if not (PROCESSED_DATA_PATH / 'player_features.csv').exists():
        print("❌ Feature file not found! Run feature_analysis.py first.")
        return
    
    print("Creating charts:")
    plot_age_value_curve()
    plot_position_distribution()
    plot_league_comparison()
    plot_top_players()
    plot_age_position_heatmap()
    plot_value_distribution()
    plot_nationality_analysis()
    plot_club_values()
    
    print("\n" + "="*60)
    print("✅ VISUALIZATIONS COMPLETE!")
    print("="*60)
    print(f"\n8 charts saved to: {VISUALIZATIONS_PATH}")
    print(f"\nNext step: Train the prediction model")
    print(f"    python src/train_model.py")


if __name__ == "__main__":
    main()
