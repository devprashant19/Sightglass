import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Button, Eyebrow } from '../ui/Button';
import { DATA_ROOT, diagnoseLive, getWhatIf } from '../lib/api';
import { COMP, cycleNo, isHealthy } from '../lib/data';
import { useStore } from '../lib/store';
import { COMPONENTS, type Prediction, type WhatIf as WhatIfData, type WhatIfPoint } from '../lib/types';

const KINDS: Array<{ type: 'flow' | 'temperature' | 'ripple'; title: string; note: string; unit: string }> = [
  { type: 'flow', title: 'Reduce flow', note: 'Scale FS1 and FS2 down, as a leaking pump would. Motor power is left as it was.', unit: '%' },
  { type: 'temperature', title: 'Raise temperature', note: 'Add a constant offset to TS1–TS4, as a failing cooler would.', unit: '°C' },
  { type: 'ripple', title: 'Add pressure ripple', note: 'Amplify the variation of PS1–PS6 around their mean, as a weak accumulator would.', unit: '%' },
];

const fmtAmt = (type: string, a: number) => (a === 0 ? 'none' : `${a > 0 ? '+' : '−'}${Math.abs(a)}${type === 'temperature' ? ' °C' : '%'}`);

/** What-if lab: perturb a healthy cycle and watch the diagnosis and the evidence change. Precomputed grid, or live when the API is up. */
export function WhatIf() {
  const { healthState } = useStore();
  const [ids, setIds] = useState<string[]>([]);
  const [id, setId] = useState<string | null>(null);
  const [data, setData] = useState<WhatIfData | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [kind, setKind] = useState<'flow' | 'temperature' | 'ripple'>('flow');
  const [step, setStep] = useState(0);
  const [live, setLive] = useState<{ key: string; p: Prediction } | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`${DATA_ROOT}/hydraulic/whatif/index.json`).then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((j: { cycles: string[] }) => { setIds(j.cycles ?? []); setId((j.cycles ?? [])[0] ?? null); })
      .catch((e: Error) => setErr(`what-if index: ${e.message}`));
  }, []);
  useEffect(() => {
    if (!id) return;
    setData(null); setLive(null);
    getWhatIf(id).then(setData).catch((e: Error) => setErr(e.message));
  }, [id]);

  const base = data?.grid.find((g) => g.type === 'baseline' || g.amount === 0) ?? null;
  const ladder: WhatIfPoint[] = useMemo(() => {
    if (!data) return [];
    const pts = data.grid.filter((g) => g.type === kind).sort((a, b) => Math.abs(a.amount) - Math.abs(b.amount));
    return base ? [{ ...base, type: kind, label: 'none' }, ...pts] : pts;
  }, [data, kind, base]);
  const cur = ladder[Math.min(step, Math.max(0, ladder.length - 1))];
  useEffect(() => { setStep(0); setLive(null); }, [kind, id]);

  const key = `${id}-${kind}-${cur?.amount}`;
  const p = live && live.key === key ? live.p : cur?.prediction;
  const runLive = async () => {
    if (!id || !cur) return;
    setBusy(true); setErr(null);
    try {
      const out = await diagnoseLive(id, cur.amount ? [{ type: kind, amount: cur.amount }] : []);
      setLive({ key, p: out });
    } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  };
  const k = KINDS.find((x) => x.type === kind)!;

  return (
    <section className="sec" id="whatif" aria-labelledby="whatif-h">
      <div className="container"><div className="inner pad plan">
        <div className="plan-head">
          <Eyebrow>What-if lab</Eyebrow>
          <h2 className="t-h2" id="whatif-h">Break a healthy cycle on purpose.</h2>
          <p className="t-small">Start from a healthy test cycle, inject a fault into its signals, and see whether Sightglass names the right part and cites the sensor you changed. Every step on the slider was run through the same engine; with the live API running you can re-run any step yourself.</p>
        </div>
        <div className="plan-grid">
          <div className="plan-left">
            <label className="fld">
              <span className="t-mono">Healthy cycle</span>
              <select value={id ?? ''} onChange={(e) => setId(e.target.value)} disabled={!ids.length}>
                {ids.map((x) => <option key={x} value={x}>Cycle {cycleNo(x)}</option>)}
              </select>
            </label>
            <div className="plan-presets" role="radiogroup" aria-label="Fault to inject">
              {KINDS.map((x) => (
                <button key={x.type} type="button" role="radio" aria-checked={kind === x.type} className={`mode ${kind === x.type ? 'on' : ''}`} onClick={() => setKind(x.type)}>
                  <b>{x.title}</b><span>{x.note}</span>
                </button>
              ))}
            </div>
            <label className="fld wide">
              <span className="t-mono">Amount · {cur ? fmtAmt(kind, cur.amount) : '…'}</span>
              <input className="range" type="range" min={0} max={Math.max(0, ladder.length - 1)} step={1} value={Math.min(step, Math.max(0, ladder.length - 1))}
                onChange={(e) => { setStep(Number(e.target.value)); setLive(null); }} disabled={ladder.length < 2} aria-valuetext={cur ? fmtAmt(kind, cur.amount) : ''} />
              <span className="range-ticks t-mono" aria-hidden="true">{ladder.map((g) => <i key={g.amount}>{fmtAmt(kind, g.amount)}</i>)}</span>
            </label>
            {healthState === 'live' && <div><Button label={busy ? 'Diagnosing…' : 'Re-run this step live'} busy={busy} disabled={busy || !cur} onClick={runLive} /></div>}
          </div>
          <div className="plan-out" aria-live="polite">
            {err && <div className="bubble err" role="alert">{err}</div>}
            {!err && !p && <p className="t-small chat-empty">Loading the precomputed grid…</p>}
            {p && (
              <div>
                <div className="plan-sum">
                  <span className={`verdict ${COMPONENTS.every((c) => isHealthy(c, p.labels[c]?.value)) ? 'allow' : 'deny'}`}>
                    {COMPONENTS.every((c) => isHealthy(c, p.labels[c]?.value)) ? 'Still healthy' : `Fault found: ${COMPONENTS.filter((c) => !isHealthy(c, p.labels[c]?.value)).map((c) => COMP[c].short).join(', ')}`}
                  </span>
                  <span className="t-small">{!cur || cur.amount === 0 ? 'no change applied' : `${k.title.toLowerCase()} by ${Math.abs(cur.amount)}${kind === 'temperature' ? ' °C' : '%'}`} · {p.claims.filter((c) => c.status === 'verified').length}/{p.claims.length} claims verified · {live && live.key === key ? 'live' : 'precomputed'}</span>
                </div>
                <ol className="plan-steps">
                  {COMPONENTS.map((c, ci) => {
                    const l = p.labels[c];
                    const was = base?.prediction.labels[c];
                    const changed = was && l && was.value !== l.value;
                    return (
                      <li key={c} className={l && isHealthy(c, l.value) ? 'ok' : 'no'}>
                        <span className="t-code">{String(ci + 1).padStart(2, '0')}</span>
                        <div className="plan-desc"><div>{COMP[c].title}</div><div className="t-code step-meta">{changed ? `changed from ${was!.name}` : 'unchanged'}</div></div>
                        <AnimatePresence mode="popLayout" initial={false}>
                          <motion.span key={`${c}-${l?.value}`} className={`verdict ${l && isHealthy(c, l.value) ? 'allow' : 'deny'}`}
                            initial={{ rotateX: 90, opacity: 0 }} animate={{ rotateX: 0, opacity: 1 }} exit={{ rotateX: -90, opacity: 0 }} transition={{ duration: 0.35 }}>
                            {l && isHealthy(c, l.value) ? 'HEALTHY' : 'FAULT'}<em>{l?.name}</em>
                          </motion.span>
                        </AnimatePresence>
                        <span />
                        <span className={changed ? 'down' : 'up'} aria-hidden="true">{changed ? '●' : '·'}</span>
                      </li>
                    );
                  })}
                </ol>
                <p className="t-small plan-legend whatif-text">{p.rationale.split('\n').find((line) => !isHealthyLine(line)) ?? p.rationale.split('\n')[0]}</p>
              </div>
            )}
          </div>
        </div>
      </div></div>
    </section>
  );
}

/** A paragraph whose label line names a healthy state. */
function isHealthyLine(line: string) {
  return /:\s*(full efficiency|optimal|no leakage)\./i.test(line);
}
