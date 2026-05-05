import season from '../../data/generated/season-summary.json';
import gameLog from '../../data/generated/game-log.json';
import standings from '../../data/generated/standings.json';
import hitting from '../../data/generated/hitting-stats.json';
import sabermetrics from '../../data/generated/hitting-sabermetrics.json';
import pitching from '../../data/generated/pitching-stats.json';
import statcast from '../../data/generated/statcast-metrics.json';
import latestGameDetails from '../../data/generated/latest-game-details.json';
import latestGameHighlights from '../../data/generated/latest-game-highlights.json';
import scoreboard from '../../data/generated/scoreboard.json';
import prospects from '../../data/generated/prospects.json';
import recapIndex from '../../content/recaps/index.json';

export const data = {
  season,
  gameLog,
  standings,
  hitting,
  sabermetrics,
  pitching,
  statcast,
  latestGameDetails,
  latestGameHighlights,
  scoreboard,
  prospects,
  recaps: recapIndex,
};
