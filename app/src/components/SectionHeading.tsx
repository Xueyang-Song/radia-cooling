interface SectionHeadingProps {
  eyebrow: string
  title: string
  description: string
}

export function SectionHeading({ eyebrow, title, description }: SectionHeadingProps) {
  return (
    <div className="max-w-4xl">
      <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[var(--accent)]">{eyebrow}</p>
      <h2 className="mt-3 font-serif text-3xl leading-tight text-[var(--ink)] md:text-4xl">{title}</h2>
      <p className="mt-3 max-w-3xl text-sm leading-7 text-[var(--muted)] md:text-base">{description}</p>
    </div>
  )
}