# Build prompt — Sightglass, complete project

Paste everything below the line into a coding agent (for example Claude Code) started in an empty folder that will become the `sightglass` repo. Copy the `phases/` folder into that repo first, so the agent can read it.

---

You are building **Sightglass**, a machine-health time-series language model (TSLM) for the TimeNet hackathon. Sightglass diagnoses industrial machine faults from raw sensor data and explains each diagnosis with numbers that are checked against the signal. You will build the whole project end to end: dataset connector, physics feature extraction, rationale generation, baselines, OpenTSLM fine-tuning, evaluation with a faithfulness checker, static export, inference API, and a public dashboard. Later you will extend it to two more machine types and a pooled model.

The name is **Sightglass** everywhere: the repo is `sightglass`, the Python package is `sightglass` (`src/sightglass/`), env vars use the prefix `SIGHTGLASS_`, the tracker project is `sightglass`, the site title is "Sightglass". Don't use any other project name in code, docs, configs or UI.

## 1. Source of truth

The detailed plan is in `phases/`. Read **all** of it before writing code, in this order:

1. `phases/README.md` — principles, architecture, repo layout, conventions, timeline, risks, definition of done.
2. `phases/00-setup.md` to `phases/07-dashboard.md` — round 1 (hydraulic test rig).
3. `phases/08-round2-bearings.md`, `phases/09-round3-wind.md`, `phases/10-pooled-model.md` — later rounds.
4. `phases/11-submission-and-outreach.md` — README, model card, video, posts.

The phase files define the interfaces (dataclasses, function signatures, file paths, JSON shapes, config fields). Implement them as written. If you find a real reason to change an interface (an external API works differently, a design flaw), make the change, update the phase file in the same commit, and list it in your progress report. Don't drift silently.

## 2. Non-negotiable rules

1. **Never fabricate results.** Every metric, table, chart value, README number and dashboard number must come from a file in `results/` written by a script from a real run. If a run hasn't happened (for example because it needs a GPU you don't have), leave the result missing and say so. Never type a plausible number.
2. **Mock data is labelled as mock.** The dashboard may run on `web/public/data-mock/` until real exports exist. Mock files carry `"mock": true`, and the UI shows a visible "Mock data" banner whenever any loaded file has it.
3. **Verify external APIs before use.** TimeNet and OpenTSLM names in the plan come from research notes and may be out of date. Before writing code against either, read their current README, docs and source (clone them; pin a commit SHA). Every place the plan says **(verify)** needs this. Record what you found in `docs/timenet-notes.md` and `docs/opentslm-notes.md`. Do the same for sktime, LightGBM, uPlot and any other library whose API you're not certain of: check the installed version's docs.
4. **Split by group, never by random window.** The test split is never used for tuning anything: hyperparameters, templates, tolerances, thresholds or prompt wording.
5. **Pre-register evaluation rules.** `configs/faithfulness.yaml` and `docs/eval-protocol.md` must be committed before any test-split metric is computed. Record that commit SHA in the README.
6. **Reproducibility.** Every run is one YAML config + one command + one seed, and writes `results/runs/<run_id>/` with `config.yaml`, `metrics.json`, `predictions.jsonl`, `git_sha.txt`, `env.txt`.
7. **No secrets in the repo.** API keys (OpenAI for the GPT-4o baseline, W&B, Hugging Face) come from environment variables or a gitignored `.env`. Add `.env.example` with names only.
8. **Licences.** Record every dataset's and backbone's licence in its dataset card, the model card and the README. Don't commit raw dataset files to the repo.
9. **Don't do human-only actions.** You must not open PRs on other people's repos, post to Discord, X or LinkedIn, submit forms, spend cloud credits, or accept licence terms on the team's behalf. Prepare everything for these steps (PR description, post drafts, deploy scripts), then list them under "Needs a human" in your report and continue with work that doesn't depend on them.

## 3. Environment and tooling

- Python 3.11, `uv` (or `pip` + `venv`) with a pinned lockfile. Node 20 LTS + pnpm for `web/`.
- Package layout as in `phases/README.md` → "Repositories". `pyproject.toml` uses a `src/` layout.
- Quality: ruff (lint + format), mypy (strict on `src/sightglass/physics`, `eval`, `rationales`, `export`), pytest with markers `slow` and `gpu`. Pre-commit for ruff, mypy, a 5 MB file-size block.
- CI (GitHub Actions): lint, type-check, `pytest -m "not slow and not gpu"`, web lint + type-check + Vitest, JSON Schema validation of mock data.
- `Makefile` targets: `setup`, `data`, `rationales`, `baselines`, `train`, `eval`, `export`, `site`, `api`, `test`, `lint`, `all`. Each target prints what it runs.
- **GPU work.** You may be on a machine without a GPU. Write all training and inference code so it runs on CPU with a tiny smoke config (`configs/train/smoke_cpu.yaml`: Gemma-3 270M or a tiny stand-in, 8 cycles, 2 steps) that CI can run under the `slow` marker. Full runs are launched on Nebius by a human with `scripts/run_and_shutdown.sh`. If a GPU is available to you, run the real configs.

## 4. Build order and acceptance checks

Work milestone by milestone. Finish each one, run its checks, commit, and write a short progress note in `docs/progress.md` before moving on. Commit small and often, with clear messages (`connector: add convert() for UCI hydraulic`).

### M0 — Scaffold (phase 00)
- Create the repo structure, `pyproject.toml`, `Makefile`, pre-commit, CI, `src/sightglass/utils/` (`config.py` with pydantic models, `seed.py`, `runs.py`, `log.py`), `.gitignore`, `.env.example`, `docs/`.
- Clone TimeNet and OpenTSLM into `third_party/` (gitignored) at pinned SHAs; write the two notes files described in rule 3.
- Write `scripts/idle-shutdown.sh` and `scripts/run_and_shutdown.sh` (not executed by you).
- **Check:** `make lint test` passes; CI config is valid; notes files exist and answer: how records, sources, signals, per-signal time axes, annotations, tasks and splits are declared in TimeNet; which make targets exist; how OpenTSLM-Flamingo is built, which checkpoints are published, how multiple series are passed in one prompt, and how training is launched.

### M1 — Hydraulic connector and loader (phase 01)
- Download the UCI hydraulic dataset (#447), compute and pin its SHA-256.
- EDA notebook and `docs/hydraulic-eda.md`: confirm sensor shapes, label meanings (including what each stable-flag value means), class counts, label sequence, neighbour autocorrelation, virtual-sensor leakage check. Decide the split with the decision table in phase 01 and record why.
- Connector in a TimeNet fork layout under `connector/timenet_connectors/datasets/<org>/uci_hydraulic/` inside this repo (so it can be copied into the fork): `connector.py`, `dataset.yaml`, `tests/`. Grouped split plus a random split for the leakage check.
- `src/sightglass/data/`: `Signal`, `Cycle`, `load_cycles()` reading through TimeNet's own loader, with an `.npz` cache keyed by build hash.
- Draft the PR description in `docs/pr/hydraulic.md` with the sample plot.
- **Check:** all connector tests in phase 01 pass (2,205 records, lengths, no NaNs, label sets, disjoint splits, every class in train, deterministic convert); TimeNet's make targets pass on the connector if you can run them; `load_cycles("hydraulic", "train")` returns cycles with correct shapes.

### M2 — Physics features and rationales (phase 02)
- `physics/base.py`, `physics/hydraulic.py` with every feature in the table; `HealthyReference` fit on train only.
- Link analysis → `configs/physics/hydraulic_links.yaml` with effect sizes; thresholds written in the file header before computing them.
- `rationales/format.py`, `templates.py`, `builder.py`, `qa.py`; canonical evidence-clause grammar exactly as in phase 02; seeded template choice.
- `scripts/build_rationales.py` → `data/rationales/hydraulic.jsonl`, `data/qa/hydraulic.jsonl`.
- **Check:** extractor unit tests on synthetic signals; round-trip test (build → parse → verify) at 100 %; corruption test catches every changed number; reference built from train ids only. Write 50 random rationales to `docs/rationale-spotcheck.md` for a human to review.

### M3 — Faithfulness checker (phase 05, sections 0 and 2)
Build this **before** any model output exists, against M2's rationales.
- Commit `configs/faithfulness.yaml` and `docs/eval-protocol.md` first (rule 5).
- `eval/faithfulness.py` (`parse_claims`, `verify`, `Verdict`), `eval/consistency.py`, `eval/metrics.py` with bootstrap CIs.
- **Check:** parser tests for every template variant and edge case; ground-truth rationales score 100 % claim accuracy; corrupted ones are caught; metric functions match `sklearn` on small examples.

### M4 — Baselines (phase 03)
- `baselines/` with the shared `Baseline` protocol; B0 majority, B1 LightGBM (with and without virtual features), B2 MiniRocket, B3 1D-CNN, B4 tokenized-text LLM, B5 GPT-4o on plots (200-cycle stratified test sample; needs `OPENAI_API_KEY`; skip with a clear message if absent).
- `scripts/run_baselines.py` → run folders + `results/baselines.json`.
- **Check:** B0–B2 run end to end for real on CPU and their results are in `results/baselines.json`; B3/B4 run on the smoke config on CPU and have full configs ready for GPU; re-running B0–B2 with the same seed reproduces metrics exactly.

### M5 — OpenTSLM fine-tuning (phase 04)
- `tslm/prompt.py` (downsampling with the feature-drift check, train-split normalisation, prompt and target building exactly as in phase 04), `tslm/model.py`, `tslm/train.py`, `tslm/generate.py`. Keep every OpenTSLM import inside `src/sightglass/tslm/`.
- Configs: `smoke_cpu.yaml`, `hydraulic_flamingo_gemma270m.yaml`, `hydraulic_flamingo_llama1b.yaml`, and one per ablation (`no_virtual`, `label_only`, `gpt4o_rationales`, `base_backbone`, `random_split`).
- Epoch checkpoints, auto-resume, tracker logging, val-only generation at the end of training.
- **Check:** the downsampling drift report is written to `docs/downsampling.md`; the smoke config trains and generates on CPU; the 100-cycle overfit test config exists and, if you have a GPU, passes (loss near zero, outputs reproduce targets). List the full GPU runs to launch under "Needs a human", with exact commands and estimated hours.

### M6 — Evaluation (phase 05, sections 1, 3–5)
- `scripts/evaluate.py` (generate once with `--generate`, then score from saved predictions), `scripts/make_readme_table.py`.
- Leakage and robustness checks, failure analysis → `results/failures.json` (tags computed automatically; the written analysis left as `TODO(human)` fields).
- `results/summary.json` derived from the other result files.
- **Check:** `make eval` reruns every evaluation from saved predictions without a GPU; every file in the outputs table of phase 05 exists for every run that has predictions; missing runs are listed, not faked.

### M7 — Export and API (phase 06)
- `export/schema.py` (pydantic models → JSON Schemas in `web/src/schema/`), `export/site.py`, `export/perturb.py`, `scripts/export_site_data.py`.
- Hand-built mock export in `web/public/data-mock/` with `"mock": true`, matching the schema exactly, so M8 can start in parallel.
- `api/` FastAPI app with the four endpoints, validation, inference-time faithfulness, rate limit, CORS, env config, Dockerfiles (GPU and CPU), `docker-compose.yml`, `scripts/deploy_api.sh`.
- **Check:** export validates against the schemas; `rationale[span[0]:span[1]]` contains the cited sensor for every claim; API tests pass with a stub model; `/diagnose` on a stored cycle gives the same claims as the export.

### M8 — Dashboard (phase 07)
- `web/` with Vite + React + TypeScript (strict), Tailwind, uPlot, Recharts, hash routing; types generated from the JSON Schemas.
- All nine pages. Build the explorer first and to the spec in phase 07 section 4 (synced sensor charts, healthy bands, `ClaimChip` hover/tap highlighting the sensor and time window, ✓/✗ icons with text, reveal true label, shareable URLs, keyboard navigation, phone layout).
- Mock-data banner (rule 2). Light and dark mode. Open Graph tags.
- CI check that blocks hard-coded numeric literals in JSX text outside an allow-list.
- **Check:** Vitest and Playwright tests from phase 07 pass at 1280×800 and 390×844; Lighthouse performance ≥ 85 and accessibility ≥ 95 on home and explorer; `pnpm build` output deploys as static files (write `docs/deploy-web.md` for Vercel and GitHub Pages).

### M9 — Round 1 docs and launch kit (phase 11)
- README following phase 11's structure, with the results table generated from `results/` (or "pending run" cells).
- `MODEL_CARD.md`, `docs/pr/hydraulic.md` final, `docs/video-script.md`, `docs/posts/day1.md`, `day7.md`, `day14.md` (every number pulled from `results/summary.json` by a small script, or a placeholder if absent).
- **Check:** the round-1 definition-of-done list in `phases/README.md` is copied into `docs/progress.md` with each item marked done, blocked (with reason) or needs a human.

### M10 — Round 2: HUST bearings (phase 08)
Start only after M1–M9 pass. Add `connector/.../hust_bearing/`, `data/windowing.py`, `physics/bearing.py` (fault-frequency formulas, envelope spectrum, kurtosis, crest factor), new clause forms in the rationale grammar and parser, leave-one-condition-out evaluation, window- and recording-level metrics, and the bearing explorer page with fault-frequency markers.
- **Check:** synthetic-impulse test finds BPFO; splits are grouped by recording; the parser and verifier handle order-match claims; bearing page renders from mock and real exports.

### M11 — Round 3: CARE wind turbines (phase 09)
Start only after M10. Before any connector work, write the ShareAlike question and both fallback paths into `docs/competition-notes.md`, and mark the licence decision as "Needs a human". Then build `physics/wind.py` (normal-behaviour models fit on normal periods of train turbines, residual features), early-warning windows and labels, event-level metrics (detection rate, warning lead time, false alarms per turbine-month), and the wind-farm page.
- **Check:** normal-behaviour residuals on held-out normal periods are centred near zero; splits are by turbine or event; lead-time metric has unit tests on hand-made event timelines.

### M12 — Pooled model (phase 10)
Pooled training config with temperature-scaled task sampling, pooled-vs-single evaluation, leave-one-dataset-out ablation config, `results/pooled.json`, cross-machine page, final README and model card, `v1.0` tag.

## 5. Coding standards

- Small, pure, typed functions in `physics`, `rationales` and `eval`; no global state; no randomness without an explicit seeded `np.random.Generator`.
- The same extractor code builds rationales, verifies claims and checks live answers. Never duplicate feature logic.
- Configs are validated pydantic models; unknown keys are an error.
- Log with `sightglass.utils.log`, not `print`, outside scripts.
- Fail loudly with clear messages on shape mismatches, missing files, schema violations and wrong licences.
- Tests sit next to what they test in `tests/<package>/`. Use small fixtures; never download full datasets in CI.
- Docstrings say what a function returns and its units.

## 6. When you're unsure

- If an external API differs from the plan, follow the real API, document it, and adapt the plan file.
- If a decision is the team's to make (licence interpretation, which split when the EDA is ambiguous, spending credits, publishing), stop on that item, write the options and your recommendation in `docs/decisions.md`, and continue with other work.
- If a result looks too good (for example a baseline near 100 % on every component), check for leakage before reporting it: split, normalisation fitted on all data, virtual sensors, neighbour cycles.

## 7. Reporting

At the end of each milestone, append to `docs/progress.md`:

```
## M<n> — <name> — <date>
Done: <what was built, with file paths>
Checks: <each acceptance check, pass/fail, with the command run>
Results produced: <files in results/ created or updated, or "none">
Changed from plan: <interface or design changes, and which phase file was updated>
Needs a human: <exact actions, commands, links, estimated time/cost>
Next: <the next milestone>
```

Your final message after each working session summarises the latest entries: what works, what was verified and how, what's blocked, and the exact next steps for the team.
