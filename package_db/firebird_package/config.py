"""
Configuration file for firebird_package

This file provides default configurations and fallback implementations
when the 'api' module is not available.
"""

import logging
import os
from typing import Optional

# Default logger configuration
def get_default_logger(name: str = "firebird_package") -> logging.Logger:
    """
    Create a default logger when api.core.loggerconfig is not available
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# Database connection function
def get_fdb_connection():
    """
    Create Firebird database connection using local credentials
    """
    try:
        import fdb
    except ImportError:
        raise ImportError(
            "fdb package not installed. Install it with: pip install fdb"
        )

    connection = fdb.connect(
        'localhost:/Users/anuragakp456/firebird_DB/transcript.fdb',
        user='SYSDBA',
        password='masterkey'
    )

    return connection

# Environment-based configuration
DATABASE_HOST = os.getenv("FIREBIRD_HOST", "localhost")
DATABASE_PORT = os.getenv("FIREBIRD_PORT", "3050")
DATABASE_PATH = os.getenv("FIREBIRD_DATABASE_PATH", "")
DATABASE_USER = os.getenv("FIREBIRD_USER", "")
DATABASE_PASSWORD = os.getenv("FIREBIRD_PASSWORD", "")

def get_database_config() -> dict:
    """
    Get database configuration from environment variables
    """
    return {
        "host": DATABASE_HOST,
        "port": DATABASE_PORT,
        "database": DATABASE_PATH,
        "user": DATABASE_USER,
        "password": DATABASE_PASSWORD,
    }