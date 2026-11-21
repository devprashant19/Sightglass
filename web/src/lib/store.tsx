import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import {
  diagnoseLive, getCycle, getDataset, getFailures, getHealth, getIndex, getLinks, getManifest, getResults, getSummary,
} from './api';
import type { Cycle, DatasetIndex, DatasetInfo, Failure, Health, IndexItem, Links, Manifest, Prediction, Results, Summary } from './types';

export type RunStatus = 'idle' | 'running' | 'done' | 'error';
export type ResultSource = 'live' | 'precomputed';

interface Store {
  manifest: Manifest | null;
  summary: Summary | null;
  index: DatasetIndex | null;
  dataset: DatasetInfo | null;
  links: Links | null;
  results: Results | null;
  failures: Failure[];
  loadError: string | null;
  /** Live API health; null while checking or when offline. */
  health: Health | null;
  healthState: 'checking' | 'live' | 'offline';
  cycleId: string | null;
  cycle: Cycle | null;
  cycleError: string | null;
  selectCycle: (id: string) => Promise<Cycle | null>;
  status: RunStatus;
  result: Prediction | null;
  resultFor: string | null;
  resultSource: ResultSource | null;
  runError: string | null;
  startedAt: number;
  run: (id?: string) => void;
  consoleOpen: boolean;
  consoleCycle: string | null;
  openConsole: (cycleId?: string | null) => void;
  closeConsole: () => void;
  /** Sensors cited by the latest diagnosis: 'ok' if every claim on it verified, 'bad' otherwise. */
  cited: Record<string, 'ok' | 'bad'>;
  mock: boolean;
}

const Ctx = createContext<Store | null>(null);

/** A good first cycle to show: correct on all four components, every claim verified, the most faults. */
export function pickDefault(items: IndexItem[]): string | null {
  if (!items.length) return null;
  const faults = (c: IndexItem) => Object.values(c.true_labels).filter((v, i) => v !== [100, 100, 0, 130][i]).length;
  const scored = [...items].sort((a, b) =>
    (b.correct - a.correct) || (Number(b.is_faithful) - Number(a.is_faithful)) || (faults(b) - faults(a)) || a.cycle_index - b.cycle_index);
  return scored[0].id;
}

const MIN_RUN_MS = 2300; // long enough for the streaming log to read as steps, short enough not to feel slow

export function StoreProvider({ children }: { children: ReactNode }) {
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [index, setIndex] = useState<DatasetIndex | null>(null);
  const [dataset, setDataset] = useState<DatasetInfo | null>(null);
  const [links, setLinks] = useState<Links | null>(null);
  const [results, setResults] = useState<Results | null>(null);
  const [failures, setFailures] = useState<Failure[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [healthState, setHealthState] = useState<'checking' | 'live' | 'offline'>('checking');
  const [cycleId, setCycleId] = useState<string | null>(null);
  const [cycle, setCycle] = useState<Cycle | null>(null);
  const [cycleError, setCycleError] = useState<string | null>(null);
  const [status, setStatus] = useState<RunStatus>('idle');
  const [result, setResult] = useState<Prediction | null>(null);
  const [resultFor, setResultFor] = useState<string | null>(null);
  const [resultSource, setResultSource] = useState<ResultSource | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [startedAt, setStartedAt] = useState(0);
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [consoleCycle, setConsoleCycle] = useState<string | null>(null);
  const cache = useRef(new Map<string, Cycle>());
  const busy = useRef(false);
  const live = useRef(false);

  useEffect(() => {
    const fail = (what: string) => (e: Error) => setLoadError(`${what}: ${e.message}`);
    getManifest().then((m) => {
      setManifest(m);
      if ((m.schema_version ?? 0) < 2) setLoadError(`the export is schema v${m.schema_version ?? '?'}; this page needs v2 (run make export)`);
    }).catch(fail('manifest'));
    getSummary().then(setSummary).catch(fail('summary'));
    getIndex().then(setIndex).catch(fail('cycle index'));
    getDataset().then(setDataset).catch(() => undefined);
    getLinks().then(setLinks).catch(() => undefined);
    getResults().then(setResults).catch(() => undefined);
    getFailures().then(setFailures).catch(() => undefined);
    getHealth()
      .then((h) => { setHealth(h); setHealthState('live'); live.current = true; })
      .catch(() => { setHealthState('offline'); live.current = false; });
  }, []);

  const selectCycle = useCallback(async (id: string) => {
    setCycleId(id);
    setCycleError(null);
    const hit = cache.current.get(id);
    if (hit) { setCycle(hit); return hit; }
    try {
      const c = await getCycle(id);
      cache.current.set(id, c);
      setCycle(c);
      return c;
    } catch (e) {
      setCycleError((e as Error).message);
      return null;
    }
  }, []);

  // First cycle: ?cycle=ID deep link, else the best-scoring one.
  useEffect(() => {
    if (!index || cycleId) return;
    const want = new URLSearchParams(location.search).get('cycle');
    const ok = want && index.cycles.some((c) => c.id === want) ? want : pickDefault(index.cycles);
    if (ok) void selectCycle(ok);
  }, [index, cycleId, selectCycle]);

  const run = useCallback((id?: string) => {
    if (busy.current) return;
    const target = id ?? cycleId;
    if (!target) return;
    busy.current = true;
    setStatus('running');
    setRunError(null);
    setStartedAt(performance.now());
    const t0 = performance.now();
    const hold = <T,>(v: T) => new Promise<T>((res) => window.setTimeout(() => res(v), Math.max(0, MIN_RUN_MS - (performance.now() - t0))));
    (async () => {
      const c = await selectCycle(target);
      if (!c) throw new Error(`Could not load ${target}`);
      if (live.current) {
        try {
          const p = await diagnoseLive(target);
          return { p: await hold(p), src: 'live' as const };
        } catch {
          live.current = false;
          setHealthState('offline');
        }
      }
      return { p: await hold(c.prediction), src: 'precomputed' as const };
    })()
      .then(({ p, src }) => {
        setResult(p); setResultFor(target); setResultSource(src); setStatus('done');
        const u = new URL(location.href);
        u.searchParams.set('cycle', target);
        history.replaceState(null, '', u);
      })
      .catch((e: Error) => { setRunError(e.message); setStatus('error'); })
      .finally(() => { busy.current = false; });
  }, [cycleId, selectCycle]);

  const cited = useMemo(() => {
    const out: Record<string, 'ok' | 'bad'> = {};
    for (const c of result?.claims ?? []) {
      for (const s of c.sensor.split('/')) out[s] = out[s] === 'bad' || c.status !== 'verified' ? 'bad' : 'ok';
    }
    return out;
  }, [result]);

  // Scroll locking and focus handling live in ConsoleModal.
  const openConsole = useCallback((id: string | null = null) => { setConsoleCycle(id); setConsoleOpen(true); }, []);
  const closeConsole = useCallback(() => setConsoleOpen(false), []);

  const mock = Boolean(manifest?.mock || index?.mock || cycle?.mock);

  const value: Store = {
    manifest, summary, index, dataset, links, results, failures, loadError, health, healthState,
    cycleId, cycle, cycleError, selectCycle, status, result, resultFor, resultSource, runError, startedAt, run,
    consoleOpen, consoleCycle, openConsole, closeConsole, cited, mock,
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useStore() {
  const s = useContext(Ctx);
  if (!s) throw new Error('useStore outside StoreProvider');
  return s;
}

export function scrollToId(id: string) {
  const el = document.getElementById(id);
  if (!el) return;
  const lenis = (window as unknown as { __lenis?: { scrollTo: (t: Element, o?: object) => void } }).__lenis;
  if (lenis) lenis.scrollTo(el, { offset: -88, duration: 1.2 });
  else window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 72, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
}
