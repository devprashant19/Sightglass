"""Engine.check_rationale: grading text written by another model with the engine's own checker."""

import re

import pytest

from sightglass.data.loader import load_cycles
from sightglass.engine import ENGINE_PATH, Engine
from sightglass.rationales.builder import COMPONENTS

pytestmark = pytest.mark.skipif(not ENGINE_PATH.is_file(), reason="needs make data + engine.pkl")


@pytest.fixture(scope="module")
def setup() -> tuple[Engine, object, dict]:
    engine = Engine.load(ENGINE_PATH)
    cycle = load_cycles("hydraulic", split="test")[0]
    d = engine.diagnose(cycle)
    return engine, cycle, d


def test_engine_text_checks_the_same_as_the_engine(setup: tuple) -> None:
    engine, cycle, d = setup
    p = engine.check_rationale(cycle, d["rationale"], "copy")
    for k in COMPONENTS:
        assert p["labels"][k]["value"] == d["labels"][k]["value"]
    assert [c["status"] for c in p["claims"]] == [c["status"] for c in d["claims"]]
    assert [c["component"] for c in p["claims"]] == [c["component"] for c in d["claims"]]
    assert p["consistency"] == d["consistency"]


def test_a_changed_number_is_caught(setup: tuple) -> None:
    engine, cycle, d = setup
    first = d["claims"][0]
    a, b = first["span"]
    clause = d["rationale"][a:b]
    # Multiply the first stated value by 1.5: far outside the 5% tolerance.
    m = re.search(r"(\d+(?:\.\d+)?)", clause[len(first["sensor"]) :])
    assert m is not None
    s = a + len(first["sensor"]) + m.start(1)
    e = a + len(first["sensor"]) + m.end(1)
    bad = d["rationale"][:s] + f"{float(m.group(1)) * 1.5:.3g}" + d["rationale"][e:]
    p = engine.check_rationale(cycle, bad, "tampered")
    assert p["claims"][0]["status"] == "wrong_value"


def test_unreadable_text_scores_nothing(setup: tuple) -> None:
    engine, cycle, _ = setup
    p = engine.check_rationale(cycle, "The machine seems fine overall.", "vague")
    assert all(p["labels"][k]["value"] is None for k in COMPONENTS)
    assert p["claims"] == []
    assert not any(p["consistency"].values())
