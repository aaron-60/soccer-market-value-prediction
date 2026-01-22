"""
predict.py - Load the trained model and make predictions

Usage:
    python src/predict.py
"""

import joblib
import pandas as pd
from pathlib import Path


# ============================================================================
# LOAD MODEL
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
model_path = PROJECT_ROOT / "models" / "market_value_model.joblib"

if not model_path.exists():
    print("❌ Model not found! Run train_model.py first.")
    print(f"   Expected: {model_path}")
    exit(1)

model_data = joblib.load(model_path)

model = model_data['model']
feature_names = model_data['feature_names']
metrics = model_data['metrics']

print("="*60)
print("⚽ SOCCER MARKET VALUE - PREDICTION TOOL")
print("="*60)
print(f"\n✅ Model loaded successfully!")
print(f"\nModel Performance:")
print(f"  R² Score: {metrics['r2']:.4f}")
print(f"  MAE: €{metrics['mae']/1e6:.2f}M")
print(f"  RMSE: €{metrics['rmse']/1e6:.2f}M")
print(f"\nFeatures used ({len(feature_names)}):")
for f in feature_names:
    print(f"  • {f}")


# ============================================================================
# EXAMPLE PREDICTIONS
# ============================================================================

def predict_player(name, age, position, is_top5, appearances, goals, assists, minutes, club_rank=0.5):
    """
    Predict market value for a player.
    
    Parameters:
    - name: Player name (for display)
    - age: Player age
    - position: 'GK', 'DEF', 'MID', or 'ATT'
    - is_top5: True if plays in Top 5 league (EPL, La Liga, Serie A, Bundesliga, Ligue 1)
    - appearances: Total career appearances
    - goals: Total career goals
    - assists: Total career assists
    - minutes: Total career minutes
    - club_rank: 0-1 (1 = top club like Real Madrid, 0 = small club)
    """
    
    # Position encoding
    pos_map = {'GK': 0, 'DEF': 1, 'MID': 2, 'ATT': 3}
    position_encoded = pos_map.get(position.upper(), 2)
    
    # Calculate derived stats
    goals_per_90 = (goals * 90 / minutes) if minutes > 0 else 0
    assists_per_90 = (assists * 90 / minutes) if minutes > 0 else 0
    minutes_per_game = (minutes / appearances) if appearances > 0 else 0
    productivity_score = goals * 3 + assists * 2 + appearances * 0.1
    
    # Create feature dict
    player_data = {
        'age': age,
        'position_encoded': position_encoded,
        'is_top5_league': 1 if is_top5 else 0,
        'league_tier': 1 if is_top5 else 2,
        'total_appearances': appearances,
        'total_goals': goals,
        'total_assists': assists,
        'total_minutes': minutes,
        'goals_per_90': goals_per_90,
        'assists_per_90': assists_per_90,
        'minutes_per_game': minutes_per_game,
        'club_value_rank': club_rank,
        'productivity_score': productivity_score
    }
    
    # Predict
    df = pd.DataFrame([player_data])
    predicted = model.predict(df)[0]
    
    return predicted


print("\n" + "="*60)
print("EXAMPLE PREDICTIONS")
print("="*60)

# Example players
examples = [
    # (Name, Age, Position, Top5League, Appearances, Goals, Assists, Minutes, ClubRank)
    ("Young Striker (Top Club)", 22, "ATT", True, 100, 40, 15, 7500, 0.95),
    ("Prime Midfielder", 27, "MID", True, 250, 35, 60, 20000, 0.85),
    ("Experienced Defender", 30, "DEF", True, 300, 15, 25, 25000, 0.80),
    ("Young Goalkeeper", 23, "GK", True, 80, 0, 0, 7200, 0.70),
    ("Lower League Attacker", 25, "ATT", False, 150, 55, 20, 12000, 0.30),
]

print(f"\n{'Player':<30} {'Age':>4} {'Pos':>4} {'Goals':>6} {'Apps':>5} {'Predicted':>12}")
print("-" * 75)

for name, age, pos, top5, apps, goals, assists, mins, club_rank in examples:
    predicted = predict_player(name, age, pos, top5, apps, goals, assists, mins, club_rank)
    print(f"{name:<30} {age:>4} {pos:>4} {goals:>6} {apps:>5} €{predicted/1e6:>10.1f}M")


# ============================================================================
# INTERACTIVE MODE
# ============================================================================

print("\n" + "="*60)
print("CREATE YOUR OWN PREDICTION")
print("="*60)

def interactive_predict():
    """Let user input their own player stats."""
    print("\nEnter player details:\n")
    print("(Just press Enter to skip and use the default value shown)\n")
    
    try:
        name = input("Player name: ").strip() or "Test Player"
        
        age_input = input("Age: ").strip()
        age = int(age_input) if age_input else 25
        
        position = input("Position - GK, DEF, MID, or ATT: ").strip().upper() or "MID"
        
        top5_input = input("Plays in Top 5 league? (yes/no): ").strip().lower()
        is_top5 = top5_input != 'no' and top5_input != 'n'
        
        apps_input = input("Total career appearances: ").strip()
        appearances = int(apps_input) if apps_input else 100
        
        goals_input = input("Total career goals: ").strip()
        goals = int(goals_input) if goals_input else 20
        
        assists_input = input("Total career assists: ").strip()
        assists = int(assists_input) if assists_input else 15
        
        mins_input = input("Total career minutes played: ").strip()
        minutes = int(mins_input) if mins_input else 8000
        
        print("\nClub rank: How big is the club?")
        print("  0.9-1.0 = Elite (Real Madrid, Man City, Bayern)")
        print("  0.7-0.9 = Top club (Dortmund, Atletico)")
        print("  0.4-0.7 = Mid-table")
        print("  0.1-0.4 = Lower league/small club")
        rank_input = input("Club rank (0.0 to 1.0): ").strip()
        club_rank = float(rank_input) if rank_input else 0.5
        club_rank = max(0, min(1, club_rank))  # Ensure between 0 and 1
        
        predicted = predict_player(name, age, position, is_top5, appearances, goals, assists, minutes, club_rank)
        
        print(f"\n{'='*50}")
        print(f"🎯 {name}")
        print(f"{'='*50}")
        print(f"Age: {age} | Position: {position} | Top 5 League: {'Yes' if is_top5 else 'No'}")
        print(f"Appearances: {appearances} | Goals: {goals} | Assists: {assists}")
        print(f"Minutes: {minutes:,} | Club Rank: {club_rank}")
        print(f"\n💰 PREDICTED VALUE: €{predicted/1e6:.1f}M")
        print(f"{'='*50}")
        
    except ValueError as e:
        print(f"\n❌ Invalid input. Please enter numbers only for numeric fields.")
    except KeyboardInterrupt:
        print("\n\nExiting...")


if __name__ == "__main__":
    try:
        interactive_predict()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
