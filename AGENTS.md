# Sightglass

## What this is

Diagnoses four components of the UCI #447 hydraulic test rig from raw sensor data, and explains each verdict with numbers that a checker recomputes from the signal. Its stance: **no number appears anywhere unless a script computed it, and nothing claims to have run that did not.** The model is LightGBM plus a rule-based explainer; the OpenTSLM fine-tune is built but not trained. How it fits together: [ARCHITECTURE.md](ARCHITECTURE.md).

## Processes and ports

| Process | Entry | Port | Owns |
|---|---|---|---|
| Pipeline | `scripts/*.py`, via `make` | none | Everything in `data/`, `results/`, `web/public/data/` |
| API (optional) | `api/main.py`, `make api` | 8000 on 127.0.0.1 | Live diagnoses of the 329 test cycles |
| Site dev server | `web/`, `make web` | 5173 on localhost (IPv6 `[::1]` on Windows) | The page. Proxies `/api` to 8000 |

The site reads static JSON and calls the API only on a local host or with `?api`.

## Source map

```
connector/.../uci/uci_hydraulic/connector.py   download + SHA-256 + convert + grouped split. The only data entry point
connector/.../hust/, connector/.../care/       SYNTHETIC stand-ins. Do not report results from them as real
src/sightglass/data/loader.py                  reads the build; SIGHTGLASS_SYNTHETIC=1 switches to fake cycles
src/sightglass/physics/hydraulic.py            the 43 features. Used by training, explanation AND checking
src/sightglass/physics/base.py                 HealthyReference.fit_per_component: the ONE reference fit, train only
src/sightglass/rationales/                     clause grammar (format.py) and text (builder.py)
src/sightglass/eval/faithfulness.py            the ONE checker: parse_claims + verify. Do not add a second
src/sightglass/eval/consistency.py             does the evidence support the label (separate from "verified")
src/sightglass/engine.py                       Engine.diagnose: used by the API, the export and evaluate.py
src/sightglass/export/perturb.py               what-if perturbations and LIMITS (the API reads LIMITS)
src/sightglass/tslm/train.py                   full mode raises NotImplementedError on purpose
api/main.py                                    three routes; strict request models
scripts/                                       pipeline steps; scripts/check_no_hardcoded_numbers.py guards web/src
configs/faithfulness.yaml                      PRE-REGISTERED tolerances. Never tune these
configs/physics/hydraulic_links.yaml           written by scripts/analyze_links.py, not by hand
results/                                       written by scripts only; README table is generated from it
web/src/lib/api.ts                             decides live vs precomputed
web/public/data/                               the export; regenerate, never edit
```

## Rules that are easy to break by accident

- **Never type a result number.** Not in `web/src` (the CI number check fails), not in `results/`, not in the README table between `<!-- results:start -->` and `<!-- results:end -->` (regenerate it with `python scripts/make_readme_table.py --write`). Prose pages link to the table instead of copying figures. A number nobody computed is the exact failure this project exists to catch.
- **The test split is sequestered.** Tuning uses `val`. The healthy reference and the links use `train` only. Fitting anything on test, or reading test results to change a tolerance, invalidates every number in the README.
- **The split is grouped by the four-label tuple.** The random split exists only for the leakage ablation. Reporting a random-split score as a result overstates it by about 0.04 mean macro-F1 (`results/ablations.json`).
- **One checker, one extractor.** The checker recomputes values with the same `HydraulicExtractor` the explainer used. A second implementation of a feature would let the two drift, and "verified" would stop meaning anything.
- **Do not change `configs/faithfulness.yaml` to make something pass.** The tolerances were fixed before any test result existed.
- **"Verified" is not "correct".** The engine's claims verify by construction. Accuracy is the label metrics, and evidence quality is consistency. Do not present the 100% as evidence that any model is faithful.
- **Say "not run" when it was not run.** B4, B5, the TSLM, bearings, wind and the pooled model have no results. Code that cannot run raises (`BaselineNotRunError`, `NotImplementedError`) and the reason is recorded. Never replace a raise with a stub that returns plausible output.
- **Synthetic data is labelled.** Synthetic cycles carry `synthetic: true`, the mock export carries `"mock": true` and shows a banner. Keep both flags wherever data flows.
- **`engine.pkl` is a pickle.** Only load one built by `scripts/train_engine.py` in this clone.
- **The site must work with no API.** Every live feature needs a precomputed fallback with a visible label.

## Data model

- `Cycle` (`src/sightglass/data/models.py`): `id` like `hydraulic-01668` (row index in the UCI files), `signals` by sensor name, `labels` for the four components, `meta` with `stable_flag` and `synthetic`.
- `Feature` (`src/sightglass/physics/base.py`): value, unit, sensor, time window.
- A diagnosis (`Engine.diagnose`): `labels`, `confidence`, `rationale`, `paragraphs`, `claims` (stated, true, reference, status), `consistency`, `latency_ms`. The static cycle files and `/api/diagnose` share this shape; `web/src/lib/types.ts` mirrors it.

Label values: cooler 3, 20, 100 (%), valve 73, 80, 90, 100 (%), pump 0, 1, 2, accumulator 90, 100, 115, 130 (bar). Healthy is 100, 100, 0, 130.

## Flows that must keep working

- `/api/diagnose` returns the same shape as `prediction` in `web/public/data/hydraulic/cycles/<id>.json`. The page renders both with one component.
- `scripts/export_site_data.py` writes `schema_version` 2. Changing the shape means changing `web/src/lib/types.ts` in the same change.
- `scripts/make_readme_table.py` rewrites only the marked block of `README.md`.

## Conventions

- Results go through `src/sightglass/utils/runs.py`: one folder per run with `config.yaml`, `env.txt`, `git_sha.txt`, `metrics.json`, `predictions.jsonl`.
- Configs load through `src/sightglass/utils/config.py`, which rejects unknown keys.
- Python line length 100, ruff rules E, F, I, B, C4, UP, Q. mypy is strict on physics, eval, rationales and export.

## Commands

```bash
uv venv --python 3.12 && uv pip sync requirements-lock.txt && uv pip install --no-deps -e .
make test            # must pass; API tests skip without make data + scripts/train_engine.py
make lint            # must pass
cd web && npm ci && npm run typecheck && npm test && npm run build && cd ..
python scripts/check_no_hardcoded_numbers.py   # must pass
```
