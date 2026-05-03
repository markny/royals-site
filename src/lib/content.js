import season from '../../data/generated/season-summary.json';
import gameLog from '../../data/generated/game-log.json';
import standings from '../../data/generated/standings.json';
import hitting from '../../data/generated/hitting-stats.json';
import pitching from '../../data/generated/pitching-stats.json';
import statcast from '../../data/generated/statcast-metrics.json';
import prospects from '../../data/generated/prospects.json';
import recapIndex from '../../content/recaps/index.json';

export const data = {
  season,
  gameLog,
  standings,
  hitting,
  pitching,
  statcast,
  prospects,
  recaps: recapIndex,
};
