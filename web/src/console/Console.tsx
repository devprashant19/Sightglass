import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Button, SightglassMark } from '../ui/Button';
import { diagnoseLive, getCycle } from '../lib/api';
import { COMP, cycleNo, isHealthy } from '../lib/data';
import { useStore } from '../lib/store';
import { COMPONENTS, type Component, type Cycle, type Prediction } from '../lib/types';
import { paragraphsOf } from '../sections/Rationale';

const EASE = [0.25, 0.46, 0.45, 0.94] as const;

type Ask = { kind: 'what' } | { kind: 'worst' } | { kind: 'healthy' } | { kind: 'part'; comp: Component };
const ASKS: Array<{ label: string; ask: Ask }> = [
  { label: 'What is wrong with it?', ask: { kind: 'what' } },
  { label: 'Is it healthy?', ask: { kind: 'healthy' } },
  { label: 'Which sensor deviates most?', ask: { kind: 'worst' } },
  ...COMPONENTS.map((c) => ({ label: `Evidence for the ${COMP[c].short.toLowerCase()}`, ask: { kind: 'part' as const, comp: c } })),
];

interface Exchange { id: number; cycle: string; question: string; state: 'thinking' | 'done' | 'error'; answer?: { cycle: Cycle; p: Prediction; source: 'live' | 'precomputed' }; ask: Ask; error?: string }

function question(ask: Ask, n: string) {
  switch (ask.kind) {
    case 'what': return `What is wrong with cycle ${n}?`;
    case 'healthy': return `Is cycle ${n} healthy?`;
    case 'worst': return `Which sensor in cycle ${n} deviates most from healthy?`;
    case 'part': return `Show me the evidence for the ${COMP[ask.comp].short.toLowerCase()} in cycle ${n}.`;
  }
}

function Answer({ ex }: { ex: Exchange }) {
  const { cycle, p, source } = ex.answer!;
  const paras = paragraphsOf(p);
  const faulty = COMPONENTS.filter((c) => !isHealthy(c, p.labels[c]?.value));
  const correct = COMPONENTS.filter((c) => p.labels[c]?.value === cycle.true_labels[c]?.value).length;
  const verified = p.claims.filter((c) => c.status === 'verified').length;
  const bubble = (key: string, head: string, body: string, ok: boolean | null, d: number) => (
    <motion.div className="bubble" key={key} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, delay: d, ease: EASE }}>
      <span className="t-mono">{head}</span>
      {ok != null && <span className={`verdict ${ok ? 'allow' : 'deny'}`}>{ok ? 'HEALTHY' : 'FAULT'}</span>}
      <span>{body}</span>
    </motion.div>
  );
  const out: JSX.Element[] = [];
  if (ex.ask.kind === 'what' || ex.ask.kind === 'healthy') {
    if (!faulty.length) out.push(bubble('none', 'Sightglass', 'All four parts look healthy. Every linked sensor is within its normal range for this rig.', true, 0));
    else if (ex.ask.kind === 'healthy') out.push(bubble('no', 'Sightglass', `No. ${faulty.map((c) => `${COMP[c].short}: ${p.labels[c].name}`).join(' · ')}.`, false, 0));
    (ex.ask.kind === 'what' ? faulty : []).forEach((c, i) => {
      const para = paras.find((q) => q.component === c);
      out.push(bubble(c, COMP[c].title, para?.text ?? p.labels[c].name, false, 0.1 + i * 0.12));
    });
  } else if (ex.ask.kind === 'worst') {
    const top = Object.entries(cycle.features ?? {}).filter(([, f]) => f.z != null && Number.isFinite(f.z)).sort((a, b) => Math.abs(b[1].z!) - Math.abs(a[1].z!))[0];
    out.push(bubble('worst', 'Largest deviation', top
      ? `${top[0]} = ${top[1].value.toPrecision(4)} ${top[1].unit}, ${top[1].z! >= 0 ? '+' : ''}${top[1].z!.toFixed(1)}σ from the healthy reference.`
      : 'This export has no feature table for the cycle.', null, 0));
  } else {
    const c = ex.ask.comp;
    const para = paras.find((q) => q.component === c);
    out.push(bubble(c, COMP[c].title, para?.text ?? p.labels[c]?.name ?? '–', isHealthy(c, p.labels[c]?.value), 0));
    const cl = p.claims.filter((x) => x.component === c);
    if (cl.length) out.push(bubble(`${c}-cl`, 'Checker', cl.map((x) => `${x.sensor} ${x.status === 'verified' ? '✓' : '✕ ' + x.status.replace('_', ' ')}`).join(' · '), null, 0.12));
  }
  return (
    <>
      {out}
      <div className={`match ${correct === 4 && verified === p.claims.length ? 'ok' : 'bad'}`}>
        <span>{correct === 4 ? '✓' : '✕'} {correct}/4 parts match the rig’s recorded condition · {verified}/{p.claims.length} claims verified against the signal</span>
        <span className="budget t-mono">{source === 'live' ? 'live engine' : 'precomputed export'} · {p.model}</span>
      </div>
    </>
  );
}

/** Ask Sightglass about a cycle. Answers are composed from the diagnosis itself, never generated free-form. */
export function Console({ startCycle, compact = false, onReady }: { startCycle?: string | null; compact?: boolean; onReady?: (focus: () => void) => void }) {
  const { index, cycleId, healthState } = useStore();
  const [cid, setCid] = useState<string>(startCycle ?? cycleId ?? '');
  const [log, setLog] = useState<Exchange[]>([]);
  const [busy, setBusy] = useState(false);
  const first = useRef<HTMLSelectElement>(null);
  const chat = useRef<HTMLDivElement>(null);
  const n = useRef(0);
  useEffect(() => { onReady?.(() => first.current?.focus()); }, [onReady]);
  useEffect(() => { if (!cid && (startCycle ?? cycleId)) setCid((startCycle ?? cycleId)!); }, [startCycle, cycleId, cid]);
  useEffect(() => { chat.current?.scrollTo({ top: chat.current.scrollHeight, behavior: 'smooth' }); }, [log]);

  const ask = async (a: Ask) => {
    if (!cid || busy) return;
    const id = ++n.current;
    setBusy(true);
    setLog((l) => [...l.slice(-5), { id, cycle: cid, question: question(a, cycleNo(cid)), state: 'thinking', ask: a }]);
    try {
      const cycle = await getCycle(cid);
      let p = cycle.prediction, source: 'live' | 'precomputed' = 'precomputed';
      if (healthState === 'live') { try { p = await diagnoseLive(cid); source = 'live'; } catch { /* fall back to the export */ } }
      await new Promise((r) => window.setTimeout(r, 450));
      setLog((l) => l.map((x) => (x.id === id ? { ...x, state: 'done', answer: { cycle, p, source } } : x)));
    } catch (e) {
      setLog((l) => l.map((x) => (x.id === id ? { ...x, state: 'error', error: (e as Error).message } : x)));
    } finally {
      setBusy(false);
    }
  };

  const items = index ? [...index.cycles].sort((a, b) => a.cycle_index - b.cycle_index) : [];
  return (
    <div className={`console ${compact ? 'compact' : ''}`}>
      <label className="fld">
        <span className="t-mono">Cycle</span>
        <select ref={first} value={cid} onChange={(e) => setCid(e.target.value)} disabled={!items.length}>
          {items.map((c) => <option key={c.id} value={c.id}>Cycle {cycleNo(c.id)} · {c.correct}/4 right · {c.verified_claims}/{c.total_claims} claims verified</option>)}
        </select>
      </label>
      <div className="presets" role="group" aria-label="Questions">
        {ASKS.map((q) => <button key={q.label} type="button" className="preset" disabled={busy || !cid} onClick={() => ask(q.ask)}>{q.label}</button>)}
      </div>
      <div className="chat" ref={chat} aria-live="polite" data-lenis-prevent>
        {!log.length && <div className="chat-empty t-small">Pick a cycle and a question. Answers are built from that cycle’s diagnosis and its checked evidence, not written free-form.</div>}
        <AnimatePresence initial={false}>
          {log.map((ex) => (
            <motion.div className="ex" key={ex.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
              <div className="bubble me">{ex.question}</div>
              {ex.state === 'thinking' && <div className="thinking"><span className="spin" /> Checking the evidence…</div>}
              {ex.state === 'error' && <div className="bubble err">Could not answer: {ex.error}</div>}
              {ex.state === 'done' && <Answer ex={ex} />}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
      {log.length > 0 && <div><Button label="Clear" variant="ghost" onClick={() => setLog([])} /></div>}
    </div>
  );
}

export function ConsoleModal() {
  const { consoleOpen, closeConsole, consoleCycle } = useStore();
  const panel = useRef<HTMLDivElement>(null);
  const focusFirst = useRef<() => void>(() => undefined);
  const lastFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const lenis = (window as unknown as { __lenis?: { stop: () => void; start: () => void } }).__lenis;
    if (consoleOpen) {
      lastFocus.current = document.activeElement as HTMLElement;
      lenis?.stop();
      document.documentElement.classList.add('modal-open');
      const t = window.setTimeout(() => focusFirst.current(), 420);
      return () => window.clearTimeout(t);
    }
    lenis?.start();
    document.documentElement.classList.remove('modal-open');
    lastFocus.current?.focus?.();
  }, [consoleOpen]);

  useEffect(() => {
    if (!consoleOpen) return;
    const key = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { e.preventDefault(); closeConsole(); return; }
      if (e.key !== 'Tab' || !panel.current) return;
      const f = [...panel.current.querySelectorAll<HTMLElement>('button:not([disabled]), input, select, textarea, a[href]')];
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    };
    addEventListener('keydown', key);
    return () => removeEventListener('keydown', key);
  }, [consoleOpen, closeConsole]);

  const step = (d: number) => ({ initial: { opacity: 0, y: -9 }, animate: { opacity: 1, y: 0 }, transition: { delay: d, duration: 0.35, ease: EASE } });

  return (
    <AnimatePresence>
      {consoleOpen && (
        <motion.div className="modal" role="dialog" aria-modal="true" aria-labelledby="console-title"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, transition: { duration: 0.25 } }} transition={{ duration: 0.2 }}
          onMouseDown={(e) => { if (e.target === e.currentTarget) closeConsole(); }} data-lenis-prevent="">
          <div className="modal-panel" ref={panel}>
            <motion.button className="modal-x" onClick={closeConsole} aria-label="Close" {...step(0)}>×</motion.button>
            <motion.div className="modal-bar" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2, duration: 0.35 }}>
              <SightglassMark size="1.1em" /><span>Ask Sightglass</span><span className="modal-bar-r t-mono">answers from checked evidence</span>
            </motion.div>
            <div className="modal-head">
              <motion.div className="modal-ico" {...step(0.23)}><SightglassMark size="1.6em" /></motion.div>
              <motion.h2 id="console-title" className="t-h3" initial={{ opacity: 0, y: -9, color: '#635f65' }} animate={{ opacity: 1, y: 0, color: '#efedf0' }} transition={{ delay: 0.37, duration: 0.45, ease: EASE }}>Ask about a cycle</motion.h2>
              <motion.p className="t-small" {...step(0.48)}>Every answer quotes the diagnosis and the evidence for that cycle, with the checker’s verdict on each number.</motion.p>
            </div>
            <div className="modal-clip">
              <motion.div initial={{ y: 25, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.09, duration: 0.4, ease: EASE }}>
                <Console startCycle={consoleCycle} compact onReady={(f) => { focusFirst.current = f; }} />
              </motion.div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/** Inline version (works without opening the modal). */
export function TrySection() {
  return (
    <section className="sec" id="ask" aria-labelledby="ask-h">
      <div className="container"><div className="inner pad try">
        <div className="try-copy">
          <div className="t-mono eyebrow">Ask it yourself</div>
          <h2 className="t-h2" id="ask-h">Question any cycle.</h2>
          <p className="t-small">Choose a held-out cycle and ask what is wrong, whether it is healthy, or for the evidence behind one part. Each answer carries the checker’s verdict on every number it quotes.</p>
        </div>
        <Console />
      </div></div>
    </section>
  );
}
