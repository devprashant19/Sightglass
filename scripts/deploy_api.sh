#!/usr/bin/env bash
# scripts/deploy_api.sh
# Deployment script for live inference API

set -euo pipefail

echo "=== Deploying Sightglass Inference API ==="

PORT=${SIGHTGLASS_PORT:-8000}
DEVICE=${SIGHTGLASS_DEVICE:-cpu}

echo "Starting Uvicorn server on port ${PORT} with device ${DEVICE}..."
uv run uvicorn api.main:app --host 0.0.0.0 --port "${PORT}"
