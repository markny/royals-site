import { ArrowDownUp } from 'lucide-react';
import { useMemo, useState } from 'react';

export default function DataTable({ columns, rows, initialSort }) {
  const [sort, setSort] = useState(initialSort ?? columns[0]?.key);
  const [direction, setDirection] = useState('desc');

  const sortedRows = useMemo(() => {
    return [...rows].sort((a, b) => {
      const left = a[sort];
      const right = b[sort];
      const result =
        typeof left === 'number' && typeof right === 'number'
          ? left - right
          : String(left ?? '').localeCompare(String(right ?? ''));
      return direction === 'asc' ? result : -result;
    });
  }, [direction, rows, sort]);

  function toggleSort(key) {
    if (key === sort) {
      setDirection((current) => (current === 'asc' ? 'desc' : 'asc'));
      return;
    }
    setSort(key);
    setDirection('desc');
  }

  return (
    <div className="table-frame">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>
                <button type="button" onClick={() => toggleSort(column.key)} title={`Sort by ${column.label}`}>
                  <span>{column.label}</span>
                  <ArrowDownUp size={14} aria-hidden="true" />
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row, rowIndex) => (
            <tr key={row.id ?? `${row.player}-${rowIndex}`}>
              {columns.map((column) => (
                <td key={column.key}>{column.render ? column.render(row[column.key], row) : row[column.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
