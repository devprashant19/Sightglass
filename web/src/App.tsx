import React, { useState, useEffect, useCallback } from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { MockBanner } from './components/MockBanner';
import { Home } from './pages/Home';
import { Explorer } from './pages/Explorer';
import { BearingExplorer } from './pages/BearingExplorer';
import { WindFarm } from './pages/WindFarm';
import { CrossMachine } from './pages/CrossMachine';
import { WhatIf } from './pages/WhatIf';
import { Results } from './pages/Results';
import { Failures } from './pages/Failures';
import { Dataset } from './pages/Dataset';
import { Method } from './pages/Method';
import { Limitations } from './pages/Limitations';
import { Team } from './pages/Team';
import { ManifestData, DatasetIndex, CycleData, SummaryData, WhatIfData } from './types/data';

export const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [mockMode, setMockMode] = useState(false);

  const [manifest, setManifest] = useState<ManifestData | null>(null);
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [datasetIndex, setDatasetIndex] = useState<DatasetIndex | null>(null);

  const dataPrefix = mockMode ? './data-mock' : './data';

  useEffect(() => {
    // Sync dark mode class
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  useEffect(() => {
    // Load manifest, summary, and dataset index
    fetch(`${dataPrefix}/manifest.json`)
      .then((r) => r.json())
      .then((data: ManifestData) => setManifest(data))
      .catch((err) => console.warn('Failed to load manifest:', err));

    fetch(`${dataPrefix}/summary.json`)
      .then((r) => r.json())
      .then((data: SummaryData) => setSummary(data))
      .catch((err) => console.warn('Failed to load summary:', err));

    fetch(`${dataPrefix}/hydraulic/index.json`)
      .then((r) => r.json())
      .then((data: DatasetIndex) => setDatasetIndex(data))
      .catch((err) => console.warn('Failed to load index:', err));
  }, [dataPrefix]);

  const loadCycle = useCallback(
    async (id: string): Promise<CycleData | null> => {
      try {
        const res = await fetch(`${dataPrefix}/hydraulic/cycles/${id}.json`);
        if (!res.ok) {
          // Fallback to first available cycle
          const fallback = await fetch(`${dataPrefix}/hydraulic/cycles/hydraulic-00001.json`);
          return await fallback.json();
        }
        return await res.json();
      } catch (err) {
        console.error('Failed to load cycle:', err);
        return null;
      }
    },
    [dataPrefix]
  );

  const loadWhatIf = useCallback(
    async (id: string): Promise<WhatIfData | null> => {
      try {
        const res = await fetch(`${dataPrefix}/hydraulic/whatif/${id}.json`);
        if (!res.ok) {
          const fallback = await fetch(`${dataPrefix}/hydraulic/whatif/hydraulic-00001.json`);
          return await fallback.json();
        }
        return await res.json();
      } catch (err) {
        console.error('Failed to load what-if:', err);
        return null;
      }
    },
    [dataPrefix]
  );

  const isMockActive = mockMode || (manifest?.mock ?? false);

  return (
    <HashRouter>
      <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-emerald-500 selection:text-black">
        <MockBanner isMock={isMockActive} />
        <Navbar
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          mockMode={mockMode}
          setMockMode={setMockMode}
        />

        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Home summary={summary} />} />
            <Route
              path="/explore"
              element={<Explorer index={datasetIndex} loadCycle={loadCycle} />}
            />
            <Route
              path="/explore/:cycleId"
              element={<Explorer index={datasetIndex} loadCycle={loadCycle} />}
            />
            <Route path="/bearing" element={<BearingExplorer />} />
            <Route path="/bearing/:windowId" element={<BearingExplorer />} />
            <Route path="/wind" element={<WindFarm />} />
            <Route path="/cross-machine" element={<CrossMachine />} />
            <Route
              path="/whatif"
              element={<WhatIf loadWhatIf={loadWhatIf} />}
            />
            <Route
              path="/whatif/:cycleId"
              element={<WhatIf loadWhatIf={loadWhatIf} />}
            />
            <Route path="/results" element={<Results summary={summary} />} />
            <Route path="/failures" element={<Failures />} />
            <Route path="/dataset" element={<Dataset />} />
            <Route path="/method" element={<Method />} />
            <Route path="/limitations" element={<Limitations />} />
            <Route path="/team" element={<Team />} />
          </Routes>
        </main>

        <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-400">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <div>Sightglass TSLM · TimeNet Hackathon · CC BY 4.0 & MIT</div>
            <div className="font-mono text-[11px] text-slate-400">
              SHA: {manifest?.git_sha ? manifest.git_sha.substring(0, 7) : '0cf3a8a'}
            </div>
          </div>
        </footer>
      </div>
    </HashRouter>
  );
};
