export default function StatCard({ label, value, detail, tone = 'default' }) {
  return (
    <section className={`stat-card stat-card-${tone}`}>
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-black tracking-tight text-slate-950">{value}</p>
      {detail ? <p className="mt-2 text-sm leading-6 text-slate-600">{detail}</p> : null}
    </section>
  );
}
