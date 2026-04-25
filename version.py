"""Recommendation system version."""

__version__ = "1.0.0"
__build__ = "20240101.001"


def get_version() -> str:
    """Get version string."""
    return f"{__version__} ({__build__})"
