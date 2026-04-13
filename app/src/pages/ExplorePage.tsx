import { useEffect, useState } from 'react'
import { LayerStack } from '../components/LayerStack'
import { SectionHeading } from '../components/SectionHeading'
import { SpectrumChart } from '../components/SpectrumChart'
import type { CandidateShowcaseItem, DatasetSample, SiteData } from '../lib/types'
import { formatValue, labelFromMetric } from '../lib/format'
import { useI18n } from '../useI18n'

interface ExplorePageProps {
  siteData: SiteData
}

export function ExplorePage({ siteData }: ExplorePageProps) {
  const { copy } = useI18n()
  const [selectedSampleId, setSelectedSampleId] = useState(siteData.dataset.selectedSamples[0]?.id ?? '')
  const [selectedCandidateId, setSelectedCandidateId] = useState(siteData.comparison.candidateShowcase[0]?.id ?? '')

  // Sync selection state when siteData changes or component remounts
  useEffect(() => {
    setSelectedSampleId(siteData.dataset.selectedSamples[0]?.id ?? '')
  }, [siteData.dataset.selectedSamples])

  useEffect(() => {
    setSelectedCandidateId(siteData.comparison.candidateShowcase[0]?.id ?? '')
  }, [siteData.comparison.candidateShowcase])

  const selectedSample = siteData.dataset.selectedSamples.find((sample) => sample.id === selectedSampleId) ?? siteData.dataset.selectedSamples[0]
  const selectedCandidate =
    siteData.comparison.candidateShowcase.find((candidate) => candidate.id === selectedCandidateId) ?? siteData.comparison.candidateShowcase[0]

  return (
    <div className="space-y-14">
      <SectionHeading
        eyebrow={copy.explore.eyebrow}
        title={copy.explore.title}
        description={copy.explore.description}
      />

      <section className="grid gap-8 lg:grid-cols-[0.42fr_0.58fr] lg:items-start">
        <div className="surface-card rounded-[2rem] p-6">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.explore.datasetSamplePicker}</p>
          <div className="mt-5 space-y-3">
            {siteData.dataset.selectedSamples.map((sample) => {
              const active = sample.id === selectedSampleId
              return (
                <button
                  key={sample.id}
                  type="button"
                  onClick={() => setSelectedSampleId(sample.id)}
                  className={[
                    'w-full rounded-2xl border px-4 py-4 text-left transition',
                    active
                      ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)] shadow-[var(--panel-shadow)]'
                      : 'border-[var(--line)] bg-[var(--panel-strong)] text-[var(--ink)] hover:border-[var(--accent)]',
                  ].join(' ')}
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] opacity-70">{sample.label}</p>
                  <p className="mt-2 text-lg font-semibold">{sample.sampleId}</p>
                  <p className="mt-2 text-sm leading-7 opacity-80">{sample.note}</p>
                </button>
              )
            })}
          </div>
        </div>

        <DatasetSamplePanel sample={selectedSample} siteData={siteData} />
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.42fr_0.58fr] lg:items-start">
        <div className="surface-card rounded-[2rem] p-6">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.explore.candidatePicker}</p>
          <div className="mt-5 space-y-3">
            {siteData.comparison.candidateShowcase.map((candidate) => {
              const active = candidate.id === selectedCandidateId
              const familyLabel = copy.enums.candidateFamily[candidate.family as keyof typeof copy.enums.candidateFamily] ?? candidate.family
              const routeLabel = copy.enums.candidateRoute[candidate.route as keyof typeof copy.enums.candidateRoute] ?? candidate.route
              return (
                <button
                  key={candidate.id}
                  type="button"
                  onClick={() => setSelectedCandidateId(candidate.id)}
                  className={[
                    'w-full rounded-2xl border px-4 py-4 text-left transition',
                    active
                      ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)] shadow-[var(--panel-shadow)]'
                      : 'border-[var(--line)] bg-[var(--panel-strong)] text-[var(--ink)] hover:border-[var(--accent)]',
                  ].join(' ')}
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] opacity-70">{familyLabel} / {routeLabel}</p>
                  <p className="mt-2 text-lg font-semibold">{candidate.label}</p>
                  <p className="mt-2 text-sm leading-7 opacity-80">{candidate.note}</p>
                </button>
              )
            })}
          </div>
        </div>

        <CandidatePanel candidate={selectedCandidate} />
      </section>
    </div>
  )
}

function DatasetSamplePanel({ sample, siteData }: { sample: DatasetSample; siteData: SiteData }) {
  const { copy, locale } = useI18n()

  return (
    <div className="space-y-6">
      <div className="surface-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.explore.realSpectrumViewer}</p>
            <h3 className="mt-3 font-serif text-3xl text-[var(--ink)]">{sample.label}</h3>
            <p className="mt-3 text-base leading-8 text-[var(--muted)]">{sample.note}</p>
          </div>
          <div className="surface-inset rounded-2xl px-4 py-3 text-sm text-[var(--muted)]">
            <div>{copy.common.sample(sample.sampleId)}</div>
            <div>{copy.common.totalThickness(formatValue(sample.totalThicknessNm, 1, locale))}</div>
          </div>
        </div>
      </div>

      <SpectrumChart sample={sample} wavelengths={siteData.dataset.wavelengths} designSpace={siteData.designSpace} />
      <LayerStack
        materials={sample.layerMaterials}
        thicknessesNm={sample.layerThicknessesNm}
        reflectorMaterial={siteData.designSpace.reflectorMaterial}
        reflectorThicknessNm={siteData.designSpace.reflectorThicknessNm}
      />
    </div>
  )
}

function CandidatePanel({ candidate }: { candidate: CandidateShowcaseItem }) {
  const { copy, locale } = useI18n()

  return (
    <div className="space-y-6">
      <div className="surface-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.explore.verifiedCandidate}</p>
            <h3 className="mt-3 font-serif text-3xl text-[var(--ink)]">{candidate.label}</h3>
            <p className="mt-3 text-base leading-8 text-[var(--muted)]">{candidate.note}</p>
          </div>
          <div className="surface-inset rounded-2xl px-4 py-3 text-right">
            <p className="text-3xl font-semibold text-[var(--ink)]">{candidate.totalAbsoluteError.toFixed(4)}</p>
            <p className="text-sm text-[var(--muted)]">{copy.common.verifiedTotalError}</p>
          </div>
        </div>
      </div>

      <LayerStack
        materials={candidate.layerMaterials}
        thicknessesNm={candidate.layerThicknessesNm}
        reflectorMaterial={candidate.reflectorMaterial}
        reflectorThicknessNm={candidate.reflectorThicknessNm}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <MetricTable title={copy.explore.targetMetrics} metrics={candidate.targets} />
        <MetricTable title={copy.explore.simulatorMetrics} metrics={candidate.simulated} />
      </div>

      <div className="surface-card-strong rounded-[1.6rem] p-5">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.explore.absoluteError}</p>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {Object.entries(candidate.absoluteError).map(([key, value]) => (
            <div key={key} className="surface-inset rounded-2xl p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">{labelFromMetric(key, locale)}</p>
              <p className="mt-3 text-2xl font-semibold text-[var(--ink)]">{formatValue(value, 4, locale)}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 break-words text-sm leading-7 text-[var(--muted)]">{copy.common.sourceFile(candidate.sourcePath)}</p>
      </div>
    </div>
  )
}

function MetricTable({ title, metrics }: { title: string; metrics: Record<string, number> }) {
  const { locale } = useI18n()

  return (
    <div className="surface-card-strong rounded-[1.6rem] p-5">
      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{title}</p>
      <div className="mt-4 space-y-3">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="surface-inset flex items-center justify-between gap-4 rounded-2xl px-4 py-3">
            <span className="text-sm text-[var(--muted)]">{labelFromMetric(key, locale)}</span>
            <span className="font-semibold text-[var(--ink)]">{formatValue(value, 4, locale)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}