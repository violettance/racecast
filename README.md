# 🏎️ RaceCast - Formula 1 Prediction System

A machine learning system for predicting Formula 1 race results using historical data, telemetry, and advanced feature engineering.

## 📁 Project Structure

```
racecast/
├── data/                    # Data storage
│   ├── raw/                # Raw data from APIs
│   └── processed/          # Processed feature data
├── docs/                   # Documentation
│   ├── data_methodology.md # Data collection & feature engineering strategy
│   └── racecast_project_plan.md
├── models/                 # Model artifacts
│   ├── data_collection/
│   ├── evaluation/
│   ├── preprocessing/
│   └── training/
├── notebooks/              # Jupyter notebooks for EDA
├── scripts/                # Executable scripts
│   └── collect_data.py    # Data collection script
├── src/                    # Source code
│   ├── config/            # Configuration
│   ├── data/              # Data collection modules
│   ├── features/          # Feature engineering
│   └── utils/             # Utilities
└── racecast_env/          # Virtual environment
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Activate virtual environment
source racecast_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp env.example .env
# Edit .env with your database credentials
```

### 2. Data Collection

```bash
# Collect historical data (2017-2024)
python scripts/collect_data.py

# Collect specific year range
python scripts/collect_data.py --start-year 2020 --end-year 2023

# Dry run (test without collecting)
python scripts/collect_data.py --dry-run
```

### 3. Feature Engineering

```bash
# Coming soon - feature engineering pipeline
python scripts/engineer_features.py
```

## 📊 Data Sources

### Primary Sources
- **Ergast API**: Historical race results, qualifying, standings (1950-2025)
- **FastF1**: Telemetry data, sector times, tire strategies (2018+)
- **F1 Live Pulse**: Real-time race data
- **Personality Database**: Driver psychology profiles

### Data Coverage
- **Time Range**: 2017-2024 (captures modern regulation eras)
- **Regulation Changes**: 2017 (wider cars) & 2022 (ground effect)
- **Race Types**: Grand Prix, Sprint races, Qualifying sessions

## 🔧 Technical Stack

- **Language**: Python 3.9+
- **ML Framework**: XGBoost, scikit-learn
- **Database**: Neon PostgreSQL
- **Data Processing**: pandas, numpy
- **API Clients**: requests, aiohttp
- **Logging**: loguru

## 📈 Model Strategy

### Phase 1: Baseline Model
- **Model**: XGBoost Ranker (pairwise ranking)
- **Target**: Final race position (1-20)
- **Features**: Driver form, constructor performance, track history

### Phase 2: Advanced Features
- **Telemetry**: Sector times, speed traps, tire strategies
- **Psychology**: Driver confidence, team morale
- **Strategic**: Pit window analysis, weather patterns

### Phase 3: Deep Learning
- **Sequential Models**: LSTM/GRU for lap-by-lap progression
- **Transformers**: Attention-based race sequence modeling

## 🎯 Evaluation Metrics

- **Top-3 Accuracy**: Percentage of races where top 3 predicted correctly
- **RMSE**: Root mean square error on position prediction
- **Kendall's Tau**: Correlation between predicted and actual rankings

## 📋 Development Roadmap

- [x] **Week 1**: API exploration and data availability assessment
- [ ] **Week 2**: Core data collection (2017-2024 race results)
- [ ] **Week 3**: Feature engineering pipeline development
- [ ] **Week 4**: Baseline XGBoost model training
- [ ] **Week 5**: FastF1 integration for telemetry features
- [ ] **Week 6**: Model iteration and performance optimization
- [ ] **Week 7**: Database schema and data migration
- [ ] **Week 8**: Production pipeline setup

## 🔍 Regulation Era Analysis

| Era | Years | Key Changes | Impact on Model |
|-----|-------|-------------|-----------------|
| **Pre-2017** | 2014-2016 | Hybrid engines, narrow cars | Historical baseline |
| **Wide Car Era** | 2017-2021 | Wider cars, bigger tires | Performance shift |
| **Ground Effect Era** | 2022+ | Simplified aero, ground effect | New aerodynamic paradigm |

## 📝 Contributing

1. Follow the established project structure
2. Update documentation for new features
3. Add tests for new functionality
4. Use semantic commit messages

## 📄 License

This project is for educational and research purposes.

---

*Last Updated: 2025-01-24*
