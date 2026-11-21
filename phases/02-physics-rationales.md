# Phase 2 — Physics-grounded rationales

| | |
|---|---|
| **Goal** | For every cycle, a training rationale in which every number is computed from that cycle's own signals, stored with structured evidence so it can be checked later. |
| **Owner** | Aman |
| **When** | Round 1, days 3–7 (rationales frozen at end of day 7) |
| **Depends on** | Phase 1 loader and split |
| **Unblocks** | Phase 4 training targets, Phase 5 faithfulness checker, Phase 7 explorer |

This phase is Sightglass's differentiator. The OpenTSLM authors generated rationales with GPT-4o from plots and list that as a limitation. Ours are computed from the signals, so they can't contain a number the signal doesn't support.

---

## Step 1 — Feature extractors (`src/sightglass/physics/`)

### Shared types (`physics/base.py`)

```python
@dataclass(frozen=True)
class Feature:
    name: str  # "FS1.mean"
    sensor: str  # "FS1"  (or "EPS1/FS1" for ratios)
    quantity: str  # "mean flow"
    unit: str  # "l/min"
    value: float
    window: tuple[float, float] | None = (
        None  # seconds within the cycle, for dashboard highlighting
    )


class Extractor(Protocol):
    dataset: str

    def feature_names(self) -> list[str]: ...
    def extract(self, cycle: Cycle) -> dict[str, Feature]: ...


@dataclass
class HealthyReference:
    mean: dict[str, float]
    std: dict[str, float]
    n_cycles: int

    @classmethod
    def fit(cls, features: list[dict[str, Feature]]) -> "HealthyReference": ...
    def z(self, f: Feature) -> float: ...
    def pct_diff(self, f: Feature) -> float: ...  # (value - mean) / |mean| * 100
    def save(self, path) -> None: ...
    @classmethod
    def load(cls, path) -> "HealthyReference": ...
```

The same `Extractor` is used three times: to build rationales (this phase), to verify claims (Phase 5), and to check live answers (Phase 6). That shared code is what makes the faithfulness check trustworthy, so it must be pure and deterministic: no randomness, no dependence on other cycles.

### Hydraulic features (`physics/hydraulic.py`)

Computed per cycle, at the native sample rate.

| Group | Feature name | Definition | Unit |
|---|---|---|---|
| Pressure | `PSk.mean`, `PSk.peak`, `PSk.ripple` | mean, max, standard deviation of PS*k* | bar |
| Pressure | `PSk.rise_time` | time from 10 % to 90 % of the main pressure step in the cycle's load profile **(define the step from the EDA plots)** | s |
| Pressure | `PS1_PS2.lag` | delay between the pressure steps of PS1 and PS2, by cross-correlation | s |
| Flow | `FS1.mean`, `FS2.mean` | mean volume flow | l/min |
| Power | `EPS1.mean` | mean motor power | W |
| Power / flow | `EPS1_per_FS1` | `EPS1.mean / FS1.mean`: power per unit of delivered flow (leakage indicator) | W·min/l |
| Temperature | `TSk.mean`, `TSk.slope` | mean, and least-squares slope over the 60 s | °C, °C/min |
| Temperature | `cooler.delta_t` | cooler inlet minus outlet temperature **(confirm which TS sensors sit either side of the cooler)** | °C |
| Vibration | `VS1.mean`, `VS1.peak` | mean and max | mm/s |
| Virtual | `CE.mean`, `CP.mean`, `SE.mean` | means; flagged `virtual=True` so ablations can drop them | %, kW, % |

- [ ] Unit test each feature on synthetic signals with known answers (a sine for ripple, a ramp for slope, a step for rise time, two shifted steps for lag).
- [ ] Rise time and lag: check on 20 real cycles by plotting the detected step on the raw signal.

### Healthy reference

- [ ] "Healthy" means all four components at full condition: cooler 100 %, valve 100 %, pump 0, accumulator 130 bar, and the stable flag set to stable.
- [ ] Fit **on the train split only**, to keep test information out of the rationales.
- [ ] If fewer than about 30 healthy train cycles exist, widen the reference per component: for component X, use cycles where X is healthy, regardless of the others. Record which option was used.
- [ ] Save to `data/reference/hydraulic_healthy.json`, with `n_cycles` and the build hash.

---

## Step 2 — Link features to components

First write the expected physics, then keep only links the train data supports.

| Component | Expected evidence (confirm on data) |
|---|---|
| Cooler | Higher temperatures and steeper temperature slope; smaller cooler temperature difference; lower CE / CP |
| Valve | Slower pressure rise and switching lag in PS1 / PS2 |
| Pump leakage | Lower flow at similar motor power; higher power-to-flow ratio |
| Accumulator | Larger pressure ripple; lower peak pressure (less buffering) |

Check each link on train only:

- [ ] For every (component, feature) pair, compute the Kruskal–Wallis H statistic across the component's classes, and Cliff's delta between healthy and the most severe class.
- [ ] Check that the **direction** matches the physics (for example, leakage should raise `EPS1_per_FS1`). A strong feature in the wrong direction is a red flag to investigate, not a link to keep.
- [ ] Check that a feature isn't mainly driven by a *different* component (for example, a temperature feature that tracks the cooler but also moves with the pump). Use a partial check: does the effect hold within each level of the other components?
- [ ] Keep a link if the effect is clear (for example |Cliff's δ| ≥ 0.33 and p < 0.01 after correction) and the direction is right. Write the thresholds down before looking at the results.
- [ ] Save to `configs/physics/hydraulic_links.yaml`:

```yaml
pump_leakage:
  - feature: EPS1_per_FS1
    direction: up        # value rises as the fault gets worse
    effect: 0.71         # Cliff's delta on train
  - feature: FS1.mean
    direction: down
    effect: -0.64
```

- [ ] Every component needs at least two kept links, preferably from different sensors. If one has fewer, write it up as a limitation and use what there is.

---

## Step 3 — Rationale templates (`src/sightglass/rationales/`)

### Format

Each rationale has three parts:

1. **Label line** — `Pump leakage: severe leakage.`
2. **Evidence clauses** — the top two or three linked features, ranked by |z| against the healthy reference. Each clause follows one **canonical grammar** so the Phase 5 parser can read it exactly:
   ```
   <SENSOR> <quantity> <value> <unit> (<pct>% <above|below> healthy)
   <SENSOR> <quantity> <value> <unit> (within <pct>% of healthy)
   ```
   Example: `FS1 mean flow 6.1 l/min (9% below healthy)`
3. **Interpretation** — one sentence of physics reasoning, chosen from 3–5 phrasings per pattern so the model doesn't memorise one sentence.

Full example (numbers illustrative):

> Pump leakage: severe leakage. Evidence: FS1 mean flow 6.1 l/min (9% below healthy); EPS1 mean power 2450 W (within 1% of healthy). The motor draws the same power but delivers less flow, which points to internal leakage.

The prose varies, but the evidence clause never does. That trade-off is deliberate: the varied interpretation stops phrase memorisation, and the fixed clause makes faithfulness checking exact rather than fuzzy.

### Number formatting

- [ ] Values: 3 significant figures, no thousands separators (`2450`, not `2,450`).
- [ ] Percentages: whole numbers; use "within *p*% of healthy" when |pct| < 2.
- [ ] Units exactly as in the dataset card.
- [ ] One function, `rationales.format.number(value, unit)`, used everywhere, including the parser's tests.

### Healthy cycles and multi-fault cycles

- A healthy component gets a short line with one supporting clause: `Cooler: full efficiency. Evidence: TS1 mean temperature 45.2 °C (within 1% of healthy).`
- A cycle with several faulty components gets one paragraph per component, ordered by severity.

### Builder

```python
@dataclass(frozen=True)
class Claim:
    sensor: str
    quantity: str
    value: float
    unit: str
    direction: Literal["above", "below", "within"]
    pct: float
    feature: str  # "FS1.mean"
    span: tuple[int, int]  # character offsets of the clause in the text


@dataclass(frozen=True)
class Rationale:
    cycle_id: str
    component: str
    label_value: int
    label_name: str
    text: str
    claims: list[Claim]
    template_id: str


def build_rationale(
    cycle: Cycle,
    features: dict[str, Feature],
    ref: HealthyReference,
    links: Links,
    component: str,
    rng: np.random.Generator,
) -> Rationale: ...
```

- [ ] The template choice uses a seeded RNG keyed on `(cycle_id, component)`, so rebuilds are identical.
- [ ] Output: `data/rationales/hydraulic.jsonl`, one line per (cycle, component), plus a joint rationale per cycle.

---

## Step 4 — Question–answer pairs

From the same features, generate QA pairs for the `diagnosis_qa` task and for training variety.

| Question type | Example | Answer |
|---|---|---|
| Component condition | "What is the condition of the cooler?" | Label line + rationale |
| Strongest deviation | "Which sensor deviates most from healthy?" | Sensor with the largest \|z\|, with its clause |
| Health check | "Is this cycle healthy?" | Yes / No + the faulty components with one clause each |
| Full diagnosis | "Diagnose this hydraulic cycle." | All four components |

- [ ] 3–5 phrasings per question type.
- [ ] Output: `data/qa/hydraulic.jsonl` with `cycle_id`, `split`, `question`, `answer`, `claims`.

## Step 5 — Optional: GPT-4o rationales from plots

The comparison point for the headline faithfulness chart.

- [ ] For 200 cycles (stratified, from **test**), render the same multi-sensor plot the dashboard uses, and ask GPT-4o for a diagnosis and an explanation, with the same instructions the OpenTSLM authors used where they're published **(verify)**.
- [ ] Ask it to use the canonical clause format, so the parser treats it fairly. Record the exact prompt in `configs/baselines/gpt4o_plots.yaml`. <!-- check-docs: ignore -->
- [ ] Store raw responses in `results/raw/gpt4o_plots.jsonl` with model name and date. <!-- check-docs: ignore -->
- [ ] Keep the API key in `.env`, never in the repo.

---

## Tests

- [ ] Extractor unit tests on synthetic signals (Step 1).
- [ ] **Round-trip test:** for every built rationale, parse it with the Phase 5 parser and recompute every claim with the extractor; 100 % must verify. A failure means a bug in the builder, the formatter or the parser.
- [ ] **Corruption test:** change one number in 1,000 rationales by ±20 %; the checker must flag every one.
- [ ] Healthy reference uses only train cycles (assert on ids).

## Exit criteria

- [ ] Every cycle has a rationale per component and a joint rationale, each with structured claims.
- [ ] `hydraulic_links.yaml` records the kept links with effect sizes.
- [ ] Round-trip test passes at 100 %.
- [ ] A human spot-check of 50 rationales (random, from train) finds no wrong numbers and no physically wrong interpretations. Record the check in `docs/rationale-spotcheck.md`.

## Risks in this phase

| Risk | What to do |
|---|---|
| A component has weak physical evidence (for example, the valve at 90 % is hard to see) | Say so in its rationale ("small deviation"), keep the link honest, and list it as a limitation |
| Virtual sensors dominate the cooler rationale | Prefer physical sensors in ranking; keep virtual features only as a tie-break, and report the ablation |
| Model learns templates, not evidence | Several interpretation phrasings; faithfulness checks numbers, not wording |
