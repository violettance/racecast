"""Configuration settings for RaceCast project."""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings:
    """Application settings (env-driven, no external deps)."""

    def __init__(self):
        # Project paths
        self.PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
        self.DATA_DIR: Path = self.PROJECT_ROOT / "data"
        self.RAW_DATA_DIR: Path = self.DATA_DIR / "raw"
        self.PROCESSED_DATA_DIR: Path = self.DATA_DIR / "processed"
        self.MODELS_DIR: Path = self.PROJECT_ROOT / "models"

        # API Configuration
        self.ERGAST_BASE_URL: str = os.getenv("ERGAST_BASE_URL", "https://api.jolpi.ca/ergast/f1")
        self.FASTF1_CACHE_DIR: Optional[Path] = Path(os.getenv("FASTF1_CACHE_DIR", str(self.DATA_DIR / "fastf1_cache")))
        self.API_KEY: Optional[str] = os.getenv("API_KEY")
        self.ALLOW_ORIGINS: str = os.getenv("ALLOW_ORIGINS", "*")

        # Database Configuration
        self.DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
        self.DB_HOST: Optional[str] = os.getenv("DB_HOST")
        self.DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
        self.DB_NAME: Optional[str] = os.getenv("DB_NAME")
        self.DB_USER: Optional[str] = os.getenv("DB_USER")
        self.DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")

        # Data Collection Settings
        self.START_YEAR: int = int(os.getenv("START_YEAR", "2017"))
        self.END_YEAR: int = int(os.getenv("END_YEAR", "2025"))
        self.MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
        self.REQUEST_DELAY: float = float(os.getenv("REQUEST_DELAY", "10.0"))

        # Model Settings
        self.RANDOM_STATE: int = int(os.getenv("RANDOM_STATE", "42"))
        self.TEST_SIZE: float = float(os.getenv("TEST_SIZE", "0.2"))
        self.CV_FOLDS: int = int(os.getenv("CV_FOLDS", "5"))
        self.MODEL_RANKER_PATH: Path = Path(os.getenv("MODEL_RANKER_PATH", "models/xgboost/xgboost_ranker_model.pkl"))

        # Feature Engineering
        self.RECENT_RACES_COUNT: int = int(os.getenv("RECENT_RACES_COUNT", "5"))
        self.MIN_RACES_FOR_STATS: int = int(os.getenv("MIN_RACES_FOR_STATS", "3"))

        # Logging
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT: str = os.getenv("LOG_FORMAT", "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}")

        # Ensure directories exist
        for p in [self.DATA_DIR, self.RAW_DATA_DIR, self.PROCESSED_DATA_DIR, self.MODELS_DIR, self.FASTF1_CACHE_DIR]:
            if p is not None:
                Path(p).mkdir(parents=True, exist_ok=True)

    def get_season_range(self) -> List[int]:
        return list(range(self.START_YEAR, self.END_YEAR + 1))


# Global settings instance
settings = Settings()
