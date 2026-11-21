"""Unit tests for bearing kinematic equations, envelope spectrum, and windowing."""

import numpy as np
from sightglass.data.windowing import slice_recording
from sightglass.physics.bearing import (
    BearingExtractor,
    BearingGeometry,
    compute_envelope_spectrum,
)


def test_bearing_kinematic_orders() -> None:
    """Verify kinematic equations against analytical values for Rexnord ER16K."""
    geom = BearingGeometry(
        name="ER16K",
        pitch_diameter_mm=38.52,
        ball_diameter_mm=7.94,
        n_balls=9,
        contact_angle_deg=0.0,
    )
    orders = geom.fault_orders()

    # Analytical expected values
    assert np.isclose(orders["BPFO"], 3.572, atol=0.01)
    assert np.isclose(orders["BPFI"], 5.428, atol=0.01)
    assert np.isclose(orders["BSF"], 2.323, atol=0.02)
    assert np.isclose(orders["FTF"], 0.397, atol=0.01)


def test_synthetic_impulse_envelope_peak() -> None:
    """A periodic impulse train modulated onto a carrier must yield an envelope peak at the impact rate."""
    fs = 51200.0
    duration = 0.5
    n = int(fs * duration)
    t = np.arange(n) / fs

    target_bpfo = 90.0  # Hz
    carrier_freq = 5000.0  # Hz

    # Create periodic impulse train at target_bpfo
    impulse_train = np.zeros(n)
    period_samples = int(fs / target_bpfo)
    for i in range(0, n, period_samples):
        impulse_train[i] = 1.0

    # Dampened impulse response (decaying sinusoid ringing at carrier_freq)
    decay = np.exp(-t[:period_samples] * 500)
    ringing = np.sin(2 * np.pi * carrier_freq * t[:period_samples])
    transient = decay * ringing

    synthetic_vib = np.convolve(impulse_train, transient, mode="same")
    synthetic_vib += 0.05 * np.random.default_rng(42).normal(size=n)

    freqs, amps = compute_envelope_spectrum(
        synthetic_vib, fs=fs, low_cut=2000.0, high_cut=10000.0
    )

    # Search between 10 Hz and 300 Hz
    mask = (freqs >= 10.0) & (freqs <= 300.0)
    peak_idx = np.argmax(amps[mask])
    detected_f = freqs[mask][peak_idx]

    assert np.isclose(detected_f, target_bpfo, atol=2.0)


def test_windowing_and_feature_extraction() -> None:
    """Verify window slicing and physical feature generation."""
    fs = 51200.0
    sig = np.random.default_rng(123).normal(0, 1.0, size=int(fs * 0.5)).astype(np.float32)

    record = {
        "id": "hust_test_001",
        "bearing_type": "ER16K",
        "defect_type": "outer_race",
        "working_condition": "C1_1000rpm_0kN",
        "shaft_speed_hz": 25.0,
        "signals": {
            "VIB": {
                "rate_hz": fs,
                "values": sig,
            }
        },
    }

    windows = slice_recording(record, window_sec=0.2, overlap=0.5, encoder_points=2048)
    assert len(windows) > 0
    assert windows[0].recording_id == "hust_test_001"
    assert len(windows[0].encoder_data) == 2048

    geom = BearingGeometry(
        name="ER16K",
        pitch_diameter_mm=38.52,
        ball_diameter_mm=7.94,
        n_balls=9,
        contact_angle_deg=0.0,
    )
    extractor = BearingExtractor(geom)
    feats = extractor.extract(windows[0])

    assert "VIB.rms" in feats
    assert "VIB.kurtosis" in feats
    assert "ENV.peak_freq" in feats
    assert "ENV.bpfo_amp" in feats
    assert feats["VIB.kurtosis"].value > 0.0
