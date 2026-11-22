.PHONY: setup data links rationales baselines engine train tslm tslm-val tslm-test eval export readme site web api test lint all clean

PYTHON ?= python
PYTEST ?= pytest
RUFF ?= ruff
MYPY ?= mypy

setup:
	@echo "=== Setting up Sightglass environment ==="
	uv venv --python 3.12
	uv pip sync requirements-lock.txt
	uv pip install --no-deps -e .

data:
	@echo "=== Downloading UCI #447 and building data/build/hydraulic ==="
	$(PYTHON) scripts/prepare_data.py

links:
	@echo "=== Measuring physics links on the train split ==="
	$(PYTHON) scripts/analyze_links.py

rationales:
	@echo "=== Generating physics rationales and QA pairs ==="
	$(PYTHON) scripts/build_rationales.py

baselines:
	@echo "=== Running baseline models (B0 - B5) ==="
	$(PYTHON) scripts/run_baselines.py

engine:
	@echo "=== Training the Sightglass engine ==="
	$(PYTHON) scripts/train_engine.py

train:
	@echo "=== Launching OpenTSLM fine-tuning (smoke or full config) ==="
	$(PYTHON) scripts/train.py --config configs/train/smoke_cpu.yaml --seed 0

tslm:
	@echo "=== Training the soft-prompt TSLM (needs requirements-tslm.txt; uses a CUDA GPU if present) ==="
	$(PYTHON) scripts/train_tslm.py train

tslm-val:
	$(PYTHON) scripts/train_tslm.py evaluate --split val

tslm-test:
	@echo "=== Test split, once, after every choice was made on val ==="
	$(PYTHON) scripts/train_tslm.py evaluate --split test

eval:
	@echo "=== Evaluating model predictions and computing faithfulness ==="
	$(PYTHON) scripts/evaluate.py

export:
	@echo "=== Exporting precomputed data for dashboard ==="
	$(PYTHON) scripts/export_site_data.py

readme:
	$(PYTHON) scripts/make_readme_table.py --write

site:
	@echo "=== Building web dashboard ==="
	cd web && npm install && npm run build

web:
	@echo "=== Website dev server on http://localhost:5173 (proxies /api to :8000) ==="
	cd web && npm install && npm run dev

api:
	@echo "=== Starting FastAPI inference server ==="
	uvicorn api.main:app --host 127.0.0.1 --port 8000

test:
	@echo "=== Running tests ==="
	$(PYTEST) -m "not slow and not gpu"

lint:
	@echo "=== Running linter and type checker ==="
	$(RUFF) check src tests scripts api connector
	$(MYPY) src/sightglass/physics src/sightglass/eval src/sightglass/rationales src/sightglass/export src/sightglass/engine.py src/sightglass/data

all: data links rationales baselines engine eval export readme lint test
	@echo "=== Sightglass pipeline completed successfully ==="

clean:
	@echo "=== Cleaning caches ==="
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info
