import { useEffect, useMemo, useRef, useState, type CSSProperties } from 'react';
import { animate, motion, useMotionValue } from 'motion/react';
import { Head } from './Story';
import { Fade, Reveal } from '../motion/Reveal';
import { COMP, cycleNo } from '../lib/data';
import { useStore } from '../lib/store';
import { renderDither } from '../gfx/canvas';
import { COMPONENTS, type Component, type Link } from '../lib/types';

const P3OUT = [0.33, 1, 0.68, 1] as const;

function linkLines(links: Link[] | undefined): string[] {
  if (!links?.length) return ['measuring links…'];
  const w = Math.max(...links.map((l) => l.feature.length)) + 2;
  return links.map((l) => {
    const arrow = l.direction === 'up' ? '↑' : '↓';
    const eff = `${l.effect >= 0 ? '+' : '−'}${Math.abs(l.effect).toFixed(2)}`;
    return `${l.feature.padEnd(w)}${arrow}  δ ${eff}${l.kept ? '' : '  (dropped)'}${l.virtual ? '  virtual' : ''}`;
  });
}

/**
 * The evidence list, one row per machine part. Rows rest at 20% and the hovered row lights up over .6 s;
 * a 24em card glides to the cursor's x and shows the physics links measured on the train split.
 * On touch screens the row in the middle of the viewport is active and shows its links inline.
 */
export function Evidence() {
  const { links } = useStore();
  const listRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(0);
  const [inside, setInside] = useState(false);
  const [canHover, setCanHover] = useState(true);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const bg = useMemo(() => (typeof document === 'undefined' ? '' : renderDither('wave', 240, 240, 2, ['#7f0fd5', '#e66157']).toDataURL()), []);

  useEffect(() => {
    const mq = matchMedia('(hover: hover) and (pointer: fine)');
    const set = () => setCanHover(mq.matches);
    set();
    mq.addEventListener('change', set);
    return () => mq.removeEventListener('change', set);
  }, []);

  useEffect(() => {
    if (canHover || !listRef.current) return;
    const rows = [...listRef.current.querySelectorAll<HTMLElement>('.rule-row')];
    const io = new IntersectionObserver((es) => {
      es.forEach((e) => { if (e.isIntersecting) setActive(Number((e.target as HTMLElement).dataset.i)); });
    }, { rootMargin: '-45% 0px -45% 0px' });
    rows.forEach((r) => io.observe(r));
    return () => io.disconnect();
  }, [canHover]);

  const place = (clientX: number, rowEl: HTMLElement | null) => {
    const list = listRef.current;
    if (!list || !rowEl) return;
    const lb = list.getBoundingClientRect();
    const card = list.querySelector<HTMLElement>('.rule-card');
    const cw = card?.offsetWidth ?? 300, ch = card?.offsetHeight ?? 300;
    const tx = Math.min(lb.width - cw, Math.max(0, clientX - lb.left - cw / 2));
    const ty = rowEl.offsetTop + rowEl.offsetHeight / 2 - ch / 2;
    animate(x, tx, { duration: 0.5, ease: P3OUT });
    animate(y, ty, { duration: 0.5, ease: P3OUT });
  };

  const rows = COMPONENTS.map((c) => ({ c, ...COMP[c], lines: linkLines(links?.[c]) }));

  return (
    <section className="sec" id="evidence" aria-labelledby="evidence-h">
      <div className="container"><div className="inner">
        <div className="pad rules-head">
          <Head id="evidence-h" eyebrow="The evidence" title="Four parts, each with its physics." sub="Every part is linked to the sensors that physically respond to it, and each link was kept only if the training data showed it. Point at a part (or scroll on a phone) to see the measured effect sizes." />
        </div>
        <div className={`rules-list ${canHover ? 'hoverable' : 'touch'} ${inside ? 'inside' : ''}`} ref={listRef}
          onPointerEnter={() => setInside(true)} onPointerLeave={() => setInside(false)}>
          {canHover && (
            <motion.div className={`rule-card ${inside ? 'on' : ''}`} style={{ x, y }} aria-hidden="true">
              <div className="rule-card-bg" style={{ backgroundImage: `url(${bg})` }} />
              {rows.map((r, i) => (
                <div key={r.c} className={`rule-code ${i === active ? 'on' : ''}`}>
                  <div className="t-mono rule-at">hydraulic_links.yaml · {r.c}</div>
                  <pre className="t-code">{r.lines.join('\n')}</pre>
                </div>
              ))}
            </motion.div>
          )}
          {rows.map((r, i) => (
            <Reveal key={r.c} amount={0.4} className={`rule-row ${i === active ? 'active' : ''}`}>
              <div data-i={i} className="rule-hit" tabIndex={0}
                onPointerEnter={(e) => { setActive(i); place(e.clientX, e.currentTarget.parentElement); }}
                onPointerMove={(e) => place(e.clientX, e.currentTarget.parentElement)}
                onFocus={(e) => { setActive(i); setInside(true); place(e.currentTarget.getBoundingClientRect().right - 260, e.currentTarget.parentElement); }}
                onBlur={() => setInside(false)}>
                <span className="rule-bar" />
                <Fade d={0}><h3 className="t-h3 rule-title">{r.title}</h3></Fade>
                <Fade as="p" className="t-small rule-text" d={0.15}>{r.text}</Fade>
                {!canHover && (
                  <div className="rule-inline" aria-hidden={i !== active}>
                    <div className="t-mono rule-at">hydraulic_links.yaml · {r.c}</div>
                    <pre className="t-code">{r.lines.join('\n')}</pre>
                  </div>
                )}
              </div>
            </Reveal>
          ))}
        </div>
      </div></div>
    </section>
  );
}

/** The sensors as a grid. Cells brighten slowly, staggered by column; sensors the latest diagnosis cites glow. */
export function SensorGrid() {
  const { dataset, cited, resultFor } = useStore();
  const [focus, setFocus] = useState<number | null>(null);
  const cols = 9;
  const sensors = dataset?.sensors ?? [];
  const citedNames = Object.keys(cited);
  const bad = citedNames.filter((n) => cited[n] === 'bad');
  const f = focus != null ? sensors[focus] : null;
  return (
    <section className="sec" aria-labelledby="sensors-h">
      <div className="container"><div className="inner">
        <div className="pad codes-head">
          <Head id="sensors-h" eyebrow="Sensors" title="Every claim names one of these." sub="An explanation may only cite a sensor that exists, in its own unit. Anything else is counted as a hallucinated sensor." />
        </div>
        <Reveal className="codes sensors" amount={0.15}>
          {sensors.map((s, i) => (
            <button key={s.name} type="button"
              className={`code ${cited[s.name] === 'ok' ? 'hit-ok' : cited[s.name] === 'bad' ? 'hit' : ''}`}
              style={{ '--c': i % cols } as CSSProperties}
              onPointerEnter={() => setFocus(i)} onFocus={() => setFocus(i)} onPointerLeave={() => setFocus(null)} onBlur={() => setFocus(null)}
              aria-describedby="sensor-msg">
              <span className="code-n t-code">{s.name}</span>
              <span className="code-name">{s.unit} · {s.rate_hz} Hz</span>
            </button>
          ))}
          {sensors.length > 0 && sensors.length % cols !== 0 && (
            <span className="code code-fill" style={{ '--c': sensors.length % cols } as CSSProperties} aria-hidden="true">
              <span className="code-n t-code">Σ</span><span className="code-name">native rates</span>
            </span>
          )}
        </Reveal>
        <p id="sensor-msg" className="codes-msg t-small" aria-live="polite">
          {f
            ? <><b className="t-code">{f.name}</b> — {f.description} ({f.source}, {f.n_samples.toLocaleString('en-US')} samples per cycle)</>
            : citedNames.length && resultFor
              ? <>Lit cells: sensors cited in the cycle {cycleNo(resultFor)} diagnosis{bad.length ? <> · coral: a claim on {bad.join(', ')} did not verify</> : ' · every claim verified'}.</>
              : <>Hover or focus a sensor to read it. Run a diagnosis and the sensors it cites light up.</>}
        </p>
      </div></div>
    </section>
  );
}


