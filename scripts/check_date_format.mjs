import { formatDate } from '../src/lib/format.js';

const checks = [
  {
    value: '2026-05-04',
    options: { weekday: 'short' },
    expected: 'Mon, May 4',
  },
  {
    value: '2026-05-03',
    options: {},
    expected: 'May 3',
  },
];

for (const check of checks) {
  const actual = formatDate(check.value, check.options);
  if (actual !== check.expected) {
    console.error(`Expected ${check.value} to format as "${check.expected}", got "${actual}"`);
    process.exit(1);
  }
}

console.log('Date formatting checks passed.');
