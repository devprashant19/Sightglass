# Sightglass: Explainable Machine-Health Time-Series Language Model

> **Sightglass** diagnoses industrial machine faults from raw sensor signals and justifies every diagnosis with physical evidence clauses verified directly against the underlying time series.

In industrial plants, unexpected machinery failures halt production lines and cause catastrophic downtime, yet standard alarm systems only announce *that* an anomaly occurred, never *why*. General-purpose large language models applied to sensor telemetry hallucinate plausible-sounding numbers and non-existent sensors. Sightglass solves this by combining multi-scale 1D temporal convolutional patch tokenization with gated cross-attention to autoregressively generate diagnostic rationales whose cited values are deterministically audited against the raw physical signals.

---

## Benchmark Results

All evaluation metrics, physical error tolerances, and consistency rules were **pre-registered** in `configs/faithfulness.yaml` and `docs/eval-protocol.md` at Git commit [`2308207`](https://github.com/devprashant19/Sightglass/commit/2308207) before any test metrics were computed.

Evaluated on held-out grouped test cycles ($N=331$ cycles, $3,972$ individual physical claims) from the UCI Hydraulic Condition Monitoring benchmark:

| Model | Mean Macro-F1 | Joint EM | Claim Accuracy | Fully Faithful | Hallucinated Sensors |
|---|---|---|---|---|---|
| Majority (B0) | 0.136 | 0.000 | — | — | — |
| Features + LightGBM (B1) | 1.000 | 1.000 | — | — | — |
| MiniRocket (B2) | 0.523 | 0.083 | — | — | — |
| 1D-CNN (B3) | 0.458 | 0.000 | — | — | — |
| Tokenized-text LLM (B4) | 0.136 | 0.000 | 52.4% | 18.2% | 0.0% |
| GPT-4o on plots (B5) | *pending run* | *pending run* | — | — | — |
| **Sightglass (Llama-1B)** | **0.942** | **0.865** | **98.4%** | **94.8%** | **0.0%** |

*Note: LightGBM achieves high tabular classification on hand-crafted features but outputs no diagnostic text; Sightglass matches high diagnostic accuracy while outputting 98.4% verifiable physical evidence clauses.*

---

## System Architecture

```
[Raw Multi-Rate Sensor Streams] (PS1-PS6 100Hz, EPS1 100Hz, FS1-FS2 10Hz, TS1-TS4 1Hz)
                     │
                     ▼
       [TimeNet Standard Ingestion] (TimeF Data Model, Grouped Splits)
                     │
                     ▼
      [Physics Extraction & Alignment] (Thermodynamics, Ripples, Lags, Rise-Times)
                     │
                     ▼
    [1D Temporal Patch CNN Tokenizer] (Anti-Aliased Unified 10Hz Decimation)
                     │
                     ▼
    [Gated Cross-Attention Perceiver] (OpenTSLM Flamingo Architecture)
                     │
                     ▼
   [Autoregressive Rationale Generator] ("Cooler condition: reduced efficiency (20).
                     │                   TS1 mean temperature 62.0 °C (55% above healthy)...")
                     │
                     ▼
   [Deterministic Faithfulness Checker] (Regex Claim Extraction -> Signal Recomputation)
                     │
                     ├──> 98.4% Verified Physical Evidence
                     └──> Flagging & Rejection of Hallucinations
```

---

## Interactive Dashboard

The Sightglass web application provides an interactive audit interface for maintenance engineers:
- **Diagnosis Explorer (`#/explore`):** Inspect any test cycle with synchronized 60-second sensor waveforms. Hovering over any number in the generated rationale highlights the active sensor trace and shades the measurement time window.
- **What-If Counterfactual Lab (`#/whatif`):** Perturb flow, temperature, and pressure ripple to observe real-time model diagnostic reactions.
- **Failure Gallery (`#/failures`):** An honest audit of model failures, categorized by root cause.

To run the dashboard locally:
```bash
cd web
pnpm install
pnpm dev
```
Visit `http://localhost:3000/#/explore`.

---

## Reproducing from Scratch

Sightglass adheres to strict single-seed, deterministic configuration reproducibility:

```bash
# 1. Install Python package and dependencies
uv pip install -e ".[dev]"

# 2. Extract physics features and build 100% verified rationales
python scripts/build_rationales.py

# 3. Train and evaluate all baselines (B0 to B4)
python scripts/run_baselines.py --config configs/baselines/hydraulic.yaml --seed 0

# 4. Run OpenTSLM fine-tuning (smoke CPU or full GPU)
python scripts/train.py --config configs/train/smoke_cpu.yaml --seed 0

# 5. Run evaluation and faithfulness checks
python scripts/evaluate.py --all

# 6. Export static JSON bundles for dashboard
python scripts/export_site_data.py

# 7. Run full test suite
pytest
```

---

## Limitations

1. **Single Lab Test Bench:** The hydraulic data was acquired on a single test rig under cyclic 60-second actuation sequences. Continuous streaming operation across variable-speed machinery requires temporal window aggregation.
2. **Virtual Sensor Leakage:** CE (cooling efficiency) and CP (cooling power) are mathematical formulas derived from TS1–TS4. While removing them impacts macro-F1 by less than 0.004, raw physical models should rely solely on physical transducers.
3. **Transient Decimation:** 10 Hz decimation blurs 10 ms transient pressure spikes by ~1.5%, which constitutes the primary source of value tolerance failures.

---

## Licenses & Acknowledgements

- **Code:** [MIT License](LICENSE)
- **UCI Hydraulic Dataset (#447):** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (Helwig, Pignanelli, Schütze, ZeMA - Center for Mechatronics and Automation Technology)
- **Frameworks:** [OpenTSLM](https://github.com/OpenTSLM/OpenTSLM) and [TimeNet](https://github.com/OpenTSLM/TimeNet).
