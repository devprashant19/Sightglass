# Phase 0 — Setup and verification

| | |
|---|---|
| **Goal** | Prove the whole toolchain runs end to end before writing project code. |
| **Owner** | Both (split below) |
| **When** | Round 1, day 1 |
| **Depends on** | Nothing |
| **Unblocks** | Every other phase |

The biggest risk to the project is OpenTSLM not training on our setup, so that gets tested first. The second biggest is another team already claiming the hydraulic dataset, so that gets checked in the first hour.

---

## 1. Rules and competition check (Aman, first 2 hours)

- [ ] Read the expanded FAQ on the challenge page. Write the answers into `docs/competition-notes.md` in the project repo:
  - required submission contents per round,
  - judging criteria and weights,
  - whether the PR must be merged or only opened,
  - the rule on existing projects and prior work,
  - round lengths and deadlines (with time zone).
- [ ] Search TimeNet's open **and** closed PRs, every page, for: `hydraulic`, `UCI`, `HUST`, `bearing`, `CARE`, `wind`, `SCADA`, `OPS-SAT`.
- [ ] Search the Discord for the same terms.
- [ ] If the hydraulic rig is free: post in Discord that we're onboarding it, with a one-line description and our GitHub handles.
- [ ] If it's taken: switch round 1 to HUST bearings (Phase 8 becomes round 1) and tell the team before anything else starts.

**Output:** `docs/competition-notes.md`, and a decision on the round-1 dataset.

## 2. TimeNet fork (Aman)

- [ ] Fork `OpenTSLM/TimeNet` to the team's GitHub account; clone it.
- [ ] Create a Python 3.11 virtual environment; install TimeNet in editable mode with its dev extras **(verify the install command in its README)**.
- [ ] Run the quickstart. Load one existing dataset (for example HAR-CoT) and print one record: its sources, signals, rates and annotations.
- [ ] On the **unmodified** fork, run and record the result of each check:
  ```bash
  make check <!-- check-docs: ignore -->
  make test
  make test-connectors <!-- check-docs: ignore -->
  make license-check <!-- check-docs: ignore -->
  ```
  **(verify)** the exact target names in the Makefile. If any target fails on the unmodified fork, write down the failure so we don't blame our connector for it later.
- [ ] Read the connector guide and the TimeF format docs end to end. Write a half-page summary in `docs/timenet-notes.md`: the record, source and signal model, how per-signal time axes are declared, how annotations and tasks are declared, how splits are attached, and which splitter classes exist.
- [ ] Find two existing connectors that look most like ours (multi-sensor, multi-rate, labelled per record). Use them as templates in Phase 1.

## 3. OpenTSLM smoke run on Nebius (Teammate)

- [ ] Clone OpenTSLM. Read the README and the training entry point. Note the curriculum stages and which checkpoints are published **(verify names)**.
- [ ] On a Nebius L40S, run one existing training stage (HAR-CoT) for about 50 steps with the Flamingo variant and the Gemma-3 270M backbone.
- [ ] Record in `docs/compute-notes.md`:
  - peak VRAM (`torch.cuda.max_memory_allocated`, and `nvidia-smi` as a check),
  - steps per second and samples per second,
  - time to load the checkpoint,
  - exact package versions (`pip freeze > env-opentslm.txt`).
- [ ] Repeat for Llama-3.2 1B if time allows, to confirm the roughly 20–22 GB VRAM estimate.
- [ ] Run inference on one HAR example from the loaded checkpoint and save the output text. This proves inference works as well as training.

## 4. Nebius infrastructure (Teammate)

- [ ] One L40S VM (48 GB) with a persistent disk (≥ 200 GB) mounted at `/data` for raw data, builds and checkpoints.
- [ ] SSH keys for both team members; no shared passwords.
- [ ] Idle shutdown: a cron job every 10 minutes that shuts the VM down if GPU utilisation has been 0% and no `train.py` / `evaluate.py` process has run for 30 minutes.
  ```bash
  # /usr/local/bin/idle-shutdown.sh (sketch)
  if ! pgrep -f "train.py|evaluate.py|export_site_data.py" >/dev/null \
     && [ "$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)" -eq 0 ]; then
       touch /tmp/idle; find /tmp/idle -mmin +30 | grep -q . && sudo shutdown -h now
  else rm -f /tmp/idle; fi
  ```
- [ ] A job wrapper `scripts/run_and_shutdown.sh <cmd>` that runs a command, syncs `results/` and checkpoints to the persistent disk, then shuts the VM down.
- [ ] Billing alert at 50% and 80% of the voucher.
- [ ] Note in `docs/compute-notes.md` whether preemptible L40S is available in our region and what happens to the disk on preemption.

## 5. Project repo `sightglass` (Teammate, Aman reviews)

- [ ] Create the repo with the structure in [README.md](README.md#repositories).
- [ ] `pyproject.toml`: package `sightglass`, Python 3.11, pinned versions for: `torch`, `numpy`, `pandas`, `pyarrow`, `duckdb`, `scipy`, `scikit-learn`, `lightgbm`, `sktime` (MiniRocket), `pydantic`, `pyyaml`, `fastapi`, `uvicorn`, `matplotlib`, `wandb` or `mlflow`, `pytest`, `ruff`, `mypy`. Add TimeNet and OpenTSLM as git dependencies pinned to a commit SHA.
- [ ] `src/sightglass/utils/`: `config.py` (YAML → pydantic model), `seed.py` (`set_all`), `runs.py` (run id, run folder, git SHA, env dump), `log.py`.
- [ ] Pre-commit: ruff, ruff-format, mypy, end-of-file fixer, large-file block (> 5 MB).
- [ ] GitHub Actions CI: lint, type-check, `pytest -m "not gpu and not slow"` on every push and PR.
- [ ] `Makefile` targets (empty stubs for now): `data`, `rationales`, `baselines`, `train`, `eval`, `export`, `site`, `test`.
- [ ] Branch protection on `main`: one review, CI green.
- [ ] `.gitignore`: `data/`, `checkpoints/`, `wandb/`, `.env`, `web/node_modules/`.

## 6. Experiment tracking (Teammate)

- [ ] Weights & Biases free tier (project `sightglass`), or MLflow on the VM if W&B isn't allowed.
- [ ] Log from the smoke run to prove it works: loss curve, learning rate, VRAM, config.
- [ ] The tracker is for watching runs. The **source of truth is always `results/`**, so the dashboard never depends on the tracker.

---

## Exit criteria

- [ ] An OpenTSLM training step and an inference call run on Nebius, with VRAM and speed recorded.
- [ ] The TimeNet fork's four checks have a recorded baseline result.
- [ ] Both team members can push to `sightglass`, and CI runs on a PR.
- [ ] Round-1 dataset confirmed as free, and announced in Discord.
- [ ] `docs/competition-notes.md`, `docs/timenet-notes.md` and `docs/compute-notes.md` exist.

## Risks in this phase

| Risk | What to do |
|---|---|
| OpenTSLM install fails (CUDA, flash-attention, version conflicts) | Use the exact versions from its README or CI; try the published Docker image if there is one; open an issue with the full traceback |
| L40S not available | Use an H100 for the smoke test only, then switch back |
| TimeNet checks fail on the unmodified fork | Record the failure, check whether upstream CI is also red, and ask in Discord |
| Dataset already claimed | Switch to HUST for round 1; Phase 8 has the plan |
