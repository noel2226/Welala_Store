"""
Logging configuration for the application.
Provides structured logging with appropriate levels.
"""

import logging
import logging.handlers
from pathlib import Path


def setup_logging(debug: bool = False) -> None:
    """
    Configure application logging.
    
    Args:
        debug: Enable debug level logging
    """
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console output
        ]
    )
    
    # Get FastAPI and SQLAlchemy loggers
    logging.getLogger("fastapi").setLevel(log_level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO if not debug else logging.DEBUG)
