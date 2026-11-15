# Phase 3 — Baselines

| | |
|---|---|
| **Goal** | Establish what simple methods achieve on the same split, so the TSLM's results mean something. |
| **Owner** | Teammate (Aman supports the features model) |
| **When** | Round 1, days 3–8 |
| **Depends on** | Phase 1 loader and split; Phase 2 features (for GBM) |
| **Unblocks** | Phase 5 comparison table |

Expect classical methods to score very high on this dataset; published work reports near-perfect accuracy on some components. That's fine. Sightglass's claim rests on explanations you can check, not on beating LightGBM at accuracy. Reporting this honestly is part of the pitch.

---

## Baselines

| # | Baseline | Input | What it is | Explains? | Compute |
|---|---|---|---|---|---|
| B0 | Majority class | — | Most common train label per component | No | None |
| B1 | Features + LightGBM | Phase 2 features | One model per component | Feature importance only | CPU, minutes |
| B2 | MiniRocket | Raw signals | Random convolutional features + ridge classifier | No | CPU, minutes |
| B3 | 1D-CNN | Resampled multi-sensor input | Small CNN, one head per component | No | 1 GPU, < 1 h |
| B4 | Tokenized-text LLM | Signals written as text | Same backbone as the TSLM, fine-tuned on the same targets | Yes, but unanchored | GPU, hours |
| B5 | GPT-4o on plots | Plot image | Zero-shot diagnosis + reason | Yes | API, 200-cycle sample |

All baselines read the same TimeNet build and the same split through `sightglass.data.load_cycles`.

## Shared interface (`src/sightglass/baselines/base.py`)

```python
class Baseline(Protocol):
    name: str

    def fit(self, train: list[Cycle], val: list[Cycle], cfg: BaselineConfig) -> None: ...
    def predict(self, cycles: list[Cycle]) -> list[Prediction]: ...


@dataclass
class Prediction:
    cycle_id: str
    labels: dict[str, int]  # one per component
    probs: dict[str, dict[int, float]] | None  # for calibration plots, if available
    rationale: str | None  # B4, B5 only
```

`scripts/run_baselines.py --config configs/baselines/hydraulic.yaml [--only B1,B2] [--seed 0]` fits, predicts on val and test, and writes one run folder per baseline plus an updated `results/baselines.json`.

## Details per baseline

### B0 Majority
- [ ] Trivial; a sanity floor for macro-F1.

### B1 Features + LightGBM
- [ ] Input: all Phase 2 features (and a variant without virtual features).
- [ ] One `LGBMClassifier` per component; tune `num_leaves`, `learning_rate`, `n_estimators` on **val** with a small grid (≤ 20 configs).
- [ ] Save feature importances (gain) per component to the run folder; Phase 7 shows them next to the physics links as a "what a classical model looks at" panel.

### B2 MiniRocket
- [ ] `sktime` MiniRocket multivariate. Resample all sensors to a common length first (for example 60 points at 1 Hz and a 600-point variant at 10 Hz) **(verify current sktime class names)**.
- [ ] Ridge classifier with cross-validated alpha, one per component.

### B3 1D-CNN
- [ ] Input: all 17 sensors resampled to 600 points (10 Hz), normalised per sensor with train statistics, stacked as 17 channels.
- [ ] Architecture: 4 conv blocks (conv → batch norm → ReLU → max pool), global average pool, four linear heads. Sum of four cross-entropy losses.
- [ ] Adam, early stopping on val macro-F1, 3 seeds.

### B4 Tokenized-text LLM
The fair comparison for Sightglass: same backbone, same targets, but signals go in as text instead of through the time-series encoder.

- [ ] Backbone: the same as the headline TSLM (Llama-3.2 1B), and Gemma-3 270M for the cheap version.
- [ ] Input: each sensor downsampled until the prompt fits the context window (for example 1 Hz for all sensors = 60 values each, 17 × 60 = 1,020 numbers), written as `PS1 (bar, 1 Hz): 151.2 152.0 ...` with 1 decimal place.
- [ ] Target: exactly the Phase 2 rationale text, so it learns the same format and the parser treats it fairly.
- [ ] LoRA fine-tuning; same epochs and early stopping as Phase 4.
- [ ] Its rationales go through the faithfulness checker in Phase 5.

### B5 GPT-4o on plots
- [ ] Uses the 200-cycle test sample and prompt from Phase 2, Step 5.
- [ ] Parse the label line for each component; unparseable answers count as wrong (report how many).
- [ ] Its rationales go through the faithfulness checker.

## Metrics written per baseline

- Per-component macro-F1 and accuracy, on val and test.
- Mean macro-F1 across components.
- Joint exact-match: all four components right in one cycle.
- Confusion matrix per component (`confusion_<component>.json`).
- For B4 and B5: rationale text, ready for Phase 5.

`results/baselines.json` shape:

```json
{
  "dataset": "hydraulic",
  "split": "grouped",
  "generated_by": "scripts/run_baselines.py",
  "git_sha": "abc1234",
  "baselines": {
    "B1_lightgbm": {
      "seeds": [0, 1, 2],
      "test": {
        "macro_f1": {"cooler_condition": 0.99, "valve_condition": 0.93, "pump_leakage": 0.97, "accumulator_pressure": 0.91, "mean": 0.95},
        "joint_exact_match": 0.84
      },
      "test_std": {"...": "..."}
    }
  }
}
```

(Numbers illustrative.)

## Tests

- [ ] Each baseline runs end to end on a 50-cycle fixture in CI (`-m slow` for B3 and B4, skipped on CPU CI).
- [ ] Predictions file has one row per test cycle and valid label values.
- [ ] Re-running with the same seed reproduces the metrics exactly (B0–B2) or within 0.005 (B3, B4).

## Exit criteria

- [ ] `results/baselines.json` contains B0–B5 with all metrics, generated by `scripts/run_baselines.py` with fixed seeds.
- [ ] B4 and B5 rationales saved for Phase 5.
- [ ] A short note in `docs/baselines.md`: which components are easy, which are hard, and whether virtual sensors change B1's cooler score.

## Risks in this phase

| Risk | What to do |
|---|---|
| B4 prompt too long for the context window | Lower the rate further, or summarise each sensor as 60 window means; record the choice |
| GPT-4o answers can't be parsed | Retry once with a format reminder; then count as wrong and report the rate |
| A baseline looks suspiciously perfect | Check for leakage first (split, normalisation fitted on all data, virtual sensors) before reporting |
