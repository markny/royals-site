import { useState } from 'react';
import { Activity, ChevronRight, Flame, Gauge, Sparkles, TrendingUp } from 'lucide-react';
import DataTable from './components/DataTable.jsx';
import Shell from './components/Shell.jsx';
import StatCard from './components/StatCard.jsx';
import { data } from './lib/content.js';
import { formatDate, formatRecord, pct, signed } from './lib/format.js';

function HomePage({ onNavigate }) {
  const { season, standings, prospects } = data;
  const latestRecap = data.recaps.items[0];
  const centralLeader = standings.al_central[0];
  const hotProspect = prospects.hot_prospects[0];
  const nextPitchers = season.next_game.probable_pitchers ?? {
    royals: { name: 'TBD' },
    opponent: { name: 'TBD' },
  };
  const nextSite = season.next_game.site ?? 'TBD';

  return (
    <div className="space-y-6">
      <section className="hero-band">
        <div className="hero-copy">
          <p className="eyebrow">Personal Royals Newsroom</p>
          <h2>{season.headline}</h2>
          <p>{season.nightly_recap}</p>
          <div className="hero-actions">
            <button type="button" onClick={() => onNavigate('recaps')} className="primary-action">
              Read Recaps <ChevronRight size={18} />
            </button>
            <button type="button" onClick={() => onNavigate('stats')} className="secondary-action">
              Explore Stats
            </button>
          </div>
        </div>
        <div className="scoreboard-panel" aria-label="Royals snapshot">
          <span className="scoreboard-label">KC</span>
          <strong>{formatRecord(season.record)}</strong>
          <span>{season.division_rank}</span>
        </div>
      </section>

      <section className="metric-grid">
        <StatCard
          label="Royals Record"
          value={formatRecord(season.record)}
          detail={`${season.record.win_pct} winning percentage through ${season.record.games_played} games`}
          tone="blue"
        />
        <StatCard
          label="AL Central"
          value={`${centralLeader.team} leads`}
          detail={`${standings.royals_entry.team}: ${standings.royals_entry.games_back} GB, ${standings.royals_entry.streak}`}
        />
        <StatCard
          label="Last Game"
          value={season.last_game.short_result}
          detail={`${season.last_game.opponent} on ${formatDate(season.last_game.date)}: ${season.last_game.score}`}
          tone="gold"
        />
        <StatCard
          label="Next Game"
          value={`${nextSite}: ${season.next_game.opponent}`}
          detail={`${formatDate(season.next_game.date, { weekday: 'short' })} at ${season.next_game.time_local} · ${season.next_game.venue ?? 'Venue TBD'} · ${nextPitchers.royals.name} vs ${nextPitchers.opponent.name}`}
        />
      </section>

      <section className="feature-grid">
        <article className="feature-panel">
          <div className="panel-heading">
            <Sparkles size={20} />
            <h3>Player of the Game</h3>
          </div>
          <p className="feature-title">{season.player_of_game.name}</p>
          <p>{season.player_of_game.reason}</p>
        </article>
        <article className="feature-panel">
          <div className="panel-heading">
            <Flame size={20} />
            <h3>Prospect Pulse</h3>
          </div>
          <p className="feature-title">{hotProspect.name}</p>
          <p>{hotProspect.note}</p>
        </article>
        <article className="feature-panel">
          <div className="panel-heading">
            <Activity size={20} />
            <h3>Latest Recap</h3>
          </div>
          <p className="feature-title">{latestRecap.title}</p>
          <p>{latestRecap.summary}</p>
        </article>
      </section>
    </div>
  );
}

function GameLogPage() {
  return (
    <section className="content-section">
      <div className="section-heading">
        <p className="eyebrow">Chronological Game Log</p>
        <h2>Royals Games</h2>
      </div>
      <div className="timeline">
        {data.gameLog.games.map((game) => (
          <article key={game.game_pk} className="timeline-item">
            <div>
              <p className="timeline-date">{formatDate(game.date, { weekday: 'short' })}</p>
              <h3>{game.matchup}</h3>
              <p>{game.venue}</p>
            </div>
            <div className="game-result">
              <span className={game.result === 'W' ? 'badge-win' : game.result === 'L' ? 'badge-loss' : 'badge-neutral'}>
                {game.result}
              </span>
              <strong>{game.score}</strong>
              <small>{game.recap_slug ? `Recap: ${game.recap_slug}` : 'Recap pending'}</small>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function StatsPage() {
  const hittingColumns = [
    { key: 'player', label: 'Hitter' },
    { key: 'avg', label: 'AVG', render: pct },
    { key: 'ops', label: 'OPS', render: pct },
    { key: 'hr', label: 'HR' },
    { key: 'rbi', label: 'RBI' },
    { key: 'ab', label: 'AB' },
  ];
  const pitchingColumns = [
    { key: 'player', label: 'Pitcher' },
    { key: 'era', label: 'ERA' },
    { key: 'whip', label: 'WHIP' },
    { key: 'so', label: 'K' },
    { key: 'ip', label: 'IP' },
  ];
  const statcastColumns = [
    { key: 'player', label: 'Player' },
    { key: 'avg_exit_velocity', label: 'EV' },
    { key: 'hard_hit_pct', label: 'Hard-Hit %' },
    { key: 'barrel_pct', label: 'Barrel %' },
    { key: 'note', label: 'Note' },
  ];

  return (
    <div className="space-y-6">
      <section className="content-section">
        <div className="section-heading">
          <p className="eyebrow">MLB Stats API</p>
          <h2>Hitting Leaders</h2>
        </div>
        <DataTable columns={hittingColumns} rows={data.hitting.players} initialSort="ops" />
      </section>
      <section className="content-section">
        <div className="section-heading">
          <p className="eyebrow">MLB Stats API</p>
          <h2>Pitching Leaders</h2>
        </div>
        <DataTable columns={pitchingColumns} rows={data.pitching.players} initialSort="so" />
      </section>
      <section className="content-section">
        <div className="section-heading">
          <p className="eyebrow">Baseball Savant Placeholder Layer</p>
          <h2>Statcast Watchlist</h2>
        </div>
        <DataTable columns={statcastColumns} rows={data.statcast.players} initialSort="hard_hit_pct" />
      </section>
    </div>
  );
}

function ProspectPage() {
  return (
    <div className="space-y-6">
      <section className="content-section accent-section">
        <div className="panel-heading">
          <TrendingUp size={20} />
          <h2>Hot Prospects</h2>
        </div>
        <div className="prospect-hot-grid">
          {data.prospects.hot_prospects.map((prospect) => (
            <article key={prospect.name} className="mini-card">
              <h3>{prospect.name}</h3>
              <p>{prospect.note}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="content-section">
        <div className="section-heading">
          <p className="eyebrow">Farm System Tracker</p>
          <h2>Top Royals Prospects</h2>
        </div>
        <div className="prospect-list">
          {data.prospects.prospects.map((prospect) => (
            <article key={prospect.name} className="prospect-row">
              <div>
                <span className="rank">#{prospect.rank}</span>
                <h3>{prospect.name}</h3>
                <p>{prospect.position} · {prospect.affiliate} · {prospect.level}</p>
              </div>
              <div className="prospect-stat">{prospect.line}</div>
              <p>{prospect.trend_note}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function StandingsPage() {
  const columns = [
    { key: 'team', label: 'Team' },
    { key: 'wins', label: 'W' },
    { key: 'losses', label: 'L' },
    { key: 'pct', label: 'PCT', render: pct },
    { key: 'games_back', label: 'GB' },
    { key: 'streak', label: 'Streak' },
  ];
  return (
    <div className="space-y-6">
      <section className="content-section">
        <div className="section-heading">
          <p className="eyebrow">Division</p>
          <h2>AL Central</h2>
        </div>
        <DataTable columns={columns} rows={data.standings.al_central} initialSort="wins" />
      </section>
      <section className="content-section">
        <div className="section-heading">
          <p className="eyebrow">Playoff Picture</p>
          <h2>AL Wild Card</h2>
        </div>
        <DataTable columns={columns} rows={data.standings.wild_card} initialSort="wins" />
      </section>
    </div>
  );
}

function RecapsPage() {
  return (
    <section className="content-section">
      <div className="section-heading">
        <p className="eyebrow">Generated Content</p>
        <h2>Daily Recaps</h2>
      </div>
      <div className="recap-grid">
        {data.recaps.items.map((recap) => (
          <article key={recap.slug} className="recap-card">
            <div className="recap-meta">
              <span>{formatDate(recap.date)}</span>
              <span>{signed(recap.standings_delta)} GB shift</span>
            </div>
            <h3>{recap.title}</h3>
            <p>{recap.summary}</p>
            <div className="recap-performers">
              {recap.key_performers.map((player) => (
                <span key={player}>{player}</span>
              ))}
            </div>
            <p className="statcast-note">
              <Gauge size={16} /> {recap.statcast_observation}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState('home');
  const generatedAt = formatDate(data.season.generated_at, { year: 'numeric', hour: 'numeric', minute: '2-digit' });
  const pages = {
    home: <HomePage onNavigate={setActivePage} />,
    games: <GameLogPage />,
    stats: <StatsPage />,
    prospects: <ProspectPage />,
    standings: <StandingsPage />,
    recaps: <RecapsPage />,
  };

  return (
    <Shell activePage={activePage} onNavigate={setActivePage} generatedAt={generatedAt}>
      {pages[activePage]}
    </Shell>
  );
}
