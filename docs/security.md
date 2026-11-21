# Security

There is little to protect. **The static site holds no secrets, takes no input that leaves the browser, and makes no API calls on a public host.** The live API is read-only over a public dataset: it has no accounts, no writes and no stored user data. What remains is keeping the API from being used to burn CPU, and keeping the one secret, an optional OpenAI key, out of the repository.

## The static site

- It fetches only files under `./data` (or `./data-mock` with `?mock`) on its own origin.
- It calls `/api` only on `localhost`, `127.0.0.1`, `[::1]`, or with `?api` in the URL (`web/src/lib/api.ts`). The static build was checked in Chrome: it made no `/api` requests, and labelled its results "Precomputed".
- The `cycle` query parameter is only compared against the ids in the export index. It is not used to build a path unless it matches one.

## The live API

`api/main.py`. What it does about each kind of input:

| Concern | What the code does |
|---|---|
| Unexpected fields | The request models forbid extra fields. Unknown keys get 422 |
| Cycle ids | `^hydraulic-\d{5}$`, and then the id must be in the test split. Anything else gets 404 before a file is opened, so the id cannot reach outside `web/public/data/hydraulic/cycles/` |
| Perturbations | At most three. Each type has a range (`LIMITS` in `src/sightglass/export/perturb.py`), checked twice: in the API and in `validate()`. Non-finite amounts are rejected |
| Volume | 30 requests a minute per client address by default (`SIGHTGLASS_RATE_PER_MIN`), on `/api/cycles` and `/api/diagnose`. Over it: 429 |
| Origins | CORS allows only the origins in `SIGHTGLASS_ALLOWED_ORIGIN`, default the two local dev addresses, with `GET` and `POST` and the `Content-Type` header |
| Binding | `make api` listens on `127.0.0.1` only |

What it deliberately does not do:

- **No authentication.** Anyone who can reach the port can run diagnoses. It is meant for local use, or behind a proxy you control.
- **The rate limit is in memory, per process, per client address.** It resets on restart, is not shared between workers, and behind a reverse proxy all clients share the proxy's address, and so one limit.
- **`/api/health` is not rate limited**, and reports the version, the git SHA and the dataset checksum. None of that is secret here.
- **`engine.pkl` is a pickle**, loaded with `pickle.load` at start-up. Loading one runs whatever code it contains. Only ever load an engine file you built yourself with `scripts/train_engine.py`.

## Secrets

- The only secret the code reads is `OPENAI_API_KEY`, for a baseline that is not implemented. Nothing requires it.
- `.env` is gitignored, and `.env.example` holds names only. The code never reads a `.env` file itself.

## Before exposing the API publicly

1. Put it behind a reverse proxy on the site's own origin, under `/api`, and add authentication or a stricter limit there.
2. Make the proxy pass the real client address, or replace the in-memory limiter. As it stands, one heavy client blocks everyone.
3. Set `SIGHTGLASS_ALLOWED_ORIGIN` to the site's origin only.
4. Run more than one worker only after moving the limit out of process memory.
5. Check that `/api/health` answers `"status": "ok"`. It answers 200 even when the engine failed to load.

There is no SECURITY.md file with a reporting address yet: that needs a contact and a promise only the owner can give.
