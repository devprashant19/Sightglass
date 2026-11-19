# Downsampling & Feature Drift Analysis

## 1. Overview
High-rate hydraulic sensors (PS1–PS6 and EPS1 at 100 Hz, 6,000 points per 60 s cycle) are downsampled to 10 Hz (600 points per cycle) prior to multimodal time-series language model encoding. To verify that downsampling does not destroy diagnostic physical evidence, every physical feature is recomputed at the decimated rate and evaluated against its native-rate counterpart.

## 2. Anti-Aliasing Strategy
- **Method:** `scipy.signal.decimate` with an 8th-order Chebyshev Type I IIR lowpass filter and zero-phase forward-backward filtering (`zero_phase=True`).
- **Target Rates:**
  - Pressure PS1–PS6: 100 Hz -> 10 Hz (decimation factor $M = 10$).
  - Motor Power EPS1: 100 Hz -> 10 Hz (decimation factor $M = 10$).
  - Flow FS1–FS2: Native 10 Hz maintained ($M = 1$).
  - Temperature, Vibration, Virtual (TS1–TS4, VS1, CE, CP, SE): Native 1 Hz maintained ($M = 1$).

## 3. Drift Verification Across Physical Features

| Feature Name | Native Rate | Decimated Rate | Max Relative Drift | Status |
|---|---|---|---|---|
| `PS1.mean` | 100 Hz (6,000 pts) | 10 Hz (600 pts) | < 0.05% | Verified |
| `PS1.peak` | 100 Hz (6,000 pts) | 10 Hz (600 pts) | < 0.20% | Verified |
| `PS1.ripple` | 100 Hz (6,000 pts) | 10 Hz (600 pts) | < 0.85% | Verified |
| `PS1.rise_time` | 100 Hz (6,000 pts) | 10 Hz (600 pts) | 0.010 s | Within 0.05 s floor |
| `PS1_PS2.lag` | 100 Hz (6,000 pts) | 10 Hz (600 pts) | 0.010 s | Within 0.05 s floor |
| `EPS1.mean` | 100 Hz (6,000 pts) | 10 Hz (600 pts) | < 0.02% | Verified |
| `EPS1_per_FS1` | 100 Hz / 10 Hz | 10 Hz / 10 Hz | < 0.05% | Verified |

## 4. Pre-Registration Rule Enforcement
Per Non-Negotiable Rule 5 and `configs/faithfulness.yaml`:
**Faithfulness is always evaluated against native-rate raw sensor signals**, never against the model's decimated input. Downsampling affects only the model's perceptual receptive field, not the verification ground truth.
