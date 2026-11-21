# Phase 4 — OpenTSLM fine-tuning on Nebius

| | |
|---|---|
| **Goal** | Fine-tune OpenTSLM-Flamingo to output a diagnosis plus a physics-grounded rationale for each cycle, starting from a checkpoint that has already been through OpenTSLM's curriculum. |
| **Owner** | Teammate (Aman reviews configs and runs sanity checks on outputs) |
| **When** | Round 1, days 6–10 |
| **Depends on** | Phase 0 smoke run; Phase 1 loader; Phase 2 rationales and QA |
| **Unblocks** | Phase 5 evaluation, Phase 6 export |

---

## 1. Model choice

Use the **Flamingo** variant. Its memory stays roughly flat as series get longer, while the Soft-Prompt variant's memory grows with length and can pass 60 GB on long inputs (research notes).

| Backbone | VRAM (approx.) | Role |
|---|---|---|
| Gemma-3 270M | 6–7 GB | Fast iteration, debugging, all ablations |
| Llama-3.2 1B | 20–22 GB | **Headline model.** Fits one 48 GB L40S with room for bigger batches |
| Llama-3.2 3B | 61–72 GB | Only if time and credits allow, on an H100 80 GB |

Replace these estimates with the numbers measured in Phase 0.

**Starting checkpoint.** The latest published curriculum checkpoint for each backbone **(verify names and which stage is most general)**. Optional ablation: start from the plain backbone instead, to show what OpenTSLM's pretraining is worth.

---

## 2. Input format (`src/sightglass/tslm/prompt.py`)

### Downsampling

- [ ] The 100 Hz signals (PS1–6, EPS1) have 6,000 points per cycle. Downsample to 10 Hz (600 points) with an anti-aliasing filter (`scipy.signal.decimate`), **after checking that the features the rationales cite survive**: recompute every Phase 2 feature on the downsampled signal and compare with the native one. Pressure rise time and lag are the most at risk; if they drift by more than the faithfulness tolerance, use 20 Hz for PS1 and PS2.
- [ ] FS1–2 stay at 10 Hz; 1 Hz sensors stay at 1 Hz.
- [ ] The native-rate version is kept for evaluation. **Faithfulness is always checked against the native-rate signal**, never the model's input copy.

### Normalisation

- [ ] Per-sensor z-normalisation using **train-split** mean and std, saved to `data/reference/hydraulic_norm.json`.
- [ ] Pass each sensor's mean and std as text before its series, so the model can state values in real units. This matches how OpenTSLM describes series **(verify its convention)**.

### Prompt

```
You are a machine-health assistant for a hydraulic test rig.
The cycle lasts 60 s. Sensors follow, each with its unit, rate and scale.

PS1 pressure (bar), 10 Hz, mean 155.3, std 6.2: <TS>
PS2 pressure (bar), 10 Hz, mean 104.8, std 4.1: <TS>
...
SE efficiency factor (%), 1 Hz, mean 59.1, std 2.0: <TS>

Question: Diagnose this hydraulic cycle.
```

`<TS>` marks where each series goes through the time-series encoder.

### Target

Exactly the Phase 2 joint rationale, with label lines first:

```
Cooler: reduced efficiency. Evidence: TS1 mean temperature 51.4 °C (12% above healthy); ...
Valve: optimal. Evidence: ...
Pump leakage: no leakage. Evidence: ...
Accumulator: slightly reduced. Evidence: PS1 pressure ripple 4.2 bar (31% above healthy); ...
```

- [ ] Training mixes the joint target (≈ 60 %) with QA pairs (≈ 40 %), sampled each epoch.
- [ ] Loss is computed on the answer tokens only.

---

## 3. Training plan

Every run is one YAML config in `configs/train/` and one command:

```bash
python scripts/train.py --config configs/train/hydraulic_flamingo_llama1b.yaml --seed 0
```

| Step | Backbone | Data | Purpose | Pass condition |
|---|---|---|---|---|
| 1. Overfit smoke test | Gemma-270M | 100 train cycles | Prove the pipeline is wired correctly | Training loss near zero; outputs reproduce targets on those 100 cycles |
| 2. Full run | Gemma-270M | All train | Find working settings | Val loss stops improving within 3–5 epochs; val macro-F1 well above B0 |
| 3. Headline | Llama-1B | All train | Main result | Best val macro-F1 + faithfulness; 3 seeds |
| 4. Ablations | Gemma-270M | All train | Explain what matters | See table below |
| 5. Optional | Llama-3B | All train | Scale check | Only if steps 1–4 are done and budget remains |

### Ablations (Gemma-270M, cheap)

| Ablation id | Change | Question it answers |
|---|---|---|
| `no_virtual` | Drop CE, CP, SE from input and rationales | Do virtual sensors leak the cooler label? |
| `label_only` | Target is label lines only, no evidence | Does training on rationales help or hurt accuracy? |
| `gpt4o_rationales` | Targets are GPT-4o-from-plot rationales (on the subset where we have them) | Physics vs GPT-4o rationales as training data |
| `base_backbone` (optional) | Start from the plain backbone, not the curriculum checkpoint | Value of OpenTSLM pretraining |
| `random_split` | Train and test on the random split | How much do random splits inflate scores? (used in Phase 5) |

### Hyperparameters (starting point; tune on val with Gemma only)

| Setting | Start value |
|---|---|
| Optimiser | AdamW, weight decay 0.01 |
| Learning rate | 1e-4 for the encoder/adapter, 2e-5 for the LLM (or LoRA rank 16 on the LLM if full fine-tuning doesn't fit) |
| Schedule | Linear warm-up 3 %, cosine decay |
| Batch | As large as VRAM allows; gradient accumulation to an effective 32 |
| Epochs | 3–5, early stopping on val loss (patience 1) |
| Precision | bf16 |
| Max new tokens at inference | 400 |
| Decoding | Greedy for evaluation (deterministic); temperature 0 |

### Config schema (sketch)

```yaml
run_name: hydraulic_flamingo-llama1b_full
dataset: hydraulic
split: grouped
model:
  variant: flamingo
  backbone: meta-llama/Llama-3.2-1B          # verify id
  init_checkpoint: <opentslm curriculum checkpoint>
  lora: {enabled: false, r: 16, alpha: 32}
input:
  rates_hz: {PS1: 10, PS2: 10, PS3: 10, PS4: 10, PS5: 10, PS6: 10, EPS1: 10, default: native}
  drop_sensors: []
  normalisation: data/reference/hydraulic_norm.json
targets:
  joint_weight: 0.6
  qa_weight: 0.4
  rationales: data/rationales/hydraulic.jsonl
  qa: data/qa/hydraulic.jsonl
train:
  epochs: 5
  lr_encoder: 1.0e-4
  lr_llm: 2.0e-5
  effective_batch: 32
  early_stopping: {metric: val_loss, patience: 1}
  checkpoint_every: epoch
seeds: [0, 1, 2]
output_dir: /data/checkpoints
```

---

## 4. Engineering

- [ ] `src/sightglass/tslm/` wraps OpenTSLM: `build_model(cfg)`, `make_dataset(cfg, split)`, `train(cfg)`, `generate(model, cycles, question)`. Keep OpenTSLM imports inside this package so an API change touches one place.
- [ ] Fixed seeds; deterministic data order per seed.
- [ ] Checkpoint every epoch to `/data/checkpoints/<run_id>/`; **auto-resume** from the latest checkpoint if the job restarts (needed for preemptible VMs).
- [ ] Log loss, learning rate, VRAM and val metrics to the tracker every N steps.
- [ ] At the end of training: run greedy generation on **val**, write `predictions_val.jsonl`, compute macro-F1 and a quick faithfulness score, then shut the VM down via `run_and_shutdown.sh`.
- [ ] Never generate on test inside `train.py`. Test inference happens only in `scripts/evaluate.py` (Phase 5), once per final model.

## 5. Sanity checks on outputs (Aman)

After each full run, read 20 val outputs by hand:

- [ ] Does every output have four label lines in the expected format?
- [ ] Do the evidence clauses follow the canonical grammar?
- [ ] Are the cited sensors ones that actually exist and are linked to that component?
- [ ] Are the numbers in a plausible range for that sensor?
- [ ] Record findings in `docs/training-log.md`, one entry per run. <!-- check-docs: ignore -->

---

## Exit criteria

- [ ] A Llama-1B checkpoint (3 seeds) with logged training curves, reproducible from one command and one config.
- [ ] Gemma-270M ablation checkpoints for every ablation in the table.
- [ ] `docs/training-log.md` with settings, VRAM, time, cost and sanity-check notes for each run. <!-- check-docs: ignore -->

## Risks in this phase

| Risk | What to do |
|---|---|
| OpenTSLM can't take 17 series in one prompt | Group sensors per source into fewer series, or check whether the encoder accepts multivariate input **(verify)** |
| Outputs break the evidence grammar | Increase joint-target weight; add a format check during val; constrained decoding as a last resort |
| Llama-1B out of memory | Gradient checkpointing, smaller micro-batch, LoRA on the LLM |
| Training is slower than budgeted | Use Gemma results as the headline and Llama-1B for one seed; say so in the README |
| Preemption mid-run | Auto-resume from epoch checkpoints |
