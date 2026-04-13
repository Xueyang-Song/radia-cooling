interface MetricCardProps {
  label: string
  value: string
  detail: string
  tone?: 'cool' | 'warm'
}

export function MetricCard({ label, value, detail, tone = 'cool' }: MetricCardProps) {
  const badgeClasses = tone === 'warm' ? 'bg-[var(--accent-warm-soft)] text-[var(--accent-warm)]' : 'bg-[var(--accent-soft)] text-[var(--accent)]'

  return (
    <article className="surface-card rounded-[1.45rem] p-5">
      <p className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] ${badgeClasses}`}>{label}</p>
      <p className="mt-4 text-3xl font-semibold tracking-tight text-[var(--ink)] md:text-4xl">{value}</p>
      <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{detail}</p>
    </article>
  )
}