import json
import os
import pickle
from pathlib import Path
from typing import Any, Optional

import pandas as pd


class S3Client:
    """Simple S3 client wrapper."""

    def __init__(self, bucket_name: str, region: str = "us-east-1") -> None:
        import boto3

        self.bucket_name = bucket_name
        self.s3_client = boto3.client("s3", region_name=region)

    def upload_file(self, file_path: str, s3_key: str) -> None:
        """Upload file to S3."""
        self.s3_client.upload_file(file_path, self.bucket_name, s3_key)

    def download_file(self, s3_key: str, file_path: str) -> None:
        """Download file from S3."""
        self.s3_client.download_file(self.bucket_name, s3_key, file_path)

    def upload_dataframe(self, df: pd.DataFrame, s3_key: str, format: str = "parquet") -> None:
        """Upload DataFrame to S3."""
        local_path = f"/tmp/{Path(s3_key).name}"
        if format == "parquet":
            df.to_parquet(local_path, index=False)
        elif format == "csv":
            df.to_csv(local_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        self.upload_file(local_path, s3_key)
        os.remove(local_path)

    def download_dataframe(self, s3_key: str, format: str = "parquet") -> pd.DataFrame:
        """Download DataFrame from S3."""
        local_path = f"/tmp/{Path(s3_key).name}"
        self.download_file(s3_key, local_path)
        if format == "parquet":
            df = pd.read_parquet(local_path)
        elif format == "csv":
            df = pd.read_csv(local_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        os.remove(local_path)
        return df

    def list_files(self, prefix: str) -> list[str]:
        """List files in S3 with given prefix."""
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix,
        )
        if "Contents" not in response:
            return []
        return [obj["Key"] for obj in response["Contents"]]

    def exists(self, s3_key: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception:
            return False


class RedisClient:
    """Simple Redis client wrapper."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
    ) -> None:
        import redis

        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
        )

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.client.set(key, value, ex=ttl)

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        value = self.client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def delete(self, key: str) -> None:
        """Delete key from Redis."""
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        return bool(self.client.exists(key))

    def clear(self) -> None:
        """Clear all keys from current database."""
        self.client.flushdb()

    def incr(self, key: str) -> int:
        """Increment value."""
        return self.client.incr(key)


class PineconeClient:
    """Simple Pinecone client wrapper using Pinecone v3.1.0+."""

    def __init__(
        self,
        api_key: str,
        index_name: str,
        host: str = "",
        environment: str = "gcp-starter",
    ) -> None:
        from pinecone import Pinecone

        # Initialize Pinecone with API key
        # If host is provided, use it; otherwise fall back to environment (legacy)
        if host:
            self.pc = Pinecone(api_key=api_key, host=host)
        else:
            # Legacy: use environment if host not provided
            self.pc = Pinecone(api_key=api_key)

        # Get the index
        self.index = self.pc.Index(index_name)

    def upsert_vectors(
        self,
        vectors: list[tuple[str, list[float]]],
        namespace: str = "",
    ) -> None:
        """Upsert vectors to Pinecone."""
        self.index.upsert(vectors=vectors, namespace=namespace)

    def query(
        self,
        vector: list[float],
        top_k: int = 10,
        namespace: str = "",
    ) -> list[dict]:
        """Query similar vectors."""
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
        )
        return results.matches


def save_pickle(obj: Any, path: str) -> None:
    """Save object to pickle file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def load_pickle(path: str) -> Any:
    """Load object from pickle file."""
    with open(path, "rb") as f:
        return pickle.load(f)


def ensure_dir(path: str) -> Path:
    """Ensure directory exists."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
