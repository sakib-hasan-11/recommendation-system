import sys
from pathlib import Path

import pytest

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def setup_env():
    """Setup test environment."""
    import os

    os.environ["ENV"] = "test"
    os.environ["LOG_LEVEL"] = "WARNING"
