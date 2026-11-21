# Compute: the plan for the GPU fine-tune

**Status: planned, not provisioned.** No GPU instance has been used for this project. Every result in `results/` was produced on a laptop CPU. This page records the setup that was planned for the OpenTSLM fine-tune, and what the two shutdown scripts in the repository do.

## Planned hardware

- A cloud GPU with enough memory for OpenTSLM-Flamingo on Llama-3.2 1B: about 20 GB. An L40S (48 GB) on Nebius was the candidate. Not rented.
- Persistent storage for the raw data, the build, checkpoints and exports.
- Until then, the CPU smoke configuration (`configs/train/smoke_cpu.yaml`) runs the training loop on 64 real train cycles to check loading, normalisation and checkpointing. It writes losses only, and those are not model results.

## The shutdown scripts

Both exist and have not been run on a VM.

- `scripts/idle-shutdown.sh`: meant to run from cron. If no `train.py`, `evaluate.py` or `export_site_data.py` process is running and `nvidia-smi` reports 0% GPU use for 30 minutes, it shuts the machine down.
- `scripts/run_and_shutdown.sh`: runs a command, copies results and checkpoints to persistent storage, then shuts down.

Preemptible instances, per-epoch checkpoints and automatic resume were part of the plan. `src/sightglass/tslm/train.py` writes checkpoints in the smoke mode; resume on a preempted GPU run has not been tried, because there has been no GPU run.
