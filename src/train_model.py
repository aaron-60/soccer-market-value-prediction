"""
train_model.py
==============
Trains a machine learning model to predict player market values.

Usage:
    python src/train_model.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"
MODELS_PATH = PROJECT_ROOT / "models"
VISUALIZATIONS_PATH = PROJECT_ROOT / "visualizations"

MODELS_PATH.mkdir(parents=True, exist_ok=True)

# Model settings
TEST_SIZE = 0.2
RANDOM_STATE = 42

COLORS = {"primary": "#3498db", "secondary": "#e74c3c", "success": "#2ecc71"}


# ============================================================================
# DATA PREPARATION
# ============================================================================

def load_data():
    """Load and prepare data for modeling."""
    print("\n1. Loading data...")
    
    ml_path = PROCESSED_DATA_PATH / 'ml_dataset.csv'
    if not ml_path.exists():
        raise FileNotFoundError(f"ML dataset not found: {ml_path}\nRun feature_analysis.py first.")
    
    df = pd.read_csv(ml_path)
    print(f"   Loaded {len(df):,} players")
    
    # Define features
    feature_cols = [
        'age', 'height_cm', 'position_encoded', 'foot_encoded',
        'is_top5_league', 'league_tier',
        'total_appearances', 'total_goals', 'total_assists', 'total_minutes',
        'goals_per_90', 'assists_per_90', 'minutes_per_game',
        'club_value_rank', 'productivity_score'
    ]
    
    # Keep only available features
    available = [c for c in feature_cols if c in df.columns]
    print(f"   Using {len(available)} features: {available}")
    
    X = df[available].fillna(df[available].median())
    y = df['market_value']
    
    return X, y, available, df


# ============================================================================
# MODEL TRAINING
# ============================================================================

def train_model(X_train, X_test, y_train, y_test, feature_names):
    """Train Random Forest model."""
    print("\n2. Training Random Forest model...")
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n   📊 Model Performance:")
    print(f"   R² Score:  {r2:.4f}")
    print(f"   MAE:       €{mae/1e6:.2f}M")
    print(f"   RMSE:      €{rmse/1e6:.2f}M")
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n   📊 Top 10 Feature Importance:")
    for _, row in importance.head(10).iterrows():
        bar = '█' * int(row['importance'] * 40)
        print(f"   {row['feature']:<25} {row['importance']:.3f} {bar}")
    
    return model, importance, {'mae': mae, 'rmse': rmse, 'r2': r2}, y_pred


def cross_validate(model, X, y):
    """Perform cross-validation."""
    print("\n3. Cross-validating model...")
    
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
    print(f"   CV R² Scores: {cv_scores.round(3)}")
    print(f"   Mean R²: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    
    return cv_scores


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_results(y_test, y_pred, importance, metrics):
    """Create model results visualization."""
    print("\n4. Creating visualizations...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. Actual vs Predicted
    ax = axes[0, 0]
    ax.scatter(y_test/1e6, y_pred/1e6, alpha=0.3, s=20, c=COLORS['primary'])
    max_val = max(y_test.max(), y_pred.max()) / 1e6
    ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Perfect Prediction')
    ax.set_xlabel('Actual Value (€M)')
    ax.set_ylabel('Predicted Value (€M)')
    ax.set_title(f'Actual vs Predicted | R² = {metrics["r2"]:.3f}')
    ax.legend()
    ax.set_xlim(0, np.percentile(y_test/1e6, 99))
    ax.set_ylim(0, np.percentile(y_pred/1e6, 99))
    
    # 2. Residuals
    ax = axes[0, 1]
    residuals = (y_pred - y_test) / 1e6
    ax.scatter(y_pred/1e6, residuals, alpha=0.3, s=20, c=COLORS['secondary'])
    ax.axhline(y=0, color='red', linestyle='--', linewidth=2)
    ax.set_xlabel('Predicted Value (€M)')
    ax.set_ylabel('Residual (€M)')
    ax.set_title('Residuals Analysis')
    
    # 3. Feature Importance
    ax = axes[1, 0]
    top_feat = importance.head(12)
    colors = plt.cm.viridis(np.linspace(0.3, 0.8, len(top_feat)))
    ax.barh(range(len(top_feat)), top_feat['importance'], color=colors)
    ax.set_yticks(range(len(top_feat)))
    ax.set_yticklabels(top_feat['feature'])
    ax.invert_yaxis()
    ax.set_xlabel('Importance')
    ax.set_title('Top 12 Features')
    
    # 4. Error Distribution
    ax = axes[1, 1]
    error_pct = ((y_pred - y_test) / y_test) * 100
    error_pct = error_pct[(error_pct > -200) & (error_pct < 200)]
    ax.hist(error_pct, bins=50, color=COLORS['success'], edgecolor='white', alpha=0.7)
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
    ax.axvline(x=error_pct.median(), color='blue', linestyle='-', linewidth=2,
               label=f'Median: {error_pct.median():.1f}%')
    ax.set_xlabel('Prediction Error (%)')
    ax.set_ylabel('Frequency')
    ax.set_title('Error Distribution')
    ax.legend()
    
    plt.suptitle('Market Value Prediction Model Results', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_PATH / 'model_results.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: model_results.png")


# ============================================================================
# PREDICTIONS
# ============================================================================

def show_predictions(model, X, df, n=10):
    """Show sample predictions."""
    print("\n5. Sample Predictions:")
    
    predictions = model.predict(X)
    
    results = df[['player_name', 'age', 'position_group', 'current_club_name', 'market_value']].copy()
    results['predicted'] = predictions
    results['error'] = results['predicted'] - results['market_value']
    results['error_pct'] = (results['error'] / results['market_value']) * 100
    
    print("\n   📈 Most UNDERVALUED (model predicts higher):")
    print("   " + "-" * 75)
    for _, row in results.nlargest(n, 'error').iterrows():
        print(f"   {row['player_name'][:25]:<26} Actual: €{row['market_value']/1e6:>5.1f}M  "
              f"Predicted: €{row['predicted']/1e6:>5.1f}M  ({row['error_pct']:+.0f}%)")
    
    print("\n   📉 Most OVERVALUED (model predicts lower):")
    print("   " + "-" * 75)
    for _, row in results.nsmallest(n, 'error').iterrows():
        print(f"   {row['player_name'][:25]:<26} Actual: €{row['market_value']/1e6:>5.1f}M  "
              f"Predicted: €{row['predicted']/1e6:>5.1f}M  ({row['error_pct']:+.0f}%)")
    
    # Save all predictions
    results.to_csv(PROCESSED_DATA_PATH / 'predictions.csv', index=False)
    print(f"\n   ✓ All predictions saved to: predictions.csv")
    
    return results


def save_model(model, feature_names, metrics):
    """Save the trained model."""
    print("\n6. Saving model...")
    
    model_data = {
        'model': model,
        'feature_names': feature_names,
        'metrics': metrics
    }
    
    model_path = MODELS_PATH / 'market_value_model.joblib'
    joblib.dump(model_data, model_path)
    print(f"   ✓ Model saved to: {model_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Train and evaluate the prediction model."""
    print("\n" + "="*60)
    print("⚽ SOCCER MARKET VALUE - MODEL TRAINING")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    X, y, feature_names, df = load_data()
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"\n   Train: {len(X_train):,} | Test: {len(X_test):,}")
    
    # Train
    model, importance, metrics, y_pred = train_model(X_train, X_test, y_train, y_test, feature_names)
    
    # Cross-validate
    cv_scores = cross_validate(model, X, y)
    
    # Visualize
    plot_results(y_test.values, y_pred, importance, metrics)
    
    # Sample predictions
    show_predictions(model, X, df)
    
    # Save model
    save_model(model, feature_names, metrics)
    
    # Summary
    print("\n" + "="*60)
    print("✅ MODEL TRAINING COMPLETE!")
    print("="*60)
    print(f"""
    Model Performance:
    • R² Score: {metrics['r2']:.4f}
    • MAE: €{metrics['mae']/1e6:.2f}M
    • RMSE: €{metrics['rmse']/1e6:.2f}M
    • CV Mean R²: {cv_scores.mean():.4f}
    
    Top Features:
""")
    for _, row in importance.head(5).iterrows():
        print(f"    • {row['feature']}: {row['importance']:.3f}")
    
    print(f"""
    Output Files:
    • Model: {MODELS_PATH / 'market_value_model.joblib'}
    • Predictions: {PROCESSED_DATA_PATH / 'predictions.csv'}
    • Visualization: {VISUALIZATIONS_PATH / 'model_results.png'}
    
    🎉 Project Complete! Check the visualizations folder for all charts.
    """)


if __name__ == "__main__":
    main()
