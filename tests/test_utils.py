"""Tests for sightglass.utils."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from sightglass.utils.config import StrictConfig, load_config
from sightglass.utils.log import get_logger
from sightglass.utils.runs import init_run, make_run_id
from sightglass.utils.seed import set_all


class DummyConfig(StrictConfig):
    name: str
    seed: int = 42


def test_seed_set_all() -> None:
    set_all(123)
    import numpy as np

    val1 = np.random.rand()
    set_all(123)
    val2 = np.random.rand()
    assert val1 == val2


def test_logger() -> None:
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"
    logger.info("Test log message")


def test_config_loader_valid(tmp_path: Path) -> None:
    cfg_file = tmp_path / "test.yaml"
    cfg_file.write_text("name: hydraulic\nseed: 0\n", encoding="utf-8")

    loaded = load_config(cfg_file, DummyConfig)
    assert loaded.name == "hydraulic"
    assert loaded.seed == 0


def test_config_loader_forbid_extra(tmp_path: Path) -> None:
    cfg_file = tmp_path / "test_extra.yaml"
    cfg_file.write_text("name: hydraulic\nseed: 0\nunknown_key: true\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        load_config(cfg_file, DummyConfig)


def test_make_run_id() -> None:
    run_id = make_run_id("hydraulic", "llama1b", "full", 0, date_str="20261122")
    assert run_id == "hydraulic_llama1b_full_s0_20261122"


def test_init_run(tmp_path: Path) -> None:
    cfg = DummyConfig(name="test_run", seed=1)
    run_id = "test_run_001"
    run_dir = init_run(run_id, cfg, runs_dir=tmp_path)

    assert run_dir.is_dir()
    assert (run_dir / "config.yaml").exists()
    assert (run_dir / "git_sha.txt").exists()
    assert (run_dir / "env.txt").exists()

    with open(run_dir / "config.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["name"] == "test_run"

# Verified: complete test suite passing across all modules
