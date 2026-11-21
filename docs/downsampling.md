# Downsampling and feature drift (real data)

The TSLM input uses the 100 Hz sensors (PS1–PS6, EPS1) at 10 Hz. Faithfulness is always
checked against the **native-rate** signals, so downsampling can only affect what the model sees,
never the verification.

Measured on 200 real train cycles (2026-11-22): every feature recomputed after
`scipy.signal.decimate(x, 10, ftype="iir", zero_phase=True)` and compared with the native value.

| Feature | Median relative drift | Max relative drift | Max absolute drift |
|---|---|---|---|
| `PS1.mean` | 1.14% | 1.14% | 1.84 bar |
| `PS1.peak` | 1.04% | 1.30% | 2.48 bar |
| `PS1.ripple` | 1.05% | 1.06% | 0.159 bar |
| `PS2.rise_time` | 1.17% | 1.28% | 0.12 s |
| `PS1_PS2.lag` | 0.41% | 0.61% | 0.06 s |
| `EPS1.mean` | 1.14% | 1.15% | 29.1 W |
| `EPS1_per_FS1` | 1.14% | 1.15% | 4.33 W·min/l |
| `PS2.ripple` | 1.12% | 1.13% | 0.528 bar |

The near-constant ~1.1% on means is a gain change from the IIR anti-aliasing filter, not lost
detail. All drifts are below the 5% value tolerance, but a model that copies numbers from its
10 Hz input would be about 1% off; bin-averaging (used for the dashboard and the CNN/MiniRocket
inputs) has no such gain error and should replace `decimate` in `tslm/prompt.py` before the
TSLM run. That change has not been made yet.
