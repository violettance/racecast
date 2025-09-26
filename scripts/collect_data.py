#!/usr/bin/env python3
"""
Data collection script for RaceCast project.
Collects historical F1 data from various sources.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import click
from loguru import logger

from src.config.settings import settings
from src.utils.logging import setup_logging
from src.data.collectors.ergast_collector import ErgastCollector


@click.command()
@click.option('--start-year', default=settings.START_YEAR, help='Start year for data collection')
@click.option('--end-year', default=settings.END_YEAR, help='End year for data collection')
@click.option('--source', default='ergast', type=click.Choice(['ergast', 'fastf1', 'all']), 
              help='Data source to collect from')
@click.option('--dry-run', is_flag=True, help='Dry run without actual data collection')
def main(start_year: int, end_year: int, source: str, dry_run: bool):
    """Collect F1 historical data from various sources."""
    
    # Setup logging
    setup_logging()
    
    logger.info(f"Starting data collection for {start_year}-{end_year}")
    logger.info(f"Data source: {source}")
    logger.info(f"Dry run: {dry_run}")
    
    if dry_run:
        logger.info("DRY RUN: Would collect data but not actually executing")
        return
    
    try:
        if source in ['ergast', 'all']:
            collect_ergast_data(start_year, end_year)
        
        if source in ['fastf1', 'all']:
            collect_fastf1_data(start_year, end_year)
            
        logger.success("Data collection completed successfully!")
        
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        sys.exit(1)


def collect_ergast_data(start_year: int, end_year: int):
    """Collect data from Ergast API."""
    logger.info("Collecting data from Ergast API")
    
    collector = ErgastCollector()
    
    try:
        # Collect historical data
        historical_data = collector.collect_historical_data(start_year, end_year)
        
        # Log summary
        for data_type, df in historical_data.items():
            logger.info(f"Collected {len(df)} {data_type} records")
            
        logger.success(f"Ergast data collection completed for {start_year}-{end_year}")
        
    except Exception as e:
        logger.error(f"Failed to collect Ergast data: {e}")
        raise


def collect_fastf1_data(start_year: int, end_year: int):
    """Collect data from FastF1 API."""
    logger.info("Collecting data from FastF1 API")
    
    from src.data.collectors.fastf1_collector import FastF1Collector
    collector = FastF1Collector()
    
    try:
        # Collect historical data
        historical_data = collector.collect_historical_data(start_year, end_year)
        
        # Log summary
        for data_type, df in historical_data.items():
            logger.info(f"Collected {len(df)} {data_type} records")
            
        logger.success(f"FastF1 data collection completed for {start_year}-{end_year}")
        
    except Exception as e:
        logger.error(f"Failed to collect FastF1 data: {e}")
        raise


if __name__ == "__main__":
    main()
