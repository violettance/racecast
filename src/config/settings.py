"""Configuration settings for RaceCast project."""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    
    # API Configuration
    ERGAST_BASE_URL: str = "https://api.jolpi.ca/ergast/f1"
    FASTF1_CACHE_DIR: Optional[Path] = DATA_DIR / "fastf1_cache"
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    
    # Data Collection Settings
    START_YEAR: int = 2017
    END_YEAR: int = 2024
    MAX_RETRIES: int = 3
    REQUEST_DELAY: float = 0.5  # seconds between requests
    
    # Model Settings
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    CV_FOLDS: int = 5
    
    # Feature Engineering
    RECENT_RACES_COUNT: int = 5  # for form calculation
    MIN_RACES_FOR_STATS: int = 3  # minimum races for statistical features
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @validator("DATA_DIR", "RAW_DATA_DIR", "PROCESSED_DATA_DIR", "MODELS_DIR", pre=True)
    def create_directories(cls, v):
        """Create directories if they don't exist."""
        if isinstance(v, (str, Path)):
            path = Path(v)
            path.mkdir(parents=True, exist_ok=True)
            return path
        return v
    
    def get_season_range(self) -> List[int]:
        """Get list of seasons to process."""
        return list(range(self.START_YEAR, self.END_YEAR + 1))


# Global settings instance
settings = Settings()
