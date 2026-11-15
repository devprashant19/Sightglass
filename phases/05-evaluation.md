# Phase 5 — Evaluation and faithfulness

| | |
|---|---|
| **Goal** | One results table and a few charts that answer three questions. Is the diagnosis accurate? Are the explanations true? Does it hold up without leaks? |
| **Owner** | Aman (Teammate helps with claim parsing) |
| **When** | Round 1, days 6–11. The checker is built on days 6–8 against Phase 2 rationales, before any model output exists. |
| **Depends on** | Phase 2 extractors; Phase 3 baselines; Phase 4 checkpoints |
| **Unblocks** | Phase 6 export, Phase 7 results pages, README |

---

## 0. Pre-registration (before any test result is seen)

Write `configs/faithfulness.yaml` and `docs/eval-protocol.md` and commit them **before** running anything on test. The commit SHA goes in the README, so anyone can see the rules weren't changed after the results came in.

```yaml
# configs/faithfulness.yaml
relative_tolerance: 0.05          # a value is correct if within 5 % of the recomputed value
absolute_floor:                   # for values near zero, use an absolute tolerance instead
  "°C/min": 0.05
  "s": 0.05
  "%": 1.0
pct_tolerance_points: 3           # "9% below healthy" is correct if the true difference is 6–12 %
within_threshold_pct: 2           # "within p% of healthy" needs |true pct| <= max(p, 2) + tolerance
direction_neutral_band_pct: 2     # |true pct| below this counts as "within", not above/below
```

Main metrics, splits, seeds, the test sample for GPT-4o, and the tie-break rules all go in `eval-protocol.md`.

---

## 1. Diagnosis metrics (`src/sightglass/eval/metrics.py`)

Test split only; it's never touched during tuning.

- [ ] Macro-F1 per component, and the mean across components.
- [ ] Accuracy per component.
- [ ] Joint exact-match: all four components right in one cycle.
- [ ] Confusion matrix per component, showing which severity levels get confused.
- [ ] 95 % bootstrap confidence intervals (1,000 resamples over cycles) for mean macro-F1 and joint exact-match.
- [ ] Seed variance: mean ± std over seeds 0, 1, 2 for the main runs.
- [ ] Unparseable outputs (no valid label line for a component) count as wrong; report how many there were.

---

## 2. Faithfulness checker (`src/sightglass/eval/faithfulness.py`) — the headline metric

### Parse

```python
@dataclass(frozen=True)
class ParsedClaim:
    component: str | None
    sensor: str
    quantity: str
    value: float
    unit: str
    direction: Literal["above", "below", "within"] | None
    pct: float | None
    span: tuple[int, int]


def parse_claims(text: str, vocab: SensorVocab) -> tuple[list[ParsedClaim], list[str]]:
    """Return parsed claims and any numeric fragments that couldn't be parsed."""
```

- [ ] A regex for the canonical clause grammar from Phase 2, built from the sensor and quantity vocabulary.
- [ ] A looser fallback pattern for free-form numbers (for GPT-4o, which may drift from the format). Anything with a number that matches neither is recorded as an **unparsed numeric claim** and reported, never silently dropped.
- [ ] Map `(sensor, quantity)` to a feature name through `SensorVocab` (for example `("FS1", "mean flow") → "FS1.mean"`). Unknown pairs are logged.

### Verify

```python
@dataclass(frozen=True)
class Verdict:
    claim: ParsedClaim
    feature: str | None
    true_value: float | None
    true_pct: float | None
    value_ok: bool | None
    direction_ok: bool | None
    status: Literal[
        "verified",
        "wrong_value",
        "wrong_direction",
        "unknown_sensor",
        "unknown_quantity",
        "unit_mismatch",
    ]


def verify(
    claims: list[ParsedClaim],
    cycle: Cycle,
    extractor: Extractor,
    ref: HealthyReference,
    cfg: FaithfulnessConfig,
) -> list[Verdict]: ...
```

- [ ] Recompute the true value from the cycle's **native-rate** signals with the same Phase 2 extractor.
- [ ] A value is correct if it's within the relative tolerance, or the absolute floor for its unit.
- [ ] A direction is correct if the stated above / below / within matches the true percentage difference from the healthy reference, using the neutral band.
- [ ] Units must match the dataset card exactly; a mismatch is its own status.

### Report

| Metric | Definition |
|---|---|
| **Claim accuracy** | % of parsed numeric claims with `status = verified` (value and direction both right) |
| Value accuracy | % of claims with the value right, ignoring direction |
| Direction accuracy | % of claims with above / below / within right |
| Hallucinated-sensor rate | % of claims citing a sensor that doesn't exist |
| Unparsed-claim rate | Unparsed numeric fragments ÷ all numeric fragments |
| Claims per rationale | Average number of claims (a model that makes no claims shouldn't look perfect) |
| **Fully faithful rationales** | % of rationales where every claim verifies and there's at least one claim |
| Label–rationale consistency | See below |

### Label–rationale consistency (`eval/consistency.py`)

Does the explanation actually support the label it states?

- [ ] For each component's paragraph, take the stated label and the cited features.
- [ ] Rule: at least one cited feature must be a **kept link** for that component (from `hydraulic_links.yaml`), and its true deviation must point in the link's direction for a faulty label, or sit within the neutral band for a healthy label.
- [ ] Report % of paragraphs that are consistent, per component.

### Who gets checked

Run the checker on:

1. **Phase 2 ground-truth rationales** — must score 100 %. This validates the checker itself.
2. **Corrupted ground truth** (numbers changed ±20 %) — must score about 0 % on the corrupted claims.
3. **Sightglass** (Llama-1B, 3 seeds; Gemma-270M).
4. **B4 tokenized-text LLM.**
5. **B5 GPT-4o on plots** (200-cycle sample; Sightglass is also reported on the same 200 cycles for a fair comparison).

This comparison — Sightglass vs the tokenized LLM vs GPT-4o on plots — is the core result.

### Manual audit

- [ ] Hand-check 100 randomly chosen Sightglass claims against the plots and the extractor output. Record agreement with the automatic verdict in `docs/faithfulness-audit.md`. If agreement is under 95 %, fix the checker before reporting anything.

---

## 3. Leakage and robustness checks

| Check | How | What we report |
|---|---|---|
| Virtual-sensor ablation | Phase 4 `no_virtual` run, plus B1 without virtual features | Drop in cooler macro-F1 and in faithfulness |
| Neighbour leakage | Phase 4 `random_split` run vs grouped split, and the same for B1 | Score gap; a large gap means random splits inflate scores |
| Unstable cycles | Metrics on the subset with the "not yet stable" flag | Accuracy and faithfulness on the harder subset |
| Seed variance | 3 seeds on main runs | Mean ± std |
| Training on rationales | Phase 4 `label_only` vs full | Does adding evidence to targets change accuracy? |
| Rationale source | Phase 4 `gpt4o_rationales` vs physics | Faithfulness of a model trained on each |
| Downsampling | Features on 10 Hz vs native | Max relative drift per feature |

---

## 4. Failure analysis (feeds the dashboard's failure gallery)

- [ ] Collect every test cycle where Sightglass was wrong on a label or had at least one unverified claim.
- [ ] Tag each with an error type: `wrong_severity_adjacent` (e.g. 90 % vs 80 % valve), `wrong_component`, `wrong_value`, `wrong_direction`, `hallucinated_sensor`, `inconsistent`, `format`.
- [ ] Pick 10–15 representative cases and write a two- or three-sentence analysis of each: what went wrong and the likely reason.
- [ ] Output: `results/failures.json`.

---

## 5. Outputs

`scripts/evaluate.py --run <run_id> [--split test] [--subset gpt4o_200]` writes:

| File | Contents |
|---|---|
| `results/eval_<run_id>.json` | Diagnosis metrics, CIs, confusion matrices, faithfulness metrics, consistency |
| `results/faithfulness_<model>.json` | Per-claim verdicts (for the explorer's ticks and crosses) |
| `results/ablations.json` | One row per ablation, with deltas against the reference run |
| `results/summary.json` | The headline numbers the home page shows; generated from the files above, never edited by hand |
| `results/failures.json` | Failure cases with tags and analysis |

`make eval` reruns every evaluation from saved predictions in minutes, without the GPU (predictions are generated once per model with `--generate`).

README results table (generated by `scripts/make_readme_table.py`):

| Model | Mean macro-F1 | Joint EM | Claim accuracy | Fully faithful | Hallucinated sensors |
|---|---|---|---|---|---|
| Majority | … | … | — | — | — |
| Features + LightGBM | … | … | — | — | — |
| MiniRocket | … | … | — | — | — |
| 1D-CNN | … | … | — | — | — |
| Tokenized-text LLM (1B) | … | … | … | … | … |
| GPT-4o on plots (200) | … | … | … | … | … |
| **Sightglass (Llama-1B)** | … | … | … | … | … |

---

## Tests

- [ ] Parser unit tests: every clause variant from the templates; numbers with signs and decimals; units with symbols (`°C`, `l/min`); clauses at the start, middle and end of sentences.
- [ ] Verifier unit tests on synthetic cycles with known features.
- [ ] Round-trip (100 %) and corruption (≈ 0 %) tests from Phase 2 run in CI.
- [ ] Metric tests against `sklearn.metrics` on small hand-made examples.

## Exit criteria

- [ ] `configs/faithfulness.yaml` committed before any test-split result.
- [ ] `results/eval_*.json`, `ablations.json`, `summary.json` and `failures.json` exist, all from `scripts/evaluate.py`.
- [ ] Manual audit shows ≥ 95 % agreement with the checker.
- [ ] README results table generated from `results/`.

## Risks in this phase

| Risk | What to do |
|---|---|
| Parser misses claims in GPT-4o output | Report the unparsed-claim rate next to its score; show examples on the method page |
| Sightglass loses on accuracy to LightGBM | Expected; say so plainly and lead with faithfulness, which LightGBM can't offer |
| Tolerances look tuned to help us | They're pre-registered; also report claim accuracy at 2 % and 10 % in an appendix |
| A model scores high by making few claims | Report claims per rationale and "fully faithful" (needs ≥ 1 claim) alongside claim accuracy |
