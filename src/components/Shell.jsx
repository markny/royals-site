import { BarChart3, CalendarDays, ClipboardList, Home, Medal, Newspaper, Table2 } from 'lucide-react';

const navItems = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'games', label: 'Games', icon: CalendarDays },
  { id: 'box', label: 'Box', icon: ClipboardList },
  { id: 'stats', label: 'Stats', icon: Table2 },
  { id: 'prospects', label: 'Prospects', icon: Medal },
  { id: 'standings', label: 'Standings', icon: BarChart3 },
  { id: 'recaps', label: 'Recaps', icon: Newspaper },
];

export default function Shell({ activePage, onNavigate, children, generatedAt }) {
  return (
    <div className="min-h-screen bg-stone-50 text-slate-950">
      <header className="border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.24em] text-royal-700">Kansas City Royals</p>
              <h1 className="mt-1 text-3xl font-black tracking-tight text-slate-950 sm:text-4xl">
                Season Tracker
              </h1>
            </div>
            <p className="text-sm text-slate-500">Updated {generatedAt}</p>
          </div>
          <nav className="flex gap-2 overflow-x-auto pb-1" aria-label="Primary navigation">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  className={`nav-button ${isActive ? 'nav-button-active' : ''}`}
                  onClick={() => onNavigate(item.id)}
                >
                  <Icon size={17} aria-hidden="true" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}
