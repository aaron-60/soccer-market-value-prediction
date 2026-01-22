# ⚽ Soccer Player Market Value Prediction

A data analysis and machine learning project that predicts football player market values using Transfermarkt data.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![SQL](https://img.shields.io/badge/SQL-SQLite-green.svg)

---

## 📊 Project Overview

Analyzes **400,000+ player valuations** to predict market values based on:
- Age, position, nationality
- Performance stats (goals, assists, appearances)
- League and club quality

---

## 🚀 Quick Start

```bash
# 1. Setup
python -m pip install -r requirements.txt

# 2. Run pipeline
python src/data_pipeline.py      # Download & load data
python src/feature_analysis.py   # Create features & analyze
python src/visualizations.py     # Generate charts
python src/train_model.py        # Train ML model
```

📖 **See [GUIDE.md](GUIDE.md) for detailed instructions**

---

## 📁 Project Structure

```
soccer-market-value-prediction/
├── src/
│   ├── data_pipeline.py      # Download, explore, load to SQL
│   ├── feature_analysis.py   # Feature engineering + analysis
│   ├── visualizations.py     # Generate charts
│   └── train_model.py        # Train prediction model
├── data/
│   ├── raw/                  # CSV files from Kaggle
│   └── processed/            # SQLite DB + feature CSVs
├── visualizations/           # Generated charts (PNG)
├── models/                   # Saved ML models
├── sql/                      # SQL queries
├── GUIDE.md                  # Detailed run instructions
└── requirements.txt
```

---

## 📈 Sample Results

**Model Performance:**
- R² Score: ~0.78
- MAE: ~€2.1M
- RMSE: ~€5.4M

**Key Findings:**
- Players peak in value at ages 25-28
- Attackers are valued 40-60% higher than defenders
- Premier League players have 30-50% premium

---

## 📊 Data Source

[Kaggle: Football Data from Transfermarkt](https://www.kaggle.com/datasets/davidcariboo/player-scores)

- 30,000+ players
- 400,000+ market valuations
- 60,000+ games
- 1,200,000+ appearances

---

## 📄 License

MIT License - See LICENSE file
