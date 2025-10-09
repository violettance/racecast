# 🏎️ RaceCast - Formula 1 Prediction System

A complete machine learning system for predicting Formula 1 race results using historical data, telemetry, and advanced feature engineering. Features a trained XGBoost model, FastAPI backend, and comprehensive data pipeline.

## 📁 Project Structure

```
racecast/
├── data/                    # Data storage
│   ├── raw/                # Raw data from APIs
│   ├── processed/          # Processed feature data
│   │   └── xgboost/        # Final model dataset
│   └── fastf1_cache/       # FastF1 telemetry cache
├── docs/                   # Documentation
│   ├── data_methodology.md # Data collection & feature engineering strategy
│   ├── racecast_project_plan.md # Project roadmap
│   ├── frontend_integration_runbook.md # Frontend integration guide
│   └── enhanced_dataset_documentation.md # Dataset details
├── models/                 # Model artifacts
│   └── xgboost/           # Trained XGBoost models
│       ├── xgboost_model.pkl
│       ├── xgboost_ranker_model.pkl
│       └── label_encoders.pkl
├── notebooks/              # Jupyter notebooks for EDA & training
│   ├── 01_data_exploration.ipynb
│   ├── 02_fastf1_data_exploration.ipynb
│   ├── 03_eda_final_dataset.ipynb
│   ├── 04_manual_eda_final_dataset.ipynb
│   └── 05_xgboost_model.ipynb
├── scripts/                # Executable scripts
│   ├── collect_data.py    # Data collection script
│   └── predict_singapore_2025.py # Prediction example
├── src/                    # Source code
│   ├── api/               # FastAPI backend
│   │   └── main.py        # API endpoints
│   ├── config/            # Configuration
│   ├── data/              # Data collection modules
│   ├── features/          # Feature engineering
│   ├── services/          # ML prediction service
│   ├── db/                # Database models & session
│   └── utils/             # Utilities
├── results/                # Prediction outputs
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
├── Procfile              # Back4App deployment config
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

### 3. Model Training

```bash
# Run the complete training pipeline
jupyter notebook notebooks/05_xgboost_model.ipynb

# Or run prediction example
python scripts/predict_singapore_2025.py
```

### 4. Backend API

```bash
# Start FastAPI server
uvicorn src.api.main:app --reload

# Test health endpoint
curl http://localhost:8000/healthz

# Make prediction (requires API key if set)
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"year": 2025, "round": 19, "persist": true}'
```

### 5. Docker Deployment

```bash
# Build Docker image
docker build -t racecast-backend .

# Run locally with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:port/db" \
  -e API_KEY="your_api_key" \
  racecast-backend

# Deploy to Back4App (see docs/deploy_back4app.md)
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
- **Backend**: FastAPI, uvicorn
- **Database**: Neon PostgreSQL (SQLAlchemy ORM)
- **Data Processing**: pandas, numpy
- **API Clients**: requests, aiohttp
- **Logging**: loguru
- **Deployment**: Docker, Back4App

## 📈 Model Strategy

### ✅ Phase 1: Baseline Model (COMPLETED)
- **Model**: XGBoost Ranker (pairwise ranking)
- **Target**: Final race position (1-20)
- **Features**: Driver form, constructor performance, track history, qualifying position
- **Performance**: Top-3 accuracy ~60-70%, trained on 2018-2024 data

![Model Performance](images/model_performance.png)

### ✅ Phase 2: Advanced Features (COMPLETED)
- **Telemetry**: Sector times, speed traps, tire strategies (FastF1 integration)
- **Psychology**: Driver confidence, team morale (driver personality data)
- **Strategic**: Pit window analysis, weather patterns
- **Data**: Enhanced dataset with 50+ features including telemetry and psychological profiles

### 🔮 Phase 3: Deep Learning (FUTURE)
- **Sequential Models**: LSTM/GRU for lap-by-lap progression
- **Transformers**: Attention-based race sequence modeling

## 🎯 Evaluation Metrics

- **Top-3 Accuracy**: Percentage of races where top 3 predicted correctly
- **RMSE**: Root mean square error on position prediction
- **Kendall's Tau**: Correlation between predicted and actual rankings

## 📋 Development Roadmap

- [x] **Week 1**: API exploration and data availability assessment
- [x] **Week 2**: Core data collection (2017-2024 race results)
- [x] **Week 3**: Feature engineering pipeline development
- [x] **Week 4**: Baseline XGBoost model training
- [x] **Week 5**: FastF1 integration for telemetry features
- [x] **Week 6**: Model iteration and performance optimization
- [x] **Week 7**: Database schema and data migration
- [x] **Week 8**: Production pipeline setup
- [x] **Backend API**: FastAPI with prediction endpoints
- [x] **Database**: Neon PostgreSQL with predictions/results tables
- [x] **Docker**: Containerization and Back4App deployment
- [x] **Documentation**: Frontend integration guide
- [ ] **Frontend**: Next.js dashboard (separate repo)
- [ ] **Automation**: GitHub Actions for race weekend predictions

## 🔍 Regulation Era Analysis

| Era | Years | Key Changes | Impact on Model |
|-----|-------|-------------|-----------------|
| **Pre-2017** | 2014-2016 | Hybrid engines, narrow cars | Historical baseline |
| **Wide Car Era** | 2017-2021 | Wider cars, bigger tires | Performance shift |
| **Ground Effect Era** | 2022+ | Simplified aero, ground effect | New aerodynamic paradigm |

## 🚀 API Endpoints

### Health Check
- `GET /healthz` - Check API status and model loading

### Predictions
- `GET /predictions?year={YYYY}&round={R}` - Get predictions for a race
- `POST /predict` - Generate and optionally save predictions
- `POST /update_results` - Fetch and save actual race results

### Example Usage
```bash
# Get predictions for 2025 US Grand Prix
curl "https://your-backend.com/predictions?year=2025&round=19"

# Generate predictions (requires API key)
curl -X POST "https://your-backend.com/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY" \
  -d '{"year": 2025, "round": 19, "persist": true}'
```

## 📚 Documentation

- [Project Plan](docs/racecast_project_plan.md) - Overall project roadmap
- [Data Methodology](docs/data_methodology.md) - Data collection and feature engineering
- [Frontend Integration](docs/frontend_integration_runbook.md) - API contract and frontend setup
- [Enhanced Dataset](docs/enhanced_dataset_documentation.md) - Detailed dataset documentation

## 📝 Contributing

1. Follow the established project structure
2. Update documentation for new features
3. Add tests for new functionality
4. Use semantic commit messages

## 📄 License

This project is for educational and research purposes.

---

*Last Updated: 2025-01-24*
