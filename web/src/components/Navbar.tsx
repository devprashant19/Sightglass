import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, Gauge, Sliders, BarChart2, AlertOctagon, Database, Cpu, HelpCircle, Users, Sun, Moon, Disc, Wind, Layers } from 'lucide-react';

interface NavbarProps {
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
  mockMode: boolean;
  setMockMode: (val: boolean) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ darkMode, setDarkMode, mockMode, setMockMode }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: Activity },
    { path: '/explore', label: 'Explorer', icon: Gauge },
    { path: '/bearing', label: 'Bearings', icon: Disc },
    { path: '/wind', label: 'Wind Farm', icon: Wind },
    { path: '/cross-machine', label: 'Pooled TSLM', icon: Layers },
    { path: '/whatif', label: 'What-If Lab', icon: Sliders },
    { path: '/results', label: 'Results', icon: BarChart2 },
    { path: '/failures', label: 'Failures', icon: AlertOctagon },
    { path: '/dataset', label: 'Dataset', icon: Database },
    { path: '/method', label: 'Method', icon: Cpu },
    { path: '/limitations', label: 'Limitations', icon: HelpCircle },
    { path: '/team', label: 'Team', icon: Users },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 group-hover:border-emerald-400 transition-colors">
            <Gauge className="w-5 h-5" />
          </div>
          <div>
            <div className="font-bold text-lg tracking-tight text-white flex items-center gap-2">
              Sightglass
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                TSLM
              </span>
            </div>
            <div className="text-[11px] text-slate-400 -mt-1 hidden sm:block">
              Machine-Health Time-Series Model
            </div>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = item.path === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(item.path);

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  active
                    ? 'bg-slate-800 text-emerald-400 border border-slate-700'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          {/* Mock mode toggle */}
          <button
            onClick={() => setMockMode(!mockMode)}
            className={`text-xs px-2.5 py-1 rounded border font-mono transition-colors ${
              mockMode
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-slate-200'
            }`}
            title="Toggle between real exported artifacts and simulated mock data"
          >
            {mockMode ? 'Mock: ON' : 'Mock: OFF'}
          </button>

          {/* Theme toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-md bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition-colors"
            aria-label="Toggle theme"
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
};
