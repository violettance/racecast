"""Ergast API data collector."""

from typing import Dict, List, Optional
import pandas as pd
from loguru import logger

from src.config.settings import settings
from .base import BaseCollector


class ErgastCollector(BaseCollector):
    """Collector for Ergast F1 API data."""
    
    def __init__(self):
        super().__init__("Ergast")
        self.base_url = settings.ERGAST_BASE_URL
    
    def collect_races(self, year: int) -> pd.DataFrame:
        """Collect race calendar for a season."""
        url = f"{self.base_url}/{year}/races.json"
        data = self._make_request(url)
        
        races = []
        for race in data['MRData']['RaceTable']['Races']:
            race_info = {
                'year': int(race['season']),
                'round': int(race['round']),
                'race_name': race['raceName'],
                'circuit_id': race['Circuit']['circuitId'],
                'circuit_name': race['Circuit']['circuitName'],
                'country': race['Circuit']['Location']['country'],
                'locality': race['Circuit']['Location']['locality'],
                'latitude': float(race['Circuit']['Location']['lat']),
                'longitude': float(race['Circuit']['Location']['long']),
                'date': race['date'],
                'time': race.get('time', ''),
                'url': race['url']
            }
            races.append(race_info)
        
        df = pd.DataFrame(races)
        logger.info(f"Collected {len(df)} races for {year}")
        return df
    
    def collect_results(self, year: int) -> pd.DataFrame:
        """Collect race results for a season."""
        url = f"{self.base_url}/{year}/results.json"
        params = {'limit': 1000}  # Ensure we get all results
        data = self._make_request(url, params)
        
        results = []
        for race in data['MRData']['RaceTable']['Races']:
            race_info = {
                'year': int(race['season']),
                'round': int(race['round']),
                'race_name': race['raceName'],
                'circuit_id': race['Circuit']['circuitId'],
                'date': race['date']
            }
            
            for result in race['Results']:
                result_info = race_info.copy()
                result_info.update({
                    'position': int(result['position']) if result['position'].isdigit() else None,
                    'position_text': result['positionText'],
                    'points': float(result['points']),
                    'driver_id': result['Driver']['driverId'],
                    'driver_code': result['Driver']['code'],
                    'driver_number': result['Driver']['permanentNumber'],
                    'driver_first_name': result['Driver']['givenName'],
                    'driver_last_name': result['Driver']['familyName'],
                    'driver_nationality': result['Driver']['nationality'],
                    'constructor_id': result['Constructor']['constructorId'],
                    'constructor_name': result['Constructor']['name'],
                    'constructor_nationality': result['Constructor']['nationality'],
                    'grid': int(result['grid']) if result['grid'].isdigit() else None,
                    'laps': int(result['laps']),
                    'status': result['status'],
                    'time_millis': int(result['Time']['millis']) if 'Time' in result else None,
                    'time_text': result['Time']['time'] if 'Time' in result else None,
                    'fastest_lap_rank': int(result['FastestLap']['rank']) if 'FastestLap' in result else None,
                    'fastest_lap_time': result['FastestLap']['Time']['time'] if 'FastestLap' in result else None,
                    'fastest_lap_speed': float(result['FastestLap']['AverageSpeed']['speed']) if 'FastestLap' in result else None
                })
                results.append(result_info)
        
        df = pd.DataFrame(results)
        logger.info(f"Collected {len(df)} race results for {year}")
        return df
    
    def collect_qualifying(self, year: int) -> pd.DataFrame:
        """Collect qualifying results for a season."""
        url = f"{self.base_url}/{year}/qualifying.json"
        params = {'limit': 1000}
        data = self._make_request(url, params)
        
        qualifying = []
        for race in data['MRData']['RaceTable']['Races']:
            race_info = {
                'year': int(race['season']),
                'round': int(race['round']),
                'race_name': race['raceName'],
                'circuit_id': race['Circuit']['circuitId'],
                'date': race['date']
            }
            
            for result in race['QualifyingResults']:
                qual_info = race_info.copy()
                qual_info.update({
                    'position': int(result['position']),
                    'driver_id': result['Driver']['driverId'],
                    'driver_code': result['Driver']['code'],
                    'driver_number': result['Driver']['permanentNumber'],
                    'driver_first_name': result['Driver']['givenName'],
                    'driver_last_name': result['Driver']['familyName'],
                    'constructor_id': result['Constructor']['constructorId'],
                    'constructor_name': result['Constructor']['name'],
                    'q1_time': result.get('Q1', None),
                    'q2_time': result.get('Q2', None),
                    'q3_time': result.get('Q3', None)
                })
                qualifying.append(qual_info)
        
        df = pd.DataFrame(qualifying)
        logger.info(f"Collected {len(df)} qualifying results for {year}")
        return df
    
    def collect_driver_standings(self, year: int) -> pd.DataFrame:
        """Collect driver championship standings for a season."""
        url = f"{self.base_url}/{year}/driverstandings.json"
        data = self._make_request(url)
        
        standings = []
        for standing_list in data['MRData']['StandingsTable']['StandingsLists']:
            for standing in standing_list['DriverStandings']:
                standing_info = {
                    'year': int(standing_list['season']),
                    'round': int(standing_list['round']) if standing_list['round'] else None,
                    'position': int(standing['position']),
                    'points': float(standing['points']),
                    'wins': int(standing['wins']),
                    'driver_id': standing['Driver']['driverId'],
                    'driver_code': standing['Driver']['code'],
                    'driver_number': standing['Driver']['permanentNumber'],
                    'driver_first_name': standing['Driver']['givenName'],
                    'driver_last_name': standing['Driver']['familyName'],
                    'constructor_id': standing['Constructors'][0]['constructorId'],
                    'constructor_name': standing['Constructors'][0]['name']
                }
                standings.append(standing_info)
        
        df = pd.DataFrame(standings)
        logger.info(f"Collected {len(df)} driver standings for {year}")
        return df
    
    def collect_constructor_standings(self, year: int) -> pd.DataFrame:
        """Collect constructor championship standings for a season."""
        url = f"{self.base_url}/{year}/constructorstandings.json"
        data = self._make_request(url)
        
        standings = []
        for standing_list in data['MRData']['StandingsTable']['StandingsLists']:
            for standing in standing_list['ConstructorStandings']:
                standing_info = {
                    'year': int(standing_list['season']),
                    'round': int(standing_list['round']) if standing_list['round'] else None,
                    'position': int(standing['position']),
                    'points': float(standing['points']),
                    'wins': int(standing['wins']),
                    'constructor_id': standing['Constructor']['constructorId'],
                    'constructor_name': standing['Constructor']['name'],
                    'constructor_nationality': standing['Constructor']['nationality']
                }
                standings.append(standing_info)
        
        df = pd.DataFrame(standings)
        logger.info(f"Collected {len(df)} constructor standings for {year}")
        return df
    
    def collect_season_data(self, year: int) -> Dict[str, pd.DataFrame]:
        """Collect all data for a specific season."""
        logger.info(f"Collecting Ergast data for {year} season")
        
        season_data = {
            'races': self.collect_races(year),
            'results': self.collect_results(year),
            'qualifying': self.collect_qualifying(year),
            'driver_standings': self.collect_driver_standings(year),
            'constructor_standings': self.collect_constructor_standings(year)
        }
        
        # Save raw data
        for data_type, df in season_data.items():
            self._save_raw_data(df, f"ergast_{data_type}_{year}")
        
        return season_data
    
    def collect_historical_data(self, start_year: int, end_year: int) -> Dict[str, pd.DataFrame]:
        """Collect historical data across multiple seasons."""
        logger.info(f"Collecting Ergast historical data from {start_year} to {end_year}")
        
        all_data = {
            'races': [],
            'results': [],
            'qualifying': [],
            'driver_standings': [],
            'constructor_standings': []
        }
        
        for year in range(start_year, end_year + 1):
            try:
                season_data = self.collect_season_data(year)
                for data_type, df in season_data.items():
                    all_data[data_type].append(df)
            except Exception as e:
                logger.error(f"Failed to collect data for {year}: {e}")
                continue
        
        # Combine all years
        combined_data = {}
        for data_type, dfs in all_data.items():
            if dfs:
                combined_data[data_type] = pd.concat(dfs, ignore_index=True)
                # Save combined historical data
                self._save_raw_data(
                    combined_data[data_type], 
                    f"ergast_{data_type}_{start_year}_{end_year}"
                )
        
        return combined_data
