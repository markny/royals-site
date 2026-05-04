export function formatDate(value, options = {}) {
  if (!value) return 'TBD';
  const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  const date = dateOnly
    ? new Date(Number(dateOnly[1]), Number(dateOnly[2]) - 1, Number(dateOnly[3]))
    : new Date(value);
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
