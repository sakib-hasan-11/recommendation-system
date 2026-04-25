import logging
from typing import Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)


class RankingModel(keras.Model):
    """Ranking neural network model."""

    def __init__(
        self,
        hidden_units: list[int] = [256, 128],
        dropout_rate: float = 0.2,
    ) -> None:
        super().__init__()
        self.dense_layers = []
        self.dropout_layers = []

        for units in hidden_units:
            self.dense_layers.append(keras.layers.Dense(units, activation="relu"))
            self.dropout_layers.append(keras.layers.Dropout(dropout_rate))

        self.output_layer = keras.layers.Dense(1, activation="sigmoid")

    def call(self, features: tf.Tensor, training: bool = False) -> tf.Tensor:
        """Forward pass."""
        x = features

        for dense, dropout in zip(self.dense_layers, self.dropout_layers):
            x = dense(x)
            x = dropout(x, training=training)

        return self.output_layer(x)


def build_ranking_model(
    feature_dim: int,
    hidden_units: list[int] = [256, 128],
    dropout_rate: float = 0.2,
    learning_rate: float = 0.001,
) -> keras.Model:
    """Build and compile ranking model."""
    model = RankingModel(hidden_units=hidden_units, dropout_rate=dropout_rate)

    model.build((None, feature_dim))

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss=keras.losses.BinaryCrossentropy(),
        metrics=["auc", "accuracy"],
    )

    logger.info(f"Ranking model built: feature_dim={feature_dim}, hidden_units={hidden_units}")

    return model
