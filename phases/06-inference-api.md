# Phase 6 — Static export and inference API

| | |
|---|---|
| **Goal** | Give the dashboard everything it needs as static files, plus an optional live service, so the demo works even when the GPU is off. |
| **Owner** | Teammate |
| **When** | Round 1, days 10–12. The export **schema** is agreed on day 2 (see Phase 7). |
| **Depends on** | Phase 4 checkpoints; Phase 5 results |
| **Unblocks** | Phase 7 on real data |

---

## 1. Two modes

| Mode | What it is | When it's used |
|---|---|---|
| **Precomputed (default)** | `scripts/export_site_data.py` runs the model on every test cycle once and writes static JSON. The dashboard reads only these files. | Always. Free to host, instant, and it can't go down during judging. |
| **Live (optional)** | A FastAPI service on a small Nebius GPU (or a CPU box running Gemma-270M) for diagnosing an uploaded or edited cycle. | Demos and judging windows only, switched on manually. |

The dashboard checks `/health` on load. If the API doesn't answer within 2 seconds, live features are hidden and everything else works.

---

## 2. Static export (`scripts/export_site_data.py`)

Writes to `web/public/data/`. Every file has a `schema_version` field.

```
web/public/data/
  manifest.json                 # schema_version, generated_at, git_sha, datasets, models
  summary.json                  # headline numbers (copied from results/summary.json)
  hydraulic/
    index.json                  # list of test cycles: id, true labels, predicted labels, verdict counts, tags
    cycles/hydraulic-01423.json # one file per test cycle (below)
    results.json                # model vs baselines, per-component F1, confusion matrices
    faithfulness.json           # comparison across models
    ablations.json
    failures.json
    dataset.json                # sensors, rates, labels, split method, PR link, load snippet
    whatif/hydraulic-00012.json # precomputed perturbation grid for the what-if lab
```

### Per-cycle file

```json
{
  "schema_version": 1,
  "id": "hydraulic-01423",
  "dataset": "hydraulic",
  "meta": {"cycle_index": 1423, "stable_flag": 0},
  "true_labels": {"cooler_condition": {"value": 20, "name": "reduced efficiency"}},
  "signals": {
    "PS1": {"unit": "bar", "rate_hz": 10, "source": "pressure", "values": [151.2, 152.0]}
  },
  "prediction": {
    "model": "sightglass-llama1b-s0",
    "labels": {"cooler_condition": {"value": 20, "name": "reduced efficiency"}},
    "rationale": "Cooler: reduced efficiency. Evidence: TS1 mean temperature 51.4 °C (12% above healthy); ...",
    "claims": [
      {
        "span": [42, 86],
        "component": "cooler_condition",
        "sensor": "TS1",
        "feature": "TS1.mean",
        "stated": {"value": 51.4, "unit": "°C", "direction": "above", "pct": 12},
        "true": {"value": 51.1, "pct": 11.5},
        "status": "verified",
        "window": [0, 60]
      }
    ]
  },
  "baselines": {"B1_lightgbm": {"labels": {}}},
  "features": {"TS1.mean": {"value": 51.1, "unit": "°C", "z": 2.3, "pct": 11.5}}
}
```

- [ ] Signals for display: 100 Hz sensors at 10 Hz, others native. About 5,000 numbers per cycle, roughly 40 KB as JSON; with ~330 test cycles that's ~13 MB in total, fine for static hosting. Round display values to 4 significant figures.
- [ ] `claims[].span` are character offsets into `rationale`, so the UI can highlight the exact text.
- [ ] `claims[].window` is the time range the feature uses, so the UI can shade the right part of the chart.
- [ ] Validate every output file against a JSON Schema (`web/src/schema/*.json`, generated from pydantic models in `src/sightglass/export/schema.py`). Export fails if validation fails.

### What-if grid

For 5–10 healthy test cycles, precompute a grid of perturbations and the model's answer for each:

| Perturbation | Levels |
|---|---|
| Reduce flow (FS1, FS2) | 0, −5, −10, −15, −20 % |
| Raise temperature (TS1–4) | 0, +2, +4, +6, +8 °C |
| Add pressure ripple (PS1–6) | 0, +25, +50, +100 % of std |

One perturbation at a time (15 points per cycle) plus a small 2-D grid for flow × temperature. Each result stores the full prediction and claims, so the lab can show the diagnosis changing without the live API.

Perturbations live in `src/sightglass/export/perturb.py` and are shared with the API.

---

## 3. Live API (`api/`)

FastAPI, one process, model loaded once at start-up.

| Method | Path | Request | Response |
|---|---|---|---|
| GET | `/health` | — | `{model, version, device, git_sha, uptime_s}` |
| GET | `/cycles/{id}` | — | Stored test cycle (same shape as the per-cycle export file) |
| POST | `/diagnose` | `{dataset, signals: {name: {rate_hz, values}}}` | `{labels, rationale, claims[] with verdicts, latency_ms}` |
| POST | `/diagnose/perturb` | `{cycle_id, perturbations: [{type, sensors, amount}]}` | Same as `/diagnose`, plus the perturbed signals |

- [ ] Request validation with pydantic: known sensor names only, rates must match the dataset card, length caps (for example ≤ 6,000 samples per sensor), finite numbers only.
- [ ] Faithfulness is checked at inference time with the same `eval/faithfulness.py`, so every live answer shows which claims verified.
- [ ] Rate limit (for example 10 requests per minute per IP) with `slowapi` or a simple in-memory token bucket.
- [ ] CORS limited to the dashboard's domain.
- [ ] Timeouts: generation capped at 400 new tokens and 20 seconds.
- [ ] No secrets in the repo; config through environment variables (`SIGHTGLASS_CHECKPOINT`, `SIGHTGLASS_DEVICE`, `SIGHTGLASS_ALLOWED_ORIGIN`).
- [ ] Structured JSON logs; never log full uploaded signals.

### Packaging

- [ ] `api/Dockerfile`: CUDA base image for GPU, a slim CPU variant for Gemma-270M.
- [ ] `docker compose up` runs it locally with a mounted checkpoint.
- [ ] `scripts/deploy_api.sh` starts the Nebius VM, pulls the image, runs it behind Caddy with HTTPS, and prints the URL.

---

## Tests

- [ ] Export: schema validation for every file; one file per test cycle; spans point at the right text (`rationale[span[0]:span[1]]` contains the sensor name).
- [ ] API: `pytest` with FastAPI's `TestClient` and a stub model; invalid requests return 422; oversize inputs are rejected; `/diagnose` on a stored cycle returns the same claims as the export.
- [ ] Load test: 20 sequential `/diagnose` calls on Gemma-270M; record p50 and p95 latency.

## Exit criteria

- [ ] Static export covers the full test set and passes schema validation.
- [ ] What-if grid exported for at least 5 cycles.
- [ ] Live API returns a diagnosis in under a few seconds with Gemma-270M, and its claims match the static export for the same cycle.

## Risks in this phase

| Risk | What to do |
|---|---|
| Export too large for the host | Lower display rate to 5 Hz for pressure, or gzip (both Vercel and GitHub Pages serve compressed files) |
| Live API down during judging | It's optional by design; the static site never depends on it |
| Abuse of the public endpoint | Rate limit, input caps, switch the VM off outside demo windows |
