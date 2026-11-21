# Troubleshooting

Problems that have happened while building and running this, with the exact text you will see. Most come from a missing build step, or from Windows.

## Installing

| Symptom | Cause and fix |
|---|---|
| `npm ci` or `npm install` in `web/` fails with `EPERM: operation not permitted` on a file under `node_modules` (often esbuild's binary) | Windows will not replace a file another process holds open, and a running `vite` dev or preview server holds esbuild's. Stop every `vite` or `node` process started from `web/`, then run it again. Closing the terminal is not always enough: check Task Manager for a leftover `node.exe` |
| `make data` fails, or the disk fills during the pipeline | The download, the unzipped files and the build need about 1 GB in `data/`, and the Python environment about 1.3 GB more. Free space first, then run `make data` again. A complete, checksummed zip is not downloaded twice |
| `Checksum mismatch for https://archive.ics.uci.edu/...` | The download was cut off, or UCI changed the file. The connector deletes the partial download. Run `make data` again; if it fails the same way, the archive has changed and the pinned SHA-256 in the connector no longer matches |

## Running the pipeline or the API

| Symptom | Cause and fix |
|---|---|
| `No dataset build at data/build/hydraulic. Run make data ...` | The loader found no build. Run `make data`, or point `SIGHTGLASS_BUILD` at an existing one |
| `/api/health` answers `"status": "unavailable"` with `"error": "dataset build missing (run make data)"` | Same cause, seen from the API. Every other route answers 503 until it is fixed and the API restarted |
| `/api/health` says `data\models\engine.pkl missing (run scripts/train_engine.py)` (forward slashes on Linux and macOS) | The engine was never trained in this clone: it is gitignored. Run `python scripts/train_engine.py` after `make data`, then restart the API. `scripts/evaluate.py` and `scripts/export_site_data.py` need it too |
| `/api/cycles/<id>` returns `Cycle not exported; run scripts/export_site_data.py` | The id is a test cycle but its file is not in `SIGHTGLASS_WEB_DATA` |
| `hydraulic-00012 is not a test cycle.` | The API serves only the 329 test cycles. Ids are listed in `web/public/data/hydraulic/index.json` |
| `pytest` reports skips with `needs data/build and engine.pkl`, or `real UCI #447 build not present` | Expected without the build: the four API tests and one loader test skip. Run `make data` and `python scripts/train_engine.py` to include them |

## The website

| Symptom | Cause and fix |
|---|---|
| `curl http://127.0.0.1:5173` (or `:4300` for preview) refuses the connection, but the browser works | On Windows, Vite listens on `localhost`, which resolves to the IPv6 address `[::1]`, not to `127.0.0.1`. Use `http://localhost:5173`. `netstat -ano` shows it: `[::1]:4300 ... LISTENING` |
| `{"error":"The live API is not running on port 8000. Start it with \"make api\"."}` in the network tab | The dev or preview server's proxy found nothing on the API port. Harmless: the page falls back to the precomputed results. Start `make api`, or set `SIGHTGLASS_API_PORT` if it runs elsewhere |
| A result says **Precomputed** although `make api` is running | The page checks the API once at load, with a 2.5 s timeout, and only on a local host or with `?api`. Reload after the API has finished starting: it loads the engine and the build first |
| `?cycle=...` opens a different cycle from the one asked for | The id is not in the export, so the page falls back to its default cycle without saying so. Use an id from `web/public/data/hydraulic/index.json` |
| `The exported results could not be loaded (...). Run make export and reload.` | `web/public/data/` is missing or incomplete. Run `make export`, which needs the engine |
| A **Mock data** banner across the top | The URL has `?mock`. Those five cycles are synthetic, and the API is off in that mode |
