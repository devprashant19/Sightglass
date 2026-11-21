#!/usr/bin/env bash
# Start the live inference API on this machine, from the environment `make setup` created.
# Needs the data build (make data) and the trained engine (python scripts/train_engine.py).
set -euo pipefail

PORT=${SIGHTGLASS_PORT:-8000}
PYTHON=${PYTHON:-.venv/bin/python}
[ -x "$PYTHON" ] || PYTHON=.venv/Scripts/python.exe

echo "Starting the Sightglass API on 0.0.0.0:${PORT}"
exec "$PYTHON" -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT}"
