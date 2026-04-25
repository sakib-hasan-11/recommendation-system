import logging

import numpy as np

logger = logging.getLogger(__name__)


def recall_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int = 10) -> float:
    """Calculate recall@k metric."""
    if len(y_true) == 0:
        return 0.0

    # Get top k predictions
    top_k_indices = np.argsort(y_pred)[-k:]
    top_k_predictions = np.zeros_like(y_pred)
    top_k_predictions[top_k_indices] = 1

    # Calculate recall
    tp = np.sum(y_true * top_k_predictions)
    total_relevant = np.sum(y_true)

    if total_relevant == 0:
        return 0.0

    return tp / total_relevant


def ndcg_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int = 10) -> float:
    """Calculate NDCG@k metric."""
    if len(y_true) == 0:
        return 0.0

    # Sort by predictions
    sorted_indices = np.argsort(y_pred)[::-1][:k]
    sorted_y_true = y_true[sorted_indices]

    # Calculate DCG
    dcg = np.sum(sorted_y_true / np.log2(np.arange(2, k + 2)))

    # Calculate IDCG
    ideal_y_true = np.sort(y_true)[::-1][:k]
    idcg = np.sum(ideal_y_true / np.log2(np.arange(2, k + 2)))

    if idcg == 0:
        return 0.0

    return dcg / idcg


def mean_reciprocal_rank(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate Mean Reciprocal Rank."""
    if len(y_true) == 0:
        return 0.0

    sorted_indices = np.argsort(y_pred)[::-1]
    sorted_y_true = y_true[sorted_indices]

    if not np.any(sorted_y_true):
        return 0.0

    rank = np.argmax(sorted_y_true) + 1
    return 1.0 / rank


def precision_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int = 10) -> float:
    """Calculate precision@k."""
    if len(y_true) == 0:
        return 0.0

    top_k_indices = np.argsort(y_pred)[-k:]
    top_k_predictions = np.zeros_like(y_pred)
    top_k_predictions[top_k_indices] = 1

    tp = np.sum(y_true * top_k_predictions)
    return tp / k
