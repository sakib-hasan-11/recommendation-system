import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn

from common.config import load_config
from common.logger import configure_logging, get_logger
from common.utils import PineconeClient, RedisClient
from serving.api.main import create_app
from serving.cache.manager import CacheManager
from serving.recommender.service import RecommenderService

logger = get_logger(__name__)


def main() -> None:
    """Main API server."""
    config = load_config()
    configure_logging(
        log_level=config.log_level,
        log_format=config.log_format,
        log_file=config.log_file,
    )

    logger.info("Starting API server")

    try:
        # Initialize Redis
        logger.info("Initializing Redis client")
        redis_client = RedisClient(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            password=config.redis_password,
        )

        # Initialize Pinecone
        logger.info("Initializing Pinecone client")
        pinecone_client = PineconeClient(
            api_key=config.pinecone_api_key,
            host=config.pinecone_host,
            index_name=config.pinecone_index_name,
            environment=config.pinecone_environment,
        )

        # Load models
        logger.info("Loading models")
        # TODO: Load two-tower and ranking models from S3 or local

        # Initialize services
        cache_manager = CacheManager(redis_client, ttl=config.cache_ttl)

        # TODO: Uncomment when models are available
        # recommender_service = RecommenderService(
        #     two_tower_model=two_tower_model,
        #     ranking_model=ranking_model,
        #     pinecone_client=pinecone_client,
        #     item_id_to_name=item_id_to_name,
        # )

        # Create FastAPI app
        # app = create_app(recommender_service, cache_manager)

        # Run server
        logger.info(f"Starting server on {config.api_host}:{config.api_port}")
        # uvicorn.run(
        #     app,
        #     host=config.api_host,
        #     port=config.api_port,
        #     workers=config.api_workers,
        #     log_level=config.log_level.lower(),
        # )

        logger.info("Server started successfully")

    except Exception as e:
        logger.error(f"Error starting API server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
