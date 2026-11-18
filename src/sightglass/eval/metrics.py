"""Diagnostic and statistical evaluation metrics with bootstrap confidence intervals."""

from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score


def compute_component_metrics(
    y_true: list[int] | np.ndarray,
    y_pred: list[int] | np.ndarray,
) -> dict[str, Any]:
    """Compute macro-F1, accuracy, and confusion matrix for a single component."""
    yt = np.asarray(y_true)
    yp = np.asarray(y_pred)

    macro_f1 = float(f1_score(yt, yp, average="macro", zero_division=0))
    acc = float(accuracy_score(yt, yp))
    cm = confusion_matrix(yt, yp).tolist()

    return {
        "macro_f1": macro_f1,
        "accuracy": acc,
        "confusion_matrix": cm,
    }


def compute_joint_exact_match(
    targets: dict[str, list[int]],
    predictions: dict[str, list[int]],
) -> float:
    """Compute proportion of cycles where all component predictions exactly match truth."""
    components = list(targets.keys())
    n = len(targets[components[0]])
    exact_matches = 0

    for i in range(n):
        match = all(targets[comp][i] == predictions[comp][i] for comp in components)
        if match:
            exact_matches += 1

    return float(exact_matches / n) if n > 0 else 0.0


def compute_bootstrap_ci(
    values: list[float] | np.ndarray,
    n_resamples: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Compute empirical 95% bootstrap confidence interval."""
    arr = np.asarray(values)
    if len(arr) == 0:
        return 0.0, 0.0

    rng = np.random.default_rng(seed)
    boot_means = np.empty(n_resamples)

    for i in range(n_resamples):
        sample = rng.choice(arr, size=len(arr), replace=True)
        boot_means[i] = np.mean(sample)

    alpha = (1.0 - ci) / 2.0
    lower = float(np.percentile(boot_means, 100.0 * alpha))
    upper = float(np.percentile(boot_means, 100.0 * (1.0 - alpha)))
    return lower, upper
