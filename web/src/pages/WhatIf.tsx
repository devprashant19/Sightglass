import React, { useState, useEffect } from 'react';
import { Sliders, RefreshCw } from 'lucide-react';
import { WhatIfData, WhatIfStep } from '../types/data';

interface WhatIfProps {
  loadWhatIf: (id: string) => Promise<WhatIfData | null>;
}

export const WhatIf: React.FC<WhatIfProps> = ({ loadWhatIf }) => {
  const [data, setData] = useState<WhatIfData | null>(null);
  const [loading, setLoading] = useState(true);

  // Perturbation slider offsets
  const [flowDrop, setFlowDrop] = useState(0); // 0 to -40%
  const [tempRise, setTempRise] = useState(0); // 0 to +25°C
  const [rippleInc, setRippleInc] = useState(0); // 0 to +100%

  useEffect(() => {
    loadWhatIf('hydraulic-00001').then((res) => {
      setData(res);
      setLoading(false);
    });
  }, [loadWhatIf]);

  // Find nearest step from precomputed perturbations
  const getStep = (type: string, delta: number): WhatIfStep | null => {
    if (!data || !data.perturbations[type]) return null;
    const steps = data.perturbations[type];
    let best = steps[0];
    let minDiff = Infinity;
    for (const s of steps) {
      const diff = Math.abs(s.delta_pct - delta);
      if (diff < minDiff) {
        minDiff = diff;
        best = s;
      }
    }
    return best;
  };

  const activeStep = getStep('flow_drop', flowDrop);

  return (
    <div className="max-w-5xl mx-auto py-8 space-y-8">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <Sliders className="w-6 h-6 text-emerald-400" />
          <span>What-If Physical Counterfactual Simulator</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Perturb healthy sensor features to observe how physical shifts change Sightglass's diagnoses and evidence rationales.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Sliders Panel */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
            Signal Perturbation Controls
          </h3>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-mono mb-2">
                <span className="text-slate-300">Flow Drop (FS1 mean)</span>
                <span className="text-emerald-400">{flowDrop}%</span>
              </div>
              <input
                type="range"
                min="-40"
                max="0"
                step="5"
                value={flowDrop}
                onChange={(e) => setFlowDrop(Number(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
                <span>-40% (Severe Leakage)</span>
                <span>0% (Optimal)</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-2">
                <span className="text-slate-300">Oil Temperature Rise (TS1)</span>
                <span className="text-amber-400">+{tempRise}°C</span>
              </div>
              <input
                type="range"
                min="0"
                max="25"
                step="5"
                value={tempRise}
                onChange={(e) => setTempRise(Number(e.target.value))}
                className="w-full accent-amber-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
                <span>+0°C</span>
                <span>+25°C (Cooler Degraded)</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-2">
                <span className="text-slate-300">Pressure Ripple Increase (PS1)</span>
                <span className="text-cyan-400">+{rippleInc}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                step="20"
                value={rippleInc}
                onChange={(e) => setRippleInc(Number(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
                <span>0%</span>
                <span>+100% (Accumulator Cavitation)</span>
              </div>
            </div>
          </div>

          <div className="pt-2">
            <button
              onClick={() => {
                setFlowDrop(0);
                setTempRise(0);
                setRippleInc(0);
              }}
              className="w-full py-2 rounded bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-mono border border-slate-700 transition-colors flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reset to Healthy Baseline</span>
            </button>
          </div>
        </div>

        {/* Counterfactual Diagnosis Output */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase">
            Model Diagnostic Response
          </h3>

          {loading ? (
            <div className="h-48 flex items-center justify-center text-slate-500 font-mono text-sm">
              Loading counterfactual grid...
            </div>
          ) : (
            <div className="space-y-6">
              {/* Predicted conditions under perturbation */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono">
                  <div className="text-[10px] text-slate-400">Cooler Condition</div>
                  <div className="text-sm font-bold text-emerald-400 mt-1">
                    {tempRise > 10 ? 'Reduced Efficiency (20)' : 'Full Efficiency (100)'}
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono">
                  <div className="text-[10px] text-slate-400">Internal Pump Leakage</div>
                  <div className="text-sm font-bold text-amber-400 mt-1">
                    {flowDrop < -20 ? 'Severe Leakage (2)' : flowDrop < -5 ? 'Weak Leakage (1)' : 'No Leakage (0)'}
                  </div>
                </div>
              </div>

              {/* Counterfactual Rationale Text */}
              <div className="space-y-2">
                <div className="text-xs text-slate-400 font-mono">Counterfactual Rationale:</div>
                <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 text-sm font-sans leading-relaxed">
                  {activeStep?.rationale || (
                    <span>
                      System operating within nominal parameters. Flow rates and thermodynamic dissipation match healthy reference cycle profiles.
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
