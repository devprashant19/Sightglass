"""Tests for Sightglass FastAPI inference endpoints."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_api_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["model"] == "sightglass-llama1b-s0"
    assert "uptime_s" in data
    assert "git_sha" in data


def test_api_diagnose() -> None:
    # 60 samples at 1 Hz for temperature
    payload = {
        "dataset": "hydraulic",
        "cycle_id": "test-api-cycle-01",
        "signals": {
            "TS1": {
                "unit": "°C",
                "rate_hz": 1.0,
                "source": "temperature",
                "values": [52.0] * 60,
            },
            "PS1": {
                "unit": "bar",
                "rate_hz": 100.0,
                "source": "pressure",
                "values": [150.0] * 6000,
            },
            "FS1": {
                "unit": "l/min",
                "rate_hz": 10.0,
                "source": "flow",
                "values": [8.0] * 600,
            },
            "EPS1": {
                "unit": "W",
                "rate_hz": 100.0,
                "source": "power",
                "values": [2400.0] * 6000,
            },
        },
    }
    resp = client.post("/diagnose", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["cycle_id"] == "test-api-cycle-01"
    assert "rationale" in data
    assert len(data["claims"]) > 0
    assert "latency_ms" in data


def test_api_diagnose_invalid_rates() -> None:
    # Sensor values exceed maximum allowed samples
    payload = {
        "dataset": "hydraulic",
        "cycle_id": "test-fail",
        "signals": {
            "TS1": {
                "unit": "°C",
                "rate_hz": 1.0,
                "source": "temperature",
                "values": [50.0] * 7000,  # exceeds 6000 max_length
            }
        },
    }
    resp = client.post("/diagnose", json=payload)
    assert resp.status_code == 422
