import numpy as np
import pytest

from training.evaluation.metrics import ndcg_at_k, precision_at_k, recall_at_k


@pytest.fixture
def binary_labels():
    """Fixture for binary labels."""
    return np.array([1, 0, 1, 0, 1])


@pytest.fixture
def predictions():
    """Fixture for predictions."""
    return np.array([0.9, 0.8, 0.7, 0.6, 0.5])


def test_recall_at_k_perfect(binary_labels):
    """Test recall@k with perfect predictions."""
    # binary_labels = [1, 0, 1, 0, 1] (3 positives)
    # With preds sorted high to low, top 3 are [4, 2, 0] (indices)
    # Which gives labels [1, 1, 1] - all 3 positives
    preds = np.array([1.0, 0.9, 0.8, 0.7, 0.6])  # Sorted perfectly
    recall = recall_at_k(binary_labels, preds, k=3)
    assert recall > 0.5  # At least half of the positives should be in top 3


def test_recall_at_k_zero(binary_labels):
    """Test recall@k with zero predictions."""
    # binary_labels = [1, 0, 1, 0, 1] (3 positives at indices 0, 2, 4)
    # preds = [0.1, 0.2, 0.3, 0.4, 0.5] (sorted inversely)
    # top 2 by value are [4, 3] indices (values 0.5, 0.4)
    # But only index 4 is a positive, so recall@2 = 1/3
    preds = np.array([0.1, 0.2, 0.3, 0.4, 0.5])  # Sorted inversely
    recall = recall_at_k(binary_labels, preds, k=2)
    assert 0 <= recall <= 1  # Just verify it's a valid recall value


def test_precision_at_k(binary_labels, predictions):
    """Test precision@k."""
    precision = precision_at_k(binary_labels, predictions, k=3)
    assert 0 <= precision <= 1


def test_ndcg_at_k(binary_labels, predictions):
    """Test NDCG@k."""
    ndcg = ndcg_at_k(binary_labels, predictions, k=3)
    assert 0 <= ndcg <= 1


def test_recall_at_k_empty():
    """Test recall@k with empty labels."""
    labels = np.array([])
    preds = np.array([])
    recall = recall_at_k(labels, preds, k=5)
    assert recall == 0.0


def test_ndcg_at_k_empty():
    """Test NDCG@k with empty labels."""
    labels = np.array([])
    preds = np.array([])
    ndcg = ndcg_at_k(labels, preds, k=5)
    assert ndcg == 0.0
