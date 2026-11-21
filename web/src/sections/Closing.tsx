import { useEffect, useRef, useState, type CSSProperties } from 'react';
import { motion, useMotionValue, useScroll, useSpring, useTransform } from 'motion/react';
import { Head } from './Story';
import { Chars, Fade, Reveal, T, useInViewOnce } from '../motion/Reveal';
import { ScrubChars } from '../motion/Scrub';
import { Rails, rng } from '../motion/Ambient';
import { Globe, PointCloud } from '../gfx/Art';
import { Button, Eyebrow, SightglassMark } from '../ui/Button';
import { REPO, UCI_URL } from '../lib/data';
import { scrollToId, useStore } from '../lib/store';

/** Dim line with a static blurred tail, then a sharp line 0.9 s later. */
export function Statement() {
  return (
    <section className="sec" aria-label="Why it matters">
      <div className="container"><div className="inner">
        <Reveal className="statement" amount={0.5}>
          <p className="t-h1 st-dim"><Chars text="Anyone can label a fault." st={0.034} tail={{ chars: 12, px: 8 }} /></p>
          <div className="st-sep" />
          <p className="t-h1"><Chars text="Few can show the evidence." d={0.9} st={0.034} /></p>
        </Reveal>
        <Rails seed={14} rails={5} />
      </div></div>
    </section>
  );
}

const CLOUDS = [
  { kind: 'lock' as const, t: 'Black-box labels', p: 'A classifier says “pump: severe leakage” and stops there. The engineer still has to work out why, with the machine running.' },
  { kind: 'drift' as const, t: 'Explanations read off a plot', p: 'A chatbot looks at a chart and writes a confident sentence. The numbers it quotes are never checked against the signal.' },
  { kind: 'infinity' as const, t: 'Leaky splits', p: 'Neighbouring cycles are near copies. Split them at random and the test set leaks into training, so the score flatters the model.' },
];

export function FailureModes() {
  return (
    <section className="sec" aria-labelledby="fail-h">
      <div className="container"><div className="inner">
        <div className="pad fail-head"><Head id="fail-h" eyebrow="How diagnostics mislead" title="Three failure modes" center /></div>
        <div className="clouds">
          {CLOUDS.map((c, i) => (
            <Reveal className="cloud-col" key={c.t} amount={0.25}>
              <Fade d={i * 0.08} dur={0.9} className="cloud-art"><PointCloud kind={c.kind} /></Fade>
              <Fade d={0.4 + i * 0.08}><h3 className="t-h4">{c.t}</h3></Fade>
              <Fade as="p" className="t-small" d={0.5 + i * 0.08}>{c.p}</Fade>
            </Reveal>
          ))}
        </div>
      </div></div>
    </section>
  );
}

const COMPARE: Array<[string, string]> = [
  ['Says which class, never why', 'Names the sensor, the value and the gap to healthy'],
  ['Explanations written after the fact', 'Evidence computed from the signal first'],
  ['Nobody checks the explanation', 'Every stated number recomputed and checked'],
  ['Random splits flatter the score', 'Whole operating conditions held out for testing'],
  ['Accuracy is the only number', 'Faithfulness reported next to accuracy'],
  ['A new model for every machine', 'One TimeNet format, one more machine each round'],
];

function CompareRow({ a, b }: { a: string; b: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [on, setOn] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setOn(true); io.disconnect(); } }, { rootMargin: '0px 0px -35% 0px' });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <div ref={ref} className={`cmp-row ${on ? 'on' : ''}`} role="row">
      <div className="cmp-a" role="cell"><i />{a}</div>
      <div className="cmp-b" role="cell"><i />{b}</div>
    </div>
  );
}

export function Compare() {
  return (
    <section className="sec" aria-labelledby="cmp-h">
      <div className="container"><div className="inner">
        <div className="pad scrub-head">
          <Reveal><Fade d={0}><Eyebrow>What we believe</Eyebrow></Fade></Reveal>
          <ScrubChars as="h2" className="t-h1" offset={['start 75%', 'start 35%']} from={0.25} soft={6} text="Machine data will not get simpler. Its explanations have to be checkable." />
        </div>
        <div className="pad cmp-wrap">
          <Head id="cmp-h" eyebrow="Our approach" title="A different way to diagnose" />
          <div className="cmp" role="table" aria-label="A black-box classifier compared with Sightglass">
            <div className="cmp-row cmp-h on" role="row">
              <div className="t-mono" role="columnheader">A black-box classifier</div>
              <div className="t-mono cmp-brand" role="columnheader"><SightglassMark size="1.2em" /> The Sightglass way</div>
            </div>
            {COMPARE.map(([a, b]) => <CompareRow key={a} a={a} b={b} />)}
          </div>
        </div>
      </div></div>
    </section>
  );
}

const TABS = [
  { t: 'Maintenance engineers', p: 'Get a diagnosis you can act on: which part, how bad, and the sensor readings that show it. Check any number against the trace before you open the machine.' },
  { t: 'Reliability teams', p: 'See where the model is unsure or wrong. Every miss is in the failure gallery with its evidence, so you can decide where a human still needs to look.' },
  { t: 'ML researchers', p: 'Reuse the TimeNet connector, the physics rationales and the faithfulness checker. Score your own model’s explanations by the same pre-registered rules.' },
];

/** Three columns; the active one is bright with a rule that grows over 5 s, then advances. */
export function UseFor() {
  const [i, setI] = useState(0);
  const [ref, seen] = useInViewOnce<HTMLDivElement>(0.4);
  const [paused, setPaused] = useState(false);
  useEffect(() => {
    if (!seen || paused) return;
    const id = window.setTimeout(() => setI((v) => (v + 1) % TABS.length), 5000);
    return () => window.clearTimeout(id);
  }, [i, seen, paused]);
  return (
    <section className="sec" aria-labelledby="use-h">
      <div className="container"><div className="inner">
        <div className="usefor" ref={ref} onPointerEnter={() => setPaused(true)} onPointerLeave={() => setPaused(false)}>
          <Reveal className="usefor-h"><Fade d={0}><Eyebrow>Use Sightglass for…</Eyebrow></Fade></Reveal>
          <div className="tabs" role="tablist" aria-label="Who Sightglass is for" id="use-h">
            {TABS.map((t, k) => (
              <button key={t.t} role="tab" aria-selected={k === i} className={`tab ${k === i ? 'on' : ''}`} onClick={() => setI(k)} onFocus={() => setI(k)}>
                <span className="tab-rule"><i key={`${k}-${i}-${seen}-${paused}`} className={k === i && seen && !paused ? 'run' : k === i ? 'full' : ''} /></span>
                <span className="t-h4">{t.t}</span>
                <span className="t-small">{t.p}</span>
              </button>
            ))}
          </div>
        </div>
      </div></div>
    </section>
  );
}

export function Where() {
  return (
    <section className="sec" aria-labelledby="where-h">
      <div className="container"><div className="inner">
        <div className="pad where">
          <Head id="where-h" eyebrow="Where it goes next" title="One format, more machines." center />
          <div className="where-wrap">
            <Globe markers={[
              { lat: 22, lon: -40, label: 'HYDRAULIC RIG · NOW' },
              { lat: -18, lon: 10, label: 'BEARINGS · ROUND 2' },
              { lat: 35, lon: 60, label: 'WIND TURBINES · ROUND 3' },
              { lat: -40, lon: 110, label: 'ONE POOLED MODEL · FINAL' },
            ]} />
            <Reveal className="where-card" amount={0.5}>
              <Fade d={0}><div className="where-pin" /></Fade>
              <Fade d={0.1}><div className="t-h4">TimeNet</div></Fade>
              <Fade d={0.2}><div className="t-mono">Connector · physics · checker</div></Fade>
            </Reveal>
          </div>
        </div>
      </div></div>
    </section>
  );
}

/** Purple panel: corners round as it scrolls in, background drifts with the mouse, squares blink. */
export function FinalCta() {
  const { openConsole, cycleId, run } = useStore();
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end end'] });
  const radius = useTransform(useSpring(scrollYProgress, { stiffness: 140, damping: 30 }), [0, 1], ['0em', '2.5em']);
  const { scrollYProgress: bgP } = useScroll({ target: ref, offset: ['start end', 'start 30%'] });
  const bgOpacity = useTransform(bgP, [0, 1], [0, 1]);
  const bgY = useTransform(bgP, [0, 1], ['0%', '-10%']);
  const sideL = useTransform(bgP, [0, 1], ['-100%', '0%']);
  const sideR = useTransform(bgP, [0, 1], ['100%', '0%']);
  const mx = useMotionValue(0), my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 40, damping: 20 }), sy = useSpring(my, { stiffness: 40, damping: 20 });
  useEffect(() => {
    const move = (e: PointerEvent) => { mx.set(((e.clientX / innerWidth) - 0.5) * 60); my.set(((e.clientY / innerHeight) - 0.5) * 60); };
    addEventListener('pointermove', move);
    return () => removeEventListener('pointermove', move);
  }, [mx, my]);
  const r = rng(77);
  const squares = Array.from({ length: 21 }, () => ({ x: r() * 100, y: r() * 100, d: r() * 4, p: 1.6 + r() * 2.4 }));
  return (
    <section className="sec cta-sec" aria-labelledby="cta-h">
      <div className="container">
        <motion.div ref={ref} className="cta" style={{ borderRadius: radius }}>
          <motion.div className="cta-bg" style={{ opacity: bgOpacity, y: bgY }}>
            <motion.div className="cta-par" style={{ x: sx, y: sy }}>
              <motion.div className="cta-side l" style={{ x: sideL }} />
              <motion.div className="cta-side r" style={{ x: sideR }} />
              {squares.map((s, i) => <i key={i} className="cta-sq" style={{ left: `${s.x}%`, top: `${s.y}%`, animationDelay: `${s.d}s`, animationDuration: `${s.p}s` } as CSSProperties} />)}
            </motion.div>
          </motion.div>
          <Reveal className="cta-copy" amount={0.4}>
            <h2 className="t-h1" id="cta-h"><Chars text="Look inside the machine." st={0.04} /></h2>
            <Fade as="p" className="t-p cta-p" d={T.para + 0.25}>Pick any held-out cycle, read the diagnosis, and check every number it gives you against the signal. Or read the code that produced it.</Fade>
            <Fade d={T.button + 0.3} dur={0.6} className="cta-actions">
              <span className="cta-halo" />
              <Button label="Ask about a cycle" variant="dark" onClick={() => openConsole(cycleId)} />
              <Button label="Run a diagnosis" variant="ghost" className="on-violet" onClick={() => { run(); window.setTimeout(() => scrollToId('explore-run'), 80); }} />
            </Fade>
          </Reveal>
        </motion.div>
      </div>
    </section>
  );
}

export function Footer() {
  const { manifest } = useStore();
  const link = (id: string, label: string) => <a href={`#${id}`} onClick={(e) => { e.preventDefault(); scrollToId(id); }}>{label}</a>;
  return (
    <footer className="footer">
      <div className="wordmark" aria-hidden="true">
        <div className="marquee-track">
          {Array.from({ length: 4 }, (_, i) => <span key={i}><SightglassMark size="0.8em" /> Sightglass</span>)}
        </div>
      </div>
      <div className="container"><div className="inner">
        <Rails seed={5} rails={3} />
        <div className="foot-card">
          <div className="foot-l">
            <a className="nav-logo" href="#top" onClick={(e) => { e.preventDefault(); scrollToId('top'); }}><SightglassMark /> <span>Sightglass</span></a>
            <p className="t-small">Machine-fault diagnosis that shows its evidence, and checks every number it states against the signal.</p>
          </div>
          <nav className="foot-links" aria-label="Footer">
            {link('explore', 'Explorer')}
            {link('evidence', 'Evidence')}
            {link('whatif', 'What-if lab')}
            {link('how', 'How it works')}
            {link('results', 'Results')}
            <a href={REPO} target="_blank" rel="noreferrer">GitHub</a>
            <a href={UCI_URL} target="_blank" rel="noreferrer">Dataset (UCI #447)</a>
          </nav>
        </div>
        <div className="foot-legal t-small" id="page-end">
          <span>Code MIT · UCI hydraulic data CC BY 4.0 (Helwig, Pignanelli, Schütze){manifest?.git_sha ? ` · build ${manifest.git_sha.slice(0, 7)}` : ''}</span>
          <span>Every number on this page is read from the exported results; nothing is typed by hand.</span>
        </div>
      </div></div>
    </footer>
  );
}
