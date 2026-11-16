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
