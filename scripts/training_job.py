import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import mlflow
import numpy as np
import pandas as pd

from common.config import load_config
from common.logger import configure_logging, get_logger
from data_pipeline.feature_engineering.engineer import (
    engineer_item_features,
    engineer_user_features,
)
from data_pipeline.splitting.splitter import DataSplitter
from training.evaluation.metrics import ndcg_at_k, recall_at_k
from training.two_tower.model import build_two_tower_model

logger = get_logger(__name__)


def load_processed_data(config) -> tuple:
    """Load processed data."""
    processed_dir = Path(config.processed_data_path)

    movies = pd.read_parquet(processed_dir / "movies.parquet")
    ratings = pd.read_parquet(processed_dir / "ratings.parquet")
    users = pd.read_parquet(processed_dir / "users.parquet")

    logger.info(f"Loaded data: movies={len(movies)}, ratings={len(ratings)}, users={len(users)}")

    return movies, ratings, users


def main() -> None:
    """Main training pipeline."""
    config = load_config()
    configure_logging(
        log_level=config.log_level,
        log_format=config.log_format,
        log_file=config.log_file,
    )

    logger.info("Starting training pipeline")

    try:
        # Setup MLflow
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        mlflow.set_experiment(config.mlflow_experiment_name)

        with mlflow.start_run():
            # Load data
            movies, ratings, users = load_processed_data(config)

            # Split data
            logger.info("Splitting data")
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
                train_ratio=0.7,
                val_ratio=0.15,
                test_ratio=0.15,
                min_user_ratings=config.min_ratings_per_user,
            )

            # Engineer features
            logger.info("Engineering features")
            user_features = engineer_user_features(train_ratings, config.min_ratings_per_user)
            item_features = engineer_item_features(
                train_ratings,
                train_movies,
                config.min_interactions_per_item,
            )

            logger.info(f"User features: {len(user_features)}, Item features: {len(item_features)}")

            # Get vocab sizes
            user_vocab_size = int(train_ratings["userId"].max()) + 1
            item_vocab_size = int(train_ratings["movieId"].max()) + 1

            logger.info(f"User vocab size: {user_vocab_size}, Item vocab size: {item_vocab_size}")

            # Build model
            logger.info("Building two-tower model")
            model = build_two_tower_model(
                user_vocab_size=user_vocab_size,
                item_vocab_size=item_vocab_size,
                embedding_dim=config.embedding_dim,
                hidden_units=config.hidden_units,
                learning_rate=config.learning_rate,
            )

            # Prepare training data
            train_user_ids = train_ratings["userId"].values.astype(np.int32)
            train_item_ids = train_ratings["movieId"].values.astype(np.int32)
            train_labels = train_ratings["rating"].values / 5.0  # Normalize to [0, 1]

            val_user_ids = val_ratings["userId"].values.astype(np.int32)
            val_item_ids = val_ratings["movieId"].values.astype(np.int32)
            val_labels = val_ratings["rating"].values / 5.0

            # Train model
            logger.info("Training model")
            history = model.fit(
                {
                    "user_id": train_user_ids,
                    "item_id": train_item_ids,
                },
                train_labels,
                validation_data=(
                    {
                        "user_id": val_user_ids,
                        "item_id": val_item_ids,
                    },
                    val_labels,
                ),
                epochs=config.epochs,
                batch_size=config.batch_size,
                verbose=1,
            )

            # Evaluate
            logger.info("Evaluating model")
            test_user_ids = test_ratings["userId"].values.astype(np.int32)
            test_item_ids = test_ratings["movieId"].values.astype(np.int32)
            test_preds, _ = model(
                {
                    "user_id": test_user_ids,
                    "item_id": test_item_ids,
                },
                training=False,
            )

            test_labels = test_ratings["rating"].values / 5.0

            # Log metrics
            mlflow.log_param("embedding_dim", config.embedding_dim)
            mlflow.log_param("hidden_units", config.hidden_units)
            mlflow.log_param("learning_rate", config.learning_rate)
            mlflow.log_param("batch_size", config.batch_size)

            mlflow.log_metric("final_train_loss", float(history.history["loss"][-1]))
            mlflow.log_metric("final_val_loss", float(history.history["val_loss"][-1]))

            # Save model
            logger.info("Saving model")
            models_dir = Path(config.processed_data_path) / "models"
            models_dir.mkdir(parents=True, exist_ok=True)

            model.save(models_dir / "two_tower_model")
            logger.info(f"Model saved to {models_dir}")

            mlflow.keras.log_model(model, "two_tower_model")

            logger.info("Training pipeline complete")

    except Exception as e:
        logger.error(f"Error in training pipeline: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
