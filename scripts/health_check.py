#!/usr/bin/env python
"""
System health check and diagnostics.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import redis

from common.config import load_config
from common.logger import get_logger

logger = get_logger(__name__)


def check_data_files(config) -> bool:
    """Check if data files exist."""
    data_dir = Path(config.data_local_path)
    required_files = ["movies.csv", "ratings.csv", "users.csv"]

    logger.info("Checking data files...")
    for file in required_files:
        file_path = data_dir / file
        if not file_path.exists():
            logger.error(f"Missing data file: {file_path}")
            return False
        logger.info(f"✓ Found {file}")

    return True


def check_redis(config) -> bool:
    """Check Redis connectivity."""
    logger.info("Checking Redis connectivity...")
    try:
        client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            socket_connect_timeout=5,
        )
        client.ping()
        logger.info(f"✓ Redis connected at {config.redis_host}:{config.redis_port}")
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False


def check_directories(config) -> bool:
    """Check required directories."""
    logger.info("Checking directories...")
    dirs_to_check = [
        config.data_local_path,
        config.processed_data_path,
        config.training_data_path,
    ]

    for dir_path in dirs_to_check:
        path = Path(dir_path)
        if not path.exists():
            logger.warning(f"Creating missing directory: {path}")
            path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory available: {path}")

    return True


def main() -> None:
    """Run health checks."""
    logger.info("=" * 60)
    logger.info("SYSTEM HEALTH CHECK")
    logger.info("=" * 60)

    config = load_config()

    checks = [
        ("Data Files", check_data_files(config)),
        ("Directories", check_directories(config)),
        ("Redis", check_redis(config)),
    ]

    logger.info("\nHealth Check Results:")
    logger.info("-" * 60)

    passed = 0
    failed = 0

    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {check_name}")
        if result:
            passed += 1
        else:
            failed += 1

    logger.info("-" * 60)
    logger.info(f"Passed: {passed}/{len(checks)}")
    logger.info(f"Failed: {failed}/{len(checks)}")
    logger.info("=" * 60)

    if failed > 0:
        logger.error("Health check failed!")
        sys.exit(1)
    else:
        logger.info("All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
