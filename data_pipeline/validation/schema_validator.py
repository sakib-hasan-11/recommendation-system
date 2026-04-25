import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validate data schema."""

    MOVIES_SCHEMA = {
        "movieId": "int64",
        "title": "object",
        "genres": "object",
    }

    RATINGS_SCHEMA = {
        "userId": "int64",
        "movieId": "int64",
        "rating": "float64",
        "timestamp": "int64",
    }

    USERS_SCHEMA = {
        "userId": "int64",
        "gender": "object",
        "age": "int64",
        "occupation": "int64",
        "zip": "object",
    }

    @staticmethod
    def validate_movies(df: pd.DataFrame) -> bool:
        """Validate movies DataFrame."""
        required_cols = set(SchemaValidator.MOVIES_SCHEMA.keys())
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing columns in movies: {missing}")

        # Check for duplicates
        if df["movieId"].duplicated().any():
            raise ValueError("Duplicate movieIds found")

        logger.info(f"Movies schema validated: {len(df)} rows")
        return True

    @staticmethod
    def validate_ratings(df: pd.DataFrame) -> bool:
        """Validate ratings DataFrame."""
        required_cols = set(SchemaValidator.RATINGS_SCHEMA.keys())
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing columns in ratings: {missing}")

        # Check rating range
        if not df["rating"].between(0.5, 5.0).all():
            raise ValueError("Ratings must be between 0.5 and 5.0")

        logger.info(f"Ratings schema validated: {len(df)} rows")
        return True

    @staticmethod
    def validate_users(df: pd.DataFrame) -> bool:
        """Validate users DataFrame."""
        required_cols = set(SchemaValidator.USERS_SCHEMA.keys())
        if not required_cols.issubset(set(df.columns)):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing columns in users: {missing}")

        if df["userId"].duplicated().any():
            raise ValueError("Duplicate userIds found")

        logger.info(f"Users schema validated: {len(df)} rows")
        return True


def clean_data(df: pd.DataFrame, data_type: str) -> pd.DataFrame:
    """Clean data based on type."""
    logger.info(f"Cleaning {data_type} data: {len(df)} rows")

    # Remove null values
    df = df.dropna()

    # Remove duplicates
    if data_type == "movies":
        df = df.drop_duplicates(subset=["movieId"])
    elif data_type == "ratings":
        df = df.drop_duplicates(subset=["userId", "movieId", "timestamp"])
    elif data_type == "users":
        df = df.drop_duplicates(subset=["userId"])

    logger.info(f"Cleaned {data_type} data: {len(df)} rows")
    return df


def validate_and_clean_movies(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean movies data."""
    SchemaValidator.validate_movies(df)
    return clean_data(df, "movies")


def validate_and_clean_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean ratings data."""
    SchemaValidator.validate_ratings(df)
    return clean_data(df, "ratings")


def validate_and_clean_users(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean users data."""
    SchemaValidator.validate_users(df)
    return clean_data(df, "users")
