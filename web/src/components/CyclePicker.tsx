import React, { useState } from 'react';
import { Search, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';
import { CycleIndexItem } from '../types/data';

interface CyclePickerProps {
  cycles: CycleIndexItem[];
  selectedId: string;
  onSelectCycle: (id: string) => void;
}

export const CyclePicker: React.FC<CyclePickerProps> = ({
  cycles,
  selectedId,
  onSelectCycle,
}) => {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'faithful' | 'unfaithful'>('all');

  const filteredCycles = cycles.filter((c) => {
    const matchesSearch = c.id.toLowerCase().includes(search.toLowerCase());
    if (!matchesSearch) return false;
    if (filter === 'faithful') return c.is_faithful;
    if (filter === 'unfaithful') return !c.is_faithful;
    return true;
  });

  const interestingPresets = cycles.slice(0, 4);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col h-full">
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-white mb-1 flex items-center justify-between">
          <span>Test Cycles</span>
          <span className="text-xs text-slate-400 font-mono font-normal">
            {cycles.length} loaded
          </span>
        </h3>

        {/* Preset buttons */}
        <div className="flex items-center gap-1.5 mb-3 flex-wrap">
          <span className="text-[11px] text-slate-400 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-400" /> Curated:
          </span>
          {interestingPresets.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelectCycle(c.id)}
              className={`text-[11px] font-mono px-2 py-0.5 rounded border transition-colors ${
                selectedId === c.id
                  ? 'bg-emerald-950 text-emerald-300 border-emerald-600'
                  : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white'
              }`}
            >
              #{c.cycle_index}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative mb-2">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search cycle ID..."
            className="w-full bg-slate-950 border border-slate-800 rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Filter Tabs */}
        <div className="flex rounded border border-slate-800 p-0.5 text-[11px]">
          {(['all', 'faithful', 'unfaithful'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`flex-1 py-1 rounded text-center capitalize transition-colors ${
                filter === tab ? 'bg-slate-800 text-white font-medium' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Cycle List */}
      <div className="space-y-1.5 overflow-y-auto flex-1 max-h-[500px] pr-1">
        {filteredCycles.map((c) => {
          const isSelected = c.id === selectedId;
          return (
            <button
              key={c.id}
              onClick={() => onSelectCycle(c.id)}
              className={`w-full text-left p-2.5 rounded border transition-all ${
                isSelected
                  ? 'bg-slate-800 border-emerald-500 text-white shadow-sm'
                  : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:bg-slate-800/40 hover:text-white'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-xs font-semibold">{c.id}</span>
                <span className="flex items-center gap-1 text-[11px] font-mono">
                  {c.is_faithful ? (
                    <span className="flex items-center gap-0.5 text-emerald-400">
                      <CheckCircle className="w-3 h-3" /> Faithful
                    </span>
                  ) : (
                    <span className="flex items-center gap-0.5 text-amber-400">
                      <AlertCircle className="w-3 h-3" /> Unfaithful
                    </span>
                  )}
                </span>
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>Claims: {c.verified_claims}/{c.total_claims} verified</span>
                <span>Flag: {c.stable_flag === 0 ? 'stable' : 'unstable'}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
