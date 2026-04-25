import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage caching for recommendations."""

    def __init__(self, redis_client: Any, ttl: int = 3600) -> None:
        self.redis_client = redis_client
        self.ttl = ttl

    def get_recommendations(self, user_id: int) -> Optional[list[dict]]:
        """Get cached recommendations for user."""
        key = f"recommendations:user:{user_id}"
        cached = self.redis_client.get(key)

        if cached:
            logger.info(f"Cache hit for user {user_id}")
            return json.loads(cached) if isinstance(cached, str) else cached

        return None

    def set_recommendations(
        self,
        user_id: int,
        recommendations: list[dict],
        ttl: Optional[int] = None,
    ) -> None:
        """Cache recommendations for user."""
        key = f"recommendations:user:{user_id}"
        self.redis_client.set(
            key,
            json.dumps(recommendations),
            ttl or self.ttl,
        )
        logger.info(f"Cached recommendations for user {user_id}")

    def get_similar_items(self, item_id: int) -> Optional[list[dict]]:
        """Get cached similar items."""
        key = f"similar_items:item:{item_id}"
        cached = self.redis_client.get(key)

        if cached:
            logger.info(f"Cache hit for similar items of {item_id}")
            return json.loads(cached) if isinstance(cached, str) else cached

        return None

    def set_similar_items(
        self,
        item_id: int,
        similar_items: list[dict],
        ttl: Optional[int] = None,
    ) -> None:
        """Cache similar items."""
        key = f"similar_items:item:{item_id}"
        self.redis_client.set(
            key,
            json.dumps(similar_items),
            ttl or self.ttl,
        )
        logger.info(f"Cached similar items for {item_id}")

    def invalidate_user(self, user_id: int) -> None:
        """Invalidate user recommendations cache."""
        key = f"recommendations:user:{user_id}"
        self.redis_client.delete(key)
        logger.info(f"Invalidated cache for user {user_id}")

    def invalidate_item(self, item_id: int) -> None:
        """Invalidate item similar items cache."""
        key = f"similar_items:item:{item_id}"
        self.redis_client.delete(key)
        logger.info(f"Invalidated cache for item {item_id}")

    def clear_all(self) -> None:
        """Clear all cache."""
        self.redis_client.clear()
        logger.info("Cleared all cache")
