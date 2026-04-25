#!/usr/bin/env python
"""
Initialize local development environment.
"""

import shutil
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.logger import get_logger

logger = get_logger(__name__)


def create_directories() -> None:
    """Create required directories."""
    dirs = [
        "data_local",
        "data/processed",
        "data/training",
        "data/features",
        "logs",
        "models",
        "mlruns",
    ]

    for dir_path in dirs:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"[OK] Created directory: {path}")


def create_env_file() -> None:
    """Create .env file from template."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        logger.info("[OK] .env file already exists")
        return

    if not env_example.exists():
        logger.error(".env.example not found")
        sys.exit(1)

    shutil.copy(env_example, env_file)
    logger.info("[OK] Created .env from .env.example")


def check_python_version() -> None:
    """Check Python version."""
    import sys

    if sys.version_info < (3, 10):
        logger.error("Python 3.10+ required")
        sys.exit(1)

    logger.info(f"[OK] Python {sys.version.split()[0]} detected")


def main() -> None:
    """Initialize development environment."""
    logger.info("=" * 60)
    logger.info("INITIALIZING LOCAL DEVELOPMENT ENVIRONMENT")
    logger.info("=" * 60)

    try:
        check_python_version()
        create_directories()
        create_env_file()

        logger.info("=" * 60)
        logger.info("Initialization complete!")
        logger.info("Next steps:")
        logger.info("1. Review .env configuration")
        logger.info("2. Run: make install")
        logger.info("3. Run: make run-local")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
