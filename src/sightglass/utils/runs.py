"""Run directory management and reproducibility tracking."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


def make_run_id(
    dataset: str,
    model: str,
    variant: str,
    seed: int,
    date_str: str | None = None,
) -> str:
    """Format: <dataset>_<model>_<variant>_s<seed>_<yyyymmdd>"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")
    return f"{dataset}_{model}_{variant}_s{seed}_{date_str}"


def get_git_sha() -> str:
    """Return the current git commit SHA, or 'unknown' if not in a git repo."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return "unknown"


def get_environment_dump() -> str:
    """Dump installed packages (similar to pip freeze)."""
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"], stderr=subprocess.DEVNULL
        )
        return out.decode("utf-8")
    except Exception:
        return "pip freeze unavailable"


def init_run(
    run_id: str,
    config: BaseModel | dict[str, Any],
    runs_dir: str | Path = "results/runs",
) -> Path:
    """Initialize a run folder with config.yaml, git_sha.txt, and env.txt."""
    run_dir = Path(runs_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write config.yaml
    config_path = run_dir / "config.yaml"
    if isinstance(config, BaseModel):
        config_dict = config.model_dump()
    else:
        config_dict = config

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_dict, f, default_flow_style=False, sort_keys=False)

    # 2. Write git_sha.txt
    with open(run_dir / "git_sha.txt", "w", encoding="utf-8") as f:
        f.write(f"{get_git_sha()}\n")

    # 3. Write env.txt
    with open(run_dir / "env.txt", "w", encoding="utf-8") as f:
        f.write(get_environment_dump())

    return run_dir
