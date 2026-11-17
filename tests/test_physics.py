"""Unit tests for physics feature extractors and healthy reference calculations."""

import numpy as np
import pytest

from sightglass.data.models import Cycle, Signal
from sightglass.physics.base import Feature, HealthyReference
from sightglass.physics.hydraulic import HydraulicExtractor


def test_extractor_feature_names() -> None:
    extractor = HydraulicExtractor()
    names = extractor.feature_names()
    assert "PS1.mean" in names
    assert "PS1.rise_time" in names
    assert "PS1_PS2.lag" in names
    assert "FS1.mean" in names
    assert "EPS1.mean" in names
    assert "EPS1_per_FS1" in names
    assert "TS1.mean" in names
    assert "TS1.slope" in names
    assert "cooler.delta_t" in names
    assert "VS1.mean" in names
    assert "CE.mean" in names


def test_synthetic_feature_accuracy() -> None:
    # 1. Known ramp for slope: 20 °C to 26 °C over 60 s -> slope = 6.0 °C / min
    t = np.arange(60) / 60.0
    ramp_vals = 20.0 + 6.0 * t
    ts1 = Signal("TS1", "temperature", "°C", 1.0, ramp_vals.astype(np.float32))

    # 2. Known sine wave for ripple: amplitude 10 bar -> std = 10 / sqrt(2) ≈ 7.07 bar
    t_ps = np.linspace(0, 60, 6000)
    sine_vals = 150.0 + 10.0 * np.sin(2 * np.pi * 5.0 * t_ps)
    ps1 = Signal("PS1", "pressure", "bar", 100.0, sine_vals.astype(np.float32))

    # 3. Known constant flow and power -> EPS1_per_FS1 = 2400 / 8 = 300 W·min/l
    fs1 = Signal("FS1", "flow", "l/min", 10.0, (np.ones(600) * 8.0).astype(np.float32))
    eps1 = Signal("EPS1", "power", "W", 100.0, (np.ones(6000) * 2400.0).astype(np.float32))

    cycle = Cycle(
        id="test-001",
        signals={"TS1": ts1, "PS1": ps1, "FS1": fs1, "EPS1": eps1},
        labels={},
        meta={},
    )
    extractor = HydraulicExtractor()
    features = extractor.extract(cycle)

    assert pytest.approx(features["TS1.slope"].value, rel=1e-2) == 6.0
    assert pytest.approx(features["PS1.ripple"].value, rel=1e-2) == 7.07
    assert pytest.approx(features["EPS1_per_FS1"].value, rel=1e-2) == 300.0


def test_healthy_reference_fitting() -> None:
    feat1 = {"FS1.mean": Feature("FS1.mean", "FS1", "mean flow", "l/min", 10.0)}
    feat2 = {"FS1.mean": Feature("FS1.mean", "FS1", "mean flow", "l/min", 12.0)}

    ref = HealthyReference.fit([feat1, feat2])
    assert ref.mean["FS1.mean"] == 11.0
    assert pytest.approx(ref.std["FS1.mean"], rel=1e-2) == 1.414

    test_feat = Feature("FS1.mean", "FS1", "mean flow", "l/min", 13.828)
    assert pytest.approx(ref.z(test_feat), rel=1e-2) == 2.0
    assert pytest.approx(ref.pct_diff(test_feat), rel=1e-2) == 25.7

# Test: HealthyReference tolerance bands and bounds validation

# Test: physical anomaly thresholds against healthy baseline
