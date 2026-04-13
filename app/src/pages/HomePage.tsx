import { Link } from 'react-router-dom'
import { MetricCard } from '../components/MetricCard'
import { SectionHeading } from '../components/SectionHeading'
import type { SiteData } from '../lib/types'
import { useI18n } from '../useI18n'

interface HomePageProps {
  siteData: SiteData
}

export function HomePage({ siteData }: HomePageProps) {
  const { copy } = useI18n()

  return (
    <div className="space-y-10">
      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] xl:items-start">
        <div className="surface-hero rounded-[2rem] p-7 md:p-8">
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-[var(--accent)]">{copy.home.heroEyebrow}</p>
          <h2 className="mt-4 max-w-4xl font-serif text-4xl leading-[1.02] text-[var(--ink)] md:text-5xl">
            {copy.home.heroTitle}
          </h2>
          <p className="mt-5 max-w-3xl text-base leading-8 text-[var(--muted)]">{siteData.project.summary}</p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link to="/pipeline" className="rounded-full bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-[var(--primary-foreground)] transition hover:translate-y-[-1px]">
              {copy.home.walkPipeline}
            </Link>
            <Link to="/notebook" className="rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-5 py-3 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--primary)]">
              {copy.home.openNotebook}
            </Link>
            <Link to="/compare" className="rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-5 py-3 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--accent)]">
              {copy.home.compareModels}
            </Link>
            <Link to="/research" className="rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-5 py-3 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--accent)]">
              {copy.home.readResearch}
            </Link>
          </div>

          <div className="mt-7 grid gap-3 md:grid-cols-3">
            <div className="surface-inset rounded-[1.3rem] px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.home.projectMode}</p>
              <p className="mt-3 text-lg font-semibold text-[var(--ink)]">{copy.home.projectModeTitle}</p>
              <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{copy.home.projectModeDescription}</p>
            </div>
            <div className="surface-inset rounded-[1.3rem] px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.home.dataset}</p>
              <p className="mt-3 text-lg font-semibold text-[var(--ink)]">{siteData.dataset.numSamples} WPTherml samples</p>
              <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{copy.home.datasetDescription}</p>
            </div>
            <div className="surface-inset rounded-[1.3rem] px-4 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.home.research}</p>
              <p className="mt-3 text-lg font-semibold text-[var(--ink)]">{siteData.researchLibrary.paperCount} papers reviewed</p>
              <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{copy.home.researchDescription}</p>
            </div>
          </div>
        </div>
        <div className="surface-card rounded-[2rem] p-7">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.home.retainedWorkflow}</p>
              <p className="mt-3 font-serif text-3xl leading-tight text-[var(--ink)]">{siteData.comparison.retainedWorkflow.title}</p>
            </div>
            <div className="rounded-full bg-[var(--accent-soft)] px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">{copy.home.defaultPath}</div>
          </div>
          <p className="mt-4 text-base leading-8 text-[var(--muted)]">{siteData.project.finalVerdict}</p>
          <ol className="mt-6 space-y-3">
            {siteData.comparison.retainedWorkflow.steps.map((step, index) => (
              <li key={step} className="surface-inset flex gap-3 rounded-2xl px-4 py-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--primary)] text-sm font-semibold text-[var(--primary-foreground)]">{index + 1}</span>
                <span className="text-sm leading-7 text-[var(--ink)]">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {siteData.project.heroStats.map((stat, index) => (
          <MetricCard key={stat.label} label={stat.label} value={stat.value} detail={stat.detail} tone={index % 2 === 0 ? 'cool' : 'warm'} />
        ))}
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        <article className="surface-card rounded-[2rem] p-7">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.home.visualFirst}</p>
          <h3 className="mt-4 font-serif text-3xl text-[var(--ink)]">{copy.home.visualTitle}</h3>
          <p className="mt-4 text-base leading-8 text-[var(--muted)]">{copy.home.visualDescription}</p>
          <Link to="/notebook" className="mt-5 inline-flex rounded-full bg-[var(--primary)] px-4 py-3 text-sm font-semibold text-[var(--primary-foreground)] transition hover:translate-y-[-1px]">
            {copy.home.goToNotebook}
          </Link>
        </article>
        <article className="surface-card rounded-[2rem] p-7">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.home.seePhysics}</p>
          <h3 className="mt-4 font-serif text-3xl text-[var(--ink)]">{copy.home.seePhysicsTitle}</h3>
          <p className="mt-4 text-base leading-8 text-[var(--muted)]">{copy.home.seePhysicsDescription}</p>
          <Link to="/explore" className="mt-5 inline-flex rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-4 py-3 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--primary)]">
            {copy.home.openExplore}
          </Link>
        </article>
        <article className="surface-card rounded-[2rem] p-7">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.home.sourceTrail}</p>
          <h3 className="mt-4 font-serif text-3xl text-[var(--ink)]">{copy.home.sourceTrailTitle}</h3>
          <p className="mt-4 text-base leading-8 text-[var(--muted)]">{copy.home.sourceTrailDescription}</p>
          <Link to="/research" className="mt-5 inline-flex rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-4 py-3 text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--primary)]">
            {copy.home.openResearch}
          </Link>
        </article>
      </section>

      <section className="space-y-8">
        <SectionHeading
          eyebrow={copy.home.sectionEyebrow}
          title={copy.home.sectionTitle}
          description={copy.home.sectionDescription}
        />
        <div className="grid gap-5 lg:grid-cols-2">
          {siteData.project.cards.map((card, index) => (
            <article key={card.id} className="surface-card rounded-[2rem] p-7">
              <p className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] ${index % 2 === 0 ? 'bg-[var(--accent-soft)] text-[var(--accent)]' : 'bg-[var(--accent-warm-soft)] text-[var(--accent-warm)]'}`}>
                {copy.home.chapter(index + 1)}
              </p>
              <h3 className="mt-5 font-serif text-3xl text-[var(--ink)]">{card.title}</h3>
              <p className="mt-4 text-base leading-8 text-[var(--muted)]">{card.summary}</p>
              <p className="mt-4 text-sm leading-7 text-[var(--ink)]">{card.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
        <div className="surface-card rounded-[2rem] p-7">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.home.twoReferenceWins}</p>
          <div className="mt-5 space-y-4">
            {siteData.comparison.targetResults.map((target) => (
              <div key={target.id} className="surface-inset rounded-2xl p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-semibold text-[var(--ink)]">{target.label}</h3>
                    <p className="mt-1 text-sm leading-7 text-[var(--muted)]">{target.summary}</p>
                  </div>
                  <div className="rounded-full bg-[var(--accent-soft)] px-3 py-1 text-sm font-semibold text-[var(--accent)]">
                    {target.contenders[0].value.toFixed(4)} {copy.common.verifiedTotalError}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="surface-card rounded-[2rem] p-7">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.home.whatHappenedOverTime}</p>
          <div className="mt-5 space-y-4">
            {siteData.timeline.slice(0, 4).map((event, index) => (
              <div key={event.id} className="surface-inset flex gap-4 rounded-2xl p-4">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[var(--primary)] text-sm font-semibold text-[var(--primary-foreground)]">{index + 1}</span>
                <div>
                  <h3 className="font-semibold text-[var(--ink)]">{event.title}</h3>
                  <p className="mt-2 text-sm leading-7 text-[var(--muted)]">{event.summary}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}