from datetime import datetime

from feast import Entity, Feature, FeatureView, FileSource
from feast.types import Float32, Int32


def define_user_features() -> FeatureView:
    """Define user feature view."""
    user_source = FileSource(
        path="data/features/user_features.parquet",
        event_timestamp_column="timestamp",
    )

    user_features_view = FeatureView(
        name="user_features",
        entities=["user_id"],
        features=[
            Feature(name="num_ratings", dtype=Int32),
            Feature(name="avg_rating", dtype=Float32),
            Feature(name="std_rating", dtype=Float32),
        ],
        source=user_source,
    )

    return user_features_view


def define_item_features() -> FeatureView:
    """Define item feature view."""
    item_source = FileSource(
        path="data/features/item_features.parquet",
        event_timestamp_column="timestamp",
    )

    item_features_view = FeatureView(
        name="item_features",
        entities=["item_id"],
        features=[
            Feature(name="num_ratings", dtype=Int32),
            Feature(name="avg_rating", dtype=Float32),
            Feature(name="std_rating", dtype=Float32),
        ],
        source=item_source,
    )

    return item_features_view
