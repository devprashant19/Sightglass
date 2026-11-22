---
language:
- en
tags:
- time-series
- predictive-maintenance
- explainable-ai
datasets:
- uci_hydraulic_447
metrics:
- macro-f1
- joint-exact-match
- claim-accuracy
---

# Model card — Sightglass engine (hydraulic)

This card covers the **Sightglass engine**. The small time-series language model trained alongside it (soft prompts into SmolLM2-135M) is described in [docs/tslm.md](docs/tslm.md), with its test result in `results/tslm_test.json` and the README table. The OpenTSLM-Flamingo fine-tune has not been run.

## Model details

- **Diagnosis:** one LightGBM classifier per component on 43 physics features extracted at native sample rates; hyperparameters chosen on the validation split (`results/engine_training.json`).
- **Explanation:** the rationale engine states, for the *predicted* label, the 1–3 linked features that best show it, with values and deviations from a per-component healthy reference fitted on train cycles only.
- **Verification:** every stated number is parsed from the text and recomputed from the cycle's signals (`src/sightglass/eval/faithfulness.py`, tolerances in `configs/faithfulness.yaml`); a consistency check tests whether the evidence supports each label.
- **Version:** 1.1.0 · files: `data/models/engine.pkl` (rebuild with `python scripts/train_engine.py`).

## Intended use

Decision support for people learning or prototyping condition monitoring on the UCI hydraulic rig. **Not** a safety system, and not validated on any real plant. Always look at the cited sensor and time window before acting.

## Data

UCI #447 "Condition monitoring of hydraulic systems" (CC BY 4.0; Helwig, Pignanelli, Schütze, I2MTC 2015). 2,205 cycles, 17 sensors. Grouped split by the four-label condition tuple: 1,543 train, 333 val, 329 test. See `docs/hydraulic-eda.md`.

## Evaluation (real test split, 329 cycles)

All figures are in `results/summary.json` and `results/eval_engine.json`, written by `scripts/evaluate.py`. The comparison with the baselines is the [README results table](README.md#results); the method and the failure cases are in [docs/model.md](docs/model.md).

| Metric | Value |
|---|---|
| Mean macro-F1 (95% bootstrap CI) | 0.959 (0.948–0.970) |
| Cooler / valve / pump / accumulator macro-F1 | 1.000 / 0.997 / 0.969 / 0.870 |
| Joint exact match | 0.842 |
| Claims verified against the signal | 2,721 of 2,721 — expected by construction, since the engine computes them from the signal |
| Label–evidence consistency | 63.7% of component paragraphs (lowest for accumulator and pump) |

Checker validation (`results/checker_validation.json`): 17,883 of 17,883 reference claims verify; 1,000 of 1,000 single-value ±20% corruptions and 529 of 529 direction flips are caught.

## Limitations

- Single laboratory rig with deliberately set fault levels.
- Virtual sensors (CE, CP, SE) are derived from other sensors; CE alone separates the cooler classes. Removing them changes B1's mean macro-F1 by +0.002.
- Accumulator: one physics link survives the stratified check (PS2 ripple); lowest accuracy and consistency.
- What-if runs show learned shortcuts: warming TS1–TS4 by 2 °C changes the accumulator verdict on healthy cycles.
- One small language model has been graded by the checker ([docs/tslm.md](docs/tslm.md)); the two language-model baselines and OpenTSLM-Flamingo were not run.
- Random splits inflate scores (+0.039 mean macro-F1 for B1); only grouped-split numbers are reported as results.
