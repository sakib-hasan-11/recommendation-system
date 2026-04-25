import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class LocalDataLoader:
    """Load data from local filesystem."""

    def __init__(self, data_dir: str) -> None:
        self.data_dir = Path(data_dir)

    def load_movies(self, separator: str = ",") -> pd.DataFrame:
        """Load movies data."""
        path = self.data_dir / "movies.csv"
        logger.info(f"Loading movies from {path}")
        df = pd.read_csv(path, sep=separator)
        logger.info(f"Loaded {len(df)} movies")
        return df

    def load_ratings(self, separator: str = ",") -> pd.DataFrame:
        """Load ratings data."""
        path = self.data_dir / "ratings.csv"
        logger.info(f"Loading ratings from {path}")
        df = pd.read_csv(path, sep=separator)
        logger.info(f"Loaded {len(df)} ratings")
        return df

    def load_users(self, separator: str = ",") -> pd.DataFrame:
        """Load users data."""
        path = self.data_dir / "users.csv"
        logger.info(f"Loading users from {path}")
        df = pd.read_csv(path, sep=separator)
        logger.info(f"Loaded {len(df)} users")
        return df

    def load_all(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all data."""
        movies = self.load_movies()
        ratings = self.load_ratings()
        users = self.load_users()
        return movies, ratings, users


class S3DataLoader:
    """Load data from S3."""

    def __init__(self, bucket_name: str, prefix: str, region: str = "us-east-1") -> None:
        import boto3

        self.bucket_name = bucket_name
        self.prefix = prefix
        self.s3_client = boto3.client("s3", region_name=region)

    def load_csv(self, key: str) -> pd.DataFrame:
        """Load CSV from S3."""
        logger.info(f"Loading {key} from S3")
        obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        df = pd.read_csv(obj["Body"])
        logger.info(f"Loaded {len(df)} rows")
        return df

    def load_parquet(self, key: str) -> pd.DataFrame:
        """Load Parquet from S3."""
        logger.info(f"Loading {key} from S3")
        obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        df = pd.read_parquet(obj["Body"])
        logger.info(f"Loaded {len(df)} rows")
        return df
