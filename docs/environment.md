# Environment

**Nothing is required.** Every variable has a working default, and none of them is a secret except `OPENAI_API_KEY`, which only matters to a baseline that is not implemented yet. The code reads them with `os.environ` or `process.env` directly: there is no `.env` loader, so a `.env` file is only read if you export it into your shell yourself.

[`.env.example`](../.env.example) lists the same eight names.

## Data

| Variable | Default | Read by | What |
|---|---|---|---|
| `SIGHTGLASS_BUILD` | `data/build/hydraulic` | `src/sightglass/data/loader.py` | Folder of the converted UCI #447 build that `make data` writes |
| `SIGHTGLASS_SYNTHETIC` | unset | `src/sightglass/data/loader.py` | `1` makes the loader generate synthetic cycles instead of reading the build. For tests and CI only; synthetic cycles carry `synthetic: true` |

## Live API

| Variable | Default | Read by | What |
|---|---|---|---|
| `SIGHTGLASS_WEB_DATA` | `web/public/data` | `api/main.py` | The exported site data that `/api/cycles/{id}` serves |
| `SIGHTGLASS_ALLOWED_ORIGIN` | `http://localhost:5173,http://127.0.0.1:5173` | `api/main.py` | Comma-separated origins that CORS allows |
| `SIGHTGLASS_RATE_PER_MIN` | `30` | `api/main.py` | Requests per minute per client address, for the rate-limited routes |

## Website

| Variable | Default | Read by | What |
|---|---|---|---|
| `SIGHTGLASS_API_PORT` | `8000` | `web/vite.config.ts` | The port the dev and preview servers proxy `/api` to |

## Baselines

| Variable | Default | Read by | What |
|---|---|---|---|
| `OPENAI_API_KEY` | unset | `src/sightglass/baselines/gpt4o_plots.py` | Without it, `scripts/run_baselines.py` records the GPT-4o baseline as not run. With it, the baseline still does not run: rendering, calling and parsing are not implemented |

## Screenshots

| Variable | Default | Read by | What |
|---|---|---|---|
| `BROWSER` | unset | `docs/screenshots/capture.mjs` | Path to a Chrome, Edge or Chromium, if the script does not find one in the usual places |

## Set by the code, not read

`src/sightglass/utils/seed.py` sets `PYTHONHASHSEED` to the run's seed. Python reads it only at start-up, so this affects processes the run starts afterwards, not the run itself.

## Scripts

| Variable | Default | Read by | What |
|---|---|---|---|
| `SIGHTGLASS_PORT` | `8000` | `scripts/deploy_api.sh` | Port the script serves the API on. The API itself always runs on the CPU; there is no device setting |

## A minimal file

You need none. The site calls the API by the relative path `/api`, through the Vite proxy in development, so CORS only matters to a client on another origin. A typical change is a stricter rate limit and the API on another port:

```bash
export SIGHTGLASS_RATE_PER_MIN=10
export SIGHTGLASS_API_PORT=8010
uvicorn api.main:app --host 127.0.0.1 --port 8010
make web
```
