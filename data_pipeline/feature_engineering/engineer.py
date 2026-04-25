import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering for recommendation system."""

    @staticmethod
    def engineer_user_features(
        ratings: pd.DataFrame,
        min_interactions: int = 5,
    ) -> pd.DataFrame:
        """
        Engineer user features.

        Returns:
            DataFrame with userId and user features
        """
        user_features = (
            ratings.groupby("userId")
            .agg(
                num_ratings=("movieId", "count"),
                avg_rating=("rating", "mean"),
                std_rating=("rating", "std"),
                min_rating=("rating", "min"),
                max_rating=("rating", "max"),
                latest_timestamp=("timestamp", "max"),
            )
            .reset_index()
        )

        # Filter by minimum interactions
        user_features = user_features[user_features["num_ratings"] >= min_interactions]

        # Fill NaN values
        user_features["std_rating"] = user_features["std_rating"].fillna(0)

        logger.info(f"Engineered features for {len(user_features)} users")
        return user_features

    @staticmethod
    def engineer_item_features(
        ratings: pd.DataFrame,
        movies: pd.DataFrame,
        min_ratings: int = 5,
    ) -> pd.DataFrame:
        """Engineer item (movie) features."""
        item_features = (
            ratings.groupby("movieId")
            .agg(
                num_ratings=("userId", "count"),
                avg_rating=("rating", "mean"),
                std_rating=("rating", "std"),
                min_rating=("rating", "min"),
                max_rating=("rating", "max"),
            )
            .reset_index()
        )

        # Filter by minimum ratings
        item_features = item_features[item_features["num_ratings"] >= min_ratings]

        # Merge with movie titles and genres
        item_features = item_features.merge(movies, on="movieId", how="left")

        # Fill NaN values
        item_features["std_rating"] = item_features["std_rating"].fillna(0)

        logger.info(f"Engineered features for {len(item_features)} items")
        return item_features

    @staticmethod
    def engineer_interaction_features(
        ratings: pd.DataFrame,
    ) -> pd.DataFrame:
        """Engineer interaction-level features."""
        interaction_features = ratings.copy()

        # Calculate recency (days since interaction)
        max_timestamp = interaction_features["timestamp"].max()
        interaction_features["recency_days"] = (
            max_timestamp - interaction_features["timestamp"]
        ) / (24 * 3600)

        # Create rating categories
        interaction_features["rating_category"] = pd.cut(
            interaction_features["rating"],
            bins=[0, 2, 3, 4, 5],
            labels=["low", "medium", "high", "very_high"],
        )

        logger.info(f"Engineered {len(interaction_features)} interaction features")
        return interaction_features

    @staticmethod
    def create_training_dataset(
        ratings: pd.DataFrame,
        movies: pd.DataFrame,
        user_features: pd.DataFrame,
        item_features: pd.DataFrame,
    ) -> pd.DataFrame:
        """Create training dataset with all features."""
        # Merge ratings with user features
        dataset = ratings.merge(user_features, on="userId", how="left", suffixes=("", "_user"))

        # Merge with item features
        dataset = dataset.merge(item_features, on="movieId", how="left", suffixes=("", "_item"))

        logger.info(f"Created training dataset with {len(dataset)} samples")
        return dataset


# Module-level wrapper functions for backward compatibility
def engineer_user_features(
    ratings: pd.DataFrame,
    min_interactions: int = 5,
) -> pd.DataFrame:
    """Engineer user features - wrapper for FeatureEngineer class."""
    return FeatureEngineer.engineer_user_features(ratings, min_interactions)


def engineer_item_features(
    ratings: pd.DataFrame,
    movies: pd.DataFrame,
    min_ratings: int = 5,
) -> pd.DataFrame:
    """Engineer item features - wrapper for FeatureEngineer class."""
    return FeatureEngineer.engineer_item_features(ratings, movies, min_ratings)


def engineer_interaction_features(
    ratings: pd.DataFrame,
) -> pd.DataFrame:
    """Engineer interaction features - wrapper for FeatureEngineer class."""
    return FeatureEngineer.engineer_interaction_features(ratings)


def create_training_dataset(
    ratings: pd.DataFrame,
    movies: pd.DataFrame,
    user_features: pd.DataFrame,
    item_features: pd.DataFrame,
) -> pd.DataFrame:
    """Create training dataset - wrapper for FeatureEngineer class."""
    return FeatureEngineer.create_training_dataset(ratings, movies, user_features, item_features)
