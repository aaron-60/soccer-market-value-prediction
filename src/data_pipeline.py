"""
data_pipeline.py
================
Downloads the Kaggle dataset, explores it, and loads into SQLite database.

Usage:
    python src/data_pipeline.py

This combines:
- Downloading data from Kaggle
- Exploring the CSV files
- Loading everything into SQLite
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

# Try to import kagglehub
try:
    import kagglehub
    KAGGLEHUB_AVAILABLE = True
except ImportError:
    KAGGLEHUB_AVAILABLE = False


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = PROCESSED_DATA_PATH / "player_market_value.db"

KAGGLE_DATASET = "davidcariboo/player-scores"

EXPECTED_FILES = [
    "players.csv",
    "clubs.csv", 
    "competitions.csv",
    "games.csv",
    "appearances.csv",
    "player_valuations.csv",
]

# Create directories
RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)


# ============================================================================
# DATABASE SCHEMA
# ============================================================================

SCHEMA_SQL = """
-- Drop existing tables
DROP TABLE IF EXISTS appearances;
DROP TABLE IF EXISTS player_valuations;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS clubs;
DROP TABLE IF EXISTS competitions;

-- Competitions (Leagues/Tournaments)
CREATE TABLE competitions (
    competition_id TEXT PRIMARY KEY,
    competition_code TEXT,
    name TEXT NOT NULL,
    sub_type TEXT,
    type TEXT,
    country_id INTEGER,
    country_name TEXT,
    domestic_league_code TEXT,
    confederation TEXT,
    url TEXT
);

-- Clubs
CREATE TABLE clubs (
    club_id INTEGER PRIMARY KEY,
    club_code TEXT,
    name TEXT NOT NULL,
    domestic_competition_id TEXT,
    total_market_value REAL,
    squad_size INTEGER,
    average_age REAL,
    foreigners_number INTEGER,
    foreigners_percentage REAL,
    national_team_players INTEGER,
    stadium_name TEXT,
    stadium_seats INTEGER,
    net_transfer_record TEXT,
    coach_name TEXT,
    last_season INTEGER,
    url TEXT,
    FOREIGN KEY (domestic_competition_id) REFERENCES competitions(competition_id)
);

-- Players
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    name TEXT NOT NULL,
    last_season INTEGER,
    current_club_id INTEGER,
    player_code TEXT,
    country_of_birth TEXT,
    city_of_birth TEXT,
    country_of_citizenship TEXT,
    date_of_birth DATE,
    sub_position TEXT,
    position TEXT,
    foot TEXT,
    height_cm INTEGER,
    contract_expiration_date DATE,
    agent_name TEXT,
    image_url TEXT,
    url TEXT,
    current_club_domestic_competition_id TEXT,
    current_club_name TEXT,
    market_value_in_eur REAL,
    highest_market_value_in_eur REAL,
    FOREIGN KEY (current_club_id) REFERENCES clubs(club_id)
);

-- Games/Matches
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY,
    competition_id TEXT,
    season INTEGER,
    round TEXT,
    date DATE,
    home_club_id INTEGER,
    away_club_id INTEGER,
    home_club_goals INTEGER,
    away_club_goals INTEGER,
    home_club_position INTEGER,
    away_club_position INTEGER,
    stadium TEXT,
    attendance INTEGER,
    referee TEXT,
    url TEXT,
    home_club_name TEXT,
    away_club_name TEXT,
    FOREIGN KEY (competition_id) REFERENCES competitions(competition_id)
);

-- Player Appearances
CREATE TABLE appearances (
    appearance_id TEXT PRIMARY KEY,
    game_id INTEGER,
    player_id INTEGER,
    player_club_id INTEGER,
    player_current_club_id INTEGER,
    date DATE,
    player_name TEXT,
    competition_id TEXT,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    minutes_played INTEGER DEFAULT 0,
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Player Market Valuations
CREATE TABLE player_valuations (
    valuation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    date DATE,
    market_value_in_eur REAL,
    current_club_id INTEGER,
    player_club_domestic_competition_id TEXT,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Indexes for performance
CREATE INDEX idx_players_club ON players(current_club_id);
CREATE INDEX idx_players_position ON players(position);
CREATE INDEX idx_players_value ON players(market_value_in_eur);
CREATE INDEX idx_appearances_player ON appearances(player_id);
CREATE INDEX idx_appearances_date ON appearances(date);
CREATE INDEX idx_valuations_player ON player_valuations(player_id);
CREATE INDEX idx_valuations_date ON player_valuations(date);
CREATE INDEX idx_games_date ON games(date);
"""


# ============================================================================
# STEP 1: DOWNLOAD DATA
# ============================================================================

def download_data():
    """Download dataset from Kaggle."""
    print("\n" + "="*60)
    print("STEP 1: DOWNLOADING DATA FROM KAGGLE")
    print("="*60)
    
    # Check if data already exists
    existing_files = list(RAW_DATA_PATH.glob("*.csv"))
    if len(existing_files) >= 5:
        print(f"\n✓ Found {len(existing_files)} CSV files already downloaded")
        for f in existing_files:
            print(f"  - {f.name}")
        return True
    
    if KAGGLEHUB_AVAILABLE:
        try:
            print(f"\nDownloading: {KAGGLE_DATASET}")
            downloaded_path = kagglehub.dataset_download(KAGGLE_DATASET)
            print(f"Downloaded to: {downloaded_path}")
            
            # Copy files to our data/raw directory
            import shutil
            downloaded_path = Path(downloaded_path)
            for file in downloaded_path.iterdir():
                if file.is_file() and file.suffix == '.csv':
                    dest = RAW_DATA_PATH / file.name
                    shutil.copy2(file, dest)
                    print(f"  Copied: {file.name}")
            return True
            
        except Exception as e:
            print(f"\n❌ Download failed: {e}")
    else:
        print("\n⚠ kagglehub not installed. Install with: pip install kagglehub")
    
    # Manual download instructions
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  MANUAL DOWNLOAD REQUIRED                                    ║
╠══════════════════════════════════════════════════════════════╣
║  1. Go to: https://www.kaggle.com/datasets/davidcariboo/    ║
║            player-scores                                     ║
║                                                              ║
║  2. Click "Download" (173 MB ZIP file)                       ║
║                                                              ║
║  3. Extract all CSV files to:                                ║
║     {str(RAW_DATA_PATH):<50} ║
║                                                              ║
║  4. Run this script again                                    ║
╚══════════════════════════════════════════════════════════════╝
""")
    return False


# ============================================================================
# STEP 2: EXPLORE DATA
# ============================================================================

def explore_data():
    """Explore the downloaded CSV files."""
    print("\n" + "="*60)
    print("STEP 2: EXPLORING DATA")
    print("="*60)
    
    csv_files = list(RAW_DATA_PATH.glob("*.csv"))
    
    if not csv_files:
        print("\n❌ No CSV files found!")
        return False
    
    print(f"\nFound {len(csv_files)} CSV files:\n")
    print(f"{'File':<30} {'Rows':>12} {'Columns':>10} {'Size (MB)':>12}")
    print("-" * 68)
    
    total_rows = 0
    total_size = 0
    
    for filepath in sorted(csv_files):
        try:
            df = pd.read_csv(filepath, low_memory=False, nrows=5)  # Quick peek
            full_df = pd.read_csv(filepath, low_memory=False)
            
            rows = len(full_df)
            cols = len(full_df.columns)
            size_mb = filepath.stat().st_size / (1024 * 1024)
            
            print(f"{filepath.name:<30} {rows:>12,} {cols:>10} {size_mb:>12.1f}")
            
            total_rows += rows
            total_size += size_mb
            
        except Exception as e:
            print(f"{filepath.name:<30} ERROR: {e}")
    
    print("-" * 68)
    print(f"{'TOTAL':<30} {total_rows:>12,} {'-':>10} {total_size:>12.1f}")
    
    return True


# ============================================================================
# STEP 3: LOAD TO SQL
# ============================================================================

def load_csv_to_table(conn, csv_path: Path, table_name: str, chunksize: int = 50000) -> int:
    """Load a CSV file into a database table."""
    if not csv_path.exists():
        print(f"  ⚠ File not found: {csv_path.name}")
        return 0
    
    print(f"  Loading {csv_path.name}...", end=" ", flush=True)
    
    total_rows = 0
    for i, chunk in enumerate(pd.read_csv(csv_path, low_memory=False, chunksize=chunksize)):
        chunk.columns = [c.strip().lower().replace(' ', '_') for c in chunk.columns]
        chunk.to_sql(table_name, conn, if_exists='append' if i > 0 else 'replace', index=False)
        total_rows += len(chunk)
    
    print(f"✓ ({total_rows:,} rows)")
    return total_rows


def load_to_database():
    """Load all CSV files into SQLite database."""
    print("\n" + "="*60)
    print("STEP 3: LOADING DATA INTO SQLITE DATABASE")
    print("="*60)
    print(f"\nDatabase: {DATABASE_PATH}")
    
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        # Create schema
        print("\nCreating database schema...")
        cursor = conn.cursor()
        cursor.executescript(SCHEMA_SQL)
        conn.commit()
        print("✓ Schema created")
        
        # Load each CSV
        print("\nLoading CSV files...")
        load_order = [
            ("competitions.csv", "competitions"),
            ("clubs.csv", "clubs"),
            ("players.csv", "players"),
            ("games.csv", "games"),
            ("appearances.csv", "appearances"),
            ("player_valuations.csv", "player_valuations"),
        ]
        
        total_rows = 0
        for csv_name, table_name in load_order:
            csv_path = RAW_DATA_PATH / csv_name
            rows = load_csv_to_table(conn, csv_path, table_name)
            total_rows += rows
        
        # Create helpful view
        print("\nCreating analytical view...")
        cursor.execute("""
        CREATE VIEW IF NOT EXISTS player_features AS
        SELECT 
            p.player_id,
            p.name as player_name,
            p.position,
            p.sub_position,
            p.foot,
            p.height_cm,
            p.country_of_citizenship as nationality,
            p.date_of_birth,
            CAST((julianday('now') - julianday(p.date_of_birth)) / 365.25 AS INTEGER) as age,
            p.current_club_id,
            p.current_club_name,
            p.current_club_domestic_competition_id as league_id,
            p.market_value_in_eur as market_value,
            p.highest_market_value_in_eur as peak_market_value,
            COALESCE(stats.total_appearances, 0) as total_appearances,
            COALESCE(stats.total_goals, 0) as total_goals,
            COALESCE(stats.total_assists, 0) as total_assists,
            COALESCE(stats.total_minutes, 0) as total_minutes,
            CASE WHEN COALESCE(stats.total_minutes, 0) > 0 
                 THEN ROUND(COALESCE(stats.total_goals, 0) * 90.0 / stats.total_minutes, 3)
                 ELSE 0 END as goals_per_90,
            CASE WHEN COALESCE(stats.total_minutes, 0) > 0 
                 THEN ROUND(COALESCE(stats.total_assists, 0) * 90.0 / stats.total_minutes, 3)
                 ELSE 0 END as assists_per_90
        FROM players p
        LEFT JOIN (
            SELECT 
                player_id,
                COUNT(*) as total_appearances,
                SUM(goals) as total_goals,
                SUM(assists) as total_assists,
                SUM(minutes_played) as total_minutes
            FROM appearances
            GROUP BY player_id
        ) stats ON p.player_id = stats.player_id
        WHERE p.market_value_in_eur IS NOT NULL 
          AND p.market_value_in_eur > 0
          AND p.date_of_birth IS NOT NULL;
        """)
        conn.commit()
        print("✓ player_features view created")
        
        # Summary
        print("\n" + "-"*40)
        print("DATABASE SUMMARY")
        print("-"*40)
        
        for _, table_name in load_order:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name:<25} {count:>12,} rows")
        
        db_size = DATABASE_PATH.stat().st_size / (1024*1024)
        print(f"\n  Database size: {db_size:.1f} MB")
        
        return True
        
    finally:
        conn.close()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the complete data pipeline."""
    print("\n" + "="*60)
    print("⚽ SOCCER MARKET VALUE - DATA PIPELINE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Download
    if not download_data():
        print("\n❌ Please download the data manually and run again.")
        return False
    
    # Step 2: Explore
    if not explore_data():
        return False
    
    # Step 3: Load to SQL
    if not load_to_database():
        return False
    
    print("\n" + "="*60)
    print("✅ DATA PIPELINE COMPLETE!")
    print("="*60)
    print(f"""
Next step: Run feature engineering and analysis
    python src/feature_analysis.py
""")
    return True


if __name__ == "__main__":
    main()
