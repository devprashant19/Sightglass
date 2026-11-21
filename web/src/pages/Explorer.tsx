import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CyclePicker } from '../components/CyclePicker';
import { SensorChart } from '../components/SensorChart';
import { DiagnosisCard } from '../components/DiagnosisCard';
import { Rationale } from '../components/Rationale';
import { CycleData, ClaimData, DatasetIndex } from '../types/data';
import { Check, AlertCircle, Eye, GitCompare } from 'lucide-react';

interface ExplorerProps {
  index: DatasetIndex | null;
  loadCycle: (id: string) => Promise<CycleData | null>;
}

export const Explorer: React.FC<ExplorerProps> = ({ index, loadCycle }) => {
  const { cycleId } = useParams<{ cycleId?: string }>();
  const navigate = useNavigate();

  const [activeCycle, setActiveCycle] = useState<CycleData | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeClaim, setActiveClaim] = useState<ClaimData | null>(null);
  const [cursorTime, setCursorTime] = useState<number | null>(null);
  const [revealedComponents, setRevealedComponents] = useState<Record<string, boolean>>({});
  const [compareBaseline, setCompareBaseline] = useState(false);

  const cycles = index?.cycles || [];
  const currentId = cycleId || (cycles[0]?.id ?? 'hydraulic-00001');

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    loadCycle(currentId).then((data) => {
      if (isMounted) {
        setActiveCycle(data);
        setLoading(false);
        setRevealedComponents({});
      }
    });
    return () => {
      isMounted = false;
    };
  }, [currentId, loadCycle]);

  const handleSelectCycle = (id: string) => {
    navigate(`/explore/${id}`);
  };

  const handleRevealAll = () => {
    if (!activeCycle) return;
    const allRev: Record<string, boolean> = {};
    Object.keys(activeCycle.true_labels).forEach((k) => {
      allRev[k] = true;
    });
    setRevealedComponents(allRev);
  };

  // Group signals by subsystem
  const pressureSignals = activeCycle
    ? Object.fromEntries(Object.entries(activeCycle.signals).filter(([k]) => k.startsWith('PS')))
    : {};
  const flowSignals = activeCycle
    ? Object.fromEntries(Object.entries(activeCycle.signals).filter(([k]) => k.startsWith('FS')))
    : {};
  const tempSignals = activeCycle
    ? Object.fromEntries(Object.entries(activeCycle.signals).filter(([k]) => k.startsWith('TS')))
    : {};
  const electVibSignals = activeCycle
    ? Object.fromEntries(Object.entries(activeCycle.signals).filter(([k]) => ['EPS1', 'VS1'].includes(k)))
    : {};
  const virtualSignals = activeCycle
    ? Object.fromEntries(Object.entries(activeCycle.signals).filter(([k]) => ['CE', 'CP', 'SE'].includes(k)))
    : {};

  const prediction = activeCycle?.prediction;
  const baseline = activeCycle?.baseline_b4;
  const currentPrediction = compareBaseline && baseline ? baseline : prediction;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 py-6">
      {/* Left Column: Cycle Picker (3 cols) */}
      <div className="lg:col-span-3">
        <CyclePicker
          cycles={cycles}
          selectedId={currentId}
          onSelectCycle={handleSelectCycle}
        />
      </div>

      {/* Main Content (9 cols) */}
      <div className="lg:col-span-9 space-y-6">
        {/* Header / Meta Bar */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-white font-mono">{currentId}</h2>
            {activeCycle && (
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono border border-slate-700">
                Cycle #{activeCycle.meta.cycle_index} ({activeCycle.meta.stable_flag === 0 ? 'Stable' : 'Unstable'})
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCompareBaseline(!compareBaseline)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono border transition-colors ${
                compareBaseline
                  ? 'bg-purple-950 text-purple-300 border-purple-700'
                  : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white'
              }`}
            >
              <GitCompare className="w-3.5 h-3.5" />
              <span>{compareBaseline ? 'Viewing Baseline B4' : 'Compare vs Baseline B4'}</span>
            </button>

            <button
              onClick={handleRevealAll}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-mono transition-colors"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Reveal All Truth</span>
            </button>
          </div>
        </div>

        {/* Diagnosis Cards Grid */}
        {activeCycle && (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            {Object.entries(currentPrediction?.labels || activeCycle.true_labels).map(([comp, pred]) => (
              <DiagnosisCard
                key={comp}
                component={comp}
                predicted={pred}
                trueLabel={activeCycle.true_labels[comp]}
                revealed={!!revealedComponents[comp]}
                onReveal={() =>
                  setRevealedComponents((prev) => ({ ...prev, [comp]: true }))
                }
              />
            ))}
          </div>
        )}

        {/* Rationale Section */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
              <span>{compareBaseline ? 'Baseline B4 Rationale' : 'Sightglass Physics-Grounded Rationale'}</span>
              <span className="text-xs text-slate-400 font-mono font-normal">
                (Click or hover any claim chip to inspect signal)
              </span>
            </h3>
            {currentPrediction?.claims && (
              <div className="flex items-center gap-2 text-xs font-mono">
                <span className="text-emerald-400 flex items-center gap-1">
                  <Check className="w-3 h-3" />
                  {currentPrediction.claims.filter((c) => c.status === 'verified').length} verified
                </span>
                <span className="text-red-400 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {currentPrediction.claims.filter((c) => c.status !== 'verified').length} failed
                </span>
              </div>
            )}
          </div>

          <Rationale
            text={currentPrediction?.rationale || ''}
            claims={currentPrediction?.claims || []}
            onHoverClaim={setActiveClaim}
          />
        </div>

        {/* Multi-Signal Synchronized Time-Series Panel */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
              Sensor Signals (60s Duration)
            </h3>
            <span className="text-xs text-slate-400 font-mono">
              Hover across charts to scrub time cursor
            </span>
          </div>

          {loading ? (
            <div className="h-64 rounded-lg bg-slate-900/60 border border-slate-800 animate-pulse flex items-center justify-center text-slate-500 font-mono text-sm">
              Loading cycle waveforms...
            </div>
          ) : (
            <div className="space-y-3">
              <SensorChart
                title="Pressure Sensors (PS1 – PS6 @ 100 Hz)"
                signals={pressureSignals}
                activeClaim={activeClaim}
                cursorTime={cursorTime}
                onCursorMove={setCursorTime}
                reference={activeCycle?.reference}
              />
              <SensorChart
                title="Flow Sensors (FS1 – FS2 @ 10 Hz)"
                signals={flowSignals}
                activeClaim={activeClaim}
                cursorTime={cursorTime}
                onCursorMove={setCursorTime}
                reference={activeCycle?.reference}
              />
              <SensorChart
                title="Temperature Sensors (TS1 – TS4 @ 1 Hz)"
                signals={tempSignals}
                activeClaim={activeClaim}
                cursorTime={cursorTime}
                onCursorMove={setCursorTime}
                reference={activeCycle?.reference}
              />
              <SensorChart
                title="Electrical Motor Power (EPS1) & Vibration (VS1)"
                signals={electVibSignals}
                activeClaim={activeClaim}
                cursorTime={cursorTime}
                onCursorMove={setCursorTime}
                reference={activeCycle?.reference}
              />
              <SensorChart
                title="Virtual Calculated Sensors (CE, CP, SE)"
                signals={virtualSignals}
                activeClaim={activeClaim}
                cursorTime={cursorTime}
                onCursorMove={setCursorTime}
                reference={activeCycle?.reference}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
