import logging
from typing import Optional

from fastapi import FastAPI

logger = logging.getLogger(__name__)


def create_app(
    recommender_service,
    cache_manager,
) -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Recommendation System API",
        description="Production-grade recommendation system API",
        version="1.0.0",
    )

    # Import and include routes
    from serving.api.routes import create_routes

    router = create_routes(recommender_service, cache_manager)
    app.include_router(router)

    @app.on_event("startup")
    async def startup():
        logger.info("API startup")

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("API shutdown")

    return app
