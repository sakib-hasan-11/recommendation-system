import numpy as np
import pandas as pd
import pytest

from data_pipeline.validation.schema_validator import SchemaValidator


@pytest.fixture
def valid_movies_df():
    """Fixture for valid movies DataFrame."""
    return pd.DataFrame(
        {
            "movieId": [1, 2, 3],
            "title": ["Movie 1", "Movie 2", "Movie 3"],
            "genres": ["Action", "Comedy", "Drama"],
        }
    )


@pytest.fixture
def valid_ratings_df():
    """Fixture for valid ratings DataFrame."""
    return pd.DataFrame(
        {
            "userId": [1, 1, 2],
            "movieId": [1, 2, 1],
            "rating": [5.0, 3.0, 4.0],
            "timestamp": [1000, 1001, 1002],
        }
    )


@pytest.fixture
def valid_users_df():
    """Fixture for valid users DataFrame."""
    return pd.DataFrame(
        {
            "userId": [1, 2, 3],
            "gender": ["M", "F", "M"],
            "age": [25, 30, 35],
            "occupation": [1, 2, 3],
            "zip": ["12345", "67890", "11111"],
        }
    )


def test_validate_movies(valid_movies_df):
    """Test movies schema validation."""
    assert SchemaValidator.validate_movies(valid_movies_df) is True


def test_validate_ratings(valid_ratings_df):
    """Test ratings schema validation."""
    assert SchemaValidator.validate_ratings(valid_ratings_df) is True


def test_validate_users(valid_users_df):
    """Test users schema validation."""
    assert SchemaValidator.validate_users(valid_users_df) is True


def test_validate_movies_missing_columns():
    """Test movies validation with missing columns."""
    df = pd.DataFrame(
        {
            "movieId": [1, 2],
            "title": ["Movie 1", "Movie 2"],
        }
    )
    with pytest.raises(ValueError):
        SchemaValidator.validate_movies(df)


def test_validate_ratings_invalid_range():
    """Test ratings validation with invalid rating range."""
    df = pd.DataFrame(
        {
            "userId": [1, 2],
            "movieId": [1, 2],
            "rating": [5.5, 6.0],  # Invalid
            "timestamp": [1000, 1001],
        }
    )
    with pytest.raises(ValueError):
        SchemaValidator.validate_ratings(df)
