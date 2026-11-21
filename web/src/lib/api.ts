import type { Cycle, DatasetIndex, DatasetInfo, Failure, Health, Links, Manifest, Prediction, Results, Summary, WhatIf } from './types';

/** Static export root. `?mock` in the URL switches to the labelled mock export. */
export const DATA_ROOT = typeof location !== 'undefined' && new URLSearchParams(location.search).has('mock') ? './data-mock' : './data';

async function json<T>(path: string, init?: RequestInit, timeoutMs = 15000): Promise<T> {
  const ctl = new AbortController();
  const t = window.setTimeout(() => ctl.abort(), timeoutMs);
  try {
    const r = await fetch(path, { ...init, signal: ctl.signal });
    const text = await r.text();
    let body: unknown;
    try { body = text ? JSON.parse(text) : {}; } catch { throw new Error(`${path} did not return JSON (HTTP ${r.status})`); }
    if (!r.ok) {
      const msg = (body as { detail?: unknown; error?: unknown }).detail ?? (body as { error?: unknown }).error;
      throw new Error(typeof msg === 'string' ? msg : `HTTP ${r.status} from ${path}`);
    }
    return body as T;
  } catch (e) {
    if ((e as Error).name === 'AbortError') throw new Error(`${path} timed out`);
    throw e;
  } finally {
    window.clearTimeout(t);
  }
}

const data = <T,>(p: string) => json<T>(`${DATA_ROOT}/${p}`);

export const getManifest = () => data<Manifest>('manifest.json');
export const getSummary = () => data<Summary>('summary.json');
export const getIndex = () => data<DatasetIndex>('hydraulic/index.json');
export const getDataset = () => data<DatasetInfo>('hydraulic/dataset.json');
export const getLinks = () => data<Links>('hydraulic/links.json');
export const getResults = () => data<Results>('hydraulic/results.json');
/** Wrong labels first, then wrong claims, then evidence that does not support its label. */
const failRank = (f: Failure) => (f.tags.some((t) => t.startsWith('wrong')) ? 0 : f.tags.some((t) => /claim|value|direction|sensor/.test(t)) ? 1 : 2);
export const getFailures = () => data<Failure[] | { failures: Failure[] }>('hydraulic/failures.json')
  .then((f) => (Array.isArray(f) ? f : f.failures ?? []))
  .then((fs) => [...fs].sort((a, b) => failRank(a) - failRank(b) || b.tags.length - a.tags.length));
export const getCycle = (id: string) => data<Cycle>(`hydraulic/cycles/${encodeURIComponent(id)}.json`);
export const getWhatIf = (id: string) => data<WhatIf>(`hydraulic/whatif/${encodeURIComponent(id)}.json`);

/**
 * Live inference service (FastAPI). Optional: the page works without it. Only probed where it can exist
 * (local dev/preview, or `?api` in the URL), so a static deploy never makes a request that is bound to fail.
 * Off with `?mock`, so mock cycles are never mixed with live answers about real data.
 */
export const API_ENABLED = typeof location !== 'undefined' && DATA_ROOT === './data'
  && (/^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname) || new URLSearchParams(location.search).has('api'));
export const getHealth = () => (API_ENABLED ? json<Health>('/api/health', undefined, 2500) : Promise.reject(new Error('live API not enabled on this host')));
export interface Perturbation { type: 'flow' | 'temperature' | 'ripple'; amount: number }
export const diagnoseLive = (cycleId: string, perturbations: Perturbation[] = []) =>
  json<Prediction>('/api/diagnose', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cycle_id: cycleId, perturbations }),
  }, 30000);
