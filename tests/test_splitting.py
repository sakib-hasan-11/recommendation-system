import pandas as pd
import pytest

from data_pipeline.splitting.splitter import DataSplitter


@pytest.fixture
def ratings_df():
    """Fixture for ratings DataFrame."""
    return pd.DataFrame(
        {
            "userId": [1, 1, 1, 1, 2, 2, 2, 2],
            "movieId": [1, 2, 3, 4, 1, 2, 5, 6],
            "rating": [5.0, 4.0, 3.0, 2.0, 5.0, 5.0, 4.0, 3.0],
            "timestamp": [1000, 1001, 1002, 1003, 1100, 1101, 1102, 1103],
        }
    )


@pytest.fixture
def movies_df():
    """Fixture for movies DataFrame."""
    return pd.DataFrame(
        {
            "movieId": [1, 2, 3, 4, 5, 6],
            "title": ["M1", "M2", "M3", "M4", "M5", "M6"],
            "genres": ["A", "B", "C", "A", "B", "C"],
        }
    )


@pytest.fixture
def users_df():
    """Fixture for users DataFrame."""
    return pd.DataFrame(
        {
            "userId": [1, 2],
            "gender": ["M", "F"],
            "age": [25, 30],
            "occupation": [1, 2],
            "zip": ["12345", "67890"],
        }
    )


def test_temporal_split(ratings_df):
    """Test temporal split."""
    train, val, test = DataSplitter.temporal_split(
        ratings_df,
        timestamp_col="timestamp",
        train_ratio=0.6,
        val_ratio=0.2,
        test_ratio=0.2,
    )

    # 8 items total: train=int(8*0.6)=4, val=int(8*0.2)=1, test=remaining=3
    assert len(train) == 4
    assert len(val) == 1
    assert len(test) == 3
    assert len(train) + len(val) + len(test) == len(ratings_df)


def test_user_temporal_split(ratings_df, movies_df, users_df):
    """Test user-based temporal split."""
    # Use higher ratios to ensure val and test have data with only 4 items per user
    train_r, val_r, test_r, train_m, val_m, test_m = DataSplitter.user_temporal_split(
        ratings_df,
        movies_df,
        users_df,
        train_ratio=0.5,
        val_ratio=0.25,
        test_ratio=0.25,
        min_user_ratings=2,
    )

    assert len(train_r) > 0
    assert len(val_r) > 0  # Now should have data with 0.25 ratio
    assert len(test_r) > 0
    assert len(train_r) + len(val_r) + len(test_r) == len(ratings_df)


def test_temporal_split_no_leakage(ratings_df):
    """Test that temporal split prevents leakage."""
    train, val, test = DataSplitter.temporal_split(
        ratings_df,
        timestamp_col="timestamp",
        train_ratio=0.5,
        val_ratio=0.25,
        test_ratio=0.25,
    )

    # Ensure no overlap
    train_max = train["timestamp"].max()
    val_min = val["timestamp"].min()
    val_max = val["timestamp"].max()
    test_min = test["timestamp"].min()

    assert train_max < val_min, "Train and val have overlapping timestamps"
    assert val_max < test_min, "Val and test have overlapping timestamps"
