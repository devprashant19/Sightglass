# Sightglass Web Dashboard Deployment Guide

The Sightglass web application is a static Single-Page Application (SPA) built with Vite, React, TypeScript, and Tailwind CSS. All data is pre-exported as static JSON in `public/data/`, and all routes use hash-based routing (`#/explore/...`), requiring zero server-side URL rewrite configuration.

---

## 1. Local Preview

```bash
cd web
pnpm install
pnpm build
pnpm preview
```
Visit `http://localhost:4173/` in your browser.

---

## 2. GitHub Pages Deployment

Sightglass can be hosted on GitHub Pages for free:

1. Build the production bundle:
   ```bash
   cd web
   pnpm build
   ```
2. The compiled assets are placed in `web/dist/`.
3. In GitHub Repository Settings -> Pages, select Source: **GitHub Actions** or deploy from `gh-pages` branch using the `web/dist/` directory.

---

## 3. Vercel Deployment

```bash
vercel deploy --prod
```
- **Framework Preset**: Vite
- **Root Directory**: `web`
- **Build Command**: `pnpm build`
- **Output Directory**: `dist`

---

## 4. Live API Connection (Optional)

When the FastAPI inference service is deployed (`docker-compose up -d api-cpu`), the dashboard will automatically query live inference and counterfactual perturbations via `http://localhost:8000/diagnose/perturb`.
