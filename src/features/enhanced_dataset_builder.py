"""Enhanced Dataset Builder for XGBoost Model Training."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from loguru import logger
import warnings
warnings.filterwarnings('ignore')

from src.config.settings import settings


class EnhancedDatasetBuilder:
    """Build enhanced dataset by merging Ergast and FastF1 data at driver level."""
    
    def __init__(self):
        self.processed_dir = settings.PROCESSED_DATA_DIR
        self.xgboost_dir = self.processed_dir / 'xgboost'
        self.xgboost_dir.mkdir(exist_ok=True)
        
        # Input files
        self.ergast_file = self.processed_dir / 'f1_race_prediction_dataset.csv'
        self.fastf1_file = self.processed_dir / 'fastf1_features_engineered.csv'
        
        # Output file
        self.enhanced_file = self.xgboost_dir / 'enhanced_f1_dataset.csv'
        
    def load_datasets(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load Ergast and FastF1 datasets."""
        logger.info("Loading datasets...")
        
        ergast_df = pd.read_csv(self.ergast_file)
        fastf1_df = pd.read_csv(self.fastf1_file)
        
        # Remove 2017 from Ergast (FastF1 starts from 2018)
        ergast_df = ergast_df[ergast_df['year'] >= 2018].copy()
        
        logger.info(f"Ergast: {ergast_df.shape[0]} records (2018-2025)")
        logger.info(f"FastF1: {fastf1_df.shape[0]} records (2018-2025)")
        
        return ergast_df, fastf1_df
    
    def create_driver_mapping(self) -> Dict[str, str]:
        """Create mapping from FastF1 abbreviations to Ergast driver_ids."""
        driver_mapping = {
            # Current drivers
            'VER': 'max_verstappen', 'HAM': 'hamilton', 'BOT': 'bottas', 'RUS': 'russell',
            'NOR': 'norris', 'PER': 'perez', 'SAI': 'sainz', 'LEC': 'leclerc',
            'ALO': 'alonso', 'STR': 'stroll', 'VET': 'vettel', 'RAI': 'raikkonen',
            'RIC': 'ricciardo', 'OCO': 'ocon', 'GAS': 'gasly', 'TSU': 'tsunoda',
            'ALB': 'albon', 'LAT': 'latifi', 'MSC': 'mick_schumacher', 'MAZ': 'mazepin',
            'HUL': 'hulkenberg', 'MAG': 'kevin_magnussen', 'ZHO': 'zhou', 'PIA': 'piastri',
            
            # Additional mappings
            'GRO': 'grosjean', 'KVY': 'kvyat', 'GIO': 'giovinazzi', 'DEV': 'de_vries',
            'SAR': 'sargeant', 'NIC': 'nyck_de_vries', 'BEA': 'bearman', 'COL': 'colapinto',
            'LAW': 'lawson', 'DOO': 'doohan', 'HAD': 'hadjar',
            
            # Historical drivers
            'VAN': 'vandoorne', 'ERI': 'ericsson', 'WEH': 'wehrlein', 'SIR': 'sirotkin',
            'HAR': 'hartley', 'FIT': 'fittipaldi', 'AIT': 'aitken', 'SCH': 'schumacher'
        }
        
        logger.info(f"Driver mapping created: {len(driver_mapping)} mappings")
        return driver_mapping
    
    def prepare_ergast_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare Ergast data with race-level and driver-level features."""
        logger.info("Preparing Ergast data...")
        
        # Ensure required columns exist
        required_cols = ['year', 'round', 'driver_id', 'position']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in Ergast data: {missing_cols}")
        
        # Add merge key
        df['merge_key'] = df['year'].astype(str) + '_' + df['round'].astype(str) + '_' + df['driver_id']
        
        logger.info(f"Ergast data prepared: {df.shape[0]} records")
        return df
    
    def prepare_fastf1_data(self, df: pd.DataFrame, driver_mapping: Dict[str, str]) -> pd.DataFrame:
        """Prepare FastF1 data with driver mapping."""
        logger.info("Preparing FastF1 data...")
        
        # Map driver abbreviations to driver_ids
        df['driver_id'] = df['driver_abbreviation'].map(driver_mapping)
        
        # Remove unmapped drivers
        before_count = len(df)
        df = df.dropna(subset=['driver_id']).copy()
        after_count = len(df)
        
        logger.info(f"Driver mapping: {after_count}/{before_count} records kept ({after_count/before_count*100:.1f}%)")
        
        # Add merge key
        df['merge_key'] = df['year'].astype(str) + '_' + df['round'].astype(str) + '_' + df['driver_id']
        
        # Select FastF1 specific features (exclude overlapping columns)
        fastf1_features = [
            'merge_key', 'driver_abbreviation', 'driver_number',
            
            # Telemetry features
            'fastest_lap_time', 'avg_lap_time', 'lap_time_std', 'total_laps',
            'avg_sector1_time', 'avg_sector2_time', 'avg_sector3_time',
            'max_speed', 'avg_speed', 'speed_variance',
            
            # Weather features
            'air_temp', 'track_temp', 'humidity', 'wind_speed',
            
            # Tire strategy features
            'main_compound', 'compound_changes', 'pit_stops',
            'is_soft_primary', 'is_hard_primary', 'is_medium_primary',
            'is_intermediate', 'is_wet', 'compound_changes_normalized',
            'pit_stops_normalized', 'low_pit_strategy', 'aggressive_pit_strategy',
            
            # Performance metrics
            'speed_consistency', 'speed_efficiency', 'total_sector_time',
            'sector1_dominance', 'sector2_dominance', 'sector3_dominance',
            'lap_time_efficiency', 'lap_time_consistency_score',
            
            # Weather impact features
            'temp_differential', 'is_hot_conditions', 'is_cold_conditions',
            'is_high_track_temp', 'is_high_humidity', 'is_low_humidity', 'is_windy_conditions',
            
            # Era features
            'is_2018_2021_era', 'is_2022_plus_era', 'is_covid_season_2020', 'has_sprint_format',
            'era_adjusted_speed', 'era_adjusted_laps',
            
            # Relative performance features
            'avg_lap_time_vs_race_avg', 'avg_lap_time_vs_race_best', 'avg_lap_time_rank_in_race',
            'max_speed_vs_race_avg', 'max_speed_vs_race_best', 'max_speed_rank_in_race',
            'avg_speed_vs_race_avg', 'avg_speed_vs_race_best', 'avg_speed_rank_in_race',
            'grid_to_finish_change', 'position_gained', 'position_lost'
        ]
        
        # Keep only existing columns
        available_features = [col for col in fastf1_features if col in df.columns]
        df_selected = df[available_features].copy()
        
        logger.info(f"FastF1 features selected: {len(available_features)} features")
        return df_selected
    
    def merge_datasets(self, ergast_df: pd.DataFrame, fastf1_df: pd.DataFrame) -> pd.DataFrame:
        """Merge Ergast and FastF1 datasets on driver level."""
        logger.info("Merging datasets...")
        
        # Perform LEFT JOIN to keep all Ergast records
        merged_df = ergast_df.merge(
            fastf1_df, 
            on='merge_key', 
            how='left',
            suffixes=('', '_fastf1')
        )
        
        # Add FastF1 availability flag
        merged_df['has_fastf1_data'] = merged_df['driver_abbreviation'].notna()
        
        logger.info(f"Merge complete: {merged_df.shape[0]} total records")
        logger.info(f"Records with FastF1 data: {merged_df['has_fastf1_data'].sum()} ({merged_df['has_fastf1_data'].mean()*100:.1f}%)")
        
        # Clean up merge key
        merged_df = merged_df.drop('merge_key', axis=1)
        
        return merged_df
    
    def add_xgboost_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add XGBoost-specific features for ranking."""
        logger.info("Adding XGBoost features...")
        
        # Group key for XGBoost ranking
        df['group_key'] = df['year'].astype(str) + '_' + df['round'].astype(str)
        
        # Target variable (position to predict)
        df['target_position'] = df['position']
        
        # Convert position to rank (1st place = rank 1, DNF = max rank + 1)
        df['rank'] = df.groupby('group_key')['position'].transform(
            lambda x: x.fillna(x.max() + 1)
        )
        
        # Add race size (number of drivers in race)
        df['race_size'] = df.groupby('group_key')['driver_id'].transform('count')
        
        # Position as percentile within race
        df['position_percentile'] = df['rank'] / df['race_size']
        
        logger.info("XGBoost features added")
        return df
    
    def validate_dataset(self, df: pd.DataFrame) -> None:
        """Validate the enhanced dataset."""
        logger.info("Validating enhanced dataset...")
        
        # Check required columns
        required_cols = ['year', 'round', 'driver_id', 'position', 'target_position', 'group_key']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Check data completeness
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"Years covered: {df['year'].min()}-{df['year'].max()}")
        logger.info(f"Total races: {df['group_key'].nunique()}")
        logger.info(f"Unique drivers: {df['driver_id'].nunique()}")
        logger.info(f"Records with FastF1: {df['has_fastf1_data'].sum()}/{len(df)} ({df['has_fastf1_data'].mean()*100:.1f}%)")
        
        # Check missing values in key features
        key_features = ['position', 'grid_position', 'constructor_id']
        for feature in key_features:
            if feature in df.columns:
                missing_pct = df[feature].isna().mean() * 100
                logger.info(f"Missing {feature}: {missing_pct:.1f}%")
        
        logger.info("Dataset validation complete ✅")
    
    def save_enhanced_dataset(self, df: pd.DataFrame) -> Path:
        """Save the enhanced dataset."""
        logger.info(f"Saving enhanced dataset to {self.enhanced_file}")
        
        # Save full dataset
        df.to_csv(self.enhanced_file, index=False)
        
        # Save data info
        info_file = self.xgboost_dir / 'dataset_info.txt'
        with open(info_file, 'w') as f:
            f.write(f"Enhanced F1 Dataset for XGBoost\n")
            f.write(f"================================\n\n")
            f.write(f"Generated: {pd.Timestamp.now()}\n")
            f.write(f"Records: {df.shape[0]}\n")
            f.write(f"Features: {df.shape[1]}\n")
            f.write(f"Years: {df['year'].min()}-{df['year'].max()}\n")
            f.write(f"Total races: {df['group_key'].nunique()}\n")
            f.write(f"Unique drivers: {df['driver_id'].nunique()}\n")
            f.write(f"FastF1 coverage: {df['has_fastf1_data'].mean()*100:.1f}%\n\n")
            f.write(f"Target variable: target_position (race finish position)\n")
            f.write(f"Group key: group_key (year_round for XGBoost ranking)\n")
            f.write(f"Use rank:pairwise objective in XGBoost\n")
        
        logger.info(f"Enhanced dataset saved: {self.enhanced_file}")
        logger.info(f"Dataset info saved: {info_file}")
        
        return self.enhanced_file
    
    def build_enhanced_dataset(self) -> pd.DataFrame:
        """Build the complete enhanced dataset."""
        logger.info("🚀 Building Enhanced F1 Dataset for XGBoost...")
        
        # 1. Load datasets
        ergast_df, fastf1_df = self.load_datasets()
        
        # 2. Create driver mapping
        driver_mapping = self.create_driver_mapping()
        
        # 3. Prepare datasets
        ergast_prepared = self.prepare_ergast_data(ergast_df)
        fastf1_prepared = self.prepare_fastf1_data(fastf1_df, driver_mapping)
        
        # 4. Merge datasets
        merged_df = self.merge_datasets(ergast_prepared, fastf1_prepared)
        
        # 5. Add XGBoost features
        enhanced_df = self.add_xgboost_features(merged_df)
        
        # 6. Validate dataset
        self.validate_dataset(enhanced_df)
        
        # 7. Save dataset
        self.save_enhanced_dataset(enhanced_df)
        
        logger.info("✅ Enhanced dataset building complete!")
        return enhanced_df


def main():
    """Main function to build enhanced dataset."""
    builder = EnhancedDatasetBuilder()
    dataset = builder.build_enhanced_dataset()
    return dataset


if __name__ == "__main__":
    dataset = main()
