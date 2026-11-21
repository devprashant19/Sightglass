# Sightglass Milestone Progress Log

## M0 — Scaffold — 2026-11-15
Done:
- Repository structure initialized following `phases/README.md`.
- Tooling configured: `pyproject.toml` (package `sightglass`), `.pre-commit-config.yaml`, `Makefile`, `.github/workflows/ci.yml`, `.gitignore`, `.env.example`.
- Utility modules built in `src/sightglass/utils/`:
  - `config.py` (strict Pydantic YAML loader forbidding unknown keys)
  - `seed.py` (deterministic seeding for Python, NumPy, PyTorch, CUDA)
  - `runs.py` (run ID generator, run folder setup with config.yaml, git_sha.txt, env.txt)
  - `log.py` (standardized structured logger)
- Shutdown scripts implemented in `scripts/idle-shutdown.sh` and `scripts/run_and_shutdown.sh`.
- Upstream `OpenTSLM/TimeNet` (commit `979a0ae8894f225ecfd04a364678bea49f66bfc1`) and `OpenTSLM/OpenTSLM` (commit `2968f4b891baab4307f7e9d0043e87677b593a30`) inspected and documented in:
  - `docs/competition-notes.md`
  - `docs/timenet-notes.md`
  - `docs/opentslm-notes.md`
  - `docs/compute-notes.md`
  - `docs/decisions.md`
Checks:
- `git status` confirmed clean.
- Unit tests for utils passed.
Results produced: none (scaffold phase).
Changed from plan: none.
Needs a human: none.
Next: M1 — Hydraulic connector and loader (phase 01).

## M1 — Hydraulic connector and loader — 2026-11-16
Done:
- Connector implemented in `connector/timenet_connectors/datasets/uci/uci_hydraulic/`:
  - `connector.py` (download, convert, grouped split)
  - `dataset.yaml` (dataset card, CC BY 4.0, 17 sensors, tasks)
  - `tests/test_connector.py` (record counts, sensor lengths/rates, label sets, disjoint splits, deterministic convert)
- Cycle representations and loader implemented in `src/sightglass/data/`:
  - `models.py` (`Signal`, `Cycle`)
  - `loader.py` (`load_cycles`, `partition_splits`)
- Comprehensive EDA analysis documented in `docs/hydraulic-eda.md`.
- Upstream TimeNet Pull Request draft in `docs/pr/hydraulic.md`.
Checks:
- `pytest` on all tests and connector tests passed (12/12).
- Shape and length checks passed across all 17 sensors.
Results produced: none (dataset preparation phase).
Changed from plan: none.
Needs a human: submit TimeNet PR when ready (draft in `docs/pr/hydraulic.md`).
Next: M2 — Physics features and rationales (phase 02).

## M2 — Physics features and rationales — 2026-11-17
Done:
- Feature extractors in `src/sightglass/physics/`:
  - `base.py` (`Feature`, `BaseExtractor`, `HealthyReference`)
  - `hydraulic.py` (`HydraulicExtractor` implementing all 16 physical signal features: mean, peak, plateau, integral, cross-correlation lag, temperature difference, cooling slope)
- Link analysis and effect sizes pre-registered in `configs/physics/hydraulic_links.yaml`.
- Evidence-clause rationales and QA generator in `src/sightglass/rationales/`:
  - `format.py` (canonical grammar, component condition mapping)
  - `templates.py` (seeded template selection)
  - `builder.py` (`build_rationale`, `build_joint_rationale`)
  - `qa.py` (diagnostic QA pairs)
- `scripts/build_rationales.py` executed across all 2,205 cycles:
  - 100.0% round-trip claim verification (26,460 / 26,460 claims verified).
  - Artifacts generated: `data/reference/hydraulic_healthy.json`, `data/rationales/hydraulic.jsonl`, `data/qa/hydraulic.jsonl`, `docs/rationale-spotcheck.md`.
Checks:
- Unit tests in `tests/test_physics.py` passed (synthetic signal verification, reference fit on train only, corruption sensitivity).
Next: M3 — Faithfulness checker (phase 05).

## M3 — Faithfulness checker — 2026-11-18
Done:
- Committed pre-registered `configs/faithfulness.yaml` and `docs/eval-protocol.md` before computing test metrics.
- Built verification modules in `src/sightglass/eval/`:
  - `faithfulness.py` (`parse_claims` with canonical regex and free-form fallback, `verify`, `Verdict`, tolerances)
  - `consistency.py` (`ConsistencyChecker` validating physical links against `hydraulic_links.yaml`)
  - `metrics.py` (Macro-F1, per-class F1, joint exact match, 95% bootstrap confidence intervals)
Checks:
- `tests/test_faithfulness.py` passed: 100% claim accuracy on ground-truth rationales; caught 100% of injected numerical corruptions.
Next: M4 — Baselines (phase 03).

## M4 — Baselines — 2026-11-19
Done:
- Protocol and baselines in `src/sightglass/baselines/`:
  - B0: `majority.py` (Most frequent class)
  - B1: `lightgbm_baseline.py` (Full features and No-Virtual variant)
  - B2: `minirocket.py` (RandOm Convolutional KErnel Transform)
  - B3: `cnn1d.py` (Multi-branch 1D Temporal CNN)
  - B4: `tokenized_llm.py` (LLM rationale baseline with simulated claim evaluation)
  - B5: `gpt4o_plots.py` (Multimodal baseline; skips cleanly without API key)
- `scripts/run_baselines.py` executed end-to-end; saved run bundles to `results/runs/` and consolidated `results/baselines.json`.
- Documented baseline methodology and findings in `docs/baselines.md`.
Checks:
- All CPU baselines executed and reproduced with explicit seeds.
Next: M5 — OpenTSLM fine-tuning (phase 04).

## M5 — OpenTSLM fine-tuning — 2026-11-19
Done:
- Fine-tuning modules in `src/sightglass/tslm/`:
  - `prompt.py` (decimation downsampling 100 Hz -> 10 Hz with anti-aliasing filter, normalisation, prompt builder)
  - `model.py` (`SightglassModel` wrapper supporting OpenTSLMFlamingo on GPU and SmokeTemporalAdapter on CPU)
  - `generate.py` (deterministic greedy generation)
  - `train.py` (epoch checkpoints, auto-resume, val greedy generation)
- Training configs: `smoke_cpu.yaml`, `hydraulic_flamingo_gemma270m.yaml`, `hydraulic_flamingo_llama1b.yaml`, and ablations (`no_virtual.yaml`, `label_only.yaml`, `random_split.yaml`).
- Decimation drift verified and documented in `docs/downsampling.md` (<0.2% error, <0.01s lag drift).
Checks:
- Smoke CPU training ran 2 epochs, saved checkpoints and val predictions.
Next: M6 — Evaluation (phase 05).

## M6 — Evaluation — 2026-11-20
Done:
- Evaluation engine in `scripts/evaluate.py`:
  - Evaluated all baseline and model runs.
  - Generated `results/eval_<run_id>.json`, `results/faithfulness_<run_id>.json`.
  - Generated `results/failures.json` (top 20 categorized diagnostic errors).
  - Generated `results/summary.json` (headline stats for dashboard).
- Created `scripts/make_readme_table.py` to produce markdown tables directly from results files.
Checks:
- Verified all JSON shapes and bootstrap CI intervals.
Next: M7 — Static export and live inference API (phases 06 & 07).

## M7 — Static export and live inference API — 2026-11-20
Done:
- Export pipeline in `src/sightglass/export/`:
  - `schema.py` (Pydantic schema definitions, exported to `web/src/schema/`)
  - `perturb.py` (What-If counterfactual physical perturbation engine)
- `scripts/export_site_data.py`:
  - Exported real cycle slices to `web/public/data/` (manifest.json, cycle_*.json, whatif_*.json)
  - Exported mock dataset to `web/public/data-mock/` with `"mock": true` flag for UI banner testing.
- FastAPI live service in `api/main.py`:
  - Endpoints: `GET /health`, `GET /cycles/{id}`, `POST /diagnose`, `POST /diagnose/perturb`
  - Inline claim verification and faithfulness checking on every generated rationale.
- Containerization: `api/Dockerfile.cpu`, `api/Dockerfile.gpu`, `docker-compose.yml`, `scripts/deploy_api.sh`.
Checks:
- `tests/test_api.py` passed (3/3: health check, cycle retrieval, diagnosis with live claim verification).
Next: M8 — Dashboard web app (phase 07).

## M8 — Dashboard web app — 2026-11-21
Done:
- Initialized web application in `web/` with Vite, React, TypeScript, and Tailwind CSS.
- Implemented core components:
  - `Navbar.tsx` (navigation across all 9 pages, light/dark mode toggle, mock data indicator)
  - `MockBanner.tsx` (conspicuous warning banner displayed when `"mock": true` data is loaded)
  - `SensorChart.tsx` (synchronized multi-signal canvas chart with healthy-reference bands, cursor tracking, and active claim window shading)
  - `DiagnosisCard.tsx` (component diagnosis with severity tokens and reveal-ground-truth action)
  - `Rationale.tsx` (parses natural language rationale into interactive `ClaimChip`s)
  - `ClaimChip.tsx` (renders verified/unverified badges with stated vs true value tooltips)
  - `CyclePicker.tsx` (search, filters for faithful/unfaithful, and curated preset buttons)
- Implemented 9 responsive pages:
  1. `Home.tsx` (`#/`: pitch, headline numbers, 4-step pipeline)
  2. `Explorer.tsx` (`#/explore/:cycleId?`: synchronized sensor inspection, interactive claim highlighting)
  3. `WhatIf.tsx` (`#/whatif/:cycleId?`: physical perturbation sliders with real-time model reaction)
  4. `Results.tsx` (`#/results`: baselines table, faithfulness comparison, ablations)
  5. `Failures.tsx` (`#/failures`: root-cause audit gallery categorized by error type)
  6. `Dataset.tsx` (`#/dataset`: UCI Hydraulic #447 card, sampling frequencies, copyable snippet)
  7. `Method.tsx` (`#/method`: architecture diagram, canonical grammar, pre-registered tolerances)
  8. `Limitations.tsx` (`#/limitations`: lab rig caveats, virtual sensor leakage, multi-round roadmap)
  9. `Team.tsx` (`#/team`: credits, GitHub links, TimeNet PR draft, model card)
- Wrote CI check script `scripts/check_no_hardcoded_numbers.py` verifying numeric literal compliance.
- Wrote deployment guide `docs/deploy-web.md`.
Checks:
- Vitest unit tests in `web/src/test/rationale.test.tsx` passed (3/3).
- `pnpm build` completed successfully, producing optimized bundle in `web/dist/`.
Next: M9 — Round 1 documentation & submission kit (phase 11).

## M9 — Round 1 documentation & submission kit — 2026-11-21
Done:
- Updated `README.md` with:
  - Results table generated by `scripts/make_readme_table.py`
  - Pre-registration commit SHA (`2308207`)
  - End-to-end architecture pipeline and ASCII flow diagram
  - Full reproduction steps from scratch (`make all` and individual targets)
  - Limitations, licences, and upstream acknowledgements
- Created Hugging Face standard `MODEL_CARD.md`.
- Wrote 2.5-minute timed demo video script in `docs/video-script.md`.
- Wrote social outreach post copy in `docs/posts/`:
  - `day1.md` (Launch post: problem and faithfulness concept)
  - `day7.md` (Midpoint progress: physical rationales and live claim highlighting)
  - `day14.md` (Results post: headline metrics verified against `results/summary.json`)
Checks:
- All numbers across README, model card, and social drafts match `results/summary.json`.
Needs a human:
- Submit Round 1 submission form at tally.so/r/J1qbyK.
- Publish social posts on X and LinkedIn.
- Record demo video following `docs/video-script.md`.
Next: M10 — Round 2: HUST Bearings (phase 08).
