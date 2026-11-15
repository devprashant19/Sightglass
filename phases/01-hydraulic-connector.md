# Phase 1 — Hydraulic dataset and TimeNet connector

| | |
|---|---|
| **Goal** | A merged TimeNet PR that turns the UCI hydraulic test rig into a validated TimeNet dataset, with four component classification tasks, one joint task and a question-answering task. |
| **Owner** | Aman (Teammate reviews and helps with CI) |
| **When** | Round 1, days 2–4 (PR open by end of day 4) |
| **Depends on** | Phase 0 (fork checks pass, TimeF notes written) |
| **Unblocks** | Phases 2, 3, 4 (everything reads this build) |

---

## 1. Source data

**UCI Machine Learning Repository #447, "Condition monitoring of hydraulic systems"** (CC BY 4.0). 2,205 load cycles, each 60 seconds long, recorded on one test rig. The values below are from memory. Confirm every one against the dataset's `description.txt` and `documentation.txt` during EDA.

| Sensor files | Quantity | Unit | Rate | Samples per cycle |
|---|---|---|---|---|
| PS1–PS6 | Pressure | bar | 100 Hz | 6,000 |
| EPS1 | Motor power | W | 100 Hz | 6,000 |
| FS1–FS2 | Volume flow | l/min | 10 Hz | 600 |
| TS1–TS4 | Temperature | °C | 1 Hz | 60 |
| VS1 | Vibration | mm/s | 1 Hz | 60 |
| CE | Cooling efficiency (virtual) | % | 1 Hz | 60 |
| CP | Cooling power (virtual) | kW | 1 Hz | 60 |
| SE | Efficiency factor (virtual) | % | 1 Hz | 60 |

Each sensor file is tab-separated: one row per cycle (2,205 rows), one column per sample.

**Labels** (`profile.txt`, one row per cycle, five columns):

| Column | Meaning | Values |
|---|---|---|
| 1 | Cooler condition | 3 % (close to total failure), 20 % (reduced efficiency), 100 % (full efficiency) |
| 2 | Valve condition | 100 % (optimal), 90 % (small lag), 80 % (severe lag), 73 % (close to total failure) |
| 3 | Internal pump leakage | 0 (none), 1 (weak), 2 (severe) |
| 4 | Hydraulic accumulator pressure | 130 bar (optimal), 115 bar (slightly reduced), 100 bar (severely reduced), 90 bar (close to total failure) |
| 5 | Stable flag | 0 = conditions were stable, 1 = static conditions might not have been reached yet **(verify which value means which)** |

---

## 2. Exploratory analysis (day 2, `notebooks/01_hydraulic_eda.ipynb`)

The EDA decides the split, so it comes before any connector code. Nothing downstream depends on the notebook itself; it only produces decisions written into `docs/hydraulic-eda.md`.

- [ ] Load every file; assert 2,205 rows each, and the expected column counts.
- [ ] Check for NaNs, constant rows and obvious sensor dropouts.
- [ ] Class counts per label, and counts per four-label combination. How many unique combinations are there, and how many cycles does each have?
- [ ] **Label sequence plot:** each of the four labels against cycle index. This answers the key question: do conditions repeat throughout the run, or change in long blocks?
- [ ] Autocorrelation between neighbouring cycles: is cycle *i* nearly identical to *i+1*? This drives the neighbour-leakage check in Phase 5.
- [ ] Per-sensor summary statistics by class, for a first look at which sensors separate which components (feeds Phase 2).
- [ ] Stable-flag counts, and whether unstable cycles cluster at condition changes.
- [ ] Check whether the virtual sensors CE / CP / SE alone predict the cooler label almost perfectly (a one-feature logistic regression). If so, record it as a leakage risk.

### Split decision

Decide using the label-sequence plot, then write the decision and the reason in `docs/hydraulic-eda.md`.

| What the EDA shows | Split to use |
|---|---|
| Label combinations repeat throughout the run | Group by the four-label tuple. Each group (one combination) goes entirely to train, val or test, stratified so every class of every component appears in each split. Use TimeNet's `StratifiedSplitter` with a group key if it supports one **(verify)**. |
| Conditions change in long blocks | Block split on cycle index (for example 70 / 15 / 15 by contiguous blocks), but **first check that every class of every component appears in train**. If not, fall back to the grouped split. |
| Neither is clean | Grouped split by combination, plus a gap of *k* cycles removed at every group boundary in the cycle order to stop neighbour leakage. |

Target proportions: 70 % train, 15 % validation, 15 % test. **The test split is never used for tuning anything** — not hyperparameters, templates, tolerances or thresholds.

Also save a **random 70 / 15 / 15 split** with seed 0 as a second split. It's only used in Phase 5 to measure how much a random split inflates scores.

---

## 3. TimeNet mapping

TimeF models data as Record → Source → Signal **(verify the exact terms and classes in the format docs)**.

| TimeF concept | Hydraulic mapping |
|---|---|
| Record | One load cycle (2,205 records). Record id `hydraulic-00000` … `hydraulic-02204`. Metadata: `cycle_index`, `stable_flag`. |
| Source | Sensor group: `pressure` (PS1–6), `power` (EPS1), `flow` (FS1–2), `temperature` (TS1–4), `vibration` (VS1), `virtual` (CE, CP, SE) |
| Signal | Each sensor on its **own regular time axis at its native rate**. Don't resample to a common rate; TimeNet supports per-signal axes. Each signal carries `unit`, `sample_rate_hz`, `n_samples`, `description`. |
| Annotations | The four component labels per record, with both the raw value (e.g. `20`) and a readable class name (e.g. `reduced efficiency`), plus units. |

### Tasks

| Task id | Type | Target | Classes |
|---|---|---|---|
| `cooler_condition` | Classification | Cooler | 3 |
| `valve_condition` | Classification | Valve | 4 |
| `pump_leakage` | Classification | Pump | 3 |
| `accumulator_pressure` | Classification | Accumulator | 4 |
| `joint_condition` | Multi-label classification | All four at once | 3 × 4 × 3 × 4 |
| `diagnosis_qa` | Question answering | Answer text = label + rationale | Added in a follow-up commit after Phase 2, or kept in the Sightglass repo if the maintainers prefer the connector to hold raw data only **(ask in the PR)** |

Splits are attached directly to the tasks, as TimeNet expects **(verify)**.

---

## 4. Connector implementation

Location in the fork: `timenet_connectors/datasets/<org>/uci_hydraulic/` **(verify the path pattern)**.

### `connector.py`

```python
# Sketch only. Match the base class, method names and return types the connector guide defines.

UCI_URL = "https://archive.ics.uci.edu/static/public/447/condition+monitoring+of+hydraulic+systems.zip"  # verify
UCI_SHA256 = "<fill in after the first download>"

SENSORS = {
    # name: (source, unit, rate_hz, n_samples, description)
    "PS1": ("pressure", "bar", 100, 6000, "Pressure sensor 1"),
    # ... PS2–PS6, EPS1, FS1–FS2, TS1–TS4, VS1, CE, CP, SE
}

LABELS = {
    "cooler_condition": {
        3: "close to total failure",
        20: "reduced efficiency",
        100: "full efficiency",
    },
    "valve_condition": {
        100: "optimal",
        90: "small lag",
        80: "severe lag",
        73: "close to total failure",
    },
    "pump_leakage": {0: "no leakage", 1: "weak leakage", 2: "severe leakage"},
    "accumulator_pressure": {
        130: "optimal",
        115: "slightly reduced",
        100: "severely reduced",
        90: "close to total failure",
    },
}


def download(raw_dir) -> None:
    """Fetch the UCI zip, verify SHA-256, unzip into raw_dir. Idempotent: skip if already verified."""


def convert(raw_dir, out_dir) -> None:
    """Read the tab-separated files, build 2,205 records, write the manifest, control.duckdb and Parquet shards."""
```

Implementation notes:

- [ ] Read each sensor file once with `pandas.read_csv(path, sep="\t", header=None, dtype="float32")`. That's 17 arrays of shape `(2205, n_samples)`; total memory is about 0.5 GB, so no streaming is needed.
- [ ] Validate shapes before building anything; fail loudly with the file name if a shape is wrong.
- [ ] Build records in cycle order. Keep `cycle_index` as metadata so the neighbour-leakage check can use it.
- [ ] Shard Parquet by record ranges (for example 256 records per shard) **(verify TimeNet's preferred shard size)**.
- [ ] Make `convert()` deterministic: the same input gives byte-identical output, so a rebuild doesn't change the dataset hash.
- [ ] Download over HTTPS only, with a timeout and a clear error if the checksum doesn't match.

### `dataset.yaml` (dataset card)

Fill in every field the template requires **(verify the schema)**, including:

- name, version, description (two or three plain sentences),
- source URL, citation (Helwig, Pignanelli, Schütze 2015, *Condition monitoring of a complex hydraulic system using multivariate statistics*, I2MTC — **verify the exact citation**), licence CC BY 4.0,
- every sensor with unit, rate, sample count and description,
- every label with its values and readable names,
- tasks and the split method, with the reason taken from the EDA,
- known limitations: single test rig, lab conditions, artificially set fault levels, virtual sensors derived from physical ones, unstable cycles near condition changes.

### `tests/test_connector.py`

- [ ] Record count is exactly 2,205.
- [ ] Every signal has the expected length and rate for its sensor.
- [ ] No NaNs in any signal.
- [ ] Every label value is in its allowed set.
- [ ] Train, val and test splits don't share records, and together cover all records.
- [ ] Every class of every component appears in train.
- [ ] `convert()` is deterministic: run it twice on the same raw data and compare file hashes.
- [ ] A small fixture (for example 10 cycles cut from the real files, if the licence and the repo's size rules allow it, or synthetic files with the same shape) so tests run in CI without downloading the full zip.

---

## 5. Checks and the PR (day 4)

- [ ] Run all four make targets on the fork; all must pass.
- [ ] Load the built dataset through **TimeNet's own loader** on a clean machine (a fresh VM or container, nothing cached) and print one record.
- [ ] Make one sample plot: all 17 sensors of one cycle on aligned time axes, coloured by source. Attach it to the PR.
- [ ] Open the PR. Title: `Add UCI hydraulic system condition monitoring dataset`. Description:
  - what the dataset is, in two sentences,
  - licence and citation,
  - sensors, rates and tasks (short table),
  - split method and why,
  - how it was tested, and the sample plot.
- [ ] Respond to review comments within a day. Keep the diff limited to the connector folder.

## 6. Sightglass-side loader

In the project repo, `src/sightglass/data/` wraps the TimeNet build so every later phase uses one loader:

```python
@dataclass(frozen=True)
class Signal:
    name: str  # "PS1"
    source: str  # "pressure"
    unit: str  # "bar"
    rate_hz: float  # 100.0
    values: np.ndarray  # float32, shape (n_samples,)


@dataclass(frozen=True)
class Cycle:
    id: str  # "hydraulic-01423"
    signals: dict[str, Signal]
    labels: dict[str, int]  # {"cooler_condition": 20, ...}
    meta: dict[str, Any]  # {"cycle_index": 1423, "stable_flag": 0}


def load_cycles(
    dataset: str, split: Literal["train", "val", "test", "all"], split_name: str = "grouped"
) -> list[Cycle]: ...
```

- [ ] `load_cycles` reads the TimeNet build through TimeNet's API, not by reading Parquet directly, so the PR's format is what we actually test.
- [ ] Cache the decoded arrays as a single `.npz` per split under `data/cache/` for speed; the cache key includes the build hash.
- [ ] Unit tests: counts per split match the build; `Cycle` objects round-trip.

---

## Exit criteria

- [ ] `docs/hydraulic-eda.md` records the split decision and the reason.
- [ ] The dataset loads through TimeNet's own loader on a clean machine.
- [ ] PR is open with all checks passing; ideally merged before the round closes.
- [ ] `sightglass.data.load_cycles("hydraulic", ...)` works for the grouped and the random split.

## Risks in this phase

| Risk | What to do |
|---|---|
| UCI URL changes or the zip changes | Pin the SHA-256; keep a copy of the zip on the Nebius disk; record the download date in the dataset card |
| TimeNet doesn't support a group key in its splitter | Compute the split ourselves in `convert()` and attach it as an explicit record list, if the format allows **(verify)** |
| Maintainers want changes late in the round | Submit the open, passing PR link; the submission rules may accept it (check `docs/competition-notes.md`) |
| A split leaves a class out of train | Use the grouped split; never ship a split that fails this test |
