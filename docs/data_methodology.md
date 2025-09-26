# 🏎️ RaceCast Data Methodology & Feature Engineering Strategy

## 📊 Data Collection Strategy

### Historical Data Scope
- **Time Range**: 2017-2024 (8 seasons)
- **Rationale**: Captures modern F1 era with comprehensive regulation changes

### Regulation Era Analysis
Understanding major technical regulation changes that affect performance patterns:

| **Aspect** | **2017 Changes** | **2022 Changes** |
|------------|------------------|------------------|
| **Car Dimensions** | Total car width increased. Front tires: 305mm, Rear tires: 405mm (wider) | Simplified car geometry. Limited aero devices. Ground effect-focused design |
| **Tires** | Much wider tires: Front 305mm, Rear 405mm | Wheel diameter: 13" → 18". Improved tire structure and compounds |
| **Weight & Fuel** | Minimum weight increased. Fuel limit: 100kg → 105kg | Heavier cars continue. Aero simplification, downforce via ground effect |
| **Aerodynamics** | New limits on front/rear wings, diffusers. More aggressive bargeboard designs allowed | Aero complexity heavily limited. Front/rear wings simplified. Bargeboards removed. Ground effect emphasized |
| **Brakes** | Exotic brake caliper materials banned. Simpler material usage | No major brake material changes. Focus remained on aero and ground behavior |
| **Development Limits** | Power unit development token system removed. Part usage limits restructured | "Sliding scale" aero testing system (wind tunnel/CFD) - unsuccessful teams get more testing time |
| **Ground Effect** | Classic aero devices primary. Ground effect not main design focus | Ground effect reintroduced as primary design philosophy. Underfloor aerodynamics critical |

### Primary Data Sources

#### 1. Ergast API (Historical Racing Data)
**Coverage**: 1950-2025 (76 seasons total)  
**Available Data Types**:
- ✅ Race Results (position, points, lap times, fastest lap)
- ✅ Qualifying Results (Q1, Q2, Q3 times)
- ✅ Driver/Constructor Standings
- ✅ Circuit Information (location, characteristics)
- ✅ Sprint Results
- ✅ Pit Stop Data
- ✅ Lap-by-Lap Data

**Data Quality**: 
- Millisecond precision timing data
- Complete driver profiles (name, nationality, DOB, permanent number)
- Constructor details (team name, nationality)
- Grid positions, lap counts, retirement reasons

#### 2. FastF1 API (Telemetry & Advanced Data)
**Coverage**: 2018-present  
**Planned Data Types**:
- 🔄 Sector times and mini-sector data
- 🔄 Speed trap data
- 🔄 Tire compound usage
- 🔄 Weather conditions
- 🔄 Track temperature
- 🔄 Session-specific telemetry

#### 3. F1 Live Pulse API (Real-time Data)
**Coverage**: Current seasons  
**Planned Data Types**:
- 🔄 Live timing data
- 🔄 Radio communications
- 🔄 Strategic decisions
- 🔄 Pit window analysis

#### 4. Social/Psychology Data Sources
**Coverage**: 2020-present (planned)  
**Planned Data Types**:
- 🔄 Driver personality profiles (Personality Database)
- 🔄 Social media sentiment
- 🔄 Media hype metrics
- 🔄 Team dynamics indicators

## 🔧 Feature Engineering Framework

### A. Core Performance Features

#### A1. Driver Performance Metrics
- **Recent Form**: Last 5 races average position
- **Track Familiarity**: Historical performance at specific circuit
- **Qualifying vs Race Performance**: Grid position improvement/decline
- **Consistency Score**: Standard deviation of finishing positions
- **Wet Weather Performance**: Performance in rain conditions
- **Pressure Handling**: Performance when championship is at stake

#### A2. Constructor Performance Metrics
- **Team Form**: Last 5 races average constructor points
- **Development Trajectory**: Performance improvement over season
- **Reliability Score**: DNF rate and mechanical failure frequency
- **Strategic Competence**: Pit stop efficiency and strategy success rate
- **Aero Package Effectiveness**: Track-specific performance patterns

#### A3. Circuit-Specific Features
- **Track Characteristics**: Length, corners, elevation changes
- **Power Unit Sensitivity**: Straight-line speed importance
- **Tire Degradation Patterns**: Historical tire wear rates
- **Overtaking Difficulty**: DRS zones and passing opportunities
- **Weather Patterns**: Historical weather probability

### B. Advanced Features (Phase 2)

#### B1. Telemetry-Derived Features
- **Sector Performance Breakdown**: S1, S2, S3 relative performance
- **Braking Performance**: Late braking capability
- **Cornering Speed**: Through specific corner types
- **Energy Management**: ERS deployment efficiency

#### B2. Strategic Features
- **Tire Strategy Optimization**: Compound selection effectiveness
- **Pit Window Timing**: Optimal vs actual pit timing
- **Race Pace vs Qualifying Pace**: Long-run performance prediction
- **Safety Car Probability**: Historical SC likelihood per track

#### B3. Psychological/Social Features
- **Driver Confidence**: Recent media sentiment
- **Team Morale**: Social media engagement patterns
- **Pressure Index**: Championship standings pressure
- **Rivalry Impact**: Head-to-head historical performance

## 📈 Model Development Pipeline

### Phase 1: Baseline Model (XGBoost)
**Target Variable**: Final race position (1-20)  
**Model Type**: XGBoost Ranker (pairwise ranking)  
**Evaluation Metrics**:
- Top-3 accuracy
- RMSE on position prediction
- Kendall's Tau correlation

### Phase 2: Advanced Models
**Alternative Approaches**:
- LightGBM (faster training, larger datasets)
- Bayesian models (uncertainty quantification)
- Neural networks (complex pattern recognition)

### Phase 3: Sequential Models (Future)
**For Telemetry Data**:
- LSTM/GRU (lap-by-lap progression)
- Transformer models (attention-based racing sequences)

## 🗄️ Data Storage Strategy

### Neon PostgreSQL Schema Design
```sql
-- Core Tables
races          -- Race metadata, circuit info, weather
drivers        -- Driver profiles, career stats
constructors   -- Team information, technical specs
results        -- Historical race results
qualifying     -- Qualifying session results
telemetry      -- Lap-by-lap and sector data
predictions    -- Model predictions with confidence
evaluations    -- Model performance tracking
```

### Data Pipeline Architecture
```
Raw Data (CSV) → Data Validation → Feature Engineering → Neon DB → Model Training
                      ↓                    ↓              ↓           ↓
                 Anomaly Detection    Feature Store   Real-time API  Performance Monitoring
```

## 📝 Methodology Notes

### Data Quality Considerations
1. **Regulation Era Segmentation**: Models may need era-specific training
2. **Missing Data Handling**: Imputation strategies for incomplete telemetry
3. **Outlier Detection**: Identify and handle unusual race circumstances
4. **Feature Scaling**: Normalization for different measurement units

### Validation Strategy
1. **Time-based Split**: Train on early seasons, validate on recent seasons
2. **Cross-validation**: Stratified by track and weather conditions
3. **Walk-forward Analysis**: Simulate real-time prediction scenarios

### Bias Mitigation
1. **Regulation Era Weighting**: Adjust importance of older data
2. **Track Diversity**: Ensure balanced representation across circuit types
3. **Weather Conditions**: Account for varying weather patterns

---

## 📅 Implementation Timeline

- [x] **Week 1**: Ergast API exploration and data availability assessment
- [ ] **Week 2**: Core data collection (2017-2024 race results, qualifying)
- [ ] **Week 3**: Feature engineering pipeline development
- [ ] **Week 4**: Baseline XGBoost model training and evaluation
- [ ] **Week 5**: FastF1 integration for telemetry features
- [ ] **Week 6**: Model iteration and performance optimization
- [ ] **Week 7**: Database schema implementation and data migration
- [ ] **Week 8**: Production pipeline setup and validation

---

## 🔍 Current Status

### Completed
- [x] Ergast API comprehensive analysis
- [x] Data source mapping and availability assessment
- [x] Regulation era documentation and analysis framework

### In Progress
- [ ] Data collection script development
- [ ] Feature engineering pipeline design

### Next Steps
1. Implement data collection scripts for Ergast API
2. Design and test feature engineering functions
3. Set up development environment with required Python packages
4. Create initial data validation and quality checks

---

*Last Updated: 2025-01-24*  
*Next Review: After Phase 1 data collection completion*
