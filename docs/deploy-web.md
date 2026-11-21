# Sightglass website: run and deploy

The site in `web/` is one long page (Vite + React + TypeScript), with motion from `motion` and smooth scrolling from `lenis`. It reads the static export in `web/public/data/`, written by `scripts/export_site_data.py`. Every number on the page comes from that export.

## Run it locally

```bash
make api          # optional: live engine on 127.0.0.1:8000
make web          # dev server on http://localhost:5173 (proxies /api to port 8000)
```

Without the API, the page uses the precomputed results in the export and labels them "Precomputed". With the API running, "Run a diagnosis", the what-if lab's "Re-run this step live" and the console call the live engine.

The page only probes `/api` on `localhost` (or when the URL has `?api`), so a static deploy never makes a request that is bound to fail.

Useful URLs:

| URL | What it does |
|---|---|
| `/?cycle=hydraulic-01423` | Opens that test cycle in the explorer |
| `/?cycle=hydraulic-01423&run` | Also runs it and scrolls to the result |
| `/?cycle=hydraulic-01423&ask` | Opens the console on that cycle |
| `/?mock` | Uses the 5-cycle synthetic mock export (shows a "Mock data" banner) |

## Check before deploying

```bash
cd web
npm ci
npm run typecheck
npm test
npm run build                                  # output in web/dist
cd .. && python scripts/check_no_hardcoded_numbers.py
```

## GitHub Pages

The build uses relative paths (`base: './'`), so `web/dist/` can be served from any sub-path. Publish `web/dist/` with a Pages workflow or from a `gh-pages` branch.

## Vercel

- Root directory: `web`
- Build command: `npm run build`
- Output directory: `dist`

The export is about 18 MB of JSON (329 test cycles). Both hosts serve it compressed.

## Live API in production (optional)

Deploy `api/` with its Dockerfile (`docker compose up api-cpu`), put it behind the same origin as the site under `/api`, and open the site with `?api` (or serve it from that origin). If the API is unreachable, the page falls back to the precomputed export and says so.
