#!/usr/bin/env bash
# scripts/run_and_shutdown.sh
# Job wrapper: runs the command, syncs results to persistent storage, then shuts down.
# Usage: ./scripts/run_and_shutdown.sh <command>

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <command>"
    exit 1
fi

COMMAND="$*"
echo "=== Starting Sightglass Task: ${COMMAND} at $(date) ==="

START_TIME=$(date +%s)
EXIT_CODE=0

eval "${COMMAND}" || EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "=== Task finished with exit code ${EXIT_CODE} in ${DURATION}s at $(date) ==="

# Sync results to persistent disk if mounted at /data
if [ -d "/data" ]; then
    echo "=== Syncing results and checkpoints to /data ==="
    mkdir -p /data/results /data/checkpoints
    rsync -av results/ /data/results/ || true
    rsync -av checkpoints/ /data/checkpoints/ || true
fi

echo "=== Initiating VM shutdown ==="
sudo shutdown -h now
