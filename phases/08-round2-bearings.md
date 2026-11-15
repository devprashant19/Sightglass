# Phase 8 — Round 2: HUST bearings

| | |
|---|---|
| **Goal** | Add bearing fault diagnosis from high-rate vibration, with explanations based on bearing fault frequencies, and a test on an operating condition the model hasn't seen. |
| **Owner** | Both (Aman: connector, physics, eval; Teammate: training, export, bearing page) |
| **When** | Round 2 (about two weeks) |
| **Depends on** | Round 1 pipeline (Phases 1–7), reused as-is |
| **Unblocks** | Phase 10 pooled model |

Each later round reuses Phases 1–7. Only the connector, the physics module and one dashboard page are new. The day-by-day plan follows the round-1 table in [README.md](README.md#two-week-round-day-by-day), with "hydraulic" swapped for "bearing".

---

## 1. Data and licence

- **HUST bearing dataset** (Mendeley Data, CC BY 4.0). Before writing code, confirm that Mendeley's terms on AI use and text-mining don't override the CC BY licence, and write the answer in `docs/competition-notes.md`.
- From the research notes **(verify every number)**: 99 recordings, 6 defect types, 5 bearing types, 3 working conditions (loads or speeds), sampled at 51.2 kHz.
- [ ] Repeat the Phase 0 PR and Discord search for "HUST" and "bearing" on day 1 of the round.

## 2. Connector (`timenet_connectors/datasets/<org>/hust_bearing/`)

Same structure as Phase 1.

| TimeF concept | Bearing mapping |
|---|---|
| Record | One recording (99 records) |
| Source | Accelerometer (and tachometer or speed channel if present) |
| Signal | Vibration at 51.2 kHz, native rate, full length |
| Annotations | Defect type, bearing type, working condition, shaft speed, bearing geometry (pitch diameter, ball diameter, number of balls, contact angle) |

- [ ] Bearing geometry per bearing type goes in `dataset.yaml` with its source (datasheet or the dataset paper), because the fault frequencies depend on it.
- [ ] Tasks: `defect_type` (6 classes), and `diagnosis_qa` after the rationales exist.
- [ ] **Splits are by recording, never by window.** Headline split is leave-one-condition-out: train on two working conditions, test on the third, rotated three times. Also a grouped stratified split by recording for comparison.

## 3. Windowing (`src/sightglass/data/windowing.py`)

- [ ] Raw 51.2 kHz recordings are far too long for the model. Cut short windows (start with 0.2 s = 10,240 samples; try 0.1 and 0.5 s), with 50 % overlap for train and no overlap for test.
- [ ] Every window keeps its recording id, so splits and metrics stay grouped by recording.
- [ ] Model input per window: the raw window downsampled for the encoder (for example to 2,048 points), **plus** the envelope spectrum and the physics features as text. Faithfulness is checked against the native-rate window.
- [ ] Recording-level prediction: majority vote (or mean probability) across a recording's windows. Report both window-level and recording-level metrics.

## 4. Physics module (`src/sightglass/physics/bearing.py`)

### Characteristic fault frequencies

With shaft frequency *f*ᵣ (Hz), number of rolling elements *n*, ball diameter *d*, pitch diameter *D* and contact angle *θ*:

| Frequency | Formula | Fault |
|---|---|---|
| BPFO | (n/2) · fᵣ · (1 − (d/D)·cos θ) | Outer race |
| BPFI | (n/2) · fᵣ · (1 + (d/D)·cos θ) | Inner race |
| BSF | (D/(2d)) · fᵣ · (1 − ((d/D)·cos θ)²) | Rolling element |
| FTF | (fᵣ/2) · (1 − (d/D)·cos θ) | Cage |

### Features per window

| Feature | Definition | Unit |
|---|---|---|
| `VIB.rms` | Root mean square | m/s² (or g; match the dataset) |
| `VIB.kurtosis` | Kurtosis (≈ 3 for a healthy, Gaussian-like signal) | — |
| `VIB.crest` | Peak ÷ RMS | — |
| `ENV.peak_freq` | Frequency of the largest envelope-spectrum peak in the fault band | Hz |
| `ENV.peak_order` | `ENV.peak_freq / fᵣ` | × shaft speed |
| `ENV.bpfo_amp`, `ENV.bpfi_amp`, `ENV.bsf_amp`, `ENV.ftf_amp` | Envelope amplitude at each fault frequency (± 2 % search band), and at 2× and 3× harmonics | same as signal |
| `ENV.bpfo_snr` etc. | Amplitude at the fault frequency ÷ median of the surrounding band | dB |

Envelope spectrum: band-pass around a resonance band (choose by spectral kurtosis / kurtogram on train, or a fixed band from the dataset paper), Hilbert transform, magnitude, remove the mean, FFT.

- [ ] Unit tests: a synthetic signal with impulses repeating at a known BPFO, modulated onto a carrier, must produce an envelope peak at that frequency.
- [ ] Healthy reference per bearing type and working condition, fit on train only.
- [ ] Link checks as in Phase 2 (each defect type should raise the amplitude at its own fault frequency).

### Rationale example

> Outer-race defect. Evidence: ENV peak order 3.6 × shaft speed (matches BPFO 3.58 ×); VIB kurtosis 7.2 (140% above healthy). Repeated impacts at the outer-race frequency point to a defect on the outer race.

The canonical clause grammar from Phase 2 gets two new forms: an order match (`matches BPFO 3.58 ×`) and a dimensionless value. The Phase 5 parser and verifier gain matching rules: an order match is correct if the stated order is within 2 % of the computed peak order **and** the named fault frequency is the nearest one.

## 5. Training and evaluation

- [ ] Same Phase 4 setup: Gemma-270M smoke test, then Llama-1B, 3 seeds, on each leave-one-condition-out fold.
- [ ] Baselines: majority; features + LightGBM; MiniRocket on windows; 1D-CNN on windows; tokenized-text LLM (on envelope-spectrum peaks, since raw windows don't fit as text).
- [ ] Metrics: macro-F1 per fold and mean across folds, at window and recording level; faithfulness as in Phase 5; confusion matrix of defect types.
- [ ] Extra check: does faithfulness hold on the unseen condition? (Explanations that stay true when the load changes are a strong claim.)

## 6. Dashboard: bearing explorer (`#/bearing/:windowId?`)

- [ ] Raw vibration window (uPlot), envelope spectrum with vertical markers at BPFO, BPFI, BSF, FTF and their harmonics, labelled.
- [ ] Hovering a claim about a fault frequency highlights its marker and the matching peak.
- [ ] Recording-level view: all windows of a recording as a strip, coloured by predicted defect.
- [ ] Results section: leave-one-condition-out table.

## Exit criteria

- [ ] HUST connector PR merged (or open and passing).
- [ ] Leave-one-condition-out results reported, with faithfulness.
- [ ] Bearing explorer page live.
- [ ] Limitations page updated: only 99 independent recordings; artificial defects; lab rig.

## Risks in this phase

| Risk | What to do |
|---|---|
| Only 99 independent recordings | Report recording-level CIs; never treat windows as independent samples in statistics |
| Bearing geometry missing for some types | Use the dataset paper; if unavailable, estimate fault frequencies from the data and say so |
| Mendeley terms restrict use | Ask in Discord; fall back to OPS-SAT or another CC BY bearing dataset |
| Envelope band choice changes results | Fix it on train only and record it in the config before test |
