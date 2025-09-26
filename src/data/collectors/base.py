"""Base classes for data collectors."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import time
import asyncio
from pathlib import Path

import pandas as pd
import requests
from loguru import logger

from src.config.settings import settings


class BaseCollector(ABC):
    """Base class for all data collectors."""
    
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RaceCast/1.0 (Formula 1 Analytics)'
        })
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with retry logic and rate limiting."""
        for attempt in range(settings.MAX_RETRIES):
            try:
                time.sleep(settings.REQUEST_DELAY)
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # Too Many Requests
                    wait_time = 60 * (attempt + 1)  # Progressive wait: 60s, 120s, 180s
                    logger.warning(f"Rate limited (429). Waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                logger.warning(f"HTTP error (attempt {attempt + 1}): {e}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise
                time.sleep(2 ** attempt)  # exponential backoff
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise
                time.sleep(2 ** attempt)  # exponential backoff
    
    def _save_raw_data(self, data: pd.DataFrame, filename: str) -> Path:
        """Save raw data to CSV."""
        filepath = settings.RAW_DATA_DIR / f"{filename}.csv"
        data.to_csv(filepath, index=False)
        logger.info(f"Saved {len(data)} records to {filepath}")
        return filepath
    
    @abstractmethod
    def collect_season_data(self, year: int) -> pd.DataFrame:
        """Collect all data for a specific season."""
        pass
    
    @abstractmethod
    def collect_historical_data(self, start_year: int, end_year: int) -> pd.DataFrame:
        """Collect historical data across multiple seasons."""
        pass


class AsyncBaseCollector(ABC):
    """Base class for async data collectors."""
    
    def __init__(self, name: str):
        self.name = name
    
    async def _make_async_request(self, session, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make async HTTP request with retry logic."""
        import aiohttp
        
        for attempt in range(settings.MAX_RETRIES):
            try:
                await asyncio.sleep(settings.REQUEST_DELAY)
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                logger.warning(f"Async request failed (attempt {attempt + 1}): {e}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
    
    @abstractmethod
    async def collect_season_data_async(self, year: int) -> pd.DataFrame:
        """Collect all data for a specific season asynchronously."""
        pass
