import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Button, Eyebrow } from '../ui/Button';
import { Chars, Fade, Reveal, T } from '../motion/Reveal';
import { Odometer } from '../motion/Odometer';
import { DitherArt } from '../gfx/Art';
import { Grid } from '../motion/Ambient';
import { COMP, HEALTHY, cycleNo, isHealthy } from '../lib/data';
import { scrollToId, useStore } from '../lib/store';
import { COMPONENTS, type Component, type Cycle, type IndexItem, type Label, type Prediction } from '../lib/types';
import { ParaText, claimsIn, paragraphsOf } from './Rationale';
import { SensorPanel } from './Signals';

const EASE = [0.25, 0.46, 0.45, 0.94] as const;

const short = (comp: Component, v: number) => (comp === 'pump_leakage' ? `leak ${v}` : comp === 'accumulator_pressure' ? `${v} bar` : `${v}%`);

/** Interesting starting points, picked from the real test index. */
export function presetsOf(items: IndexItem[]) {
  const fault = (c: IndexItem, comp: Component) => !isHealthy(comp, c.true_labels[comp]);
  const good = (c: IndexItem) => c.correct === 4 && c.is_faithful;
  // Each example gets its own cycle where possible, preferring ones diagnosed fully right.
  const used = new Set<string>();
  const pick = (label: string, f: (c: IndexItem) => boolean) => {
    const c = items.find((x) => f(x) && good(x) && !used.has(x.id)) ?? items.find((x) => f(x) && !used.has(x.id)) ?? items.find(f);
    if (c) used.add(c.id);
    return c ? { label, id: c.id } : null;
  };
  return [
    pick('Healthy cycle', (c) => c.healthy || COMPONENTS.every((k) => !fault(c, k))),
    pick('Cooler failing', (c) => c.true_labels.cooler_condition === 3),
    pick('Valve lag', (c) => c.true_labels.valve_condition <= 80 && !fault(c, 'cooler_condition')),
    pick('Pump leaking', (c) => c.true_labels.pump_leakage === 2),
    pick('Weak accumulator', (c) => c.true_labels.accumulator_pressure === 90),
    (() => { const c = items.find((x) => x.correct < 4) ?? items.find((x) => !good(x)); return c ? { label: 'A miss', id: c.id } : null; })(),
  ].filter((x): x is { label: string; id: string } => x !== null);
}

/** Dashboard tile: idles by cycling test cycles every 1.7 s; chips swap 100 ms apart, bars re-weight. */
function Mosaic() {
  const { index, status } = useStore();
  const rows = useMemo(() => {
    const items = index?.cycles ?? [];
    const ids = [...new Set(presetsOf(items).map((p) => p.id))];
    const ps = ids.map((id) => items.find((c) => c.id === id)!).filter(Boolean);
    return ps.length ? ps.slice(0, 5) : items.slice(0, 5);
  }, [index]);
  const [k, setK] = useState(0);
  useEffect(() => {
    if (!rows.length) return;
    const id = window.setInterval(() => setK((v) => (v + 1) % rows.length), status === 'running' ? 600 : 1700);
    return () => window.clearInterval(id);
  }, [rows.length, status]);
  const cur = rows[k % Math.max(1, rows.length)];
  const chips: Array<[string, string, boolean | null]> = cur ? [
    ['CYCLE', cycleNo(cur.id), null],
    ...COMPONENTS.map((c): [string, string, boolean | null] => [COMP[c].short.toUpperCase(), short(c, cur.predicted_labels[c]), isHealthy(c, cur.predicted_labels[c])]),
  ] : [];
  const maxClaims = Math.max(1, ...rows.map((r) => r.total_claims));
  return (
    <div className={`mosaic ${status === 'running' ? 'busy' : ''}`} aria-hidden="true">
      <Grid seed={33} dots={5} />
      <div className="mz-chips">
        {chips.map(([kx, v, ok], j) => (
          <div className="chip" key={kx}>{kx}
            <AnimatePresence mode="popLayout" initial={false}>
              <motion.b key={`${kx}-${v}`} initial={{ y: 10, opacity: 0, filter: 'blur(6px)' }} animate={{ y: 0, opacity: 1, filter: 'blur(0px)' }}
                exit={{ y: -10, opacity: 0, filter: 'blur(6px)' }} transition={{ duration: 0.45, delay: j * 0.1, ease: EASE }}
                className={ok == null ? '' : ok ? 'is-allow' : 'is-deny'}>{v}</motion.b>
            </AnimatePresence>
          </div>
        ))}
      </div>
      <div className="mz-agent"><DitherArt kind="pump" /></div>
      <svg className="mz-bars" viewBox="0 0 300 140" preserveAspectRatio="none">
        {rows.map((r, j) => {
          const h = 20 + (r.verified_claims / maxClaims) * 100;
          const miss = r.total_claims - r.verified_claims;
          const x = 18 + j * 58;
          return (
            <g key={r.id} opacity={j === k % rows.length ? 1 : 0.42} style={{ transition: 'opacity .4s' }}>
              <motion.rect x={x} width="26" fill={r.correct === 4 ? 'var(--violet)' : 'var(--violet-deep)'} initial={false} animate={{ y: 140 - h, height: h }} transition={{ type: 'spring', stiffness: 120, damping: 18 }} />
              {miss > 0 && <motion.rect x={x} width="26" height="5" fill="var(--coral)" initial={false} animate={{ y: 140 - h - 7 }} transition={{ type: 'spring', stiffness: 120, damping: 18 }} />}
            </g>
          );
        })}
      </svg>
      <div className="mz-stack"><DitherArt kind="stack" /></div>
      <div className="mz-fp">
        <div className="t-mono">CLAIMS</div>
        <div className="mz-fp-row"><span className="t-code">STATED</span><span className="t-code">{cur?.total_claims ?? '…'}</span></div>
        <div className="mz-fp-row"><span className="t-code">VERIFIED</span><span className="t-code">{cur?.verified_claims ?? '…'}</span></div>
        <svg viewBox="0 0 200 40" className="mz-fp-svg"><path d="M2 8 C 70 8, 90 20, 120 20 L 198 20" /><path d="M2 32 C 70 32, 90 20, 120 20" /><rect x="118" y="16" width="8" height="8" /></svg>
        <div className={`t-mono mz-fp-eq ${cur && cur.verified_claims < cur.total_claims ? 'miss' : ''}`}>
          {!cur ? '…' : cur.verified_claims === cur.total_claims ? '= ALL MATCH THE SIGNAL' : `≠ ${cur.total_claims - cur.verified_claims} DID NOT MATCH`}
        </div>
      </div>
    </div>
  );
}

const LOG = [
  (c: Cycle) => `load cycle ${cycleNo(c.id)} · ${Object.keys(c.signals).length} signals at native rate`,
  (c: Cycle) => `extract ${Object.keys(c.features ?? {}).length || 'the'} physics features`,
  () => 'compare each feature with the healthy reference',
  () => 'classify cooler, valve, pump and accumulator',
  () => 'write the evidence for each part',
  () => 'recompute every stated number from the signal',
];

/** Streaming log while a diagnosis runs: one real pipeline step every ~350 ms. */
function RunLog({ cycle, startedAt }: { cycle: Cycle | null; startedAt: number }) {
  const [now, setNow] = useState(performance.now());
  useEffect(() => { const id = window.setInterval(() => setNow(performance.now()), 90); return () => window.clearInterval(id); }, []);
  const ms = Math.max(0, now - startedAt);
  const shown = Math.min(LOG.length, 1 + Math.floor(ms / 360));
  return (
    <div className="runlog t-code" role="status" aria-live="polite">
      {LOG.slice(0, shown).map((f, i) => (
        <motion.div className="runlog-line" key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3 }}>
          <span className="runlog-t">{(i * 0.36).toFixed(2)}s</span><span>{cycle ? f(cycle) : 'loading the cycle…'}</span>
        </motion.div>
      ))}
      <div className="runlog-line"><span className="runlog-t" /><span className="runlog-caret" /></div>
    </div>
  );
}

function Verdict({ label, comp, delay, kind }: { label: Label; comp: Component; delay: number; kind?: 'truth' }) {
  const ok = isHealthy(comp, label.value);
  return (
    <motion.span className={`verdict ${ok ? 'allow' : 'deny'} ${kind ?? ''}`} initial={{ rotateX: 90, opacity: 0 }} animate={{ rotateX: 0, opacity: 1 }} transition={{ duration: 0.5, delay, ease: EASE }}>
      {ok ? 'HEALTHY' : 'FAULT'}<em>{label.name}</em>
    </motion.span>
  );
}

function Tick({ ok, delay, label }: { ok: boolean; delay: number; label: string }) {
  return (
    <svg viewBox="0 0 24 24" className={`tick ${ok ? 'ok' : 'bad'}`} role="img" aria-label={label}>
      <motion.path d={ok ? 'M4 12.5 L9.5 18 L20 6' : 'M6 6 L18 18 M18 6 L6 18'} fill="none" strokeWidth="2.4" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.5, delay }} />
    </svg>
  );
}

function Results({ cycle, p, source }: { cycle: Cycle; p: Prediction; source: 'live' | 'precomputed' | null }) {
  const [hot, setHot] = useState<number | null>(null);
  const [showAll, setShowAll] = useState(false);
  const [copied, setCopied] = useState(false);
  const paras = paragraphsOf(p);
  const correct = COMPONENTS.filter((c) => p.labels[c]?.value === cycle.true_labels[c]?.value).length;
  const verified = p.claims.filter((c) => c.status === 'verified').length;
  const top = Object.entries(cycle.features ?? {})
    .filter(([, f]) => f.z != null && Number.isFinite(f.z))
    .sort((a, b) => Math.abs(b[1].z ?? 0) - Math.abs(a[1].z ?? 0))
    .slice(0, 6);
  const share = () => {
    const u = new URL(location.href);
    u.searchParams.set('cycle', cycle.id);
    u.hash = 'explore';
    navigator.clipboard?.writeText(u.toString()).then(() => { setCopied(true); window.setTimeout(() => setCopied(false), 1600); }).catch(() => undefined);
  };
  return (
    <>
      {source === 'precomputed' && (
        <div className="replay-banner" role="note">
          Precomputed result from the static export: the live engine is not running here, so this is the same pipeline run ahead of time on this cycle. Start it locally with <code className="t-code">make api</code> to diagnose live.
        </div>
      )}
      <div className="demo-sum">
        <div><div className="t-mono">Parts diagnosed correctly</div><div className={`t-h2 ${correct === 4 ? 'ok' : 'bad'}`}><Odometer value={`${correct}/4`} play /></div><div className="demo-sub">against the rig's recorded condition</div></div>
        <div><div className="t-mono">Claims verified</div><div className={`t-h2 ${verified === p.claims.length ? 'ok' : 'bad'}`}><Odometer value={`${verified}/${p.claims.length}`} play /></div><div className="demo-sub">each recomputed from this cycle's signal</div></div>
        <div><div className="t-mono">Cycle</div><div className="t-h2"><Odometer value={cycleNo(cycle.id)} play /></div><div className="demo-sub">{cycle.meta.stable_flag === 0 ? 'stable operating conditions' : 'conditions not yet stable'}</div></div>
        <div><div className="t-mono">Engine</div><div className="t-h4">{source === 'live' ? 'Live' : 'Precomputed'}</div><div className="demo-sub">{p.model}{p.latency_ms != null ? ` · ${Math.round(p.latency_ms)} ms` : ''}</div></div>
      </div>
      <ol className="steps dx-steps">
        {COMPONENTS.map((comp, k) => {
          const d = 0.15 + k * 0.22;
          const para = paras.find((q) => q.component === comp);
          const pl = p.labels[comp];
          const tl = cycle.true_labels[comp];
          const match = pl?.value === tl?.value;
          const cl = para ? claimsIn(p, para) : [];
          return (
            <motion.li className="step dx-step" key={comp} initial={{ opacity: 0, y: 24, filter: 'blur(10px)' }} animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }} transition={{ duration: 0.6, delay: d, ease: EASE }}>
              <span className="step-n t-code">{String(k + 1).padStart(2, '0')}</span>
              <div className="step-desc"><div>{COMP[comp].title}</div><div className="t-code step-meta">{cl.length} claims · {cl.filter((c) => c.claim.status === 'verified').length} verified · healthy is {short(comp, HEALTHY[comp])}</div>
                {p.consistency?.[comp] != null && <div className={`t-code step-meta cons-flag ${p.consistency[comp] ? 'ok' : 'bad'}`}>{p.consistency[comp] ? 'evidence supports this label' : 'evidence does not clearly support this label'}</div>}</div>
              <div className="step-col"><div className="t-mono">Sightglass said</div>{pl && <Verdict label={pl} comp={comp} delay={d + 0.25} />}</div>
              <div className="step-col"><div className="t-mono">Rig recorded</div>{tl && <Verdict label={tl} comp={comp} delay={d + 0.4} kind="truth" />}</div>
              <Tick ok={match} delay={d + 0.6} label={match ? 'Diagnosis matches the recorded condition' : 'Diagnosis does not match the recorded condition'} />
              {para && <div className="dx-para"><ParaText p={p} para={para} hot={hot} setHot={setHot} /></div>}
            </motion.li>
          );
        })}
      </ol>
      <div className="dx-signals">
        <div className="wt-top">
          <div className="t-mono wt-h">Signals · {showAll ? 'all sensors' : 'sensors cited above'} · band = healthy mean ± 1<span className="lc">σ</span></div>
          <div className="wt-ctrl">
            <button type="button" onClick={() => setShowAll((v) => !v)} aria-pressed={showAll}>{showAll ? 'Cited only' : 'Show all sensors'}</button>
          </div>
        </div>
        <SensorPanel cycle={cycle} claims={p.claims} hot={hot} showAll={showAll} />
      </div>
      <div className="demo-foot">
        <div>
          <div className="t-mono demo-foot-h">Largest deviations from healthy</div>
          <table className="bal">
            <thead><tr><th>Feature</th><th>Value</th><th>Healthy</th><th>z</th></tr></thead>
            <tbody>
              {top.map(([name, f]) => {
                const ref = cycle.reference?.[name];
                return (
                  <tr key={name}><td className="t-code">{name}</td><td className="t-code">{f.value.toPrecision(4)} {f.unit}</td>
                    <td className="t-code">{ref ? ref.mean.toPrecision(4) : '–'}</td>
                    <td className={`t-code ${(f.z ?? 0) > 0 ? 'down' : 'up'}`}>{(f.z ?? 0) >= 0 ? '+' : ''}{(f.z ?? 0).toFixed(1)}</td></tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div>
          <div className="t-mono demo-foot-h">How this answer was made</div>
          <div className="fp"><span className="t-mono">Diagnosis</span><code className="t-code">{p.model}</code></div>
          <div className="fp"><span className="t-mono">Evidence</span><code className="t-code">computed from cycle {cycleNo(cycle.id)}'s own signals, then checked by the faithfulness checker</code></div>
          <div className="fp"><span className="t-mono">Consistency</span><code className="t-code">{p.consistency ? `${Object.values(p.consistency).filter(Boolean).length}/${Object.keys(p.consistency).length} paragraphs support their label` : 'not reported'}</code></div>
          <Button label={copied ? 'Link copied' : 'Copy a link to this cycle'} variant="ghost" onClick={share} />
        </div>
      </div>
    </>
  );
}

export function Explorer() {
  const { index, cycleId, cycle, selectCycle, status, run, result, resultFor, resultSource, runError, startedAt, openConsole, cycleError, linkNotice } = useStore();
  const items = index?.cycles ?? [];
  const presets = useMemo(() => presetsOf(items), [items]);
  const sorted = useMemo(() => [...items].sort((a, b) => a.cycle_index - b.cycle_index), [items]);
  const shownCycle = cycle && resultFor === cycle.id ? cycle : null;
  const go = (id: string) => { run(id); window.setTimeout(() => scrollToId('explore-run'), 80); };
  return (
    <section className="sec" id="explore" aria-labelledby="explore-h">
      <div className="container"><div className="inner">
        <div className="pad demo-top">
          <Reveal className="demo-copy">
            <span className="rule" style={{ top: '2.2em', height: '4em' }} />
            <Fade d={0}><Eyebrow>Diagnosis explorer</Eyebrow></Fade>
            <h2 className="t-h1" id="explore-h"><Chars text="Watch it find the worn part." d={0.1} /></h2>
            <Fade as="p" className="t-p" d={T.para}>
              Pick a held-out test cycle the model never trained on. Sightglass diagnoses all four parts, writes its evidence, and checks every number against the signal. Point at a claim to see the sensor it came from.
            </Fade>
            <Fade d={T.button} dur={0.6} className="demo-actions">
              <Button label={status === 'running' ? 'Diagnosing…' : resultFor ? 'Run it again' : 'Run a diagnosis'} busy={status === 'running'} disabled={status === 'running' || !cycleId} onClick={() => cycleId && go(cycleId)} />
              <Button label="Ask about a cycle" variant="ghost" onClick={() => openConsole(cycleId)} />
            </Fade>
            <Fade d={T.button + 0.15} className="dx-pick">
              <label className="fld">
                <span className="t-mono">Test cycle</span>
                <select value={cycleId ?? ''} onChange={(e) => { void selectCycle(e.target.value); }} disabled={!items.length}>
                  {sorted.map((c) => (
                    <option key={c.id} value={c.id}>
                      {cycleNo(c.id)} · {COMPONENTS.map((k) => `${COMP[k].short} ${short(k, c.true_labels[k])}`).join(' · ')}
                    </option>
                  ))}
                </select>
              </label>
              <div className="presets" role="group" aria-label="Example cycles">
                {presets.map((p) => (
                  <button key={p.label} type="button" className={`preset ${p.id === cycleId ? 'on' : ''}`} disabled={status === 'running'} onClick={() => go(p.id)}>{p.label}</button>
                ))}
              </div>
            </Fade>
          </Reveal>
          <Mosaic />
        </div>
        <div className="demo-out" id="explore-run">
          {linkNotice && <div className="replay-banner" role="note">{linkNotice}</div>}
          {status === 'running' && <RunLog cycle={cycle} startedAt={startedAt} />}
          {status === 'error' && (
            <div className="demo-err" role="alert">
              <p>The diagnosis did not finish: {runError}</p>
              <div className="demo-err-actions">{cycleId && <Button label="Try again" variant="ghost" onClick={() => go(cycleId)} />}</div>
            </div>
          )}
          {status !== 'running' && result && shownCycle && <Results cycle={shownCycle} p={result} source={resultSource} />}
          {status !== 'running' && !(result && shownCycle) && status !== 'error' && (
            <div className="demo-idle">
              <div className="t-mono">{cycleError ? `Could not load the cycle: ${cycleError}` : cycleId ? `Cycle ${cycleNo(cycleId)} is ready. Run the diagnosis, or pick an example:` : 'Loading the test cycles…'}</div>
              <ul className="idle-list">
                {presets.map((p) => {
                  const it = items.find((c) => c.id === p.id)!;
                  return (
                    <li key={p.label}>
                      <span className="t-code">{cycleNo(p.id)}</span>
                      <button type="button" className="linkish" onClick={() => go(p.id)}>{p.label} — {COMPONENTS.filter((k) => !isHealthy(k, it.true_labels[k])).map((k) => COMP[k].short).join(', ') || 'no faults'}</button>
                      <span className={`verdict ${it.correct === 4 && it.is_faithful ? 'allow' : 'deny'}`}>{it.correct}/4 · {it.verified_claims}/{it.total_claims}</span>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </div>
      </div></div>
    </section>
  );
}
