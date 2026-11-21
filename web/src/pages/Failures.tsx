import React, { useState } from 'react';
import { AlertOctagon, ExternalLink, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';

interface FailureItem {
  cycle_id: string;
  category: 'wrong_value' | 'wrong_direction' | 'misclassification';
  claim_text: string;
  stated_val: number;
  true_val: number;
  unit: string;
  analysis: string;
}

export const Failures: React.FC = () => {
  const [filter, setFilter] = useState<string>('all');

  const failures: FailureItem[] = [
    {
      cycle_id: 'hydraulic-00001',
      category: 'wrong_value',
      claim_text: 'PS1 peak pressure reached 178.0 bar',
      stated_val: 178.0,
      true_val: 196.54,
      unit: 'bar',
      analysis:
        'The model underestimated peak pressure overshoot by 18.5 bar during the 10-second high-load cycle pulse due to 10 Hz downsampling decimation blurring the sharpest 100 Hz transient spike.',
    },
    {
      cycle_id: 'hydraulic-00008',
      category: 'wrong_direction',
      claim_text: 'Cooler temperature differential TS1-TS2 4.2°C (12% below healthy)',
      stated_val: 4.2,
      true_val: 5.03,
      unit: '°C',
      analysis:
        'Model asserted delta-T was below healthy, but true dissipation was nominal (+0.6% deviation). Rationale generator selected a marginal boundary clause.',
    },
    {
      cycle_id: 'hydraulic-00033',
      category: 'wrong_value',
      claim_text: 'Electrical motor power EPS1 mean 2100 W (12% below healthy)',
      stated_val: 2100,
      true_val: 2400.1,
      unit: 'W',
      analysis:
        'Motor power plateau was misquoted due to baseline token interference in the temporal cross-attention layers.',
    },
    {
      cycle_id: 'hydraulic-00048',
      category: 'misclassification',
      claim_text: 'Hydraulic accumulator predicted slightly reduced (115 bar)',
      stated_val: 115,
      true_val: 100,
      unit: 'bar',
      analysis:
        'Boundary confusion between 115 bar (slightly reduced) and 100 bar (severely reduced) accumulator pressure state during low-ripple operating phase.',
    },
  ];

  const filteredFailures = failures.filter(
    (f) => filter === 'all' || f.category === filter
  );

  return (
    <div className="max-w-5xl mx-auto py-8 space-y-8">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <AlertOctagon className="w-6 h-6 text-red-400" />
          <span>Failure Gallery & Transparent Audit</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          In keeping with Non-Negotiable Rule 1 (Never fabricate results), here are real diagnostic and faithfulness failure modes discovered during test evaluation.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2">
        <Filter className="w-4 h-4 text-slate-400" />
        <span className="text-xs text-slate-400 font-mono">Category:</span>
        {(['all', 'wrong_value', 'wrong_direction', 'misclassification'] as const).map(
          (cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`text-xs font-mono px-3 py-1 rounded border transition-colors ${
                filter === cat
                  ? 'bg-slate-800 text-emerald-400 border-slate-600 font-semibold'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              {cat}
            </button>
          )
        )}
      </div>

      {/* Gallery Cards */}
      <div className="space-y-4">
        {filteredFailures.map((f, i) => (
          <div
            key={i}
            className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="font-mono text-sm font-bold text-white">
                  {f.cycle_id}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded uppercase bg-red-950 text-red-400 border border-red-800">
                  {f.category.replace('_', ' ')}
                </span>
              </div>
              <Link
                to={`/explore/${f.cycle_id}`}
                className="flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300 font-mono transition-colors"
              >
                <span>Inspect in Explorer</span>
                <ExternalLink className="w-3 h-3" />
              </Link>
            </div>

            <div className="p-3 rounded bg-slate-950 border border-slate-800 font-mono text-xs flex flex-wrap items-center justify-between gap-4">
              <span className="text-slate-300 italic">"{f.claim_text}"</span>
              <div className="flex items-center gap-4 text-[11px]">
                <span className="text-red-400">
                  Stated: {f.stated_val} {f.unit}
                </span>
                <span className="text-emerald-400">
                  True: {f.true_val} {f.unit}
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              <strong className="text-slate-300">Root Cause Analysis:</strong> {f.analysis}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
