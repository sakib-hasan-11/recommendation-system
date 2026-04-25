import logging
from typing import Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)


class TwoTowerModel(keras.Model):
    """Two-tower model for retrieval."""

    def __init__(
        self,
        user_vocab_size: int,
        item_vocab_size: int,
        embedding_dim: int = 64,
        hidden_units: int = 256,
    ) -> None:
        super().__init__()
        self.embedding_dim = embedding_dim

        # User tower
        self.user_embedding = keras.layers.Embedding(user_vocab_size, embedding_dim)
        self.user_dense1 = keras.layers.Dense(hidden_units, activation="relu")
        self.user_dense2 = keras.layers.Dense(embedding_dim)

        # Item tower
        self.item_embedding = keras.layers.Embedding(item_vocab_size, embedding_dim)
        self.item_dense1 = keras.layers.Dense(hidden_units, activation="relu")
        self.item_dense2 = keras.layers.Dense(embedding_dim)

    def call(
        self,
        inputs: dict,
        training: bool = False,
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        """Forward pass."""
        user_input = inputs["user_id"]
        item_input = inputs["item_id"]

        # User tower
        user_emb = self.user_embedding(user_input)
        user_out = self.user_dense1(user_emb, training=training)
        user_out = self.user_dense2(user_out, training=training)

        # Item tower
        item_emb = self.item_embedding(item_input)
        item_out = self.item_dense1(item_emb, training=training)
        item_out = self.item_dense2(item_out, training=training)

        return user_out, item_out

    def get_user_embedding(self, user_ids: np.ndarray) -> np.ndarray:
        """Get user embeddings."""
        user_emb = self.user_embedding(user_ids)
        user_out = self.user_dense1(user_emb)
        user_out = self.user_dense2(user_out)
        return user_out.numpy()

    def get_item_embedding(self, item_ids: np.ndarray) -> np.ndarray:
        """Get item embeddings."""
        item_emb = self.item_embedding(item_ids)
        item_out = self.item_dense1(item_emb)
        item_out = self.item_dense2(item_out)
        return item_out.numpy()


class RetrievalTask(keras.layers.Layer):
    """Retrieval task layer."""

    def __init__(self, **kwargs: dict) -> None:
        super().__init__(**kwargs)

    def call(self, inputs: Tuple[tf.Tensor, tf.Tensor]) -> tf.Tensor:
        """Compute similarity between user and item embeddings."""
        user_emb, item_emb = inputs
        return tf.linalg.matmul(user_emb, item_emb, transpose_b=True)


def build_two_tower_model(
    user_vocab_size: int,
    item_vocab_size: int,
    embedding_dim: int = 64,
    hidden_units: int = 256,
    learning_rate: float = 0.001,
) -> keras.Model:
    """Build and compile two-tower model."""
    # Create model
    two_tower = TwoTowerModel(
        user_vocab_size=user_vocab_size,
        item_vocab_size=item_vocab_size,
        embedding_dim=embedding_dim,
        hidden_units=hidden_units,
    )

    # Create full model with task layer
    inputs = {
        "user_id": keras.Input(shape=(), dtype=tf.int32, name="user_id"),
        "item_id": keras.Input(shape=(), dtype=tf.int32, name="item_id"),
    }

    user_emb, item_emb = two_tower(inputs)

    # Compile
    two_tower.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss=keras.losses.BinaryCrossentropy(from_logits=True),
        metrics=["mae"],
    )

    logger.info(
        f"Two-tower model built: vocab_sizes=({user_vocab_size}, {item_vocab_size}), "
        f"embedding_dim={embedding_dim}, hidden_units={hidden_units}",
    )

    return two_tower
