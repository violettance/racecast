"""Logging configuration for RaceCast project."""

import sys
from pathlib import Path
from loguru import logger

from src.config.settings import settings


def setup_logging():
    """Configure logging for the application."""
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        colorize=True
    )
    
    # Add file logger
    log_file = settings.PROJECT_ROOT / "logs" / "racecast.log"
    log_file.parent.mkdir(exist_ok=True)
    
    logger.add(
        log_file,
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logging configured successfully")
