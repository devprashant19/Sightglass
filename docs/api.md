# API

One FastAPI app, `api/main.py`, with three routes under `/api`. It is optional: the website works without it, from the static export. **It only serves the 329 test cycles, and it recomputes every answer:** features, labels, explanation and the check of every number, on each request.

It loads `data/models/engine.pkl` and the dataset build once at start-up. If either is missing it still starts, `/api/health` says why, and the other routes answer 503.

```bash
make api        # uvicorn on 127.0.0.1:8000
```

## Routes

| Method | Path | Rate limited | Returns |
|---|---|---|---|
| GET | `/api/health` | no | Engine status, version, dataset checksum, number of cycles, perturbation limits |
| GET | `/api/cycles/{cycle_id}` | yes | The stored cycle file from the static export (`web/public/data/hydraulic/cycles/<id>.json`) |
| POST | `/api/diagnose` | yes | A fresh diagnosis of a test cycle, optionally after perturbing its signals |

FastAPI's own `/docs` and `/openapi.json` are also served.

## `GET /api/health`

Real response, trimmed only of the git SHA:

```json
{
  "status": "ok",
  "error": null,
  "model": "LightGBM on physics features + Sightglass rationale engine",
  "version": "1.1.0",
  "data_source": "UCI #447 hydraulic test rig (real data)",
  "synthetic": false,
  "sha256": "24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2",
  "cycles": 329,
  "uptime_s": 0.3,
  "perturbation_limits": {"flow": [-50.0, 50.0], "temperature": [-20.0, 20.0], "ripple": [0.0, 300.0]}
}
```

Without the build or the engine, `status` is `"unavailable"` and `error` names the missing file and the command that makes it.

## `POST /api/diagnose`

Request:

```json
{ "cycle_id": "hydraulic-01668", "perturbations": [{ "type": "flow", "amount": -15 }] }
```

| Field | Rule |
|---|---|
| `cycle_id` | Must match `^hydraulic-\d{5}$` and be a test cycle |
| `perturbations` | Up to 3. `type` is `baseline`, `flow`, `temperature` or `ripple` |
| `amount` | `flow`: percent change of FS1 and FS2, -50 to 50. `temperature`: °C added to TS1 to TS4, -20 to 20. `ripple`: a 5 Hz sine added to PS1 to PS6, with an amplitude of this percent of each signal's spread, 0 to 300. `baseline` is ignored |
| anything else | Rejected: unknown fields are not allowed |

The response is the same `prediction` object the static cycle files hold, plus `cycle_id` and `true_labels`. Its keys:

| Key | What |
|---|---|
| `labels` | Per component, `{value, name}`, for example `{"value": 1, "name": "weak leakage"}` |
| `confidence` | The classifier's top probability per component |
| `rationale`, `paragraphs` | The explanation, whole and split by component, with character spans |
| `claims` | One entry per number stated: the sensor, the stated and the recomputed value, the healthy reference, `status` and the time window |
| `unparsed_numbers` | Numbers in the text the parser could not tie to a claim |
| `consistency` | Per component, whether the evidence supports the label |
| `perturbations`, `latency_ms` | What was applied, and how long the engine took |

One claim from a real response for `hydraulic-01668` with no perturbation:

```json
{
  "component": "cooler_condition", "sensor": "TS1", "feature": "TS1.slope", "quantity": "temperature slope",
  "stated": {"value": 0.415, "unit": "°C/min", "direction": "above", "pct": 5.0, "sigma": null, "basis": "pct"},
  "true": {"value": 0.4147, "pct": 4.767, "z": 0.6547},
  "reference": {"mean": 0.3959, "std": 0.02882},
  "status": "verified", "value_ok": true, "direction_ok": true, "window": [0.0, 60.0]
}
```

That cycle is healthy on all four parts, and the engine says so. With the `flow -15` perturbation above, the pump label changes to `weak leakage`.

`status` is one of `verified`, `wrong_value`, `wrong_direction`, `unknown_sensor`, `unknown_quantity` or `unit_mismatch`.

## Errors

Seen in real calls:

| Status | When | Body |
|---|---|---|
| 404 | A well-formed id that is not a test cycle | `{"detail": "hydraulic-00000 is not a test cycle."}` |
| 404 | `/api/cycles/{id}` when the export is missing | `"Cycle not exported; run scripts/export_site_data.py"` |
| 422 | `cycle_id` does not match the pattern, or an unknown field | FastAPI's validation list, for example `string_pattern_mismatch` or `extra_forbidden` |
| 422 | An amount outside its type's range | `{"detail": "flow amount must be in [-50.0, 50.0]"}` |
| 429 | More than the rate limit in a minute from one client address | `{"detail": "Too many requests; try again in a minute."}` |
| 503 | Engine or build not loaded | `{"detail": "Engine unavailable: ..."}` |

The rate limit, the allowed origins and the data folder are set by environment variables: see [`docs/environment.md`](environment.md). What the API does and does not protect is in [`docs/security.md`](security.md).

## How the site uses it

`web/src/lib/api.ts` calls `/api/health` with a 2.5 s timeout and `/api/diagnose` with a 30 s timeout, and only on `localhost`, `127.0.0.1`, `[::1]`, or when the URL has `?api`. In development Vite proxies `/api` to port 8000 (`web/vite.config.ts`). If a live call fails, the page falls back to the precomputed result and labels it.
