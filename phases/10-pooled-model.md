# Phase 10 — Final round: pooled machine-health model

| | |
|---|---|
| **Goal** | One Sightglass model trained on all three machine types, compared with the three single-dataset models on each test set. |
| **Owner** | Both |
| **When** | Final round |
| **Depends on** | Phases 1–9 (three connectors, three physics modules, three single models) |

TimeNet's own paper suggests that training on pooled data improves results. This phase tests whether that holds for machine health, and especially whether it helps the smallest dataset (bearings).

---

## 1. Training

- [ ] One OpenTSLM-Flamingo model (Llama-1B; Gemma-270M for ablations) trained on hydraulic, bearing and wind tasks together.
- [ ] Each prompt states the machine type and its sensors, so the model knows which physics applies.
- [ ] Task sampling weights: start with temperature-scaled sampling (probability ∝ size^0.5) so the large hydraulic and wind sets don't drown out bearings; tune the exponent on val.
- [ ] Same splits as the single-dataset rounds. No test data from any dataset is used for tuning.
- [ ] Config: `configs/train/pooled_flamingo_llama1b.yaml`, with per-dataset weights.

## 2. Comparisons

| Comparison | Question |
|---|---|
| Pooled vs each single model, on each test set | Does pooling help or hurt each machine? |
| Pooled vs single on bearings specifically | Does pooled training help the smallest dataset? |
| Pooled without one dataset (leave-one-dataset-out, Gemma) | Which dataset contributes the transfer? |
| Faithfulness, pooled vs single | Do explanations stay as accurate when one model covers three machines? |
| Cross-machine confusion | Does the model ever cite hydraulic sensors for a bearing, or similar? (counted as hallucinated sensors) |

- [ ] 3 seeds for the pooled Llama-1B run; CIs as in Phase 5.
- [ ] `results/pooled.json` with one row per (model, dataset) pair.

## 3. Dashboard: cross-machine page (`#/cross-machine`)

- [ ] One table: rows are datasets, columns are single vs pooled for macro-F1 (or detection rate for wind) and claim accuracy.
- [ ] One chart: paired bars per dataset, single vs pooled, with CIs.
- [ ] A short written conclusion, generated from the numbers' direction (for example "Pooling improved bearings by X points and changed hydraulic by less than the seed spread"), reviewed by hand.
- [ ] Home page headline numbers updated to "3 machine types".

## 4. Release

- [ ] Publish the pooled model weights and model card on Hugging Face (if the backbone licences allow; Llama and Gemma each have their own terms **(verify)**).
- [ ] Final README: all rounds, all results, how to reproduce each from one command.
- [ ] Tag the repo `v1.0`.

## Exit criteria

- [ ] Pooled vs single-dataset comparison published on the site and in the README.
- [ ] Model card covers all three datasets, their licences and limitations.

## Risks

| Risk | What to do |
|---|---|
| Pooling hurts one dataset | Report it honestly; try per-dataset adapters as a follow-up |
| Combined training doesn't fit the budget | Use Gemma-270M for the pooled model and say so |
| Bearings too small to see an effect | Report CIs; call the result inconclusive if they overlap |
