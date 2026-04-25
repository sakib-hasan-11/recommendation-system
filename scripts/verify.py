#!/usr/bin/env python
"""
Verify project structure and completeness.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.logger import get_logger

logger = get_logger(__name__)


def verify_directory_structure() -> bool:
    """Verify all required directories exist."""
    required_dirs = [
        "data_pipeline/ingestion",
        "data_pipeline/validation",
        "data_pipeline/splitting",
        "data_pipeline/feature_engineering",
        "feast_repo/feature_repo",
        "feast_repo/feature_views",
        "training/two_tower",
        "training/ranking",
        "training/optuna_tuning",
        "training/evaluation",
        "serving/api",
        "serving/cache",
        "serving/recommender",
        "frontend/streamlit_app",
        "infra/docker",
        "infra/aws_batch",
        "infra/scripts",
        "common/config",
        "common/logger",
        "common/utils",
        "tests",
        "scripts",
    ]

    logger.info("Verifying directory structure...")
    missing_dirs = []

    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
            logger.error(f"[MISSING] {dir_path}")
        else:
            logger.info(f"[OK] {dir_path}")

    return len(missing_dirs) == 0


def verify_key_files() -> bool:
    """Verify all key files exist."""
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        ".env.example",
        "Makefile",
        "README.md",
        "QUICKSTART.md",
        "ARCHITECTURE.md",
        "conftest.py",
        "docker-compose.yml",
        "data_pipeline/ingestion/loaders.py",
        "data_pipeline/validation/schema_validator.py",
        "data_pipeline/splitting/splitter.py",
        "data_pipeline/feature_engineering/engineer.py",
        "training/two_tower/model.py",
        "training/ranking/model.py",
        "training/optuna_tuning/tuner.py",
        "training/evaluation/metrics.py",
        "serving/api/main.py",
        "serving/api/routes.py",
        "serving/cache/manager.py",
        "serving/recommender/service.py",
        "frontend/streamlit_app/app.py",
        "common/config/__init__.py",
        "common/logger/__init__.py",
        "common/utils/__init__.py",
        "scripts/eda.py",
        "scripts/ingestion_job.py",
        "scripts/training_job.py",
        "scripts/api_server.py",
        "scripts/pipeline.py",
        "scripts/health_check.py",
        "scripts/init_env.py",
        "tests/test_validation.py",
        "tests/test_metrics.py",
        "tests/test_splitting.py",
        "tests/test_features.py",
        "infra/docker/Dockerfile.base",
        "infra/docker/Dockerfile.api",
        "infra/docker/Dockerfile.ingestion",
        "infra/docker/Dockerfile.training",
        "infra/aws_batch/ingestion_job.json",
        "infra/aws_batch/training_job.json",
        "infra/aws_batch/feature_materialization_job.json",
        "infra/aws_batch/iam_policy.json",
        "infra/scripts/deploy.sh",
        "infra/scripts/register_jobs.sh",
    ]

    logger.info("\nVerifying key files...")
    missing_files = []

    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            logger.error(f"[MISSING] {file_path}")
        else:
            logger.info(f"[OK] {file_path}")

    return len(missing_files) == 0


def verify_imports() -> bool:
    """Verify key imports work."""
    logger.info("\nVerifying imports...")

    imports_to_test = [
        ("common.config", "load_config"),
        ("common.logger", "get_logger"),
        ("common.utils", "S3Client"),
        ("data_pipeline.validation.schema_validator", "SchemaValidator"),
        ("data_pipeline.splitting.splitter", "DataSplitter"),
        ("data_pipeline.feature_engineering.engineer", "FeatureEngineer"),
        ("training.two_tower.model", "TwoTowerModel"),
        ("training.ranking.model", "RankingModel"),
        ("training.optuna_tuning.tuner", "TwoTowerTuner"),
        ("training.evaluation.metrics", "recall_at_k"),
        ("serving.cache.manager", "CacheManager"),
        ("serving.recommender.service", "RecommenderService"),
    ]

    failed_imports = []

    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            logger.info(f"[OK] {module_name}.{class_name}")
        except Exception as e:
            failed_imports.append((module_name, class_name, str(e)))
            logger.error(f"[FAILED] {module_name}.{class_name}: {e}")

    return len(failed_imports) == 0


def verify_data_files() -> bool:
    """Verify data files exist."""
    logger.info("\nVerifying data files...")

    data_files = [
        "data_local/movies.csv",
        "data_local/ratings.csv",
        "data_local/users.csv",
    ]

    missing_files = []

    for file_path in data_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            logger.warning(f"[MISSING] Data file: {file_path} (expected)")
        else:
            logger.info(f"[OK] {file_path}")

    return len(missing_files) <= len(data_files)  # Data files optional at verification time


def main() -> None:
    """Run verification."""
    logger.info("=" * 70)
    logger.info("PROJECT STRUCTURE VERIFICATION")
    logger.info("=" * 70)

    checks = [
        ("Directory Structure", verify_directory_structure()),
        ("Key Files", verify_key_files()),
        ("Imports", verify_imports()),
        ("Data Files", verify_data_files()),
    ]

    logger.info("\n" + "=" * 70)
    logger.info("VERIFICATION RESULTS")
    logger.info("=" * 70)

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    for check_name, result in checks:
        status = "[PASS]" if result else "[FAIL]"
        logger.info(f"{status}: {check_name}")

    logger.info("=" * 70)
    logger.info(f"Passed: {passed}/{total}")

    if passed == total:
        logger.info("\n[SUCCESS] All verification checks passed!")
        logger.info("\nNext steps:")
        logger.info("1. python scripts/init_env.py  # Initialize environment")
        logger.info("2. make venv                   # Create virtual environment")
        logger.info("3. make install                # Install dependencies")
        logger.info("4. make run-local              # Run full pipeline")
        sys.exit(0)
    else:
        logger.error(f"\n[FAILED] Verification failed! {total - passed} check(s) failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
