import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration."""

    # Environment
    env: str = Field(default="local", validation_alias="ENV")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_format: str = Field(default="json", validation_alias="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, validation_alias="LOG_FILE")

    # AWS
    aws_region: str = Field(default="us-east-1", validation_alias="AWS_REGION")
    aws_access_key_id: str = Field(
        default="",
        validation_alias="AWS_ACCESS_KEY_ID",
    )
    aws_secret_access_key: str = Field(
        default="",
        validation_alias="AWS_SECRET_ACCESS_KEY",
    )
    aws_batch_queue: str = Field(
        default="recommendation-queue",
        validation_alias="AWS_BATCH_QUEUE",
    )
    aws_batch_job_definition: str = Field(
        default="recommendation-job",
        validation_alias="AWS_BATCH_JOB_DEFINITION",
    )

    # S3
    s3_bucket: str = Field(default="recommendation-system", validation_alias="S3_BUCKET")
    s3_ingestion_prefix: str = Field(
        default="raw-data",
        validation_alias="S3_INGESTION_PREFIX",
    )
    s3_processed_prefix: str = Field(
        default="processed-data",
        validation_alias="S3_PROCESSED_PREFIX",
    )
    s3_models_prefix: str = Field(default="models", validation_alias="S3_MODELS_PREFIX")
    s3_feast_prefix: str = Field(default="feast-repo", validation_alias="S3_FEAST_PREFIX")

    # Feast
    feast_repo_path: str = Field(
        default="./feast_repo/feature_repo",
        validation_alias="FEAST_REPO_PATH",
    )
    feast_offline_store: str = Field(
        default="file",
        validation_alias="FEAST_OFFLINE_STORE",
    )
    feast_online_store: str = Field(
        default="redis",
        validation_alias="FEAST_ONLINE_STORE",
    )

    # Redis
    redis_host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(default=0, validation_alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, validation_alias="REDIS_PASSWORD")
    cache_ttl: int = Field(default=3600, validation_alias="CACHE_TTL")

    # Pinecone
    pinecone_api_key: str = Field(default="", validation_alias="PINECONE_API_KEY")
    pinecone_host: str = Field(
        default="",
        validation_alias="PINECONE_HOST",
    )
    pinecone_index_name: str = Field(
        default="recommendations",
        validation_alias="PINECONE_INDEX_NAME",
    )
    pinecone_environment: str = Field(
        default="gcp-starter",
        validation_alias="PINECONE_ENVIRONMENT",
    )

    # MLflow
    mlflow_tracking_uri: str = Field(
        default="http://localhost:5000",
        validation_alias="MLFLOW_TRACKING_URI",
    )
    mlflow_experiment_name: str = Field(
        default="recommendation-system",
        validation_alias="MLFLOW_EXPERIMENT_NAME",
    )
    mlflow_backend_store_uri: str = Field(
        default="sqlite:///mlflow.db",
        validation_alias="MLFLOW_BACKEND_STORE_URI",
    )
    mlflow_artifact_root: str = Field(
        default="./mlruns",
        validation_alias="MLFLOW_ARTIFACT_ROOT",
    )

    # Model Configuration
    embedding_dim: int = Field(default=64, validation_alias="EMBEDDING_DIM")
    hidden_units: int = Field(default=256, validation_alias="HIDDEN_UNITS")
    learning_rate: float = Field(default=0.001, validation_alias="LEARNING_RATE")
    batch_size: int = Field(default=32, validation_alias="BATCH_SIZE")
    epochs: int = Field(default=10, validation_alias="EPOCHS")
    validation_split: float = Field(default=0.1, validation_alias="VALIDATION_SPLIT")
    test_split: float = Field(default=0.1, validation_alias="TEST_SPLIT")

    # Feature Engineering
    recall_at_k: int = Field(default=10, validation_alias="RECALL_AT_K")
    ndcg_at_k: int = Field(default=10, validation_alias="NDCG_AT_K")
    min_ratings_per_user: int = Field(default=5, validation_alias="MIN_RATINGS_PER_USER")
    min_interactions_per_item: int = Field(
        default=5,
        validation_alias="MIN_INTERACTIONS_PER_ITEM",
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    api_workers: int = Field(default=4, validation_alias="API_WORKERS")
    api_reload: bool = Field(default=False, validation_alias="API_RELOAD")

    # Streamlit Configuration
    streamlit_port: int = Field(default=8501, validation_alias="STREAMLIT_SERVER_PORT")
    api_endpoint: str = Field(
        default="http://localhost:8000",
        validation_alias="API_ENDPOINT",
    )

    # Data Paths
    data_local_path: str = Field(default="./data_local", validation_alias="DATA_LOCAL_PATH")
    training_data_path: str = Field(
        default="./data/training",
        validation_alias="TRAINING_DATA_PATH",
    )
    processed_data_path: str = Field(
        default="./data/processed",
        validation_alias="PROCESSED_DATA_PATH",
    )

    # Optuna Configuration
    optuna_n_trials: int = Field(default=50, validation_alias="OPTUNA_N_TRIALS")
    optuna_n_jobs: int = Field(default=4, validation_alias="OPTUNA_N_JOBS")
    optuna_timeout: int = Field(default=3600, validation_alias="OPTUNA_TIMEOUT")

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",  # Ignore extra fields not defined in the model
    }


def load_config() -> Config:
    """Load configuration from environment variables and .env file."""
    return Config()


def get_config() -> Config:
    """Get the singleton config instance."""
    return load_config()
