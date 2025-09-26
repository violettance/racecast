"""Base classes for feature engineering."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd
from loguru import logger


class BaseFeatureEngineer(ABC):
    """Base class for feature engineering."""
    
    def __init__(self, name: str):
        self.name = name
        self.feature_names: List[str] = []
    
    @abstractmethod
    def engineer_features(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Engineer features from raw data."""
        pass
    
    def get_feature_names(self) -> List[str]:
        """Get list of engineered feature names."""
        return self.feature_names.copy()
    
    def validate_data(self, data: Dict[str, pd.DataFrame], required_tables: List[str]) -> bool:
        """Validate that required data tables are present."""
        missing_tables = [table for table in required_tables if table not in data]
        if missing_tables:
            logger.error(f"Missing required tables for {self.name}: {missing_tables}")
            return False
        return True


class DriverFeatureEngineer(BaseFeatureEngineer):
    """Feature engineer for driver-specific features."""
    
    def __init__(self):
        super().__init__("Driver Features")
    
    def calculate_recent_form(self, results: pd.DataFrame, n_races: int = 5) -> pd.DataFrame:
        """Calculate driver form based on recent race results."""
        # Sort by year, round
        results_sorted = results.sort_values(['year', 'round'])
        
        driver_form = []
        for driver_id in results_sorted['driver_id'].unique():
            driver_results = results_sorted[results_sorted['driver_id'] == driver_id].copy()
            
            # Calculate rolling average position
            driver_results['form_avg_position'] = (
                driver_results['position']
                .rolling(window=n_races, min_periods=1)
                .mean()
            )
            
            # Calculate rolling points average
            driver_results['form_avg_points'] = (
                driver_results['points']
                .rolling(window=n_races, min_periods=1)
                .mean()
            )
            
            # Calculate consistency (std of positions)
            driver_results['form_consistency'] = (
                driver_results['position']
                .rolling(window=n_races, min_periods=2)
                .std()
            )
            
            driver_form.append(driver_results)
        
        return pd.concat(driver_form, ignore_index=True)
    
    def calculate_track_experience(self, results: pd.DataFrame) -> pd.DataFrame:
        """Calculate driver experience at each track."""
        track_experience = []
        
        for (driver_id, circuit_id), group in results.groupby(['driver_id', 'circuit_id']):
            # Sort by year to get chronological order
            group_sorted = group.sort_values('year')
            
            # Calculate cumulative race count at this track
            group_sorted['track_experience'] = range(1, len(group_sorted) + 1)
            
            # Calculate average position at this track (up to current race)
            group_sorted['track_avg_position'] = (
                group_sorted['position']
                .expanding()
                .mean()
            )
            
            # Calculate best position at this track
            group_sorted['track_best_position'] = (
                group_sorted['position']
                .expanding()
                .min()
            )
            
            track_experience.append(group_sorted)
        
        return pd.concat(track_experience, ignore_index=True)
    
    def calculate_qualifying_vs_race_performance(self, results: pd.DataFrame, qualifying: pd.DataFrame) -> pd.DataFrame:
        """Calculate how drivers perform in race vs qualifying."""
        # Merge qualifying and race results
        merged = results.merge(
            qualifying[['year', 'round', 'driver_id', 'position']],
            on=['year', 'round', 'driver_id'],
            suffixes=('_race', '_qual')
        )
        
        # Calculate position gain/loss
        merged['position_change'] = merged['position_qual'] - merged['position_race']
        
        # Calculate rolling average position change
        merged = merged.sort_values(['driver_id', 'year', 'round'])
        merged['avg_position_change'] = (
            merged.groupby('driver_id')['position_change']
            .rolling(window=5, min_periods=1)
            .mean()
            .reset_index(0, drop=True)
        )
        
        return merged
    
    def engineer_features(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Engineer all driver features."""
        required_tables = ['results', 'qualifying']
        if not self.validate_data(data, required_tables):
            raise ValueError(f"Missing required tables for {self.name}")
        
        logger.info(f"Engineering {self.name}")
        
        # Start with results data
        features_df = data['results'].copy()
        
        # Add form features
        features_df = self.calculate_recent_form(features_df)
        
        # Add track experience features
        features_df = self.calculate_track_experience(features_df)
        
        # Add qualifying vs race performance
        qual_race_df = self.calculate_qualifying_vs_race_performance(
            data['results'], data['qualifying']
        )
        
        # Merge qualifying performance features
        features_df = features_df.merge(
            qual_race_df[['year', 'round', 'driver_id', 'position_change', 'avg_position_change']],
            on=['year', 'round', 'driver_id'],
            how='left'
        )
        
        # Store feature names
        self.feature_names = [
            'form_avg_position', 'form_avg_points', 'form_consistency',
            'track_experience', 'track_avg_position', 'track_best_position',
            'position_change', 'avg_position_change'
        ]
        
        logger.info(f"Engineered {len(self.feature_names)} driver features")
        return features_df


class ConstructorFeatureEngineer(BaseFeatureEngineer):
    """Feature engineer for constructor-specific features."""
    
    def __init__(self):
        super().__init__("Constructor Features")
    
    def calculate_team_form(self, results: pd.DataFrame, n_races: int = 5) -> pd.DataFrame:
        """Calculate constructor form based on recent results."""
        results_sorted = results.sort_values(['year', 'round'])
        
        # Calculate team points per race
        team_points = results_sorted.groupby(['year', 'round', 'constructor_id'])['points'].sum().reset_index()
        team_points.rename(columns={'points': 'team_race_points'}, inplace=True)
        
        constructor_form = []
        for constructor_id in team_points['constructor_id'].unique():
            constructor_results = team_points[team_points['constructor_id'] == constructor_id].copy()
            constructor_results = constructor_results.sort_values(['year', 'round'])
            
            # Rolling average team points
            constructor_results['team_form_avg_points'] = (
                constructor_results['team_race_points']
                .rolling(window=n_races, min_periods=1)
                .mean()
            )
            
            # Team consistency
            constructor_results['team_form_consistency'] = (
                constructor_results['team_race_points']
                .rolling(window=n_races, min_periods=2)
                .std()
            )
            
            constructor_form.append(constructor_results)
        
        team_form_df = pd.concat(constructor_form, ignore_index=True)
        
        # Merge back to original results
        results_with_team_form = results_sorted.merge(
            team_form_df[['year', 'round', 'constructor_id', 'team_form_avg_points', 'team_form_consistency']],
            on=['year', 'round', 'constructor_id'],
            how='left'
        )
        
        return results_with_team_form
    
    def calculate_reliability_metrics(self, results: pd.DataFrame) -> pd.DataFrame:
        """Calculate constructor reliability metrics."""
        results_sorted = results.sort_values(['constructor_id', 'year', 'round'])
        
        # Define DNF statuses
        dnf_statuses = ['Accident', 'Engine', 'Gearbox', 'Transmission', 'Electrical', 
                       'Hydraulics', 'Retired', 'Mechanical', 'Collision']
        
        # Create DNF flag
        results_sorted['is_dnf'] = results_sorted['status'].apply(
            lambda x: any(dnf in x for dnf in dnf_statuses) if pd.notna(x) else False
        )
        
        # Calculate rolling DNF rate
        results_sorted['reliability_score'] = (
            results_sorted.groupby('constructor_id')['is_dnf']
            .rolling(window=10, min_periods=3)
            .mean()
            .reset_index(0, drop=True)
        )
        
        # Invert so higher score = more reliable
        results_sorted['reliability_score'] = 1 - results_sorted['reliability_score']
        
        return results_sorted
    
    def engineer_features(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Engineer all constructor features."""
        required_tables = ['results']
        if not self.validate_data(data, required_tables):
            raise ValueError(f"Missing required tables for {self.name}")
        
        logger.info(f"Engineering {self.name}")
        
        # Start with results data
        features_df = data['results'].copy()
        
        # Add team form features
        features_df = self.calculate_team_form(features_df)
        
        # Add reliability features
        features_df = self.calculate_reliability_metrics(features_df)
        
        # Store feature names
        self.feature_names = [
            'team_form_avg_points', 'team_form_consistency', 'reliability_score'
        ]
        
        logger.info(f"Engineered {len(self.feature_names)} constructor features")
        return features_df
