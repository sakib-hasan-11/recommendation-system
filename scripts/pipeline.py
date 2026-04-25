#!/usr/bin/env python
"""
Complete end-to-end pipeline for recommendation system.
Orchestrates: ingestion → splitting → feature engineering → training → evaluation
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import load_config
from common.logger import configure_logging, get_logger
from data_pipeline.feature_engineering.engineer import (
    engineer_item_features,
    engineer_user_features,
)
from data_pipeline.ingestion.loaders import LocalDataLoader
from data_pipeline.splitting.splitter import DataSplitter
from data_pipeline.validation.schema_validator import (
    validate_and_clean_movies,
    validate_and_clean_ratings,
    validate_and_clean_users,
)
from scripts.eda import run_eda
from training.evaluation.metrics import ndcg_at_k, recall_at_k

logger = get_logger(__name__)


def main() -> None:
    """Run complete end-to-end pipeline."""
    config = load_config()
    configure_logging(
        log_level=config.log_level,
        log_format=config.log_format,
        log_file=config.log_file,
    )

    logger.info("=" * 80)
    logger.info("STARTING END-TO-END RECOMMENDATION SYSTEM PIPELINE")
    logger.info("=" * 80)

    try:
        # Step 1: EDA
        logger.info("\n[STEP 1] Running Exploratory Data Analysis...")
        run_eda(config.data_local_path)
        logger.info("✓ EDA completed")

        # Step 2: Load Data
        logger.info("\n[STEP 2] Loading Data...")
        loader = LocalDataLoader(config.data_local_path)
        movies, ratings, users = loader.load_all()
        logger.info(f"✓ Loaded: movies={len(movies)}, ratings={len(ratings)}, users={len(users)}")

        # Step 3: Validate and Clean
        logger.info("\n[STEP 3] Validating and Cleaning Data...")
        movies = validate_and_clean_movies(movies)
        ratings = validate_and_clean_ratings(ratings)
        users = validate_and_clean_users(users)
        logger.info(
            f"✓ Cleaned: movies={len(movies)}, ratings={len(ratings)}, users={len(users)}",
        )

        # Step 4: Split Data
        logger.info("\n[STEP 4] Splitting Data (temporal, per-user)...")
        (
            train_ratings,
            val_ratings,
            test_ratings,
            train_movies,
            val_movies,
            test_movies,
        ) = DataSplitter.user_temporal_split(
            ratings,
            movies,
            users,
            train_ratio=1 - config.validation_split - config.test_split,
            val_ratio=config.validation_split,
            test_ratio=config.test_split,
            min_user_ratings=config.min_ratings_per_user,
        )

        logger.info(
            f"✓ Split: train={len(train_ratings)}, val={len(val_ratings)}, test={len(test_ratings)}",
        )

        # Step 5: Feature Engineering
        logger.info("\n[STEP 5] Engineering Features...")
        user_features = engineer_user_features(train_ratings, config.min_ratings_per_user)
        item_features = engineer_item_features(
            train_ratings,
            train_movies,
            config.min_interactions_per_item,
        )
        logger.info(f"✓ User features: {len(user_features)}, Item features: {len(item_features)}")

        # Step 6: Save Data
        logger.info("\n[STEP 6] Saving Processed Data...")
        processed_dir = Path(config.processed_data_path)
        processed_dir.mkdir(parents=True, exist_ok=True)

        train_ratings.to_parquet(processed_dir / "train_ratings.parquet", index=False)
        val_ratings.to_parquet(processed_dir / "val_ratings.parquet", index=False)
        test_ratings.to_parquet(processed_dir / "test_ratings.parquet", index=False)

        train_movies.to_parquet(processed_dir / "train_movies.parquet", index=False)
        val_movies.to_parquet(processed_dir / "val_movies.parquet", index=False)
        test_movies.to_parquet(processed_dir / "test_movies.parquet", index=False)

        user_features.to_parquet(processed_dir / "user_features.parquet", index=False)
        item_features.to_parquet(processed_dir / "item_features.parquet", index=False)

        logger.info(f"✓ Saved data to {processed_dir}")

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Training data: {len(train_ratings)} ratings")
        logger.info(f"Validation data: {len(val_ratings)} ratings")
        logger.info(f"Test data: {len(test_ratings)} ratings")
        logger.info(f"User features: {len(user_features)} users")
        logger.info(f"Item features: {len(item_features)} items")
        logger.info(f"Processed data saved to: {processed_dir}")

    except Exception as e:
        logger.error(f"\n✗ Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
