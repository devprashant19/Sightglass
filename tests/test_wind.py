"""Unit tests for wind turbine normal-behavior modeling and early warning metrics."""

import numpy as np

from sightglass.physics.wind import (
    NormalBehaviorModel,
    WindExtractor,
    compute_early_warning_metrics,
)


def test_normal_behavior_zero_residual() -> None:
    """When measured temperatures match expected conditions, residual mean is zero."""
    n = 432  # 3 days @ 10-min rate
    power = np.linspace(100, 1800, n)
    ambient = np.full(n, 15.0)

    model = NormalBehaviorModel(intercept=0.0, coef_power=0.02, coef_ambient=1.0)
    measured = ambient + 0.02 * power  # exact theoretical model

    extractor = WindExtractor(model)
    feats = extractor.extract_window(measured, power, ambient, window_days=3.0)

    assert np.isclose(feats["gearbox.residual_mean"].value, 0.0, atol=0.01)
    assert np.isclose(feats["gearbox.residual_trend"].value, 0.0, atol=0.01)
    assert feats["gearbox.days_above"].value == 0.0


def test_early_warning_lead_time() -> None:
    """An emerging overheating trend must trigger warnings days before event threshold."""
    steps_per_day = 144
    n_days = 30
    n = n_days * steps_per_day
    fault_step = 25 * steps_per_day  # Fault event starts on day 25

    # Residuals stay normal until day 18, then drift up 0.5 °C / day
    residuals = np.random.default_rng(42).normal(0, 0.2, size=n)
    drift_start = 18 * steps_per_day
    drift_duration = n - drift_start
    residuals[drift_start:] += np.linspace(0, 5.0, drift_duration)

    metrics = compute_early_warning_metrics(
        residuals=residuals,
        fault_start_step=fault_step,
        steps_per_day=steps_per_day,
        horizon_days=14.0,
        threshold_c=2.5,
    )

    assert metrics["detection_rate"] == 1.0
    assert metrics["lead_time_days"] > 2.0  # Warns multiple days ahead
    assert metrics["lead_time_days"] <= 14.0
