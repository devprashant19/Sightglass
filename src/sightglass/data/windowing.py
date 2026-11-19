"""Time-series windowing and aggregation routines for high-frequency vibration."""

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import signal


@dataclass(frozen=True)
class BearingWindow:
    """A short temporal window extracted from high-frequency vibration."""

    window_id: str
    recording_id: str
    bearing_type: str
    defect_type: str
    working_condition: str
    shaft_speed_hz: float
    rate_hz: float
    start_sec: float
    duration_sec: float
    native_data: np.ndarray
    encoder_data: np.ndarray  # downsampled points for 1D CNN encoder (e.g. 2,048)


def slice_recording(
    record: dict[str, Any],
    window_sec: float = 0.2,
    overlap: float = 0.5,
    encoder_points: int = 2048,
) -> list[BearingWindow]:
    """Slice a continuous high-rate vibration recording into overlapping windows."""
    vib_signal = record["signals"]["VIB"]
    values = np.asarray(vib_signal["values"], dtype=np.float32)
    fs = float(vib_signal["rate_hz"])

    samples_per_window = int(window_sec * fs)
    step_samples = int(samples_per_window * (1.0 - overlap))
    if step_samples <= 0:
        step_samples = samples_per_window

    windows: list[BearingWindow] = []
    total_samples = len(values)

    w_idx = 0
    start = 0
    while start + samples_per_window <= total_samples:
        segment = values[start : start + samples_per_window]

        # Anti-aliased decimation / resample for model encoder
        if len(segment) != encoder_points:
            down = signal.resample(segment, encoder_points)
        else:
            down = segment

        bw = BearingWindow(
            window_id=f"{record['id']}_w{w_idx:04d}",
            recording_id=record["id"],
            bearing_type=record["bearing_type"],
            defect_type=record["defect_type"],
            working_condition=record["working_condition"],
            shaft_speed_hz=float(record["shaft_speed_hz"]),
            rate_hz=fs,
            start_sec=start / fs,
            duration_sec=window_sec,
            native_data=segment,
            encoder_data=down.astype(np.float32),
        )
        windows.append(bw)
        w_idx += 1
        start += step_samples

    return windows


def aggregate_recording_predictions(
    window_preds: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Aggregate window-level classifications up to recording-level via majority vote."""
    by_rec: dict[str, list[dict[str, Any]]] = {}
    for wp in window_preds:
        rec_id = wp["recording_id"]
        by_rec.setdefault(rec_id, []).append(wp)

    recording_results: dict[str, dict[str, Any]] = {}
    for rec_id, preds in by_rec.items():
        # Count label votes
        votes: dict[str, int] = {}
        true_label = preds[0]["true_defect"]
        for p in preds:
            pred = p["pred_defect"]
            votes[pred] = votes.get(pred, 0) + 1

        # Majority winner
        winner = max(votes.items(), key=lambda kv: kv[1])[0]
        recording_results[rec_id] = {
            "recording_id": rec_id,
            "true_defect": true_label,
            "pred_defect": winner,
            "vote_distribution": votes,
            "n_windows": len(preds),
        }

    return recording_results
