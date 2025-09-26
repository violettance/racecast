"""FastF1 API data collector."""

import time
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from loguru import logger
import fastf1
import warnings

from src.config.settings import settings
from .base import BaseCollector

# Suppress FastF1 warnings
warnings.filterwarnings('ignore')
fastf1.Cache.enable_cache('data/cache/')  # Enable caching


class FastF1Collector(BaseCollector):
    """Collector for FastF1 telemetry and session data."""
    
    def __init__(self):
        super().__init__("FastF1")
    
    def collect_season_data(self, year: int) -> pd.DataFrame:
        """Collect all race data for a specific season."""
        logger.info(f"Collecting FastF1 data for {year} season")
        
        try:
            # Get season schedule
            schedule = fastf1.get_event_schedule(year)
            
            # Filter to actual race events (exclude testing)
            race_schedule = schedule[schedule['EventFormat'] == 'conventional'].copy()
            
            all_races_data = []
            
            for idx, event in race_schedule.iterrows():
                try:
                    race_round = event['RoundNumber']
                    event_name = event['EventName']
                    
                    logger.info(f"Processing {year} Round {race_round}: {event_name}")
                    
                    # Get race session
                    session = fastf1.get_session(year, race_round, 'R')  # 'R' for Race
                    session.load()
                    
                    # Extract race features for all drivers
                    race_features = self._extract_race_features(session, year, race_round, event_name)
                    all_races_data.extend(race_features)
                    
                    # Add delay to be respectful to FastF1 API
                    time.sleep(settings.REQUEST_DELAY)
                    
                except Exception as e:
                    logger.warning(f"Failed to process {year} Round {race_round} ({event_name}): {e}")
                    continue
            
            df = pd.DataFrame(all_races_data)
            logger.info(f"Collected {len(df)} driver-race records for {year}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to collect FastF1 data for {year}: {e}")
            return pd.DataFrame()
    
    def _extract_race_features(self, session, year: int, race_round: int, event_name: str) -> List[Dict]:
        """Extract comprehensive features from a race session."""
        features_list = []
        
        try:
            # Get laps and results data
            laps = session.laps
            results = session.results
            
            if laps is None or len(laps) == 0:
                logger.warning(f"No laps data for {year} Round {race_round}")
                return []
            
            # Process each driver
            for idx, driver_result in results.iterrows():
                try:
                    driver_abbr = driver_result['Abbreviation']
                    driver_number = driver_result['DriverNumber']
                    
                    # Get driver's laps
                    driver_laps = laps[laps['Driver'] == driver_abbr]
                    
                    if len(driver_laps) == 0:
                        continue
                    
                    # Calculate comprehensive features
                    features = {
                        # Basic info
                        'year': year,
                        'round': race_round,
                        'race_name': event_name,
                        'date': session.date.strftime('%Y-%m-%d') if session.date else None,
                        'circuit_name': session.event['Location'] if hasattr(session, 'event') else None,
                        'event_name': event_name,
                        'driver_abbreviation': driver_abbr,
                        'driver_number': int(driver_number) if pd.notna(driver_number) else None,
                        
                        # Race result info
                        'position': int(driver_result['Position']) if pd.notna(driver_result['Position']) else None,
                        'grid_position': int(driver_result['GridPosition']) if pd.notna(driver_result['GridPosition']) else None,
                        'points': float(driver_result['Points']) if pd.notna(driver_result['Points']) else 0.0,
                        'status': driver_result['Status'] if 'Status' in driver_result else None,
                        
                        # Timing features
                        'fastest_lap_time': self._time_to_seconds(driver_laps['LapTime'].min()) if not driver_laps['LapTime'].isna().all() else None,
                        'avg_lap_time': self._time_to_seconds(driver_laps['LapTime'].mean()) if not driver_laps['LapTime'].isna().all() else None,
                        'lap_time_std': self._time_to_seconds(driver_laps['LapTime'].std()) if not driver_laps['LapTime'].isna().all() else None,
                        'total_laps': len(driver_laps),
                        
                        # Sector times
                        'avg_sector1_time': self._time_to_seconds(driver_laps['Sector1Time'].mean()) if 'Sector1Time' in driver_laps.columns and not driver_laps['Sector1Time'].isna().all() else None,
                        'avg_sector2_time': self._time_to_seconds(driver_laps['Sector2Time'].mean()) if 'Sector2Time' in driver_laps.columns and not driver_laps['Sector2Time'].isna().all() else None,
                        'avg_sector3_time': self._time_to_seconds(driver_laps['Sector3Time'].mean()) if 'Sector3Time' in driver_laps.columns and not driver_laps['Sector3Time'].isna().all() else None,
                        
                        # Speed features
                        'max_speed': driver_laps['SpeedI1'].max() if 'SpeedI1' in driver_laps.columns and not driver_laps['SpeedI1'].isna().all() else None,
                        'avg_speed': driver_laps['SpeedI1'].mean() if 'SpeedI1' in driver_laps.columns and not driver_laps['SpeedI1'].isna().all() else None,
                        'speed_variance': driver_laps['SpeedI1'].var() if 'SpeedI1' in driver_laps.columns and not driver_laps['SpeedI1'].isna().all() else None,
                        
                        # Track conditions
                        'air_temp': session.weather['AirTemp'].iloc[0] if hasattr(session, 'weather') and 'AirTemp' in session.weather.columns else None,
                        'track_temp': session.weather['TrackTemp'].iloc[0] if hasattr(session, 'weather') and 'TrackTemp' in session.weather.columns else None,
                        'humidity': session.weather['Humidity'].iloc[0] if hasattr(session, 'weather') and 'Humidity' in session.weather.columns else None,
                        'wind_speed': session.weather['WindSpeed'].iloc[0] if hasattr(session, 'weather') and 'WindSpeed' in session.weather.columns else None,
                        
                        # Compound info
                        'main_compound': driver_laps['Compound'].mode().iloc[0] if 'Compound' in driver_laps.columns and len(driver_laps['Compound'].mode()) > 0 else None,
                        'compound_changes': driver_laps['Compound'].nunique() if 'Compound' in driver_laps.columns else 0,
                        
                        # Pit stop analysis
                        'pit_stops': len(driver_laps[driver_laps['PitOutTime'].notna()]) if 'PitOutTime' in driver_laps.columns else 0,
                    }
                    
                    features_list.append(features)
                    
                except Exception as e:
                    logger.warning(f"Failed to extract features for {driver_abbr} in {year} Round {race_round}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to extract race features for {year} Round {race_round}: {e}")
        
        return features_list
    
    def _time_to_seconds(self, time_val) -> Optional[float]:
        """Convert time to seconds."""
        if pd.isna(time_val):
            return None
        
        try:
            if hasattr(time_val, 'total_seconds'):
                return time_val.total_seconds()
            elif isinstance(time_val, (int, float)):
                return float(time_val)
            else:
                return None
        except:
            return None
    
    def collect_historical_data(self, start_year: int, end_year: int) -> Dict[str, pd.DataFrame]:
        """Collect historical FastF1 data across multiple seasons."""
        logger.info(f"Collecting FastF1 historical data from {start_year} to {end_year}")
        
        all_data = []
        
        for year in range(start_year, end_year + 1):
            season_data = self.collect_season_data(year)
            if not season_data.empty:
                all_data.append(season_data)
                
                # Save individual year data
                filename = f"fastf1_features_{year}"
                self._save_raw_data(season_data, filename)
        
        if all_data:
            # Combine all years
            combined_data = pd.concat(all_data, ignore_index=True)
            
            # Save combined data
            combined_filename = f"fastf1_features_{start_year}_{end_year}"
            self._save_raw_data(combined_data, combined_filename)
            
            return {"fastf1_features": combined_data}
        
        return {}
