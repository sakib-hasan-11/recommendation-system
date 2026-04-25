import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import load_config
from common.logger import configure_logging, get_logger
from data_pipeline.ingestion.loaders import LocalDataLoader
from data_pipeline.validation.schema_validator import (
    validate_and_clean_movies,
    validate_and_clean_ratings,
    validate_and_clean_users,
)

logger = get_logger(__name__)


def main() -> None:
    """Main ingestion pipeline."""
    config = load_config()
    configure_logging(
        log_level=config.log_level,
        log_format=config.log_format,
        log_file=config.log_file,
    )

    logger.info("Starting data ingestion pipeline")

    try:
        # Load data from local
        loader = LocalDataLoader(config.data_local_path)
        movies, ratings, users = loader.load_all()

        logger.info(f"Loaded: movies={len(movies)}, ratings={len(ratings)}, users={len(users)}")

        # Validate and clean
        logger.info("Validating and cleaning data")
        movies = validate_and_clean_movies(movies)
        ratings = validate_and_clean_ratings(ratings)
        users = validate_and_clean_users(users)

        logger.info(
            f"Cleaned: movies={len(movies)}, ratings={len(ratings)}, users={len(users)}",
        )

        # Save processed data
        processed_dir = Path(config.processed_data_path)
        processed_dir.mkdir(parents=True, exist_ok=True)

        movies.to_parquet(processed_dir / "movies.parquet", index=False)
        ratings.to_parquet(processed_dir / "ratings.parquet", index=False)
        users.to_parquet(processed_dir / "users.parquet", index=False)

        logger.info(f"Saved processed data to {processed_dir}")

        # TODO: Upload to S3
        # if config.aws_access_key_id:
        #     s3_client = S3Client(config.s3_bucket, config.aws_region)
        #     s3_client.upload_dataframe(movies, f"{config.s3_processed_prefix}/movies.parquet")
        #     s3_client.upload_dataframe(ratings, f"{config.s3_processed_prefix}/ratings.parquet")
        #     s3_client.upload_dataframe(users, f"{config.s3_processed_prefix}/users.parquet")
        #     logger.info("Uploaded data to S3")

        logger.info("Data ingestion pipeline complete")

    except Exception as e:
        logger.error(f"Error in ingestion pipeline: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
