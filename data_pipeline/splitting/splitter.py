import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataSplitter:
    """Split data while preventing leakage."""

    @staticmethod
    def temporal_split(
        df: pd.DataFrame,
        timestamp_col: str,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data by time.

        Args:
            df: Input DataFrame with timestamp column
            timestamp_col: Name of timestamp column
            train_ratio: Ratio for training set
            val_ratio: Ratio for validation set
            test_ratio: Ratio for test set

        Returns:
            Tuple of (train, val, test) DataFrames
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5

        df = df.sort_values(timestamp_col)

        n = len(df)
        train_size = int(n * train_ratio)
        val_size = int(n * val_ratio)

        train = df.iloc[:train_size].copy()
        val = df.iloc[train_size : train_size + val_size].copy()
        test = df.iloc[train_size + val_size :].copy()

        logger.info(
            f"Split data: train={len(train)}, val={len(val)}, test={len(test)}",
        )

        return train, val, test

    @staticmethod
    def user_temporal_split(
        ratings: pd.DataFrame,
        movies: pd.DataFrame,
        users: pd.DataFrame,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        min_user_ratings: int = 5,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data per user by time to prevent leakage.

        Args:
            ratings: Ratings DataFrame
            movies: Movies DataFrame
            users: Users DataFrame
            train_ratio: Training ratio
            val_ratio: Validation ratio
            test_ratio: Test ratio
            min_user_ratings: Minimum ratings per user

        Returns:
            Tuple of (train_ratings, val_ratings, test_ratings,
                     train_movies, val_movies, test_movies)
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5

        # Filter users with minimum ratings
        user_counts = ratings.groupby("userId").size()
        valid_users = user_counts[user_counts >= min_user_ratings].index
        filtered_ratings = ratings[ratings["userId"].isin(valid_users)].copy()

        logger.info(
            f"Filtered to {len(valid_users)} users with >= {min_user_ratings} ratings",
        )

        train_list = []
        val_list = []
        test_list = []

        for user_id in valid_users:
            user_ratings = filtered_ratings[filtered_ratings["userId"] == user_id].sort_values(
                "timestamp",
            )

            n = len(user_ratings)
            train_size = int(n * train_ratio)
            val_size = int(n * val_ratio)

            train_list.append(user_ratings.iloc[:train_size])
            val_list.append(user_ratings.iloc[train_size : train_size + val_size])
            test_list.append(user_ratings.iloc[train_size + val_size :])

        train_ratings = pd.concat(train_list, ignore_index=True)
        val_ratings = pd.concat(val_list, ignore_index=True)
        test_ratings = pd.concat(test_list, ignore_index=True)

        # Get movies present in each split
        train_movies = movies[movies["movieId"].isin(train_ratings["movieId"])].copy()
        val_movies = movies[movies["movieId"].isin(val_ratings["movieId"])].copy()
        test_movies = movies[movies["movieId"].isin(test_ratings["movieId"])].copy()

        logger.info(
            f"User-based split: train={len(train_ratings)}, "
            f"val={len(val_ratings)}, test={len(test_ratings)}",
        )

        return train_ratings, val_ratings, test_ratings, train_movies, val_movies, test_movies
