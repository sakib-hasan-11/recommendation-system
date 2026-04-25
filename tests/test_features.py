"""Data pipeline tests."""

import pandas as pd
import pytest

from data_pipeline.feature_engineering.engineer import (
    engineer_item_features,
    engineer_user_features,
)


@pytest.fixture
def sample_ratings():
    """Sample ratings data."""
    return pd.DataFrame(
        {
            "userId": [1, 1, 1, 2, 2, 3, 3, 3],
            "movieId": [1, 2, 3, 1, 4, 2, 3, 4],
            "rating": [5.0, 4.0, 3.0, 5.0, 2.0, 4.0, 3.0, 5.0],
            "timestamp": range(1000, 1008),
        }
    )


@pytest.fixture
def sample_movies():
    """Sample movies data."""
    return pd.DataFrame(
        {
            "movieId": [1, 2, 3, 4],
            "title": ["M1", "M2", "M3", "M4"],
            "genres": ["Action", "Comedy", "Drama", "Action"],
        }
    )


def test_engineer_user_features(sample_ratings):
    """Test user feature engineering."""
    features = engineer_user_features(sample_ratings, min_interactions=1)

    assert len(features) > 0
    assert "userId" in features.columns
    assert "num_ratings" in features.columns
    assert "avg_rating" in features.columns


def test_engineer_item_features(sample_ratings, sample_movies):
    """Test item feature engineering."""
    features = engineer_item_features(
        sample_ratings,
        sample_movies,
        min_ratings=1,
    )

    assert len(features) > 0
    assert "movieId" in features.columns
    assert "num_ratings" in features.columns
