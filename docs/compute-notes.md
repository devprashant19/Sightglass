# Nebius Compute & Infrastructure Setup

## 1. Hardware Specifications
- **GPU Instance:** Nebius Cloud L40S (48 GB GDDR6 VRAM, Ada Lovelace architecture).
- **Persistent Storage:** 200 GB SSD mounted at `/data` storing raw datasets, TimeNet builds, checkpoints, and export artifacts.
- **Local Fallback:** CPU smoke configuration (`configs/train/smoke_cpu.yaml`) utilizing lightweight synthetic/subsampled series for testing in CI environments.

## 2. Cost Control & Automation
- **Idle Shutdown:** `scripts/idle-shutdown.sh` runs as a cron job checking GPU utilization via `nvidia-smi` and active processes. Shuts down instance if idle for > 30 minutes.
- **Run & Shutdown Wrapper:** `scripts/run_and_shutdown.sh` executes the training or evaluation script, syncs `/results` and `/checkpoints` to persistent `/data`, and initiates automatic shutdown.
- **Preemptible Instances:** Used for training runs with per-epoch checkpointing and automatic resumption.
