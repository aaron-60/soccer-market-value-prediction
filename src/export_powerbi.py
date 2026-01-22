"""
export_powerbi.py - Export data for Power BI

Usage:
    python src/export_powerbi.py

Creates CSV files optimized for Power BI in data/processed/powerbi/
"""

import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "player_market_value.db"
POWERBI_PATH = PROJECT_ROOT / "data" / "processed" / "powerbi"

POWERBI_PATH.mkdir(parents=True, exist_ok=True)

if not DATABASE_PATH.exists():
    print("❌ Database not found! Run data_pipeline.py first.")
    exit(1)

conn = sqlite3.connect(DATABASE_PATH)

print("="*60)
print("⚽ EXPORTING DATA FOR POWER BI")
print("="*60)

# ============================================================================
# 1. PLAYERS TABLE (Main Fact Table)
# ============================================================================
print("\n1. Exporting players...")

players_query = """
SELECT 
    p.player_id,
    p.name as player_name,
    p.position,
    p.sub_position,
    p.country_of_citizenship as nationality,
    p.date_of_birth,
    CAST((julianday('now') - julianday(p.date_of_birth)) / 365.25 AS INTEGER) as age,
    p.current_club_id,
    p.current_club_name,
    p.current_club_domestic_competition_id as league_id,
    p.market_value_in_eur as market_value,
    p.highest_market_value_in_eur as peak_market_value,
    CASE 
        WHEN p.current_club_domestic_competition_id IN ('GB1', 'ES1', 'IT1', 'L1', 'FR1') THEN 'Top 5'
        ELSE 'Other'
    END as league_tier,
    CASE 
        WHEN CAST((julianday('now') - julianday(p.date_of_birth)) / 365.25 AS INTEGER) < 21 THEN 'U21'
        WHEN CAST((julianday('now') - julianday(p.date_of_birth)) / 365.25 AS INTEGER) < 25 THEN '21-24'
        WHEN CAST((julianday('now') - julianday(p.date_of_birth)) / 365.25 AS INTEGER) < 29 THEN '25-28'
        WHEN CAST((julianday('now') - julianday(p.date_of_birth)) / 365.25 AS INTEGER) < 33 THEN '29-32'
        ELSE '33+'
    END as age_group
FROM players p
WHERE p.market_value_in_eur > 0
"""
df_players = pd.read_sql_query(players_query, conn)
df_players.to_csv(POWERBI_PATH / "players.csv", index=False)
print(f"   ✓ players.csv ({len(df_players):,} rows)")

# ============================================================================
# 2. CLUBS TABLE (Dimension)
# ============================================================================
print("2. Exporting clubs...")

clubs_query = """
SELECT 
    club_id,
    name as club_name,
    domestic_competition_id as league_id,
    total_market_value as club_total_value,
    squad_size,
    average_age as club_avg_age,
    stadium_name,
    stadium_seats
FROM clubs
WHERE club_id IN (SELECT DISTINCT current_club_id FROM players WHERE market_value_in_eur > 0)
"""
df_clubs = pd.read_sql_query(clubs_query, conn)
df_clubs.to_csv(POWERBI_PATH / "clubs.csv", index=False)
print(f"   ✓ clubs.csv ({len(df_clubs):,} rows)")

# ============================================================================
# 3. COMPETITIONS/LEAGUES TABLE (Dimension)
# ============================================================================
print("3. Exporting leagues...")

leagues_query = """
SELECT 
    competition_id as league_id,
    name as league_name,
    country_name,
    type as competition_type
FROM competitions
"""
df_leagues = pd.read_sql_query(leagues_query, conn)
df_leagues.to_csv(POWERBI_PATH / "leagues.csv", index=False)
print(f"   ✓ leagues.csv ({len(df_leagues):,} rows)")

# ============================================================================
# 4. PLAYER STATS (Aggregated Appearances)
# ============================================================================
print("4. Exporting player stats...")

stats_query = """
SELECT 
    player_id,
    COUNT(*) as total_appearances,
    SUM(goals) as total_goals,
    SUM(assists) as total_assists,
    SUM(minutes_played) as total_minutes,
    SUM(yellow_cards) as total_yellow_cards,
    SUM(red_cards) as total_red_cards,
    ROUND(SUM(goals) * 90.0 / NULLIF(SUM(minutes_played), 0), 3) as goals_per_90,
    ROUND(SUM(assists) * 90.0 / NULLIF(SUM(minutes_played), 0), 3) as assists_per_90
FROM appearances
GROUP BY player_id
"""
df_stats = pd.read_sql_query(stats_query, conn)
df_stats.to_csv(POWERBI_PATH / "player_stats.csv", index=False)
print(f"   ✓ player_stats.csv ({len(df_stats):,} rows)")

# ============================================================================
# 5. MODEL PREDICTIONS (if available)
# ============================================================================
predictions_path = PROJECT_ROOT / "data" / "processed" / "predictions.csv"
if predictions_path.exists():
    print("5. Copying predictions...")
    df_pred = pd.read_csv(predictions_path)
    df_pred.to_csv(POWERBI_PATH / "predictions.csv", index=False)
    print(f"   ✓ predictions.csv ({len(df_pred):,} rows)")

conn.close()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*60)
print("✅ EXPORT COMPLETE!")
print("="*60)
print(f"\nFiles saved to: {POWERBI_PATH}")
print(f"""
Files created:
  • players.csv      - Main player data with market values
  • clubs.csv        - Club information
  • leagues.csv      - League/competition details
  • player_stats.csv - Aggregated performance stats
  • predictions.csv  - Model predictions (if available)

Next: Import these into Power BI Desktop
""")

print("="*60)
print("POWER BI SETUP INSTRUCTIONS")
print("="*60)
print("""
1. Open Power BI Desktop

2. Get Data → Text/CSV → Import each CSV file:
   - players.csv
   - clubs.csv
   - leagues.csv
   - player_stats.csv
   - predictions.csv

3. Create Relationships (Model view):
   - players.current_club_id → clubs.club_id
   - players.league_id → leagues.league_id
   - players.player_id → player_stats.player_id
   - players.player_id → predictions.player_id

4. Suggested Visualizations:
   - Bar Chart: Top 20 players by market value
   - Pie Chart: Value distribution by position
   - Map: Total value by nationality
   - Line Chart: Average value by age
   - Scatter: Actual vs Predicted value
   - Table: Full player details with filters
""")
