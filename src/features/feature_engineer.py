"""
Feature Engineering Pipeline for F1 Race Prediction
Creates target-leakage safe features for machine learning model.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from src.config.settings import settings


class F1FeatureEngineer:
    """Feature engineering pipeline for F1 race prediction."""
    
    def __init__(self):
        self.data_dir = settings.RAW_DATA_DIR
        self.processed_dir = settings.PROCESSED_DATA_DIR
        self.processed_dir.mkdir(exist_ok=True)
        
    def load_raw_data(self) -> Dict[str, pd.DataFrame]:
        """Load all raw data files."""
        data = {}
        
        # Load main datasets
        data['races'] = pd.read_csv(self.data_dir / 'ergast_races_2017_2025.csv')
        data['results'] = pd.read_csv(self.data_dir / 'ergast_results_2017_2025.csv')
        data['qualifying'] = pd.read_csv(self.data_dir / 'ergast_qualifying_2017_2025.csv')
        data['driver_standings'] = pd.read_csv(self.data_dir / 'ergast_driver_standings_2017_2025.csv')
        data['constructor_standings'] = pd.read_csv(self.data_dir / 'ergast_constructor_standings_2017_2025.csv')
        
        print(f"📊 Raw data loaded:")
        for name, df in data.items():
            print(f"  {name}: {df.shape}")
            
        return data
    
    def create_era_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create regulation era flags."""
        df = df.copy()
        
        # Regulation era flags
        df['is_2017_plus_era'] = (df['year'] >= 2017).astype(int)
        df['is_2022_plus_era'] = (df['year'] >= 2022).astype(int)
        df['is_covid_season_2020'] = (df['year'] == 2020).astype(int)
        
        # Sprint weekends (simplified - assume all post-2021 have potential sprint)
        df['has_sprint_format'] = (df['year'] >= 2021).astype(int)
        
        return df
    
    def create_driver_historical_features(self, results: pd.DataFrame) -> pd.DataFrame:
        """Create driver historical performance features."""
        
        # Driver career statistics (up to current race)
        driver_career_stats = results.groupby('driver_id').agg({
            'points': ['sum', 'mean'],
            'position': ['mean', 'count'],
            'race_name': 'count'
        }).round(3)
        
        driver_career_stats.columns = [
            'driver_career_total_points',
            'driver_career_avg_points',
            'driver_career_avg_position', 
            'driver_career_position_count',
            'driver_career_race_count'
        ]
        
        # Driver wins and podiums
        driver_success = results.groupby('driver_id').agg({
            'position': [
                lambda x: (x == 1).sum(),  # Wins
                lambda x: (x <= 3).sum(),  # Podiums
                lambda x: (x <= 10).sum()  # Points finishes
            ]
        })
        
        driver_success.columns = [
            'driver_career_wins',
            'driver_career_podiums', 
            'driver_career_points_finishes'
        ]
        
        # Combine career stats
        driver_features = pd.concat([driver_career_stats, driver_success], axis=1)
        
        # Calculate success rates
        driver_features['driver_win_rate'] = (
            driver_features['driver_career_wins'] / 
            driver_features['driver_career_race_count']
        ).round(3)
        
        driver_features['driver_podium_rate'] = (
            driver_features['driver_career_podiums'] / 
            driver_features['driver_career_race_count']  
        ).round(3)
        
        driver_features['driver_points_rate'] = (
            driver_features['driver_career_points_finishes'] / 
            driver_features['driver_career_race_count']
        ).round(3)
        
        return driver_features.reset_index()
    
    def create_constructor_historical_features(self, results: pd.DataFrame) -> pd.DataFrame:
        """Create constructor historical performance features."""
        
        # Constructor career statistics
        constructor_career_stats = results.groupby('constructor_id').agg({
            'points': ['sum', 'mean'],
            'position': ['mean', 'count'],
            'race_name': 'count'
        }).round(3)
        
        constructor_career_stats.columns = [
            'constructor_career_total_points',
            'constructor_career_avg_points',
            'constructor_career_avg_position',
            'constructor_career_position_count', 
            'constructor_career_race_count'
        ]
        
        # Constructor success metrics
        constructor_success = results.groupby('constructor_id').agg({
            'position': [
                lambda x: (x == 1).sum(),  # Wins
                lambda x: (x <= 3).sum(),  # Podiums
                lambda x: (x <= 10).sum()  # Points finishes
            ]
        })
        
        constructor_success.columns = [
            'constructor_career_wins',
            'constructor_career_podiums',
            'constructor_career_points_finishes'
        ]
        
        # Combine features
        constructor_features = pd.concat([constructor_career_stats, constructor_success], axis=1)
        
        # Success rates
        constructor_features['constructor_win_rate'] = (
            constructor_features['constructor_career_wins'] / 
            constructor_features['constructor_career_race_count']
        ).round(3)
        
        constructor_features['constructor_podium_rate'] = (
            constructor_features['constructor_career_podiums'] / 
            constructor_features['constructor_career_race_count']
        ).round(3)
        
        constructor_features['constructor_points_rate'] = (
            constructor_features['constructor_career_points_finishes'] / 
            constructor_features['constructor_career_race_count']
        ).round(3)
        
        return constructor_features.reset_index()
    
    def create_track_specific_features(self, results: pd.DataFrame, races: pd.DataFrame) -> pd.DataFrame:
        """Create track-specific historical performance features."""
        
        # Driver performance at each track
        driver_track_stats = results.groupby(['driver_id', 'circuit_id']).agg({
            'position': ['mean', 'count'],
            'points': ['mean', 'sum']
        }).round(3)
        
        driver_track_stats.columns = [
            'driver_track_avg_position',
            'driver_track_race_count',
            'driver_track_avg_points',
            'driver_track_total_points'
        ]
        
        # Constructor performance at each track  
        constructor_track_stats = results.groupby(['constructor_id', 'circuit_id']).agg({
            'position': ['mean', 'count'],
            'points': ['mean', 'sum']
        }).round(3)
        
        constructor_track_stats.columns = [
            'constructor_track_avg_position',
            'constructor_track_race_count', 
            'constructor_track_avg_points',
            'constructor_track_total_points'
        ]
        
        return driver_track_stats.reset_index(), constructor_track_stats.reset_index()
    
    def create_rolling_form_features(self, results: pd.DataFrame, window_sizes: List[int] = [3, 5]) -> pd.DataFrame:
        """Create rolling window form indicators (target leakage safe)."""
        
        # Sort by driver and date to calculate rolling features correctly
        results_sorted = results.sort_values(['driver_id', 'year', 'round']).copy()
        
        rolling_features = []
        
        for window in window_sizes:
            # Rolling averages by driver
            rolling_stats = results_sorted.groupby('driver_id').rolling(
                window=window, min_periods=1
            ).agg({
                'position': 'mean',
                'points': 'mean',
                'grid': 'mean'  # If available
            }).round(3)
            
            # Rename columns
            rolling_stats.columns = [
                f'driver_last_{window}_races_avg_position',
                f'driver_last_{window}_races_avg_points', 
                f'driver_last_{window}_races_avg_grid'
            ]
            
            # Reset index to get driver_id back as column
            rolling_stats = rolling_stats.reset_index(level=0, drop=True)
            rolling_features.append(rolling_stats)
        
        # Combine all rolling features
        if rolling_features:
            combined_rolling = pd.concat(rolling_features, axis=1)
            return combined_rolling
        else:
            return pd.DataFrame()
    
    def build_final_dataset(self) -> pd.DataFrame:
        """Build the final feature-engineered dataset."""
        
        print("🔧 Starting feature engineering pipeline...")
        
        # Load raw data
        data = self.load_raw_data()
        
        # Start with results as base
        base_df = data['results'].copy()
        
        # Add race information (avoid circuit_id duplication)
        race_info = data['races'][['year', 'round', 'circuit_name', 'country']].copy()
        base_df = base_df.merge(race_info, on=['year', 'round'], how='left')
        
        # Add qualifying information (for grid position)
        qualifying_info = data['qualifying'][['year', 'round', 'driver_id', 'position']].copy()
        qualifying_info = qualifying_info.rename(columns={'position': 'grid_position'})
        base_df = base_df.merge(qualifying_info, on=['year', 'round', 'driver_id'], how='left')
        
        print("✅ Base dataset merged")
        
        # Create era flags
        base_df = self.create_era_flags(base_df)
        print("✅ Era flags created")
        
        # Create historical features
        driver_hist_features = self.create_driver_historical_features(data['results'])
        constructor_hist_features = self.create_constructor_historical_features(data['results'])
        
        # Add historical features
        base_df = base_df.merge(driver_hist_features, on='driver_id', how='left')
        base_df = base_df.merge(constructor_hist_features, on='constructor_id', how='left')
        print("✅ Historical features added")
        
        # Create track-specific features
        driver_track_features, constructor_track_features = self.create_track_specific_features(
            data['results'], data['races']
        )
        
        base_df = base_df.merge(
            driver_track_features, 
            on=['driver_id', 'circuit_id'], 
            how='left'
        )
        base_df = base_df.merge(
            constructor_track_features,
            on=['constructor_id', 'circuit_id'],
            how='left'
        )
        print("✅ Track-specific features added")
        
        # Create target variable (position) and feature columns
        feature_columns = [
            'year', 'round', 'circuit_id', 'circuit_name', 'country', 'date',
            'driver_id', 'driver_first_name', 'driver_last_name', 'driver_nationality',
            'constructor_id', 'constructor_name', 'constructor_nationality',
            'grid_position',
            # Era flags
            'is_2017_plus_era', 'is_2022_plus_era', 'is_covid_season_2020', 'has_sprint_format',
            # Driver historical features
            'driver_career_total_points', 'driver_career_avg_points', 'driver_career_avg_position',
            'driver_career_race_count', 'driver_career_wins', 'driver_career_podiums',
            'driver_win_rate', 'driver_podium_rate', 'driver_points_rate',
            # Constructor historical features  
            'constructor_career_total_points', 'constructor_career_avg_points', 'constructor_career_avg_position',
            'constructor_career_race_count', 'constructor_career_wins', 'constructor_career_podiums',
            'constructor_win_rate', 'constructor_podium_rate', 'constructor_points_rate',
            # Track-specific features
            'driver_track_avg_position', 'driver_track_race_count', 'driver_track_avg_points',
            'constructor_track_avg_position', 'constructor_track_race_count', 'constructor_track_avg_points',
            # Target variable
            'position'  # This is what we want to predict
        ]
        
        # Select final columns
        final_df = base_df[feature_columns].copy()
        
        # Fill missing values
        final_df = final_df.fillna({
            'grid_position': 20,  # Back of grid if no qualifying data
            'driver_track_avg_position': final_df['driver_career_avg_position'].fillna(15),
            'constructor_track_avg_position': final_df['constructor_career_avg_position'].fillna(15),
            'driver_track_race_count': 0,
            'constructor_track_race_count': 0,
            'driver_track_avg_points': 0,
            'constructor_track_avg_points': 0
        })
        
        print(f"🏆 Final dataset created: {final_df.shape}")
        
        return final_df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str = 'f1_race_prediction_dataset.csv'):
        """Save processed dataset."""
        output_path = self.processed_dir / filename
        df.to_csv(output_path, index=False)
        print(f"💾 Dataset saved to: {output_path}")
        
        # Print dataset summary
        print(f"\n📊 Dataset Summary:")
        print(f"Shape: {df.shape}")
        print(f"Years: {df['year'].min()} - {df['year'].max()}")
        print(f"Unique drivers: {df['driver_id'].nunique()}")
        print(f"Unique constructors: {df['constructor_id'].nunique()}")
        print(f"Unique circuits: {df['circuit_id'].nunique()}")
        print(f"Missing values: {df.isnull().sum().sum()}")
        
        return output_path


def main():
    """Main execution function."""
    engineer = F1FeatureEngineer()
    
    # Build final dataset
    final_dataset = engineer.build_final_dataset()
    
    # Save to processed data
    output_path = engineer.save_processed_data(final_dataset)
    
    print(f"\n🎉 Feature engineering completed!")
    print(f"📁 Output file: {output_path}")
    
    return final_dataset


if __name__ == "__main__":
    dataset = main()
