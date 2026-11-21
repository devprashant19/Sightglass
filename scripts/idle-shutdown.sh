#!/usr/bin/env bash
# scripts/idle-shutdown.sh
# Shuts down the Nebius VM if GPU utilization is 0% and no training/evaluation
# process has been running for 30 minutes.

set -euo pipefail

IDLE_FILE="/tmp/sightglass_idle_timestamp"
PROCESS_REGEX="train.py|evaluate.py|export_site_data.py"

# Check if any training or evaluation process is running
if pgrep -f "${PROCESS_REGEX}" >/dev/null; then
    rm -f "${IDLE_FILE}"
    exit 0
fi

# Check GPU utilization if nvidia-smi is available
if command -v nvidia-smi >/dev/null 2>&1; then
    GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -n1 || echo "0")
    if [ "${GPU_UTIL}" -gt 0 ]; then
        rm -f "${IDLE_FILE}"
        exit 0
    fi
fi

# If we reached here, machine is currently idle
if [ ! -f "${IDLE_FILE}" ]; then
    touch "${IDLE_FILE}"
    echo "Sightglass idle detected. Marked at $(date)"
else
    # Check if idle for >= 30 minutes
    IDLE_MINS=$(find "${IDLE_FILE}" -mmin +30 | wc -l)
    if [ "${IDLE_MINS}" -gt 0 ]; then
        echo "Sightglass VM has been idle for >30 minutes. Initiating safe shutdown..."
        rm -f "${IDLE_FILE}"
        sudo shutdown -h now
    fi
fi
