# Deployment

Two things can be deployed, and only the first is needed. **The website is static files:** one page in `web/` (Vite, React, TypeScript, `motion`, `lenis`) that reads the committed export in `web/public/data/`. The live API is an optional second process. A static host never runs it, and the page never asks for it there.

| What | Where it runs | State |
|---|---|---|
| Website | Any static host. GitHub Pages workflow in `.github/workflows/pages.yml` | Built and checked locally. Not deployed yet: the workflow publishes once Pages is enabled |
| Live API | `make api` locally. A Dockerfile and `docker-compose.yml` exist | Run locally. The container images have not been built |

## Run the website locally

```bash
make web          # npm install, then the dev server on http://localhost:5173
make api          # optional, in a second terminal: the live engine on 127.0.0.1:8000
```

The dev server proxies `/api` to port 8000 (`SIGHTGLASS_API_PORT` changes that). Without the API, every result on the page is the precomputed one from the export, labelled **Precomputed**. With it, "Run a diagnosis", the what-if lab's "Re-run this step live" and the console call the engine, and the result says **Live**.

The page only tries `/api` when the host is `localhost`, `127.0.0.1` or `[::1]`, or the URL has `?api` (`web/src/lib/api.ts`). A static deploy therefore never makes a request that is bound to fail. If a live call fails, the page falls back to the export and says so.

| URL | What it does |
|---|---|
| `/?cycle=hydraulic-01668` | Opens that test cycle in the explorer. An id that is not in the export falls back to the default cycle |
| `/?cycle=hydraulic-01668&run` | Also runs it, and scrolls to the result |
| `/?cycle=hydraulic-01668&ask` | Opens the console on that cycle |
| `/?mock` | Uses the five-cycle mock export in `web/public/data-mock/`, under a "Mock data" banner. The live API is off in this mode |
| `/?api` | Allows live calls to `/api` on a host that is not local |

## Check before deploying

```bash
cd web
npm ci
npm run typecheck
npm test
npm run build                                  # output in web/dist
cd ..
python scripts/check_no_hardcoded_numbers.py   # no result number typed into web/src
```

To look at the production build without the dev server, `npx vite preview --port 4300 --strictPort` from `web/` serves `web/dist`. The preview server proxies `/api` too, so a local API is used if one is running.

## GitHub Pages

`.github/workflows/pages.yml` runs on a push to `main` that touches `web/` or the workflow itself, or by hand. It runs `npm ci`, the type check, the tests and the build, then publishes `web/dist`.

It needs one setting, made once by the repository owner: **Settings, Pages, Source: GitHub Actions.** Once Pages is enabled, the site is served at https://devprashant19.github.io/Sightglass/. Until then the workflow cannot publish, and nothing is served.

The build uses relative paths (`base: './'` in `web/vite.config.ts`), so it works under the `/Sightglass/` sub-path with no change. The page is one URL with query parameters, so no 404 fallback page is needed.

The Pages workflow does not run `scripts/check_no_hardcoded_numbers.py`. The main CI workflow, `.github/workflows/ci.yml`, does, on every push.

## Other static hosts

Any host that serves `web/dist` works. For Vercel: root directory `web`, build command `npm run build`, output directory `dist`. This has not been tried.

The export is about 18 MB of JSON, for 329 test cycles. Hosts that compress JSON serve much less.

## Updating what the site shows

The site shows only what is in `web/public/data/`. To change it, rerun the pipeline and re-export:

```bash
python scripts/evaluate.py
python scripts/export_site_data.py
```

then commit `web/public/data/`. A push that changes it triggers the Pages workflow.

## The live API in production

Not done, and not needed for the site. If you want it:

1. The API needs the dataset build (`data/build/hydraulic`, about 370 MB), the engine (`data/models/engine.pkl`) and the export (`web/public/data`).
2. Serve it on the same origin as the site, under `/api`, and open the site with `?api`. The site calls the relative path `/api`, so an API on another origin is never used by the page, whatever CORS allows.
3. The health check is `GET /api/health`. It answers 200 even when the engine is not loaded; check that `status` is `"ok"`.

**Docker.** `api/Dockerfile.cpu` installs the pinned versions from `requirements-lock.txt` without torch (the API never imports it), copies the code and `web/public/data`, and takes the dataset build and the engine from a read-only mount of `./data`:

```bash
make data && python scripts/train_engine.py     # once, on the host
docker compose up --build                       # API on http://localhost:8000
```

The image builds (1.6 GB, Docker 29.8.1 on Windows). Serving a diagnosis from inside the container has not been verified yet: the run was cut short when the machine ran out of disk.

The rate limit is kept in process memory, per client address. Behind a proxy every request comes from the proxy's address, so they all share one limit. See [`docs/security.md`](security.md).
