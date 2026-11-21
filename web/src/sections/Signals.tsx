import { memo, useMemo } from 'react';
import { motion } from 'motion/react';
import { SOURCE_LABEL, SOURCE_ORDER } from '../lib/data';
import type { Claim, Cycle } from '../lib/types';

const EASE = [0.25, 0.46, 0.45, 0.94] as const;

/** Min/max decimation so a 600-point series stays crisp at any width. */
function points(values: number[], w: number, h: number, lo: number, hi: number, maxPts = 300) {
  const n = values.length;
  if (!n) return '';
  const span = hi - lo || 1;
  const step = Math.max(1, Math.ceil(n / maxPts));
  const out: string[] = [];
  for (let i = 0; i < n; i += step) {
    let mn = Infinity, mx = -Infinity;
    for (let j = i; j < Math.min(n, i + step); j++) { mn = Math.min(mn, values[j]); mx = Math.max(mx, values[j]); }
    const x = (i / Math.max(1, n - 1)) * w;
    out.push(`${x.toFixed(1)},${(h - ((mx - lo) / span) * h).toFixed(1)}`);
    if (step > 1) out.push(`${x.toFixed(1)},${(h - ((mn - lo) / span) * h).toFixed(1)}`);
  }
  return out.join(' ');
}

interface ChartProps {
  name: string; source?: string; unit: string; rate: number; values: number[];
  band?: { mean: number; std: number } | null;
  state: 'ok' | 'bad' | 'idle'; hot: boolean; window?: [number, number] | null; delay?: number;
}

export const SignalChart = memo(function SignalChart({ name, source, unit, rate, values, band, state, hot, window: win, delay = 0 }: ChartProps) {
  const W = 300, H = 80;
  const dur = values.length / Math.max(rate, 1e-9);
  const { lo, hi, mean } = useMemo(() => {
    let a = Infinity, b = -Infinity, s = 0;
    for (const v of values) { a = Math.min(a, v); b = Math.max(b, v); s += v; }
    if (band) { a = Math.min(a, band.mean - band.std); b = Math.max(b, band.mean + band.std); }
    const pad = (b - a) * 0.12 || Math.abs(a) * 0.05 || 1;
    return { lo: a - pad, hi: b + pad, mean: values.length ? s / values.length : 0 };
  }, [values, band]);
  const pts = useMemo(() => points(values, W, H, lo, hi), [values, lo, hi]);
  const y = (v: number) => H - ((v - lo) / (hi - lo || 1)) * H;
  const stroke = state === 'ok' ? 'var(--violet-2)' : state === 'bad' ? 'var(--coral)' : 'var(--text-mute)';
  return (
    <figure className={`sig ${state} ${hot ? 'hot' : ''}`}>
      <figcaption>
        <span className="t-code sig-name">{name}</span>
        <span className="t-mono sig-meta">{source ? `${source} · ` : ''}{unit} · {rate} Hz</span>
        <span className="t-code sig-mean">μ {Math.abs(mean) >= 100 ? mean.toFixed(1) : mean.toFixed(2)}</span>
      </figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" aria-hidden="true">
        {band && <rect x={0} width={W} y={y(band.mean + band.std)} height={Math.max(1, y(band.mean - band.std) - y(band.mean + band.std))} className="sig-band" />}
        {win && dur > 0 && <rect className="sig-win" x={(Math.max(0, win[0]) / dur) * W} width={Math.max(2, ((Math.min(dur, win[1]) - Math.max(0, win[0])) / dur) * W)} y={0} height={H} />}
        <motion.polyline points={pts} fill="none" stroke={stroke} strokeWidth={hot ? 2 : 1.2} vectorEffect="non-scaling-stroke"
          initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ duration: 0.9, delay, ease: EASE }} />
      </svg>
    </figure>
  );
});

/** Sensor charts grouped by source. Cited sensors first; the hot claim's sensor and time window are highlighted. */
export function SensorPanel({ cycle, claims, hot, showAll }: { cycle: Cycle; claims: Claim[]; hot: number | null; showAll: boolean }) {
  const state: Record<string, 'ok' | 'bad'> = {};
  for (const c of claims) for (const s of c.sensor.split('/')) state[s] = state[s] === 'bad' || c.status !== 'verified' ? 'bad' : 'ok';
  const hotClaim = hot != null ? claims[hot] : null;
  const hotSensors = new Set(hotClaim ? hotClaim.sensor.split('/') : []);
  const names = Object.keys(cycle.signals)
    .filter((n) => showAll || state[n])
    .sort((a, b) => SOURCE_ORDER.indexOf(cycle.signals[a].source) - SOURCE_ORDER.indexOf(cycle.signals[b].source));
  return (
    <div className="sig-grid">
      {names.map((n, k) => {
        const s = cycle.signals[n];
        const band = cycle.reference?.[`${n}.mean`] ?? null;
        return (
          <SignalChart key={`${cycle.id}-${n}`} name={n} source={SOURCE_LABEL[s.source] ?? s.source} unit={s.unit} rate={s.rate_hz} values={s.values} band={band}
            state={state[n] ?? 'idle'} hot={hotSensors.has(n)} window={hotSensors.has(n) ? hotClaim?.window : null} delay={0.05 * k} />
        );
      })}
    </div>
  );
}
