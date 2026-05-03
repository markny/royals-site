export function formatDate(value, options = {}) {
  if (!value) return 'TBD';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    ...options,
  }).format(date);
}

export function formatRecord(record) {
  if (!record) return '0-0';
  return `${record.wins ?? 0}-${record.losses ?? 0}`;
}

export function pct(value) {
  if (value === null || value === undefined || value === '') return '-';
  return typeof value === 'number' ? value.toFixed(3).replace(/^0/, '') : value;
}

export function signed(value) {
  if (value === null || value === undefined) return '-';
  return value > 0 ? `+${value}` : `${value}`;
}
