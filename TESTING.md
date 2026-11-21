# Testing Sightglass

Written for judges and reviewers who want to know whether this works without downloading 77 MB of sensor data or training anything.

> **For a submission form.** Sightglass diagnoses four components of the UCI #447 hydraulic test rig from raw sensor data, and a checker recomputes every number in each explanation from the signal. A minute: open the site (once GitHub Pages is enabled) or run `make web` locally, and press "Run a diagnosis". A few minutes more: run the Python and web tests. Longer: rebuild the data and the engine, and run the live API. Results, and what has not been run, are in the README.

**There are four ways in, from least effort to most.**

| Level | Effort | What you see | Needs |
|---|---|---|---|
| **1. The site** | A minute | A real test cycle diagnosed, every claim marked verified or not, the what-if lab, the results table | A browser, once Pages is enabled. Until then Node 22, and the site runs locally |
| **2. The tests** | The Python suite ran in about 25 s; installing takes longer | Connector, physics, checker and site tests passing | Python 3.12, uv, Node 22 |
| **3. The live engine** | Not timed here: the download and conversion take most of it | The API diagnosing a cycle in tens of milliseconds, and refusing bad input | Level 2, plus about 1 GB of disk |
| **4. Everything** | Longer: each baseline takes up to a minute per seed | Every file in `results/` regenerated | Level 3 |

Levels 1 to 3 were run on a Windows 11 laptop. Timings from a fresh clone are in the reproduction section below.

---

## Level 1: the site

Once Pages is enabled the site is at https://devprashant19.github.io/Sightglass/. Until then, run it locally:

```bash
git clone https://github.com/devprashant19/Sightglass.git
cd Sightglass
make web            # npm install, then http://localhost:5173
```

On Windows without `make`: `cd web`, `npm install`, `npm run dev`.

Then open **http://localhost:5173/?cycle=hydraulic-00253&run**. That runs one test cycle and scrolls to the result.

**If you only have a minute, look at this.** Cycle 253 has three of four parts right: the cooler and the valve are correct, and the pump is called *severe* leakage where the rig recorded *weak*. All nine numbers in its explanation still verify against the signal. That is the distinction the project is built around: a verified number is not a correct diagnosis, and the page shows both.

Then scroll to the **what-if lab**, keep "Reduce flow", and move the slider. A healthy cycle with its flow cut by 5% is already called a leaking pump. Choose "Raise temperature": warming the oil by 2 °C changes the *accumulator* verdict. That is a shortcut the model learned, shown rather than hidden.

Every result here says **Precomputed**: it is the same engine, run ahead of time and stored in `web/public/data/`.

---

## Level 2: the tests

### What you need

Python 3.12 with `uv`, and Node 22. You do not need the dataset, a GPU or any key.

```bash
uv venv --python 3.12
uv pip sync requirements-lock.txt   # the exact versions behind the results
uv pip install --no-deps -e .
make test                                   # Python
cd web && npm ci && npm test && cd ..       # the site
python scripts/check_no_hardcoded_numbers.py
```

Without the dataset build, the four API tests and one loader test skip, and say why. Everything else runs on synthetic fixtures with known answers: the clause parser, the round trip and corruption of claims, the consistency rule, the grouped split, the reference fitted on healthy train cycles only.

The last command checks that no result number is typed into the site. `tests/test_number_check.py` plants numbers in a copy and checks that it catches them.

---

## Level 3: the live engine

```bash
make data                          # downloads UCI #447 (about 77 MB), checks its SHA-256, builds data/build/hydraulic
python scripts/train_engine.py     # data/models/engine.pkl
make test                          # now the API tests run too
make api                           # 127.0.0.1:8000
make web                           # in a second terminal
```

The status line under the hero now says **Live engine ready**, and a diagnosis says **Live**, with its time. One measured live diagnosis took about 60 ms.

### Five minutes that show the point

1. **Ask about a healthy cycle.**
   ```bash
   curl -s -X POST http://127.0.0.1:8000/api/diagnose -H "Content-Type: application/json" -d '{"cycle_id":"hydraulic-01668"}'
   ```
   All four parts come back healthy, and every entry in `claims` has `"status": "verified"`, with the stated value beside the recomputed one.
2. **Break it.** Send `"perturbations":[{"type":"flow","amount":-15}]` with the same id. The pump label changes to `weak leakage`, and its evidence now reads `FS1 mean volume flow 5.70 l/min (13% below healthy)`. It still verifies, because the checker recomputes it from the perturbed signal.
3. **Try to make it misbehave.** An amount of `99` for flow gets 422 with the allowed range. A cycle from the training split gets 404. An extra field gets 422. These are the refusals the API tests check.
4. **Read the checker's own test.** `results/checker_validation.json` holds the result of moving 1,000 stated values by 20% and flipping 529 directions in reference explanations. It is what makes "verified" mean something.

---

## Level 4: everything

```bash
make all
```

This reruns the links, the reference rationales and the checker validation, all four baselines with their seeds, the engine, the evaluation, the export and the README table, then the linters and the tests. Compare `results/` with the committed copy: the grouped split and the seeds are fixed, so the numbers should match.

---

## Verifying it rather than taking our word for it

The results, and the command behind each, are in the [README's verified table](README.md#what-is-verified-and-what-is-not). The run folders under `results/runs/` hold each run's config, environment, predictions and metrics.

## Reproduction from a fresh clone

Every committed result was regenerated from nothing in a fresh clone, on Windows 11 with Python 3.12, and compared with what is committed. Each step below ran in order in that clone; the time is what it took there.

| Step | Command | What it showed | Time |
|---|---|---|---|
| Install | `uv venv --python 3.12`, `uv pip sync requirements-lock.txt`, `uv pip install --no-deps -e .` | The pinned environment installs from scratch | 70 s |
| Data | `python scripts/prepare_data.py` | Real download; `2205 cycles, sha256 24128aad…af1f2` | 36 s |
| Links | `python scripts/analyze_links.py` | `configs/physics/hydraulic_links.yaml` regenerated byte for byte | 19 s |
| Rationales | `python scripts/build_rationales.py` | `Round trip: 17883/17883 claims verified` | 32 s |
| Baselines | `python scripts/run_baselines.py` | B0–B3 and both ablations; B4 and B5 recorded as not run | 318 s |
| Engine | `python scripts/train_engine.py` | `data/models/engine.pkl` | 25 s |
| Evaluate | `python scripts/evaluate.py` | 329 test cycles | 22 s |
| Compare results | `python scripts/compare_with_committed.py results` | `REPRODUCED 11/11 headline numbers` | <1 s |
| Export | `python scripts/export_site_data.py` | 329 cycles, 6 what-if grids | 21 s |
| Compare export | `python scripts/compare_with_committed.py export` | `EXPORT IDENTICAL 343/343 files` | 17 s |
| Tests | `python -m pytest -q` | `39 passed`, none skipped: the API and real-data tests ran | 23 s |
| Lint | ruff, ruff format, mypy as in CI | clean | 38 s |
| Website | `npm ci`, `npm run typecheck`, `npm test`, `npm run build` in `web/` | 3 tests, production build | 35 s |

**The pinned versions matter.** An earlier fresh clone that resolved the newest numpy and scipy instead of `requirements-lock.txt` moved the engine's mean macro-F1 from 0.9589 to 0.9604, and one link's p-value in the third digit. MiniRocket, the 1D-CNN and the majority baseline still matched exactly. Retraining in the original environment reproduces every number byte for byte, so the pipeline itself is deterministic; small numeric differences in the features move LightGBM's split points.

The comparison only counts a file the pipeline rewrote after the clone was made, so an untouched committed copy cannot pass as reproduced. That check was itself seen to fail: on a clone where the pipeline had not run, it reported `NOT REGENERATED`.

**The tests can fail.** Nine faults were written into the code on purpose, each in a throwaway clone, and the test suite was run against each one:

| Fault | Caught by |
|---|---|
| The checker accepts any stated value | `tests/test_faithfulness.py` |
| The checker's tolerance loosened to 50% | `tests/test_faithfulness.py` |
| The checker ignores the stated distance from healthy | `tests/test_faithfulness.py` (this one survived at first; the test that catches it was written because of that) |
| Pressure ripple computed as the mean | `tests/test_physics.py` |
| "Above" and "below" swapped in the explanations | `tests/test_faithfulness.py`, `tests/test_physics.py` |
| The API accepts any cycle id | `tests/test_api.py` |
| The API's per-type perturbation limits removed | `tests/test_api.py` (survived at first; a case inside the coarse bounds was added) |
| The page shows every claim as verified | `web/src/test/rationale.test.tsx` |
| The dashboard number gate stops reporting | `tests/test_number_check.py` (survived at first; the test was added) |

One fault survives on purpose: removing the coarse `Field(ge=-50, le=300)` bounds on a perturbation changes nothing, because the per-type limits behind them are stricter.

Not reproduced here: Linux and macOS, so the exact numbers are shown only with the pinned versions on Windows.

---

## Known limits, stated up front

- **The diagnosis is not a language model.** It is LightGBM on physics features with a rule-based explainer. The OpenTSLM fine-tune has code and configs, needs a GPU with about 20 GB, and has not been trained.
- **The language-model baselines were not run.** So there is no comparison yet of how faithful a language model's explanations are, which is the comparison this project exists to make.
- **One laboratory rig.** Fault levels were set on purpose. Nothing here has seen a real plant.
- **Bearings and wind turbines** have connectors and physics code that run only on synthetic stand-ins.

## If something does not work

| Symptom | Cause |
|---|---|
| `EPERM` from `npm ci` on Windows | A running `vite` holds a file in `node_modules`. Stop it and retry |
| `curl http://127.0.0.1:5173` refuses, the browser works | Vite listens on `localhost`, which is `[::1]` on Windows. Use `localhost` |
| `/api/health` says `engine.pkl missing` | Run `python scripts/train_engine.py` after `make data`, then restart the API |
| Results say Precomputed with the API running | The page checks once at load. Reload after the API has started |

More in [docs/troubleshooting.md](docs/troubleshooting.md).
