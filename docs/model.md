# The model

The Sightglass engine predicts the condition of four components of one hydraulic test rig (cooler, valve, pump, accumulator) from one 60-second cycle of its 17 sensors, and explains each prediction with numbers computed from that cycle. **It is a gradient-boosted classifier plus a rule-based explainer, not a language model.** The language-model version (OpenTSLM-Flamingo) has its code and configs but has not been trained.

Use it to learn and prototype condition monitoring on the UCI rig. Do not use it to decide anything about a real machine: it has never seen one. The release record is [`MODEL_CARD.md`](../MODEL_CARD.md), and the results table lives in the [README](../README.md#results).

## Data

| | |
|---|---|
| Source | UCI #447 "Condition monitoring of hydraulic systems", downloaded by `connector/timenet_connectors/datasets/uci/uci_hydraulic/connector.py` and checked against a fixed SHA-256. Licence CC BY 4.0 |
| Size | 2,205 cycles; split by condition into 1,543 train, 333 validation and 329 test cycles (`results/summary.json`, `dataset`) |
| Split | Grouped by the four-label tuple: each of the 144 combinations goes wholly to one split, so test conditions never appear in training. Why: [`docs/hydraulic-eda.md`](hydraulic-eda.md) |
| Known gaps | One laboratory rig, fault levels set on purpose. Only 21 cycles have all four parts healthy, and all of them landed in test, so train has no fully healthy cycle |

## How a prediction is made

1. **Features.** `src/sightglass/physics/hydraulic.py` extracts 43 features at each sensor's native rate: means, peaks, ripple and rise time of the pressure lines, the PS1-to-PS2 switching lag, flow, power per unit of flow, temperature means and slopes, the virtual sensors.
2. **Labels.** One LightGBM classifier per component (`src/sightglass/baselines/lightgbm_baseline.py`), with leaves, trees and learning rate chosen on the validation split. The chosen values are in `results/engine_training.json`.
3. **Healthy reference.** For each feature, a mean and spread from the train cycles where *the component it is linked to* is healthy (stable cycles only). Features with no link use cycles where at least three of the four are healthy. This per-component fit exists because there is no fully healthy cycle in train.
4. **Links.** `scripts/analyze_links.py` measures, on train only, which features move with which component, and keeps a link only when the direction matches the expected physics and survives a check stratified by the other components. The kept links are in `configs/physics/hydraulic_links.yaml`: seven for the cooler, two for the valve, three for the pump, **one for the accumulator** (PS2 ripple).
5. **Explanation.** `src/sightglass/rationales/builder.py` writes, for each *predicted* label, up to three linked features with their value and their deviation from the healthy reference, in a fixed grammar.
6. **Check.** The text is parsed back and every number is recomputed from the signal (`src/sightglass/eval/faithfulness.py`), and `src/sightglass/eval/consistency.py` asks whether the evidence actually points to the label.

## Training

```bash
python scripts/train_engine.py      # needs make data first; writes data/models/engine.pkl
```

It trains on the 1,543 train cycles and tunes on the 333 validation cycles, on the CPU. The full run time is not recorded. The comparable B1 baseline took about half a minute per seed (`seconds` in `results/baselines.json`).

## Evaluation

All on the 329 test cycles, never used for tuning. The tolerances were fixed in `configs/faithfulness.yaml` before any test result was computed, and the rules are in [`docs/eval-protocol.md`](eval-protocol.md).

The numbers are not repeated here. They are in the [README results table](../README.md#results), generated from `results/summary.json` by `scripts/make_readme_table.py`, with bootstrap intervals in `results/eval_engine.json`. What to read in them:

- **The engine is B1.** Its labels come from the same LightGBM, so its accuracy equals B1's exactly. MiniRocket on raw signals scores slightly higher and gives no explanation at all.
- **"Claims verified" is 100% by construction.** The engine computes its numbers from the signal, so the checker agreeing shows that the two are consistent, nothing more. The checker's own reliability comes from the corruption tests in `results/checker_validation.json`.
- **Consistency is the honest weak spot.** It counts paragraphs whose recomputed evidence points to the stated label. It is high for the cooler and low for the pump and the accumulator (`consistency_per_component` in `results/summary.json`).

## Where it fails

From `results/eval_engine.json` and `results/failures.json`:

| Failure | What happens | Why |
|---|---|---|
| **Accumulator levels confused** | Most wrong labels are the accumulator: 90 bar read as 100 bar, 115 bar as 130 bar, and some 130 bar cycles read as faulty | One physics link survives the stratified check, and neighbouring pre-charge levels give similar ripple |
| **Weak pump leakage read as severe** | 7 of 82 weak-leakage test cycles predicted severe | The flow drop between the two leakage levels is small |
| **Evidence that does not support the label** | The label can be right while the cited feature sits inside the healthy spread. This is the most common entry in `results/failures.json` | The explainer cites the linked features that best show the label, and for weak links none of them does |
| **Learned shortcuts** | In the what-if lab, warming TS1 to TS4 by 2 °C on a healthy cycle changes the accumulator verdict, and cutting FS1/FS2 by 5% already flips the pump to weak leakage | Temperature is correlated with accumulator level in the training conditions. The lab exists to show this |
| **Virtual sensors** | CE (virtual cooling efficiency) alone separates the cooler classes | It is computed from other sensors. The no-virtual ablation in `results/ablations.json` measures the effect |

## Cost

Everything above runs on a laptop CPU. The one live diagnosis measured took about 60 ms through the API. The TSLM fine-tune needs a GPU with about 20 GB for Llama-3.2 1B, and was not run.

## The TSLM that is not trained

`src/sightglass/tslm/` holds the prompt builder (100 Hz sensors decimated to 10 Hz), a model wrapper and a training loop, with configs in `configs/train/`. On the CPU, `make train` runs a smoke loop over 64 cycles that proves loading, normalisation and checkpointing, and writes losses only (`results/runs/hydraulic_smoke_cpu_flamingo_s0_20261122/metrics.json`). **The full mode raises `NotImplementedError`:** OpenTSLM's curriculum trainer is not wired in. When it is, its output goes through the same parser and checker as the engine's. [`docs/downsampling.md`](downsampling.md) measures what the 10 Hz input loses.
