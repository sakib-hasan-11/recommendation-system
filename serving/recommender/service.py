import logging
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class RecommenderService:
    """Recommendation service combining two-tower and ranking models."""

    def __init__(
        self,
        two_tower_model: Any,
        ranking_model: Any,
        pinecone_client: Any,
        item_id_to_name: dict[int, str],
        embedding_dim: int = 64,
    ) -> None:
        self.two_tower_model = two_tower_model
        self.ranking_model = ranking_model
        self.pinecone_client = pinecone_client
        self.item_id_to_name = item_id_to_name
        self.embedding_dim = embedding_dim

    def get_recommendations(
        self,
        user_id: int,
        k: int = 10,
        include_ranking: bool = True,
    ) -> list[dict]:
        """Get recommendations for user."""
        logger.info(f"Generating recommendations for user {user_id}")

        # Get user embedding from two-tower model
        try:
            user_emb = self.two_tower_model.get_user_embedding(
                np.array([user_id]),
            )
            user_emb = user_emb[0].tolist()
        except Exception as e:
            logger.error(f"Error getting user embedding: {e}")
            return []

        # Query Pinecone for similar items
        try:
            results = self.pinecone_client.query(
                vector=user_emb,
                top_k=k * 2,  # Get more for ranking
            )
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            return []

        if not results:
            logger.warning(f"No results from Pinecone for user {user_id}")
            return []

        # Extract item IDs
        item_ids = [int(match.id) for match in results]
        scores = [match.score for match in results]

        recommendations = [
            {
                "item_id": item_id,
                "score": float(score),
                "name": self.item_id_to_name.get(item_id, f"Item {item_id}"),
            }
            for item_id, score in zip(item_ids, scores)
        ]

        logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
        return recommendations[:k]

    def get_similar_items(
        self,
        item_id: int,
        k: int = 10,
    ) -> list[dict]:
        """Get similar items."""
        logger.info(f"Finding similar items to {item_id}")

        try:
            item_emb = self.two_tower_model.get_item_embedding(
                np.array([item_id]),
            )
            item_emb = item_emb[0].tolist()
        except Exception as e:
            logger.error(f"Error getting item embedding: {e}")
            return []

        try:
            results = self.pinecone_client.query(
                vector=item_emb,
                top_k=k + 1,  # +1 to exclude the item itself
            )
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            return []

        similar_items = [
            {
                "item_id": int(match.id),
                "score": float(match.score),
                "name": self.item_id_to_name.get(int(match.id), f"Item {match.id}"),
            }
            for match in results
            if int(match.id) != item_id
        ]

        logger.info(f"Found {len(similar_items)} similar items")
        return similar_items[:k]
