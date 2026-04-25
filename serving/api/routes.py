import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RecommendationRequest(BaseModel):
    """Recommendation request model."""

    user_id: int
    k: int = 10


class RecommendationResponse(BaseModel):
    """Recommendation response model."""

    user_id: int
    recommendations: list[dict]


class SimilarItemsRequest(BaseModel):
    """Similar items request model."""

    item_id: int
    k: int = 10


class SimilarItemsResponse(BaseModel):
    """Similar items response model."""

    item_id: int
    similar_items: list[dict]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    message: str


def create_routes(
    recommender_service,
    cache_manager,
):
    """Create API routes."""
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    async def health():
        """Health check endpoint."""
        logger.info("Health check")
        return {
            "status": "healthy",
            "message": "Recommendation service is running",
        }

    @router.post("/recommend", response_model=RecommendationResponse)
    async def recommend(request: RecommendationRequest):
        """Get recommendations for user."""
        logger.info(f"Recommendation request for user {request.user_id}")

        # Check cache
        cached = cache_manager.get_recommendations(request.user_id)
        if cached:
            return {
                "user_id": request.user_id,
                "recommendations": cached,
            }

        # Generate recommendations
        try:
            recommendations = recommender_service.get_recommendations(
                user_id=request.user_id,
                k=request.k,
            )
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise HTTPException(status_code=500, detail="Error generating recommendations")

        # Cache results
        cache_manager.set_recommendations(request.user_id, recommendations)

        return {
            "user_id": request.user_id,
            "recommendations": recommendations,
        }

    @router.get("/similar/{item_id}", response_model=SimilarItemsResponse)
    async def similar_items(item_id: int, k: int = 10):
        """Get similar items."""
        logger.info(f"Similar items request for item {item_id}")

        # Check cache
        cached = cache_manager.get_similar_items(item_id)
        if cached:
            return {
                "item_id": item_id,
                "similar_items": cached,
            }

        # Generate similar items
        try:
            similar = recommender_service.get_similar_items(
                item_id=item_id,
                k=k,
            )
        except Exception as e:
            logger.error(f"Error finding similar items: {e}")
            raise HTTPException(status_code=500, detail="Error finding similar items")

        # Cache results
        cache_manager.set_similar_items(item_id, similar)

        return {
            "item_id": item_id,
            "similar_items": similar,
        }

    return router
