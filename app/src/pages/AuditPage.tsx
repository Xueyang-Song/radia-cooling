import { useState } from 'react'
import { EvidenceAccordion } from '../components/EvidenceAccordion'
import { MetricCard } from '../components/MetricCard'
import { SectionHeading } from '../components/SectionHeading'
import type { SiteData } from '../lib/types'
import { useI18n } from '../useI18n'

interface AuditPageProps {
  siteData: SiteData
}

type AuditWorkspaceTab = 'evidence' | 'records' | 'verdict'

export function AuditPage({ siteData }: AuditPageProps) {
  const { copy } = useI18n()
  const [activeEventId, setActiveEventId] = useState(siteData.timeline[0]?.id ?? '')
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<AuditWorkspaceTab>('evidence')
  const activeEvent = siteData.timeline.find((event) => event.id === activeEventId) ?? siteData.timeline[0]

  return (
    <div className="space-y-4 lg:h-[calc(100vh-9.5rem)]">
      <div className="space-y-4 lg:hidden">
        <SectionHeading
          eyebrow={copy.audit.eyebrow}
          title={copy.audit.title}
          description={copy.audit.description}
        />

        <div className="hidden flex-wrap gap-2 lg:flex">
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{copy.audit.checkpointCount(siteData.timeline.length)}</div>
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{copy.audit.recordCount(siteData.filesOfRecord.length)}</div>
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{copy.audit.selectedCheckpointBadge(activeEvent?.title ?? copy.common.unknown)}</div>
        </div>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4 lg:hidden">
          <MetricCard label={copy.audit.datasetSize} value={String(siteData.dataset.numSamples)} detail={copy.audit.datasetSizeDetail} />
          <MetricCard label={copy.audit.wavelengthGrid} value={String(siteData.designSpace.wavelengthPoints)} detail={copy.audit.wavelengthGridDetail} tone="warm" />
          <MetricCard label={copy.audit.retainedWinner} value={siteData.comparison.targetResults[1]?.contenders[0]?.value.toFixed(4) ?? '0.0000'} detail={copy.audit.retainedWinnerDetail} />
          <MetricCard label={copy.audit.categoricalBranch} value={siteData.comparison.targetResults[0]?.contenders[4]?.value.toFixed(4) ?? '0.0000'} detail={copy.audit.categoricalBranchDetail} tone="warm" />
        </section>
      </div>

      <section className="grid gap-4 lg:h-full lg:min-h-0 lg:grid-cols-[20rem_minmax(0,1fr)]">
        <aside className="grid gap-4 lg:min-h-0 lg:grid-rows-[auto_minmax(0,1fr)]">
          <div className="surface-hero rounded-[1.8rem] p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.audit.auditVerdict}</p>
            <h3 className="mt-3 font-serif text-3xl text-[var(--ink)]">{copy.audit.auditVerdictTitle}</h3>
            <p className="mt-4 text-sm leading-7 text-[var(--muted)]">{copy.audit.auditVerdictDescription}</p>
          </div>

          <div className="surface-card min-h-0 rounded-[1.8rem] p-4 lg:flex lg:flex-col">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.audit.auditTimeline}</p>
            <div className="mt-4 min-h-0 space-y-2 lg:overflow-y-auto lg:pr-1 app-scrollbar">
              {siteData.timeline.map((event, index) => {
                const isActive = event.id === activeEvent?.id
                return (
                  <button
                    key={event.id}
                    type="button"
                    onClick={() => {
                      setActiveEventId(event.id)
                      setActiveWorkspaceTab('evidence')
                    }}
                    className={[
                      'w-full rounded-[1.2rem] border px-4 py-4 text-left transition',
                      isActive
                        ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)] shadow-[var(--panel-shadow)]'
                        : 'border-[var(--line)] bg-[var(--panel)] text-[var(--ink)] hover:border-[var(--primary)]',
                    ].join(' ')}
                  >
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] opacity-75">{copy.audit.checkpoint(index + 1)}</p>
                    <p className="mt-2 text-base font-semibold leading-tight">{event.title}</p>
                    <p className="mt-2 text-sm leading-6 opacity-80">{event.summary}</p>
                  </button>
                )
              })}
            </div>
          </div>
        </aside>

        <div className="surface-card min-h-0 overflow-hidden rounded-[1.8rem] p-0 lg:flex lg:flex-col">
          <div className="border-b border-[var(--line)] px-4 py-3">
            <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_18rem] xl:items-start">
              <div className="min-w-0">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.audit.selectedCheckpoint}</p>
                <h3 className="mt-2 font-serif text-2xl text-[var(--ink)]">{activeEvent?.title}</h3>
                <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{activeEvent?.summary}</p>
              </div>
              <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                <div className="surface-inset rounded-[1.2rem] px-4 py-2.5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.common.evidence}</p>
                  <p className="mt-1 text-lg font-semibold text-[var(--ink)]">{activeEvent?.evidenceFiles.length ?? 0}</p>
                </div>
                <div className="surface-inset rounded-[1.2rem] px-4 py-2.5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.common.records}</p>
                  <p className="mt-1 text-lg font-semibold text-[var(--ink)]">{siteData.filesOfRecord.length}</p>
                </div>
                <div className="surface-inset rounded-[1.2rem] px-4 py-2.5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.common.timeline}</p>
                  <p className="mt-1 text-lg font-semibold text-[var(--ink)]">{siteData.timeline.length}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 border-b border-[var(--line)] px-4 py-3">
            {([
              ['evidence', copy.audit.workspaceTabs.evidence],
              ['records', copy.audit.workspaceTabs.records],
              ['verdict', copy.audit.workspaceTabs.verdict],
            ] as Array<[AuditWorkspaceTab, string]>).map(([tab, label]) => {
              const isActive = activeWorkspaceTab === tab
              return (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveWorkspaceTab(tab)}
                  className={[
                    'rounded-full border px-4 py-2 text-sm font-medium transition',
                    isActive
                      ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)]'
                      : 'border-[var(--line)] bg-[var(--panel-strong)] text-[var(--muted)] hover:border-[var(--primary)] hover:text-[var(--foreground)]',
                  ].join(' ')}
                >
                  {label}
                </button>
              )
            })}
          </div>

          <div className="flex-1 min-h-0 p-4">
            {activeWorkspaceTab === 'evidence' ? (
              <div className="h-full min-h-[520px] overflow-y-auto pr-1 app-scrollbar lg:min-h-0">
                {activeEvent ? <EvidenceAccordion files={activeEvent.evidenceFiles} editorHeight={520} /> : null}
              </div>
            ) : activeWorkspaceTab === 'records' ? (
              <div className="h-full min-h-[520px] overflow-y-auto pr-1 app-scrollbar lg:min-h-0">
                <EvidenceAccordion files={siteData.filesOfRecord.map((item) => item.viewer)} editorHeight={520} />
              </div>
            ) : (
              <div className="grid h-full min-h-[520px] gap-4 xl:grid-cols-[minmax(0,1.2fr)_20rem] lg:min-h-0">
                <div className="min-h-0 space-y-4 overflow-y-auto pr-1 app-scrollbar">
                  <div className="surface-hero rounded-[1.6rem] p-5">
                    <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.audit.verdict}</p>
                    <h4 className="mt-3 font-serif text-3xl text-[var(--ink)]">{copy.audit.auditVerdictTitle}</h4>
                    <p className="mt-4 text-sm leading-7 text-[var(--muted)] md:text-base">{copy.audit.auditVerdictDescription}</p>
                  </div>

                  <div className="surface-card rounded-[1.6rem] p-5">
                    <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.audit.checkpointSummaries}</p>
                    <div className="mt-4 space-y-3">
                      {siteData.timeline.map((event, index) => (
                        <div key={event.id} className="surface-inset rounded-[1.2rem] px-4 py-4 text-sm leading-7 text-[var(--muted)]">
                          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.audit.checkpoint(index + 1)}</p>
                          <p className="mt-2 font-semibold text-[var(--ink)]">{event.title}</p>
                          <p className="mt-2">{event.summary}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="min-h-0 space-y-4 overflow-y-auto pr-1 app-scrollbar">
                  <MetricCard label={copy.audit.datasetSize} value={String(siteData.dataset.numSamples)} detail={copy.audit.datasetSizeDetail} />
                  <MetricCard label={copy.audit.wavelengthGrid} value={String(siteData.designSpace.wavelengthPoints)} detail={copy.audit.wavelengthGridDetail} tone="warm" />
                  <MetricCard label={copy.audit.retainedWinner} value={siteData.comparison.targetResults[1]?.contenders[0]?.value.toFixed(4) ?? '0.0000'} detail={copy.audit.retainedWinnerDetail} />
                  <MetricCard label={copy.audit.categoricalBranch} value={siteData.comparison.targetResults[0]?.contenders[4]?.value.toFixed(4) ?? '0.0000'} detail={copy.audit.categoricalBranchDetail} tone="warm" />
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}