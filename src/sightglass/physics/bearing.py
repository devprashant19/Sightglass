"""Physics feature extraction, fault order equations, and envelope spectrum for bearings."""

from dataclasses import dataclass

import numpy as np
from scipy import signal

from sightglass.data.windowing import BearingWindow
from sightglass.physics.base import Feature


@dataclass(frozen=True)
class BearingGeometry:
    """Bearing internal physical dimensions."""

    name: str
    pitch_diameter_mm: float  # D
    ball_diameter_mm: float  # d
    n_balls: int  # n
    contact_angle_deg: float = 0.0  # theta

    @property
    def cos_theta(self) -> float:
        return float(np.cos(np.radians(self.contact_angle_deg)))

    @property
    def gamma(self) -> float:
        """Dimension ratio (d / D) * cos(theta)."""
        return (self.ball_diameter_mm / self.pitch_diameter_mm) * self.cos_theta

    def bpfo(self, fr: float) -> float:
        """Ball Pass Frequency Outer Race (Hz)."""
        return (self.n_balls / 2.0) * fr * (1.0 - self.gamma)

    def bpfi(self, fr: float) -> float:
        """Ball Pass Frequency Inner Race (Hz)."""
        return (self.n_balls / 2.0) * fr * (1.0 + self.gamma)

    def bsf(self, fr: float) -> float:
        """Ball Spin Frequency (Hz)."""
        d = self.ball_diameter_mm
        D = self.pitch_diameter_mm
        return (D / (2.0 * d)) * fr * (1.0 - self.gamma**2)

    def ftf(self, fr: float) -> float:
        """Fundamental Train Frequency (Cage) (Hz)."""
        return (fr / 2.0) * (1.0 - self.gamma)

    def fault_orders(self) -> dict[str, float]:
        """Fault frequencies expressed as dimensionless multiples of shaft speed (orders)."""
        return {
            "BPFO": self.bpfo(1.0),
            "BPFI": self.bpfi(1.0),
            "BSF": self.bsf(1.0),
            "FTF": self.ftf(1.0),
        }


def compute_envelope_spectrum(
    x: np.ndarray, fs: float, low_cut: float = 2000.0, high_cut: float = 10000.0
) -> tuple[np.ndarray, np.ndarray]:
    """Extract envelope spectrum via bandpass filtering, Hilbert transform, and FFT."""
    x = np.asarray(x, dtype=np.float64)

    # Optional band-pass around high-frequency resonance if nyquist allows
    nyq = 0.5 * fs
    if high_cut < nyq and low_cut < high_cut:
        try:
            sos = signal.butter(4, [low_cut / nyq, high_cut / nyq], btype="bandpass", output="sos")
            filtered = signal.sosfiltfilt(sos, x)
        except Exception:
            filtered = x
    else:
        filtered = x

    # Analytic signal via Hilbert transform
    analytic = signal.hilbert(filtered)
    envelope = np.abs(analytic)

    # Remove DC component
    envelope = envelope - np.mean(envelope)

    # FFT of envelope
    n = len(envelope)
    fft_vals = np.fft.rfft(envelope)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    amps = (2.0 / n) * np.abs(fft_vals)

    return freqs, amps


class BearingExtractor:
    """Extractor computing kinematic orders, statistical moments, and envelope peaks."""

    dataset = "hust_bearing"

    def __init__(self, geometry: BearingGeometry) -> None:
        self.geometry = geometry

    def extract(self, window: BearingWindow) -> dict[str, Feature]:
        x = window.native_data.astype(np.float64)
        fs = window.rate_hz
        fr = max(0.1, window.shaft_speed_hz)

        # 1. Classical statistical features
        mean_val = float(np.mean(x))
        rms = float(np.sqrt(np.mean(x**2)))
        peak = float(np.max(np.abs(x)))
        crest = float(peak / (rms + 1e-9))
        var = float(np.var(x))
        kurt = float(np.mean((x - mean_val) ** 4) / ((var**2) + 1e-9))

        features: dict[str, Feature] = {
            "VIB.rms": Feature(
                name="VIB.rms",
                sensor="VIB",
                quantity="RMS vibration",
                unit="m/s^2",
                value=round(rms, 3),
                window=(0.0, window.duration_sec),
            ),
            "VIB.kurtosis": Feature(
                name="VIB.kurtosis",
                sensor="VIB",
                quantity="kurtosis",
                unit="—",
                value=round(kurt, 2),
                window=(0.0, window.duration_sec),
            ),
            "VIB.crest": Feature(
                name="VIB.crest",
                sensor="VIB",
                quantity="crest factor",
                unit="—",
                value=round(crest, 2),
                window=(0.0, window.duration_sec),
            ),
        }

        # 2. Envelope spectrum & fault orders
        freqs, amps = compute_envelope_spectrum(x, fs)

        # Search band: 5 Hz to 500 Hz
        mask = (freqs >= 5.0) & (freqs <= 500.0)
        valid_freqs = freqs[mask]
        valid_amps = amps[mask]

        if len(valid_amps) > 0:
            peak_idx = int(np.argmax(valid_amps))
            peak_freq = float(valid_freqs[peak_idx])
            peak_order = float(peak_freq / fr)
            noise_floor = float(np.median(valid_amps)) + 1e-9
        else:
            peak_freq = 0.0
            peak_order = 0.0
            noise_floor = 1e-6

        features["ENV.peak_freq"] = Feature(
            name="ENV.peak_freq",
            sensor="ENV",
            quantity="envelope peak frequency",
            unit="Hz",
            value=round(peak_freq, 1),
            window=(0.0, window.duration_sec),
        )
        features["ENV.peak_order"] = Feature(
            name="ENV.peak_order",
            sensor="ENV",
            quantity="envelope peak order",
            unit="x",
            value=round(peak_order, 2),
            window=(0.0, window.duration_sec),
        )

        # Fault order amplitudes
        orders = self.geometry.fault_orders()
        for ord_name, ord_val in orders.items():
            target_f = ord_val * fr
            # +/- 2% band search
            f_band = (freqs >= target_f * 0.98) & (freqs <= target_f * 1.02)
            if np.any(f_band):
                amp = float(np.max(amps[f_band]))
                snr_db = float(20.0 * np.log10((amp / noise_floor) + 1e-6))
            else:
                amp = 0.0
                snr_db = 0.0

            features[f"ENV.{ord_name.lower()}_amp"] = Feature(
                name=f"ENV.{ord_name.lower()}_amp",
                sensor="ENV",
                quantity=f"{ord_name} amplitude",
                unit="m/s^2",
                value=round(amp, 4),
                window=(0.0, window.duration_sec),
            )
            features[f"ENV.{ord_name.lower()}_snr"] = Feature(
                name=f"ENV.{ord_name.lower()}_snr",
                sensor="ENV",
                quantity=f"{ord_name} SNR",
                unit="dB",
                value=round(snr_db, 1),
                window=(0.0, window.duration_sec),
            )

        return features
