import React, { useState } from 'react';
import { Check, X, AlertCircle } from 'lucide-react';
import { ClaimData } from '../types/data';

interface ClaimChipProps {
  claim: ClaimData;
  text: string;
  onHover?: (claim: ClaimData | null) => void;
}

export const ClaimChip: React.FC<ClaimChipProps> = ({ claim, text, onHover }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const isVerified = claim.status === 'verified';
  const isWrongValue = claim.status === 'wrong_value';

  const badgeColor = isVerified
    ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700/60 hover:bg-emerald-900'
    : isWrongValue
    ? 'bg-red-950/80 text-red-300 border-red-700/60 hover:bg-red-900'
    : 'bg-amber-950/80 text-amber-300 border-amber-700/60 hover:bg-amber-900';

  const Icon = isVerified ? Check : isWrongValue ? X : AlertCircle;

  return (
    <span
      className="relative inline-block my-0.5 cursor-pointer"
      onMouseEnter={() => {
        setShowTooltip(true);
        onHover?.(claim);
      }}
      onMouseLeave={() => {
        setShowTooltip(false);
        onHover?.(null);
      }}
      onClick={() => setShowTooltip(!showTooltip)}
    >
      <span
        className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded border text-xs font-mono font-medium transition-all ${badgeColor}`}
      >
        <Icon className="w-3 h-3 shrink-0" aria-hidden="true" />
        <span>{text}</span>
      </span>

      {showTooltip && (
        <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-lg shadow-xl text-xs z-50 pointer-events-none">
          <div className="font-semibold text-slate-200 border-b border-slate-800 pb-1 mb-2 flex items-center justify-between">
            <span>Physical Claim Audit</span>
            <span
              className={`px-1.5 py-0.2 rounded text-[10px] uppercase font-mono ${
                isVerified ? 'bg-emerald-900 text-emerald-300' : 'bg-red-900 text-red-300'
              }`}
            >
              {claim.status}
            </span>
          </div>
          <div className="space-y-1 text-slate-300 font-mono text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">Sensor / Feature:</span>
              <span className="text-white">{claim.feature || claim.sensor}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Stated Value:</span>
              <span className="text-white">
                {claim.stated.value} {claim.stated.unit}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">True Signal Value:</span>
              <span className="text-emerald-400">
                {claim.true.value} {claim.stated.unit}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Signal Deviation:</span>
              <span className={claim.true.pct >= 0 ? 'text-amber-400' : 'text-blue-400'}>
                {claim.true.pct > 0 ? `+${claim.true.pct}%` : `${claim.true.pct}%`}
              </span>
            </div>
            {claim.window && (
              <div className="flex justify-between border-t border-slate-800 pt-1 mt-1">
                <span className="text-slate-400">Time Window:</span>
                <span className="text-slate-300">
                  [{claim.window[0]}s – {claim.window[1]}s]
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </span>
  );
};
