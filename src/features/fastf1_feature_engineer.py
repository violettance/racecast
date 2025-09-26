"""
FastF1 Feature Engineering Pipeline
Creates advanced telemetry and strategy features for F1 race prediction.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from src.config.settings import settings


class FastF1FeatureEngineer:
    """Feature engineering pipeline for FastF1 telemetry data."""
    
    def __init__(self):
        self.data_dir = settings.RAW_DATA_DIR
        self.processed_dir = settings.PROCESSED_DATA_DIR
        self.processed_dir.mkdir(exist_ok=True)
        
    def load_fastf1_data(self) -> pd.DataFrame:
        """Load FastF1 complete dataset."""
        fastf1_path = self.data_dir / 'fastf1_features_2018_2025_complete.csv'
        df = pd.read_csv(fastf1_path)
        print(f"📊 FastF1 data loaded: {df.shape}")
        return df
    
    def create_performance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create performance-based features from telemetry data."""
        df = df.copy()
        
        # Speed features
        df['speed_consistency'] = df['avg_speed'] / df['max_speed']  # How close avg to max
        df['speed_efficiency'] = df['avg_speed'] / df['avg_lap_time']  # Speed per lap time
        
        # Sector performance
        df['total_sector_time'] = df['avg_sector1_time'] + df['avg_sector2_time'] + df['avg_sector3_time']
        df['sector1_dominance'] = df['avg_sector1_time'] / df['total_sector_time']
        df['sector2_dominance'] = df['avg_sector2_time'] / df['total_sector_time'] 
        df['sector3_dominance'] = df['avg_sector3_time'] / df['total_sector_time']
        
        # Lap time performance
        df['lap_time_efficiency'] = df['fastest_lap_time'] / df['avg_lap_time']  # Best vs avg
        df['lap_time_consistency_score'] = 1 / (df['lap_time_std'] + 0.001)  # Lower std = higher score
        
        return df
    
    def create_strategy_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create tire strategy and pit stop features."""
        df = df.copy()
        
        # Tire strategy
        df['is_soft_primary'] = (df['main_compound'] == 'SOFT').astype(int)
        df['is_hard_primary'] = (df['main_compound'] == 'HARD').astype(int)
        df['is_medium_primary'] = (df['main_compound'] == 'MEDIUM').astype(int)
        df['is_intermediate'] = (df['main_compound'] == 'INTERMEDIATE').astype(int)
        df['is_wet'] = (df['main_compound'] == 'WET').astype(int)
        
        # Advanced tire features
        df['compound_changes_normalized'] = df['compound_changes'] / df['total_laps']
        df['pit_stops_normalized'] = df['pit_stops'] / df['total_laps']
        
        # Strategy effectiveness
        df['low_pit_strategy'] = (df['pit_stops'] <= 1).astype(int)
        df['aggressive_pit_strategy'] = (df['pit_stops'] >= 3).astype(int)
        
        return df
    
    def create_weather_impact_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create weather-related performance features."""
        df = df.copy()
        
        # Temperature features
        df['temp_differential'] = df['track_temp'] - df['air_temp']
        df['is_hot_conditions'] = (df['air_temp'] > 25).astype(int)
        df['is_cold_conditions'] = (df['air_temp'] < 15).astype(int)
        df['is_high_track_temp'] = (df['track_temp'] > 35).astype(int)
        
        # Humidity impact
        df['is_high_humidity'] = (df['humidity'] > 70).astype(int)
        df['is_low_humidity'] = (df['humidity'] < 40).astype(int)
        
        # Wind impact
        df['is_windy_conditions'] = (df['wind_speed'] > 15).astype(int)
        
        return df
    
    def create_era_aware_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create regulation era-aware features based on years."""
        df = df.copy()
        
        # Regulation eras (same as Ergast)
        df['is_2018_2021_era'] = ((df['year'] >= 2018) & (df['year'] <= 2021)).astype(int)
        df['is_2022_plus_era'] = (df['year'] >= 2022).astype(int)
        df['is_covid_season_2020'] = (df['year'] == 2020).astype(int)
        df['has_sprint_format'] = (df['year'] >= 2021).astype(int)
        
        # Era-specific performance adjustments
        # 2022+ cars are heavier and different aero
        df['era_adjusted_speed'] = df['max_speed'].copy()
        df.loc[df['year'] >= 2022, 'era_adjusted_speed'] *= 0.98  # Slightly slower in new era
        
        # COVID season had shorter races
        df['era_adjusted_laps'] = df['total_laps'].copy()
        df.loc[df['year'] == 2020, 'era_adjusted_laps'] *= 1.1  # Normalize for shorter season
        
        return df
    
    def create_relative_performance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create relative performance features within races."""
        df = df.copy()
        
        # Performance relative to race
        for metric in ['avg_lap_time', 'max_speed', 'avg_speed']:
            if metric in df.columns:
                race_groups = df.groupby(['year', 'round'])[metric]
                df[f'{metric}_vs_race_avg'] = df[metric] / race_groups.transform('mean')
                df[f'{metric}_vs_race_best'] = df[metric] / race_groups.transform('min')
                df[f'{metric}_rank_in_race'] = race_groups.rank(ascending=(metric == 'avg_lap_time'))
        
        # Position gained/lost
        df['grid_to_finish_change'] = df['grid_position'] - df['position']
        df['position_gained'] = np.maximum(0, df['grid_to_finish_change'])
        df['position_lost'] = np.maximum(0, -df['grid_to_finish_change'])
        
        return df
    
    def build_fastf1_features(self) -> pd.DataFrame:
        """Build complete FastF1 feature set."""
        print("🔧 Starting FastF1 feature engineering...")
        
        # Load data
        df = self.load_fastf1_data()
        
        # Apply feature engineering steps
        df = self.create_performance_features(df)
        print("✅ Performance features created")
        
        df = self.create_strategy_features(df)
        print("✅ Strategy features created")
        
        df = self.create_weather_impact_features(df)
        print("✅ Weather impact features created")
        
        df = self.create_era_aware_features(df)
        print("✅ Era-aware features created")
        
        df = self.create_relative_performance_features(df)
        print("✅ Relative performance features created")
        
        print(f"🏆 FastF1 feature engineering complete: {df.shape}")
        return df
    
    def save_fastf1_features(self, df: pd.DataFrame, filename: str = 'fastf1_features_engineered.csv'):
        """Save engineered FastF1 features."""
        output_path = self.processed_dir / filename
        df.to_csv(output_path, index=False)
        print(f"💾 FastF1 features saved to: {output_path}")
        
        # Print feature summary
        print(f"\n📊 FastF1 Feature Summary:")
        print(f"Shape: {df.shape}")
        print(f"Years: {df['year'].min()} - {df['year'].max()}")
        print(f"Unique drivers: {df['driver_abbreviation'].nunique()}")
        print(f"Missing values: {df.isnull().sum().sum()}")
        
        return output_path


def main():
    """Main execution function."""
    engineer = FastF1FeatureEngineer()
    
    # Build FastF1 features
    fastf1_features = engineer.build_fastf1_features()
    
    # Save engineered features
    output_path = engineer.save_fastf1_features(fastf1_features)
    
    print(f"\n🎉 FastF1 feature engineering completed!")
    print(f"📁 Output file: {output_path}")
    
    return fastf1_features


if __name__ == "__main__":
    features = main()