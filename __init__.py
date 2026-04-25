"""
Production-grade recommendation system using MovieLens 1M.
"""

__version__ = "1.0.0"
__author__ = "MLOps Team"

from common.config import load_config
from common.logger import configure_logging, get_logger

__all__ = [
    "load_config",
    "configure_logging",
    "get_logger",
]
