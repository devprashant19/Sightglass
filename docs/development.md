# Development

Python for the pipeline and the API, TypeScript for the site. **The pipeline is a chain of scripts, each writing files the next one reads,** and every result file under `results/` comes from one of them. Nothing in `results/`, the README table or the site is edited by hand.

## Setup

```bash
uv venv --python 3.12
uv pip sync requirements-lock.txt   # the exact versions behind the results
uv pip install --no-deps -e .
cd web && npm ci && cd ..           # Node 22
```

Python 3.12 is pinned in `.python-version`. `requirements-lock.txt` holds the exact versions of every package, including the test tools and sktime, and installing from it is what makes the numbers in `results/` reproduce: a fresh resolve of the loosely pinned `pyproject.toml` picked newer libraries and moved the engine's mean macro-F1 in the third decimal, while MiniRocket, the CNN and the majority baseline came out the same. `make setup` runs the same install. The environment is about 1.3 GB, most of it PyTorch.

If you change a dependency, regenerate the lock, rerun the pipeline, and commit both together, so that the results always match the versions that made them.

## The pipeline, in order

| Step | Command | Reads | Writes |
|---|---|---|---|
| 1. Data | `make data` | The UCI zip, downloaded once (about 77 MB) | `data/raw/hydraulic`, `data/build/hydraulic` (labels, splits, one `.npy` per sensor) |
| 2. Links | `make links` | Train split | `configs/physics/hydraulic_links.yaml` |
| 3. Rationales | `make rationales` | Build, links | `data/reference/`, `data/rationales/`, `data/qa/`, `results/checker_validation.json`, `docs/rationale-spotcheck.md` |
| 4. Baselines | `make baselines` | Build | `results/baselines.json`, `results/ablations.json`, `results/runs/` |
| 5. Engine | `make engine` | Build, links | `data/models/engine.pkl`, `results/engine_training.json` |
| 6. Evaluation | `make eval` | Engine, test split, steps 3 and 4 | `results/summary.json`, `results/eval_engine.json`, `results/faithfulness_engine.json`, `results/failures.json` |
| 7. Export | `make export` | Engine, results | `web/public/data/` |
| 8. README table | `make readme` | `results/*.json` | The block between `<!-- results:start -->` and `<!-- results:end -->` in `README.md` |

`make all` runs steps 1 to 8, then the linters and the tests. The raw download and the build take about 1 GB of disk between them. Step 4 is the slowest: the CNN baseline took about a minute per seed on a laptop CPU (`seconds` in `results/baselines.json`).

`make train` is separate: it runs the CPU smoke loop of the TSLM, which writes losses only. The full fine-tune is not wired in. See [`docs/model.md`](model.md#the-tslm-that-is-not-trained).

## Layout

| Path | What |
|---|---|
| `connector/timenet_connectors/datasets/uci/uci_hydraulic/` | Download, SHA-256 check, conversion and the grouped split, with its tests |
| `connector/timenet_connectors/datasets/hust/hust_bearing/`, `connector/timenet_connectors/datasets/care/care_wind/` | Bearing and wind connectors. **Synthetic stand-ins:** they generate fake records with the right shapes |
| `src/sightglass/data/` | `loader.py` reads the build; `models.py` holds `Signal` and `Cycle` |
| `src/sightglass/physics/` | Feature extractors and `HealthyReference`. `hydraulic.py` is the one in use |
| `src/sightglass/rationales/` | The clause grammar and the text builder |
| `src/sightglass/eval/` | The faithfulness checker, the consistency check, the metrics |
| `src/sightglass/baselines/` | B0 to B5. B4 and B5 raise and are recorded as not run |
| `src/sightglass/engine.py` | The engine: features, LightGBM, rationale, check |
| `src/sightglass/export/perturb.py` | The what-if perturbations and their limits |
| `src/sightglass/tslm/` | The OpenTSLM-Flamingo wrapper, prompt builder and training loop |
| `api/main.py` | The live API |
| `scripts/` | The pipeline steps above, and the number check |
| `web/` | The site |
| `configs/` | Tolerances, links, baseline and training configs |

## The suites

| Suite | Command | Needs | Covers |
|---|---|---|---|
| Python, fast | `make test` | Nothing beyond the install | Connector, loader, physics, checker, consistency, utilities, the number check, bearings and wind on synthetic signals |
| Python, API | included in `make test` | `make data` and `make engine` | Health, a real diagnosis whose claims all verify, a perturbation, refusals. **Skipped without the build**, as is one loader test |
| Lint and types | `make lint` | | `ruff check` on all Python, `mypy` on physics, eval, rationales, export, data and the engine |
| Format | `ruff format --check src tests scripts api connector` | | As CI runs it |
| Site | `npm test` and `npm run typecheck` in `web/` | `npm ci` | The rationale splitter, claim chips, default-cycle choice |
| Numbers on the site | `python scripts/check_no_hardcoded_numbers.py` | | No result number typed into `web/src`. `tests/test_number_check.py` proves it catches planted ones |

CI (`.github/workflows/ci.yml`) runs all of these except the API tests, which skip there because CI has no build.

## How to add things

**A physics feature.** Add it to `HydraulicExtractor` in `src/sightglass/physics/hydraulic.py` with a name, unit and time window. If it should be cited as evidence, add it as a candidate in `scripts/analyze_links.py` and rerun steps 2 to 8. A link that does not survive the stratified check is dropped on purpose.

**A baseline.** Implement `fit` and `predict` like `src/sightglass/baselines/majority.py`, register it in `scripts/run_baselines.py`, and rerun steps 4, 6, 7 and 8. A baseline that cannot run raises `BaselineNotRunError` with a reason, and the reason appears in the README table.

**A model whose explanations should be checked.** Produce text in the clause grammar (`docs/eval-protocol.md`), then pass it through `parse_claims` and `verify` in `src/sightglass/eval/faithfulness.py`, as `Engine.diagnose` does. Do not change `configs/faithfulness.yaml` to make a model pass: the tolerances were fixed before any test result existed.

**A number on the site.** Add it to `scripts/export_site_data.py` and read it from the JSON in `web/src`. Typing it into a component fails the number check.

## Before calling something finished

```bash
make lint
ruff format --check src tests scripts api connector
make test
cd web && npm run typecheck && npm test && npm run build && cd ..
python scripts/check_no_hardcoded_numbers.py
```

If a result changed, rerun from the step that produced it to the end, so that `results/`, the README table and `web/public/data/` agree.
