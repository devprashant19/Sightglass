import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Eye } from 'lucide-react';
import { ComponentLabel } from '../types/data';

interface DiagnosisCardProps {
  component: string;
  predicted: ComponentLabel;
  trueLabel?: ComponentLabel;
  revealed: boolean;
  onReveal: () => void;
}

const COMPONENT_TITLES: Record<string, string> = {
  cooler_condition: 'Cooler Condition',
  valve_condition: 'Valve Condition',
  pump_leakage: 'Internal Pump Leakage',
  accumulator_pressure: 'Hydraulic Accumulator',
};

export const DiagnosisCard: React.FC<DiagnosisCardProps> = ({
  component,
  predicted,
  trueLabel,
  revealed,
  onReveal,
}) => {
  const isMatch = trueLabel && predicted.value === trueLabel.value;

  const getSeverityStyle = (text: string) => {
    const lower = text.toLowerCase();
    if (lower.includes('optimal') || lower.includes('full') || lower.includes('no leakage')) {
      return {
        border: 'border-emerald-500/40',
        bg: 'bg-emerald-950/40',
        badge: 'bg-emerald-900/60 text-emerald-300 border-emerald-700',
        icon: CheckCircle2,
      };
    }
    if (lower.includes('failure') || lower.includes('severe')) {
      return {
        border: 'border-red-500/40',
        bg: 'bg-red-950/40',
        badge: 'bg-red-900/60 text-red-300 border-red-700',
        icon: XCircle,
      };
    }
    return {
      border: 'border-amber-500/40',
      bg: 'bg-amber-950/40',
      badge: 'bg-amber-900/60 text-amber-300 border-amber-700',
      icon: AlertTriangle,
    };
  };

  const style = getSeverityStyle(predicted.name);
  const StatusIcon = style.icon;

  return (
    <div className={`p-4 rounded-lg border ${style.border} ${style.bg} transition-all`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
          {COMPONENT_TITLES[component] || component}
        </span>
        <StatusIcon className="w-4 h-4 text-slate-400" />
      </div>

      <div className="mb-3">
        <div className="text-[11px] text-slate-400 mb-0.5">Predicted Diagnosis</div>
        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded border text-xs font-medium font-mono">
          <span className={style.badge}>{predicted.name}</span>
          <span className="text-slate-400 text-[10px]">({predicted.value})</span>
        </div>
      </div>

      <div className="border-t border-slate-800/80 pt-2.5 flex items-center justify-between">
        {revealed ? (
          <div>
            <div className="text-[10px] text-slate-400 mb-0.5">Ground Truth</div>
            <div className="flex items-center gap-1.5 text-xs font-mono font-medium">
              <span className={isMatch ? 'text-emerald-400' : 'text-red-400'}>
                {trueLabel?.name} ({trueLabel?.value})
              </span>
              <span
                className={`text-[10px] px-1 rounded ${
                  isMatch ? 'bg-emerald-950 text-emerald-400' : 'bg-red-950 text-red-400'
                }`}
              >
                {isMatch ? 'Match' : 'Mismatch'}
              </span>
            </div>
          </div>
        ) : (
          <button
            onClick={onReveal}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-emerald-300 hover:bg-slate-800/60 px-2 py-1 rounded transition-colors"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Reveal Truth</span>
          </button>
        )}
      </div>
    </div>
  );
};
