.PHONY: setup data rationales baselines train eval export site api test lint all clean

PYTHON ?= python
PYTEST ?= pytest
RUFF ?= ruff
MYPY ?= mypy

setup:
	@echo "=== Setting up Sightglass environment ==="
	uv sync --all-extras

data:
	@echo "=== Preparing dataset and running EDA ==="
	$(PYTHON) -m sightglass.data.prepare_hydraulic

rationales:
	@echo "=== Generating physics rationales and QA pairs ==="
	$(PYTHON) scripts/build_rationales.py

baselines:
	@echo "=== Running baseline models (B0 - B5) ==="
	$(PYTHON) scripts/run_baselines.py --config configs/baselines/hydraulic.yaml

train:
	@echo "=== Launching OpenTSLM fine-tuning (smoke or full config) ==="
	$(PYTHON) scripts/train.py --config configs/train/smoke_cpu.yaml --seed 0

eval:
	@echo "=== Evaluating model predictions and computing faithfulness ==="
	$(PYTHON) scripts/evaluate.py --all

export:
	@echo "=== Exporting precomputed data for dashboard ==="
	$(PYTHON) scripts/export_site_data.py

site:
	@echo "=== Building web dashboard ==="
	cd web && pnpm install && pnpm build

api:
	@echo "=== Starting FastAPI inference server ==="
	uvicorn api.main:app --host 0.0.0.0 --port 8000

test:
	@echo "=== Running tests ==="
	$(PYTEST) -m "not slow and not gpu"

lint:
	@echo "=== Running linter and type checker ==="
	$(RUFF) check src tests
	$(MYPY) src/sightglass/physics src/sightglass/eval src/sightglass/rationales src/sightglass/export

all: lint test export
	@echo "=== Sightglass pipeline completed successfully ==="

clean:
	@echo "=== Cleaning caches ==="
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info
