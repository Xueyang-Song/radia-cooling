import { EvidenceAccordion } from '../components/EvidenceAccordion'
import { SectionHeading } from '../components/SectionHeading'
import type { SiteData } from '../lib/types'
import { formatValue } from '../lib/format'
import { Link } from 'react-router-dom'
import { useI18n } from '../useI18n'

interface PipelinePageProps {
  siteData: SiteData
}

export function PipelinePage({ siteData }: PipelinePageProps) {
  const { copy, locale } = useI18n()
  const designSpace = siteData.designSpace

  return (
    <div className="space-y-14">
      <SectionHeading
        eyebrow={copy.pipeline.eyebrow}
        title={copy.pipeline.title}
        description={copy.pipeline.description}
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article className="surface-card rounded-[1.8rem] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.pipeline.designSpace}</p>
          <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{designSpace.functionalLayers} layers</p>
          <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{designSpace.materials.join(', ')}</p>
        </article>
        <article className="surface-card rounded-[1.8rem] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.pipeline.thicknessBounds}</p>
          <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{formatValue(designSpace.thicknessMinNm, 0, locale)}-{formatValue(designSpace.thicknessMaxNm, 0, locale)} nm</p>
          <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.pipeline.thicknessDescription}</p>
        </article>
        <article className="surface-card rounded-[1.8rem] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.pipeline.spectralGrid}</p>
          <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{designSpace.wavelengthPoints} points</p>
          <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.pipeline.spectralDescription(formatValue(designSpace.wavelengthStartUm, 1, locale), formatValue(designSpace.wavelengthStopUm, 1, locale))}</p>
        </article>
        <article className="surface-card rounded-[1.8rem] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.pipeline.keyBands}</p>
          <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{formatValue(designSpace.solarBand[0], 1, locale)}-{formatValue(designSpace.windowBand[1], 0, locale)} μm</p>
          <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.pipeline.keyBandsDescription}</p>
        </article>
      </section>

      <section className="surface-card rounded-[2rem] p-7">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.pipeline.visualStageMap}</p>
            <h3 className="mt-3 font-serif text-4xl text-[var(--ink)]">{copy.pipeline.visualTitle}</h3>
            <p className="mt-4 text-base leading-8 text-[var(--muted)]">{copy.pipeline.visualDescription}</p>
          </div>
          <Link to="/notebook" className="inline-flex rounded-full bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-[var(--primary-foreground)] transition hover:translate-y-[-1px]">
            {copy.pipeline.openNotebook}
          </Link>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-5">
          {siteData.labNotebook.stages.map((stage, index) => (
            <article key={stage.id} className="min-w-0 rounded-[1.6rem] border border-[var(--line)] bg-[var(--panel-strong)] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.pipeline.stepLabel(index + 1, stage.eyebrow)}</p>
              <h4 className="mt-3 text-lg font-semibold leading-tight text-[var(--ink)]">{stage.title}</h4>
              <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{stage.summary}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="space-y-6">
        {siteData.pipeline.steps.map((step, index) => (
          <article key={step.id} className="surface-card rounded-[2rem] p-6">
            <div className="grid gap-4 lg:grid-cols-[auto_minmax(0,1fr)] lg:items-start">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--primary)] text-lg font-semibold text-[var(--primary-foreground)]">{index + 1}</div>
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.pipeline.stepLabel(index + 1, step.title)}</p>
                <h3 className="mt-2 font-serif text-3xl text-[var(--ink)]">{step.title}</h3>
                <p className="mt-3 max-w-4xl text-base leading-8 text-[var(--muted)]">{step.why}</p>
                <div className="mt-5 grid gap-4 md:grid-cols-2">
                  <div className="surface-inset rounded-2xl p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">{copy.pipeline.inputs}</p>
                    <ul className="mt-3 space-y-2 text-sm leading-7 text-[var(--ink)]">
                      {step.inputs.map((item) => (
                        <li key={item}>- {item}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="surface-inset rounded-2xl p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">{copy.pipeline.outputs}</p>
                    <ul className="mt-3 space-y-2 text-sm leading-7 text-[var(--ink)]">
                      {step.outputs.map((item) => (
                        <li key={item}>- {item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div className="surface-inset mt-5 rounded-2xl p-4 text-sm leading-7 text-[var(--muted)]">
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">{copy.common.evidence}</p>
                <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
                  {copy.common.fileCount(step.evidenceFiles.length)}
                </div>
              </div>
              <div className="mt-3">
                <EvidenceAccordion files={step.evidenceFiles} editorHeight={320} />
              </div>
            </div>
          </article>
        ))}
      </section>

      <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-start">
        <div className="surface-card rounded-[2rem] p-7">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.pipeline.glossary}</p>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {siteData.glossary.map((term) => (
              <div key={term.term} className="surface-inset rounded-2xl p-4">
                <h3 className="font-semibold text-[var(--ink)]">{term.term}</h3>
                <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{term.explanation}</p>
              </div>
            ))}
          </div>
        </div>
        <div className="surface-hero rounded-[2rem] p-7">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.pipeline.loopMatters}</p>
          <p className="mt-4 font-serif text-3xl text-[var(--ink)]">{copy.pipeline.loopTitle}</p>
          <p className="mt-4 text-base leading-8 text-[var(--muted)]">{copy.pipeline.loopDescription}</p>
        </div>
      </section>
    </div>
  )
}