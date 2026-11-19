"""Normal-behavior modeling, residual tracking, and early fault warning for wind turbines."""

from dataclasses import dataclass

import numpy as np

from sightglass.physics.base import Feature


@dataclass
class NormalBehaviorModel:
    """Multivariate regression estimating expected temperature from ambient temp and power."""

    intercept: float = 0.0
    coef_power: float = 0.02
    coef_ambient: float = 1.0
    threshold_95th: float = 2.5  # °C above normal

    def predict_expected(self, power_kw: np.ndarray, ambient_c: np.ndarray) -> np.ndarray:
        return np.asarray(
            self.intercept + self.coef_ambient * ambient_c + self.coef_power * power_kw,
            dtype=np.float64,
        )

    def compute_residual(
        self, measured_c: np.ndarray, power_kw: np.ndarray, ambient_c: np.ndarray
    ) -> np.ndarray:
        expected = self.predict_expected(power_kw, ambient_c)
        return np.asarray(measured_c - expected, dtype=np.float64)


class WindExtractor:
    """Extracts normal-behavior residuals and trend features over multi-day windows."""

    dataset = "care_wind"

    def __init__(self, model: NormalBehaviorModel | None = None) -> None:
        self.model = model or NormalBehaviorModel()

    def extract_window(
        self,
        measured_c: np.ndarray,
        power_kw: np.ndarray,
        ambient_c: np.ndarray,
        window_days: float = 3.0,
    ) -> dict[str, Feature]:
        residual = self.model.compute_residual(measured_c, power_kw, ambient_c)

        # 1. Residual statistics
        res_mean = float(np.mean(residual))
        res_max = float(np.max(residual))

        # 2. Linear trend (slope in °C / day)
        n = len(residual)
        t_days = np.linspace(0, window_days, n)
        if n > 1:
            slope, _ = np.polyfit(t_days, residual, deg=1)
        else:
            slope = 0.0

        # 3. Days above 95th percentile
        samples_per_day = n / max(0.1, window_days)
        samples_above = np.sum(residual > self.model.threshold_95th)
        days_above = float(samples_above / max(1.0, samples_per_day))

        return {
            "gearbox.residual_mean": Feature(
                name="gearbox.residual_mean",
                sensor="gearbox_bearing_temp_c",
                quantity="mean temperature residual",
                unit="°C",
                value=round(res_mean, 2),
                window=(0.0, window_days),
            ),
            "gearbox.residual_trend": Feature(
                name="gearbox.residual_trend",
                sensor="gearbox_bearing_temp_c",
                quantity="residual trend",
                unit="°C/day",
                value=round(float(slope), 2),
                window=(0.0, window_days),
            ),
            "gearbox.residual_max": Feature(
                name="gearbox.residual_max",
                sensor="gearbox_bearing_temp_c",
                quantity="max temperature residual",
                unit="°C",
                value=round(res_max, 2),
                window=(0.0, window_days),
            ),
            "gearbox.days_above": Feature(
                name="gearbox.days_above",
                sensor="gearbox_bearing_temp_c",
                quantity="days above healthy threshold",
                unit="days",
                value=round(days_above, 1),
                window=(0.0, window_days),
            ),
        }


def compute_early_warning_metrics(
    residuals: np.ndarray,
    fault_start_step: int | None,
    steps_per_day: int = 144,
    horizon_days: float = 14.0,
    threshold_c: float = 2.5,
) -> dict[str, float]:
    """Calculate event detection rate, warning lead time, and false alarm rate."""
    if fault_start_step is None:
        # Normal turbine: check for false alarms
        false_alarms = int(np.sum(residuals > threshold_c))
        # Total turbine months (assume 30 days per month)
        n_days = len(residuals) / steps_per_day
        months = max(0.1, n_days / 30.0)
        return {
            "detection_rate": 1.0,
            "lead_time_days": 0.0,
            "false_alarms_per_month": false_alarms / months,
        }

    # Fault event exists: check earliest trigger inside horizon
    horizon_steps = int(horizon_days * steps_per_day)
    window_start = max(0, fault_start_step - horizon_steps)

    pre_fault_residuals = residuals[window_start:fault_start_step]
    alarm_indices = np.where(pre_fault_residuals > threshold_c)[0]

    if len(alarm_indices) > 0:
        first_alarm = alarm_indices[0]
        steps_before_event = len(pre_fault_residuals) - first_alarm
        lead_days = float(steps_before_event / steps_per_day)
        return {
            "detection_rate": 1.0,
            "lead_time_days": round(lead_days, 1),
            "false_alarms_per_month": 0.0,
        }
    else:
        return {
            "detection_rate": 0.0,
            "lead_time_days": 0.0,
            "false_alarms_per_month": 0.0,
        }
