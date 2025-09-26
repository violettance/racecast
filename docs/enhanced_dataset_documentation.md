# 🏎️ Enhanced F1 Dataset Documentation

## Dataset Overview

### Purpose
The Enhanced F1 Dataset is a comprehensive machine learning-ready dataset that combines historical Formula 1 race data from Ergast API with advanced telemetry and performance metrics from FastF1 API. This dataset is specifically designed for **race position prediction** using XGBoost's ranking algorithms.

### Dataset Characteristics
- **Records**: 3,318 driver-race combinations
- **Features**: 110 total features (Ergast base + FastF1 telemetry)
- **Time Period**: 2018-2025 (8 seasons)
- **Coverage**: 166 races, 43 unique drivers
- **FastF1 Telemetry Coverage**: 71.3% of records
- **Target Variable**: `target_position` (race finish position 1-20)
- **Grouping**: `group_key` (year_round for XGBoost pairwise ranking)

### Key Use Cases
1. **Race Position Prediction**: Predict final race positions using pre-race and session data
2. **Driver Performance Analysis**: Compare driver capabilities across different conditions
3. **Strategy Optimization**: Analyze tire strategy and pit stop effectiveness
4. **Era Comparison**: Study regulation impact (2018-2021 vs 2022+ ground effect era)
5. **Weather Impact Studies**: Understand how weather affects race outcomes

---

## Data Provenance

### Data Sources

#### Ergast API (https://api.jolpi.ca/ergast/)
- **Coverage**: 2018-2025 (2017 excluded for FastF1 compatibility)
- **Records**: 3,318 driver-race combinations
- **Content**: Race results, qualifying, driver standings, constructor standings
- **Features Contributed**: ~48 base and engineered features

#### FastF1 API (https://docs.fastf1.dev/)
- **Coverage**: 2018-2025 with 71.3% telemetry availability
- **Records**: 2,366 matched driver-race combinations
- **Content**: Telemetry, strategy, weather, session data
- **Features Contributed**: ~62 advanced features

### Merge Strategy
- **Approach**: Driver-level LEFT JOIN (year + round + driver)
- **Driver Mapping**: FastF1 abbreviations (VER, HAM) → Ergast driver_ids (max_verstappen, hamilton)
- **Success Rate**: 98.9% driver mapping success
- **Race Coverage**: Weather and track conditions broadcast to all drivers in same race
- **Individual Data**: Driver-specific telemetry and performance metrics preserved

---

## Feature Dictionary

### Core Identification Features

| Feature | Type | Description | Source |
|---------|------|-------------|---------|
| `year` | int | Season year (2018-2025) | Ergast |
| `round` | int | Round number within season (1-24) | Ergast |
| `race_name` | str | Official race name (e.g., "Bahrain Grand Prix") | Ergast |
| `date` | str | Race date (YYYY-MM-DD format) | Ergast |
| `circuit_id` | str | Unique circuit identifier (e.g., "bahrain") | Ergast |
| `circuit_name` | str | Full circuit name | FastF1 |
| `event_name` | str | Event name | FastF1 |
| `driver_id` | str | Ergast driver identifier (e.g., "max_verstappen") | Ergast |
| `driver_abbreviation` | str | Three-letter driver code (e.g., "VER") | FastF1 |
| `driver_number` | int | Driver's race number | FastF1 |
| `constructor_id` | str | Team identifier (e.g., "red_bull") | Ergast |

### Target and Grouping Variables

| Feature | Type | Description | Usage |
|---------|------|-------------|--------|
| `target_position` | int | Race finish position (1-20) | **Primary target for ML** |
| `position` | int | Same as target_position | Ergast source |
| `group_key` | str | "year_round" for XGBoost grouping | **XGBoost pairwise ranking** |
| `rank` | float | Position rank (DNF = max+1) | XGBoost helper |
| `race_size` | int | Number of drivers in race | XGBoost context |
| `position_percentile` | float | Position as percentile within race | Normalized target |

### Driver Historical Performance Features

| Feature | Type | Description | Time-aware |
|---------|------|-------------|------------|
| `driver_career_wins` | int | Driver wins before this race | ✅ No future leakage |
| `driver_career_podiums` | int | Driver podiums before this race | ✅ No future leakage |
| `driver_career_total_points` | float | Career points before this race | ✅ No future leakage |
| `driver_career_avg_points` | float | Average points per race in career | ✅ Historical only |
| `driver_career_avg_position` | float | Average finish position in career | ✅ Historical only |
| `driver_career_race_count` | int | Total races completed in career | ✅ Historical only |
| `driver_win_rate` | float | Win percentage in career | ✅ Historical only |
| `driver_podium_rate` | float | Podium percentage in career | ✅ Historical only |
| `driver_points_rate` | float | Points scoring percentage | ✅ Historical only |

### Constructor Historical Performance Features

| Feature | Type | Description | Time-aware |
|---------|------|-------------|------------|
| `constructor_career_wins` | int | Constructor wins before this race | ✅ No future leakage |
| `constructor_career_podiums` | int | Constructor podiums before this race | ✅ No future leakage |
| `constructor_career_total_points` | float | Constructor points before this race | ✅ No future leakage |
| `constructor_career_avg_points` | float | Average points per race | ✅ Historical only |
| `constructor_career_avg_position` | float | Average finish position | ✅ Historical only |
| `constructor_career_race_count` | int | Total races completed | ✅ Historical only |
| `constructor_win_rate` | float | Constructor win percentage | ✅ Historical only |
| `constructor_podium_rate` | float | Constructor podium percentage | ✅ Historical only |
| `constructor_points_rate` | float | Points scoring percentage | ✅ Historical only |

### Track-Specific Performance Features

| Feature | Type | Description | Scope |
|---------|------|-------------|--------|
| `driver_track_avg_points` | float | Driver avg points at this circuit | Historical |
| `driver_track_avg_position` | float | Driver avg position at this circuit | Historical |
| `driver_track_race_count` | int | Driver races completed at this circuit | Historical |
| `constructor_track_avg_points` | float | Constructor avg points at this circuit | Historical |
| `constructor_track_avg_position` | float | Constructor avg position at this circuit | Historical |
| `constructor_track_race_count` | int | Constructor races at this circuit | Historical |

### Driver and Constructor Metadata

| Feature | Type | Description | Source |
|---------|------|-------------|---------|
| `driver_first_name` | str | Driver first name | Ergast |
| `driver_last_name` | str | Driver last name | Ergast |
| `driver_nationality` | str | Driver nationality | Ergast |
| `constructor_name` | str | Constructor full name | Ergast |
| `constructor_nationality` | str | Constructor nationality | Ergast |
| `country` | str | Race country | Ergast |

### Qualifying and Grid Features

| Feature | Type | Description | Source |
|---------|------|-------------|---------|
| `grid_position` | float | Starting grid position (1-20) | Ergast |

### Race Result Features

| Feature | Type | Description | Source |
|---------|------|-------------|---------|
| `position` | int | Final race position (same as target) | Ergast |
| `fastest_lap_time` | float | Fastest lap time in race (seconds) | FastF1 |

### Advanced Telemetry Features (FastF1-derived)

#### Lap Time Analysis
| Feature | Type | Description | Calculation |
|---------|------|-------------|-------------|
| `avg_lap_time` | float | Average lap time (seconds) | FastF1 telemetry |
| `lap_time_std` | float | Lap time standard deviation | Consistency metric |
| `total_laps` | int | Total laps completed | Race participation |
| `lap_time_efficiency` | float | Lap time performance metric | Custom calculation |
| `lap_time_consistency_score` | float | Consistency rating (0-1) | Custom metric |

#### Sector Performance
| Feature | Type | Description | Track Knowledge |
|---------|------|-------------|----------------|
| `avg_sector1_time` | float | Average sector 1 time (seconds) | Corner performance |
| `avg_sector2_time` | float | Average sector 2 time (seconds) | Middle sector speed |
| `avg_sector3_time` | float | Average sector 3 time (seconds) | Final sector execution |
| `total_sector_time` | float | Sum of all sector times | Overall pace |
| `sector1_dominance` | float | Sector 1 relative performance | Strength indicator |
| `sector2_dominance` | float | Sector 2 relative performance | Mid-track ability |
| `sector3_dominance` | float | Sector 3 relative performance | Closing speed |

#### Speed Metrics
| Feature | Type | Description | Performance Indicator |
|---------|------|-------------|----------------------|
| `max_speed` | float | Maximum speed reached (km/h) | Top speed capability |
| `avg_speed` | float | Average speed throughout race | Overall pace |
| `speed_variance` | float | Speed variation across laps | Consistency |
| `speed_consistency` | float | Speed consistency metric (0-1) | Stability |
| `speed_efficiency` | float | Speed efficiency rating | Performance |

### Weather and Track Conditions

#### Environmental Data
| Feature | Type | Description | Impact |
|---------|------|-------------|--------|
| `air_temp` | float | Air temperature (°C) | Engine/tire performance |
| `track_temp` | float | Track surface temperature (°C) | Tire degradation |
| `humidity` | float | Relative humidity (%) | Grip conditions |
| `wind_speed` | float | Wind speed (km/h) | Aerodynamic impact |
| `temp_differential` | float | Track - Air temperature difference | Condition severity |

#### Weather Impact Flags
| Feature | Type | Description | Threshold |
|---------|------|-------------|-----------|
| `is_hot_conditions` | bool | High temperature race | Air temp > 30°C |
| `is_cold_conditions` | bool | Low temperature race | Air temp < 15°C |
| `is_high_track_temp` | bool | Hot track surface | Track temp > 45°C |
| `is_high_humidity` | bool | Humid conditions | Humidity > 70% |
| `is_low_humidity` | bool | Dry conditions | Humidity < 40% |
| `is_windy_conditions` | bool | Windy race | Wind > 20 km/h |

### Tire Strategy and Pit Stops

#### Compound Selection
| Feature | Type | Description | Strategy Impact |
|---------|------|-------------|----------------|
| `main_compound` | str | Primary tire compound used | Strategy choice |
| `compound_changes` | int | Number of compound changes | Strategy complexity |
| `compound_changes_normalized` | float | Compound changes relative to race avg | Strategic aggressiveness |

#### Compound Flags
| Feature | Type | Description | Usage |
|---------|------|-------------|--------|
| `is_soft_primary` | bool | Used soft as primary compound | Aggressive strategy |
| `is_hard_primary` | bool | Used hard as primary compound | Conservative strategy |
| `is_medium_primary` | bool | Used medium as primary compound | Balanced strategy |
| `is_intermediate` | bool | Used intermediate tires | Wet conditions |
| `is_wet` | bool | Used wet weather tires | Rain conditions |

#### Pit Stop Strategy
| Feature | Type | Description | Strategic Indicator |
|---------|------|-------------|-------------------|
| `pit_stops` | int | Total number of pit stops | Strategy choice |
| `pit_stops_normalized` | float | Pit stops relative to race average | Strategic position |
| `low_pit_strategy` | bool | Fewer pit stops than average | Undercut strategy |
| `aggressive_pit_strategy` | bool | More pit stops than average | Overcut strategy |

### Era and Regulation Features

#### Regulation Periods
| Feature | Type | Description | Significance |
|---------|------|-------------|--------------|
| `is_2017_plus_era` | bool | 2017+ wider cars regulations | Wider aero package |
| `is_2018_2021_era` | bool | Pre-ground effect regulations | Old aero rules |
| `is_2022_plus_era` | bool | Ground effect era (2022+) | New aero package |
| `is_2022_plus_era_fastf1` | bool | FastF1 version of 2022+ flag | Source tracking |
| `is_covid_season_2020` | bool | COVID-affected 2020 season | Unique circumstances |
| `is_covid_season_2020_fastf1` | bool | FastF1 version of COVID flag | Source tracking |
| `has_sprint_format` | bool | Weekend includes sprint race | Different format |
| `has_sprint_format_fastf1` | bool | FastF1 version of sprint flag | Source tracking |

#### Era-Adjusted Performance
| Feature | Type | Description | Normalization |
|---------|------|-------------|---------------|
| `era_adjusted_speed` | float | Speed adjusted for regulation era | Cross-era comparison |
| `era_adjusted_laps` | float | Lap count adjusted for era | Format normalization |

### Relative Performance Metrics

#### Race Comparison Features
| Feature | Type | Description | Benchmark |
|---------|------|-------------|-----------|
| `avg_lap_time_vs_race_avg` | float | Lap time relative to race average | Performance vs field |
| `avg_lap_time_vs_race_best` | float | Lap time relative to race best | Performance vs winner |
| `avg_lap_time_rank_in_race` | int | Lap time ranking within race | Pace ranking |
| `max_speed_vs_race_avg` | float | Max speed relative to race average | Speed vs field |
| `max_speed_vs_race_best` | float | Max speed relative to race best | Speed vs fastest |
| `max_speed_rank_in_race` | int | Max speed ranking within race | Speed ranking |
| `avg_speed_vs_race_avg` | float | Avg speed relative to race average | Overall pace vs field |
| `avg_speed_vs_race_best` | float | Avg speed relative to race best | Overall pace vs best |
| `avg_speed_rank_in_race` | int | Avg speed ranking within race | Pace position |

#### Position Change Analysis
| Feature | Type | Description | Race Dynamics |
|---------|------|-------------|---------------|
| `grid_to_finish_change` | int | Position change from grid to finish | Overall performance |
| `position_gained` | int | Positions gained during race | Positive movement |
| `position_lost` | int | Positions lost during race | Performance decline |

### Data Quality and Availability

| Feature | Type | Description | Usage |
|---------|------|-------------|--------|
| `has_fastf1_data` | bool | Whether FastF1 telemetry is available | Missing data indicator |

---

## Preprocessing Notes

### Feature Engineering Pipeline

#### 1. Historical Aggregations (Time-aware)
- **No Future Leakage**: All historical features calculated using only data from races BEFORE the current race
- **Rolling Windows**: Career and season statistics updated incrementally
- **Track History**: Circuit-specific performance based on previous races at same venue

#### 2. Relative Performance Calculations
- **Race-level Benchmarks**: Each performance metric compared to race average and race best
- **Ranking Within Race**: Position of each driver's metric within the specific race
- **Percentile Calculations**: Performance expressed as percentile within race field

#### 3. Era-aware Normalization
- **Regulation Adjustment**: Performance metrics adjusted for regulation era differences
- **COVID Impact**: Special handling for 2020 season anomalies
- **Sprint Format**: Weekend format variations accounted for

#### 4. Weather Impact Features
- **Threshold-based Flags**: Weather conditions categorized using empirical thresholds
- **Differential Calculations**: Temperature differences that affect tire performance
- **Condition Severity**: Multi-factor weather impact assessment

#### 5. Strategy Analysis
- **Compound Optimization**: Tire choice analysis relative to optimal strategy
- **Pit Window Analysis**: Stop timing relative to strategic windows
- **Normalized Metrics**: Strategy choices relative to race average

### Data Quality Assurance

#### Missing Data Handling
- **FastF1 Availability**: 71.3% of records have complete telemetry (`has_fastf1_data` flag)
- **Primary Missing Features**: 
  - `driver_abbreviation`, `driver_number`: 28.7% missing (FastF1 unavailable races)
  - `fastest_lap_time`, `avg_lap_time`: ~30% missing (telemetry unavailable)
  - `max_speed`, sector times: ~30% missing (telemetry unavailable)
- **Graceful Degradation**: Missing telemetry indicated by `has_fastf1_data=False`
- **Core Features Complete**: All Ergast-derived features have 100% coverage
- **Missing Pattern**: Missing data correlates with FastF1 availability, not random

#### Validation Steps
1. **Temporal Consistency**: No future data used in historical features
2. **Range Validation**: All metrics within realistic F1 performance ranges
3. **Cross-source Validation**: Ergast and FastF1 data consistency checks
4. **Outlier Detection**: Statistical outliers flagged and verified

#### Data Types and Formats
- **Numeric Features**: Float64 for continuous metrics, Int64 for counts
- **Categorical Features**: String format for identifiers and compound types
- **Boolean Flags**: Explicit boolean type for binary indicators
- **Missing Values**: NaN for genuinely missing data, 0.0 for structural zeros

---

## Usage Recommendations

### XGBoost Configuration
```python
# Recommended XGBoost parameters for this dataset
params = {
    'objective': 'rank:pairwise',  # Pairwise ranking for position prediction
    'eval_metric': 'ndcg',         # Normalized Discounted Cumulative Gain
    'group_col': 'group_key',      # Group by year_round
    'target_col': 'target_position' # Predict race finish position
}
```

### Train/Test Split Strategy
- **Temporal Split**: Use 2018-2023 for training, 2024 for testing, 2025 for live prediction
- **Group Preservation**: Never split races (maintain group_key integrity)
- **Era Balance**: Ensure both regulation eras represented in training

### Feature Selection Guidelines
1. **Core Features**: Always include driver_id, constructor_id, grid_position
2. **Historical Features**: Essential for driver/team performance context
3. **Telemetry Features**: Use when has_fastf1_data=True for enhanced predictions
4. **Weather Features**: Critical for strategy and performance modeling
5. **Era Features**: Important for cross-regulation period analysis

### Performance Expectations
- **Baseline Accuracy**: >50% (better than random)
- **Enhanced Target**: 65-70% position prediction accuracy
- **FastF1 Boost**: Expect 5-10% improvement when telemetry available
- **Model Complexity**: 110 features support complex non-linear relationships

---

*Dataset Documentation Version 1.0*  
*Generated: 2025-09-26*  
*Data Range: 2018-2025*  
*Total Records: 3,318*  
*Features: 110*
