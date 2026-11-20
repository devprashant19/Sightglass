"""API tests. They need the real build and a trained engine; skipped otherwise (e.g. in CI)."""

import pytest
from fastapi.testclient import TestClient

from api.main import State, app

pytestmark = pytest.mark.skipif(State.engine is None, reason="needs data/build and engine.pkl")
client = TestClient(app)


def _a_test_id() -> str:
    return sorted(State.test_ids)[0]


def test_health() -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "ok"
    assert d["synthetic"] is False
    assert d["cycles"] == len(State.test_ids) > 0


def test_diagnose_real_cycle_verifies_claims() -> None:
    r = client.post("/api/diagnose", json={"cycle_id": _a_test_id()})
    assert r.status_code == 200
    d = r.json()
    assert set(d["labels"]) == {
        "cooler_condition",
        "valve_condition",
        "pump_leakage",
        "accumulator_pressure",
    }
    assert d["claims"], "the engine should cite evidence"
    for cl in d["claims"]:
        assert d["rationale"][cl["span"][0] : cl["span"][1]].startswith(cl["sensor"])
    assert "latency_ms" in d


def test_diagnose_with_perturbation() -> None:
    r = client.post(
        "/api/diagnose",
        json={"cycle_id": _a_test_id(), "perturbations": [{"type": "flow", "amount": -15}]},
    )
    assert r.status_code == 200
    assert r.json()["perturbations"] == [{"type": "flow", "amount": -15.0}]


def test_rejects_unknown_cycle_and_bad_input() -> None:
    assert client.post("/api/diagnose", json={"cycle_id": "hydraulic-99999"}).status_code == 404
    assert client.post("/api/diagnose", json={"cycle_id": "x"}).status_code == 422
    bad = {"cycle_id": _a_test_id(), "perturbations": [{"type": "flow", "amount": -90}]}
    assert client.post("/api/diagnose", json=bad).status_code == 422
    bad2 = {"cycle_id": _a_test_id(), "perturbations": [{"type": "boom", "amount": 1}]}
    assert client.post("/api/diagnose", json=bad2).status_code == 422
