import { useEffect } from 'react';
import { MotionConfig } from 'motion/react';
import { StoreProvider, scrollToId, useStore } from './lib/store';
import { ProgressiveBlur } from './motion/Ambient';
import { Hero, Nav } from './sections/Top';
import { Checks, Intro, Stats } from './sections/Story';
import { Evidence, SensorGrid } from './sections/Evidence';
import { Explorer } from './sections/Explorer';
import { WhatIf } from './sections/WhatIf';
import { HowItWorks, Proof, ResultsSection } from './sections/How';
import { Compare, FailureModes, FinalCta, Footer, Statement, UseFor, Where } from './sections/Closing';
import { ConsoleModal, TrySection } from './console/Console';
import { Boundary } from './ui/Boundary';

/** Shareable links: ?cycle=ID opens that cycle; ?run also runs it and scrolls to the result; ?ask opens the console. */
function DeepLinks() {
  const { run, openConsole, cycleId } = useStore();
  useEffect(() => {
    const q = new URLSearchParams(location.search);
    if (!cycleId) return;
    if (q.has('run')) { window.setTimeout(() => scrollToId('explore-run'), 400); run(cycleId); }
    if (q.has('ask')) openConsole(cycleId);
    // Only on first load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cycleId === null]);
  return null;
}

function MockBanner() {
  const { mock, loadError } = useStore();
  if (loadError) return <div className="mock-banner bad" role="alert">The exported results could not be loaded ({loadError}). Run <code className="t-code">make export</code> and reload.</div>;
  if (!mock) return null;
  return <div className="mock-banner" role="note">Mock data: these numbers are a synthetic stand-in for development, not real results.</div>;
}

export function App() {
  return (
    <MotionConfig reducedMotion="user">
      <StoreProvider>
        <DeepLinks />
        <a className="skip" href="#explore">Skip to the diagnosis explorer</a>
        <Nav />
        <MockBanner />
        <main>
          <Boundary name="hero"><Hero /></Boundary>
          <Boundary name="orbit"><Checks /></Boundary>
          <Boundary name="impact"><Stats /></Boundary>
          <Boundary name="intro"><Intro /></Boundary>
          <Boundary name="evidence"><Evidence /></Boundary>
          <Boundary name="sensors"><SensorGrid /></Boundary>
          <Boundary name="explorer"><Explorer /></Boundary>
          <Boundary name="what-if"><WhatIf /></Boundary>
          <Boundary name="how it works"><HowItWorks /></Boundary>
          <Boundary name="proof"><Proof /></Boundary>
          <Boundary name="results"><ResultsSection /></Boundary>
          <Boundary name="statement"><Statement /></Boundary>
          <Boundary name="failure modes"><FailureModes /></Boundary>
          <Boundary name="compare"><Compare /></Boundary>
          <Boundary name="use for"><UseFor /></Boundary>
          <Boundary name="ask"><TrySection /></Boundary>
          <Boundary name="roadmap"><Where /></Boundary>
          <Boundary name="call to action"><FinalCta /></Boundary>
        </main>
        <Boundary name="footer"><Footer /></Boundary>
        <ProgressiveBlur />
        <Boundary name="console"><ConsoleModal /></Boundary>
      </StoreProvider>
    </MotionConfig>
  );
}
