import logging
from typing import Any, Callable

import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler

logger = logging.getLogger(__name__)


class TwoTowerTuner:
    """Optuna tuner for two-tower model."""

    def __init__(
        self,
        n_trials: int = 50,
        n_jobs: int = 4,
        timeout: int = 3600,
    ) -> None:
        self.n_trials = n_trials
        self.n_jobs = n_jobs
        self.timeout = timeout

    def objective(
        self,
        trial: optuna.Trial,
        training_func: Callable[[dict[str, Any]], float],
    ) -> float:
        """Objective function for hyperparameter tuning."""
        params = {
            "embedding_dim": trial.suggest_categorical("embedding_dim", [32, 64, 128, 256]),
            "hidden_units": trial.suggest_categorical("hidden_units", [128, 256, 512]),
            "learning_rate": trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True),
            "batch_size": trial.suggest_categorical("batch_size", [16, 32, 64, 128]),
        }

        return training_func(params)

    def optimize(
        self,
        training_func: Callable[[dict[str, Any]], float],
    ) -> dict[str, Any]:
        """Run optimization."""
        sampler = TPESampler(seed=42)
        pruner = MedianPruner()

        study = optuna.create_study(
            sampler=sampler,
            pruner=pruner,
            direction="maximize",
        )

        study.optimize(
            lambda trial: self.objective(trial, training_func),
            n_trials=self.n_trials,
            n_jobs=self.n_jobs,
            timeout=self.timeout,
            show_progress_bar=True,
        )

        logger.info(f"Optimization complete. Best params: {study.best_params}")
        logger.info(f"Best value: {study.best_value}")

        return study.best_params


class RankingTuner:
    """Optuna tuner for ranking model."""

    def __init__(
        self,
        n_trials: int = 50,
        n_jobs: int = 4,
        timeout: int = 3600,
    ) -> None:
        self.n_trials = n_trials
        self.n_jobs = n_jobs
        self.timeout = timeout

    def objective(
        self,
        trial: optuna.Trial,
        training_func: Callable[[dict[str, Any]], float],
    ) -> float:
        """Objective function for hyperparameter tuning."""
        params = {
            "hidden_units": trial.suggest_categorical(
                "hidden_units",
                [[128, 64], [256, 128], [512, 256], [256, 128, 64]],
            ),
            "dropout_rate": trial.suggest_float("dropout_rate", 0.0, 0.5),
            "learning_rate": trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True),
            "batch_size": trial.suggest_categorical("batch_size", [16, 32, 64, 128]),
        }

        return training_func(params)

    def optimize(
        self,
        training_func: Callable[[dict[str, Any]], float],
    ) -> dict[str, Any]:
        """Run optimization."""
        sampler = TPESampler(seed=42)
        pruner = MedianPruner()

        study = optuna.create_study(
            sampler=sampler,
            pruner=pruner,
            direction="maximize",
        )

        study.optimize(
            lambda trial: self.objective(trial, training_func),
            n_trials=self.n_trials,
            n_jobs=self.n_jobs,
            timeout=self.timeout,
            show_progress_bar=True,
        )

        logger.info(f"Optimization complete. Best params: {study.best_params}")
        logger.info(f"Best value: {study.best_value}")

        return study.best_params
