import { SectionHeading } from '../components/SectionHeading'
import type { ModelSummary, SiteData, TargetContender } from '../lib/types'
import { formatFixed, formatValue, labelFromMetric } from '../lib/format'
import { Link } from 'react-router-dom'
import { useI18n } from '../useI18n'

interface ComparePageProps {
  siteData: SiteData
}

function statusClasses(status: ModelSummary['status'] | TargetContender['status']): string {
  switch (status) {
    case 'retained':
      return 'bg-[var(--accent-soft)] text-[var(--accent)]'
    case 'competitive':
      return 'bg-[color:color-mix(in_oklab,var(--primary)_14%,transparent)] text-[var(--primary)]'
    case 'rejected':
      return 'bg-[var(--accent-warm-soft)] text-[var(--accent-warm)]'
    default:
      return 'bg-[var(--panel-muted)] text-[var(--muted)]'
  }
}

export function ComparePage({ siteData }: ComparePageProps) {
  const { copy, locale } = useI18n()

  return (
    <div className="space-y-14">
      <SectionHeading
        eyebrow={copy.compare.eyebrow}
        title={copy.compare.title}
        description={copy.compare.description}
      />

      <section className="surface-hero rounded-[2rem] p-7">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.compare.retainedBestMethod}</p>
        <h3 className="mt-4 font-serif text-4xl text-[var(--ink)]">{siteData.comparison.retainedWorkflow.title}</h3>
        <p className="mt-4 max-w-4xl text-base leading-8 text-[var(--muted)]">{siteData.comparison.retainedWorkflow.summary}</p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link to="/notebook" className="rounded-full bg-[var(--primary)] px-4 py-3 text-sm font-semibold text-[var(--primary-foreground)] transition hover:translate-y-[-1px]">
            {copy.compare.inspectNotebook}
          </Link>
          <Link to="/explore" className="rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-4 py-3 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--primary)]">
            {copy.compare.seeWinningStructures}
          </Link>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-2">
        {siteData.comparison.models.map((model) => (
          <article key={model.id} className="surface-card min-w-0 rounded-[2rem] p-7">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] ${statusClasses(model.status)}`}>
                  {copy.enums.modelStatus[model.status]}
                </p>
                <h3 className="mt-4 font-serif text-3xl text-[var(--ink)]">{model.name}</h3>
                <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{model.family}</p>
              </div>
              <div className="surface-inset rounded-2xl px-4 py-3 text-sm text-[var(--muted)]">
                <div>{copy.compare.split}: {model.splitMode}</div>
                <div>{copy.compare.device}: {model.device}</div>
              </div>
            </div>

            <p className="mt-5 text-base leading-8 text-[var(--muted)]">{model.summary}</p>

            <div className="mt-6 grid gap-3 md:grid-cols-3">
              {Object.entries(model.metrics).map(([key, value]) => (
                <div key={key} className="surface-inset rounded-2xl p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">{labelFromMetric(key, locale)}</p>
                  <p className="mt-3 text-2xl font-semibold text-[var(--ink)]">{formatValue(value, 3, locale)}</p>
                </div>
              ))}
            </div>

            <div className="surface-inset mt-6 rounded-2xl p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">{copy.compare.verifiedHighlights}</p>
              <div className="mt-3 flex flex-wrap gap-3">
                {Object.entries(model.verifiedHighlights).map(([key, value]) => (
                  <span key={key} className="rounded-full bg-[var(--accent-soft)] px-3 py-2 text-sm font-semibold text-[var(--ink)]">
                    {key}: {formatFixed(value, 4, locale)}
                  </span>
                ))}
              </div>
            </div>
          </article>
        ))}
      </section>

      <section className="space-y-6">
        {siteData.comparison.targetResults.map((target) => {
          const maxValue = Math.max(...target.contenders.map((contender) => contender.value))
          return (
            <article key={target.id} className="surface-card rounded-[2rem] p-7">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="max-w-3xl">
                  <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{target.label}</p>
                  <h3 className="mt-3 font-serif text-3xl text-[var(--ink)]">{copy.compare.targetTitle}</h3>
                  <p className="mt-3 text-base leading-8 text-[var(--muted)]">{target.summary}</p>
                </div>
                <div className="surface-inset rounded-2xl p-4 text-sm leading-7 text-[var(--muted)]">
                  {Object.entries(target.targetMetrics).map(([key, value]) => (
                    <div key={key}>
                      {labelFromMetric(key, locale)}: {formatValue(value, 4, locale)}
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-6 space-y-4">
                {target.contenders.map((contender) => (
                  <div key={contender.label} className="surface-inset rounded-2xl p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                      <div>
                        <p className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] ${statusClasses(contender.status)}`}>
                          {copy.enums.modelStatus[contender.status]}
                        </p>
                        <p className="mt-3 font-semibold text-[var(--ink)]">{contender.label}</p>
                        <p className="mt-1 break-words text-sm text-[var(--muted)]">{contender.sourcePath}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-3xl font-semibold text-[var(--ink)]">{formatFixed(contender.value, 4, locale)}</p>
                        <p className="text-sm text-[var(--muted)]">{copy.common.verifiedTotalError}</p>
                      </div>
                    </div>
                    <div className="mt-4 h-3 overflow-hidden rounded-full bg-[var(--panel-muted)]">
                      <div
                        className={`h-full rounded-full ${contender.status === 'retained' ? 'bg-[var(--accent)]' : contender.status === 'rejected' ? 'bg-[var(--accent-warm)]' : 'bg-[#2b6aa6]'}`}
                        style={{ width: `${(contender.value / maxValue) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </article>
          )
        })}
      </section>
    </div>
  )
}