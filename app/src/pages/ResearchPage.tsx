import { startTransition, useDeferredValue, useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useSearchParams } from 'react-router-dom'
import remarkGfm from 'remark-gfm'
import { SectionHeading } from '../components/SectionHeading'
import { formatBytes } from '../lib/format'
import type { ResearchPaper, ResearchPayload, SiteData } from '../lib/types'
import { useI18n } from '../useI18n'

interface ResearchPageProps {
  siteData: SiteData
  researchPayload: ResearchPayload
}

type LibraryMode = 'guides' | 'papers'
type PaperViewMode = 'overview' | 'details' | 'pdf'

function paperStatusClasses(status: ResearchPaper['status']): string {
  switch (status) {
    case 'downloaded':
      return 'bg-[color:var(--accent-soft)] text-[var(--ink)]'
    case 'open-access-link':
      return 'bg-[rgba(59,130,246,0.14)] text-[var(--ink)]'
    default:
      return 'bg-[color:var(--accent-warm-soft)] text-[var(--ink)]'
  }
}


export function ResearchPage({ siteData, researchPayload }: ResearchPageProps) {
  const { copy, locale } = useI18n()
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)

  const paperStatusLabel = (status: ResearchPaper['status']) => copy.enums.paperStatus[status]
  const categoryLabel = (category: string) =>
    copy.enums.paperCategory[category as keyof typeof copy.enums.paperCategory] ?? category

  const mode = (searchParams.get('mode') as LibraryMode | null) ?? 'papers'
  const rawPaperView = searchParams.get('paperView')
  const paperView: PaperViewMode = rawPaperView === 'pdf' || rawPaperView === 'details' ? rawPaperView : 'overview'

  const filteredDocs = useMemo(() => {
    const needle = deferredQuery.trim().toLowerCase()
    if (!needle) {
      return researchPayload.documents
    }
    return researchPayload.documents.filter((document) => {
      const haystack = `${document.title} ${document.summary} ${document.body}`.toLowerCase()
      return haystack.includes(needle)
    })
  }, [deferredQuery, researchPayload.documents])

  const filteredPapers = useMemo(() => {
    const needle = deferredQuery.trim().toLowerCase()
    if (!needle) {
      return researchPayload.papers
    }
    return researchPayload.papers.filter((paper) => {
      const haystack = `${paper.title} ${paper.authors} ${paper.venue} ${paper.summary} ${paper.category}`.toLowerCase()
      return haystack.includes(needle)
    })
  }, [deferredQuery, researchPayload.papers])

  const activeGuideId = searchParams.get('guide') ?? filteredDocs[0]?.id ?? researchPayload.documents[0]?.id
  const activePaperId = searchParams.get('paper') ?? filteredPapers[0]?.id ?? researchPayload.papers[0]?.id
  const activeGuide = filteredDocs.find((document) => document.id === activeGuideId) ?? filteredDocs[0] ?? researchPayload.documents[0]
  const activePaper = filteredPapers.find((paper) => paper.id === activePaperId) ?? filteredPapers[0] ?? researchPayload.papers[0]

  useEffect(() => {
    const nextParams = new URLSearchParams(searchParams)
    let changed = false

    if (!nextParams.get('mode')) {
      nextParams.set('mode', 'papers')
      changed = true
    }
    if (!nextParams.get('paperView') || nextParams.get('paperView') === 'summary') {
      nextParams.set('paperView', 'overview')
      changed = true
    }
    if (mode === 'guides' && activeGuide && nextParams.get('guide') !== activeGuide.id) {
      nextParams.set('guide', activeGuide.id)
      changed = true
    }
    if (mode === 'papers' && activePaper && nextParams.get('paper') !== activePaper.id) {
      nextParams.set('paper', activePaper.id)
      changed = true
    }

    if (!changed) {
      return
    }

    startTransition(() => {
      setSearchParams(nextParams, { replace: true })
    })
  }, [activeGuide, activePaper, mode, searchParams, setSearchParams])

  const switchMode = (nextMode: LibraryMode) => {
    const nextParams = new URLSearchParams(searchParams)
    nextParams.set('mode', nextMode)
    if (nextMode === 'guides' && activeGuide) {
      nextParams.set('guide', activeGuide.id)
    }
    if (nextMode === 'papers' && activePaper) {
      nextParams.set('paper', activePaper.id)
      nextParams.set('paperView', 'overview')
    }
    startTransition(() => {
      setSearchParams(nextParams)
    })
  }

  const selectGuide = (guideId: string) => {
    const nextParams = new URLSearchParams(searchParams)
    nextParams.set('mode', 'guides')
    nextParams.set('guide', guideId)
    startTransition(() => {
      setSearchParams(nextParams)
    })
  }

  const selectPaper = (paperId: string) => {
    const nextParams = new URLSearchParams(searchParams)
    nextParams.set('mode', 'papers')
    nextParams.set('paper', paperId)
    nextParams.set('paperView', 'overview')
    startTransition(() => {
      setSearchParams(nextParams)
    })
  }

  const setPaperView = (nextView: PaperViewMode) => {
    if (!activePaper) {
      return
    }
    const nextParams = new URLSearchParams(searchParams)
    nextParams.set('mode', 'papers')
    nextParams.set('paper', activePaper.id)
    nextParams.set('paperView', nextView)
    startTransition(() => {
      setSearchParams(nextParams, { replace: true })
    })
  }

  return (
    <div className="space-y-4 lg:h-[calc(100vh-9.5rem)]">
      <div className="space-y-4 lg:hidden">
        <SectionHeading
          eyebrow={copy.research.eyebrow}
          title={copy.research.title}
          description={copy.research.description}
        />

        <div className="hidden flex-wrap gap-2 lg:flex">
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{researchPayload.documents.length} {copy.research.internalGuides}</div>
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{researchPayload.papers.length} {copy.research.papersReviewed}</div>
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{siteData.researchLibrary.pdfCount} {copy.research.localPdfs}</div>
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{siteData.researchLibrary.openAccessCount} {copy.research.resolvedLinks}</div>
        </div>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4 lg:hidden">
          <article className="rounded-[1.8rem] border border-[var(--line)] bg-[var(--panel)] p-5 shadow-[var(--panel-shadow)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.internalGuides}</p>
            <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{researchPayload.documents.length}</p>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.research.internalGuidesDescription}</p>
          </article>
          <article className="rounded-[1.8rem] border border-[var(--line)] bg-[var(--panel)] p-5 shadow-[var(--panel-shadow)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.papersReviewed}</p>
            <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{researchPayload.papers.length}</p>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.research.papersDescription}</p>
          </article>
          <article className="rounded-[1.8rem] border border-[var(--line)] bg-[var(--panel)] p-5 shadow-[var(--panel-shadow)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.localPdfs}</p>
            <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{siteData.researchLibrary.pdfCount}</p>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.research.localPdfsDescription}</p>
          </article>
          <article className="rounded-[1.8rem] border border-[var(--line)] bg-[var(--panel)] p-5 shadow-[var(--panel-shadow)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.resolvedLinks}</p>
            <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{siteData.researchLibrary.openAccessCount}</p>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.research.resolvedLinksDescription}</p>
          </article>
        </section>
      </div>

      <section className="grid gap-4 lg:h-full lg:min-h-0 lg:grid-cols-[20rem_minmax(0,1fr)]">
        <div className="grid gap-4 lg:min-h-0 lg:grid-rows-[auto_minmax(0,1fr)]">
          <div className="surface-card rounded-[1.8rem] p-4">
            <label className="block text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]" htmlFor="research-search">{copy.research.searchLabel}</label>
            <input
              id="research-search"
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={copy.research.searchPlaceholder}
              className="mt-4 w-full rounded-2xl border border-[var(--line)] bg-[var(--panel-strong)] px-4 py-3 text-[var(--ink)] outline-none transition focus:border-[var(--primary)]"
            />
            <div className="mt-4 flex flex-wrap gap-2">
              {(['papers', 'guides'] as LibraryMode[]).map((libraryMode) => {
                const isActive = mode === libraryMode
                return (
                  <button
                    key={libraryMode}
                    type="button"
                    onClick={() => switchMode(libraryMode)}
                    className={[
                      'rounded-full border px-4 py-2 text-sm font-medium transition',
                      isActive
                        ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)]'
                        : 'border-[var(--line)] bg-[var(--panel-strong)] text-[var(--muted)] hover:border-[var(--primary)] hover:text-[var(--foreground)]',
                    ].join(' ')}
                  >
                    {libraryMode === 'papers' ? copy.research.paperLibrary : copy.research.guideLibrary}
                  </button>
                )
              })}
            </div>
            <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
              {mode === 'papers'
                ? copy.research.paperVisibleCount(filteredPapers.length, researchPayload.papers.length)
                : copy.research.guideVisibleCount(filteredDocs.length, researchPayload.documents.length)}
            </p>
          </div>

          {mode === 'guides' ? (
            <div className="surface-card min-h-0 rounded-[1.8rem] p-4 lg:flex lg:flex-col">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.guideShelf}</p>
              <div className="mt-4 min-h-0 space-y-3 lg:overflow-y-auto lg:pr-1 app-scrollbar">
                {filteredDocs.map((document) => {
                  const isActive = document.id === activeGuide?.id
                  return (
                    <button
                      key={document.id}
                      type="button"
                      onClick={() => selectGuide(document.id)}
                      className={[
                        'w-full rounded-[1.2rem] border px-4 py-4 text-left transition',
                        isActive
                          ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)] shadow-[var(--panel-shadow)]'
                          : 'border-[var(--line)] bg-[var(--panel-strong)] text-[var(--ink)] hover:border-[var(--primary)]',
                      ].join(' ')}
                    >
                      <p className="text-xs font-semibold uppercase tracking-[0.22em] opacity-70">{document.sourcePath}</p>
                      <p className="mt-2 text-base font-semibold leading-tight">{document.title}</p>
                      <p className="mt-2 text-sm leading-7 opacity-85">{document.summary}</p>
                    </button>
                  )
                })}
              </div>
            </div>
          ) : (
            <div className="surface-card min-h-0 rounded-[1.8rem] p-4 lg:flex lg:flex-col">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.paperShelf}</p>
              <div className="mt-4 min-h-0 space-y-3 lg:overflow-y-auto lg:pr-1 app-scrollbar">
                {filteredPapers.map((paper) => {
                  const isActive = paper.id === activePaper?.id
                  return (
                    <button
                      key={paper.id}
                      type="button"
                      onClick={() => selectPaper(paper.id)}
                      className={[
                        'w-full rounded-[1.2rem] border px-4 py-4 text-left transition',
                        isActive
                          ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)] shadow-[var(--panel-shadow)]'
                          : 'border-[var(--line)] bg-[var(--panel-strong)] text-[var(--ink)] hover:border-[var(--primary)]',
                      ].join(' ')}
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${isActive ? 'bg-[color:color-mix(in_oklab,var(--primary-foreground)_14%,transparent)] text-inherit' : paperStatusClasses(paper.status)}`}>
                          {paperStatusLabel(paper.status)}
                        </span>
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${isActive ? 'bg-[color:color-mix(in_oklab,var(--primary-foreground)_14%,transparent)] text-inherit' : 'bg-[color:var(--accent-warm-soft)] text-[var(--ink)]'}`}>
                          {categoryLabel(paper.category)}
                        </span>
                      </div>
                      <p className="mt-3 text-base font-semibold leading-tight">{paper.title}</p>
                      <p className="mt-2 text-sm leading-7 opacity-85">{paper.summary}</p>
                      <p className="mt-3 text-xs font-semibold uppercase tracking-[0.22em] opacity-70">
                        {paper.year ?? copy.common.yearUnknown} · {paper.venue || copy.common.venueUnresolved}
                      </p>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        <div className="surface-card min-h-0 overflow-hidden rounded-[1.8rem] p-0 lg:flex lg:flex-col">
          {mode === 'guides' ? (
            activeGuide ? (
              <div className="flex h-full min-h-0 flex-col">
                <div className="border-b border-[var(--line)] px-4 py-3">
                  <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.internalProjectGuide}</p>
                  <h3 className="mt-2 font-serif text-2xl text-[var(--ink)]">{activeGuide.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{activeGuide.summary}</p>
                  <p className="mt-2 break-words text-sm text-[var(--muted)]">{copy.common.source(activeGuide.sourcePath)}</p>
                </div>
                <div className="flex-1 min-h-0 overflow-y-auto p-4 pr-3 app-scrollbar">
                  <div className="markdown-body rounded-[1.5rem] border border-[var(--line)] bg-[var(--panel-strong)] p-6">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{activeGuide.body}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-6 text-base leading-8 text-[var(--muted)]">{copy.research.noGuides}</div>
            )
          ) : activePaper ? (
            <div className="flex h-full min-h-0 flex-col">
              <div className="border-b border-[var(--line)] px-4 py-3">
                <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_18rem] xl:items-start">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${paperStatusClasses(activePaper.status)}`}>
                        {paperStatusLabel(activePaper.status)}
                      </span>
                      <span className="rounded-full bg-[color:var(--accent-warm-soft)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--ink)]">
                        {categoryLabel(activePaper.category)}
                      </span>
                    </div>
                    <h3 className="mt-3 font-serif text-2xl leading-tight text-[var(--ink)]">{activePaper.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{activePaper.summary}</p>
                    <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                      <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--muted)]">
                        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.research.authors}</p>
                        <p className="mt-2 break-words">{activePaper.authors}</p>
                      </div>
                      <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--muted)]">
                        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.research.venue}</p>
                        <p className="mt-2 break-words">{activePaper.venue || copy.common.venueUnresolved}</p>
                      </div>
                      <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--muted)]">
                        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.research.year}</p>
                        <p className="mt-2">{activePaper.year ?? copy.common.unknown}</p>
                      </div>
                      <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--muted)]">
                        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.research.citations}</p>
                        <p className="mt-2">{activePaper.citationCount}</p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="grid gap-2 sm:grid-cols-3 xl:grid-cols-1">
                      <button
                        type="button"
                        onClick={() => setPaperView('overview')}
                        className={[
                          'rounded-2xl border px-4 py-3 text-sm font-medium transition',
                          paperView === 'overview'
                            ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)]'
                            : 'border-[var(--line)] bg-[var(--panel)] text-[var(--muted)] hover:border-[var(--primary)] hover:text-[var(--foreground)]',
                        ].join(' ')}
                      >
                        {copy.research.overview}
                      </button>
                      <button
                        type="button"
                        onClick={() => setPaperView('details')}
                        className={[
                          'rounded-2xl border px-4 py-3 text-sm font-medium transition',
                          paperView === 'details'
                            ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)]'
                            : 'border-[var(--line)] bg-[var(--panel)] text-[var(--muted)] hover:border-[var(--primary)] hover:text-[var(--foreground)]',
                        ].join(' ')}
                      >
                        {copy.research.details}
                      </button>
                      <button
                        type="button"
                        onClick={() => setPaperView('pdf')}
                        disabled={!activePaper.downloadedPdfPath}
                        className={[
                          'rounded-2xl border px-4 py-3 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50',
                          paperView === 'pdf'
                            ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)]'
                            : 'border-[var(--line)] bg-[var(--panel)] text-[var(--muted)] hover:border-[var(--primary)] hover:text-[var(--foreground)]',
                        ].join(' ')}
                      >
                        {copy.research.pdf}
                      </button>
                    </div>

                    <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-1">
                      {activePaper.officialUrl ? (
                        <a
                          href={activePaper.officialUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-center text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--primary)]"
                        >
                            {copy.research.openOfficialSource}
                        </a>
                      ) : null}
                      {activePaper.downloadedPdfPath ? (
                        <a
                          href={activePaper.downloadedPdfPath}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-center text-sm font-semibold text-[var(--ink)] transition hover:border-[var(--primary)]"
                        >
                            {copy.research.openLocalPdf}
                        </a>
                      ) : null}
                    </div>

                    <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--muted)]">
                      {activePaper.downloadedPdfPath && activePaper.pdfSizeBytes
                          ? copy.research.localPdfSize(formatBytes(activePaper.pdfSizeBytes, locale))
                        : activePaper.openAccessPdfUrl
                            ? copy.research.externalPdfFound
                            : copy.research.noLocalPdf}
                    </div>
                  </div>
                </div>
              </div>

              {paperView === 'pdf' && activePaper.downloadedPdfPath ? (
                <div className="flex-1 min-h-0 p-4">
                  <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                    <div className="flex items-center justify-between gap-4 border-b border-[var(--line)] px-4 py-3">
                      <div>
                        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent-warm)]">{copy.research.embeddedLocalPdf}</p>
                        <p className="mt-1 text-sm leading-6 text-[var(--muted)]">{copy.research.embeddedPdfNote}</p>
                      </div>
                      <a
                        href={activePaper.downloadedPdfPath}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm font-medium text-[var(--ink)] transition hover:border-[var(--primary)]"
                      >
                        {copy.research.standaloneView}
                      </a>
                    </div>
                    <object
                      data={`${activePaper.downloadedPdfPath}#toolbar=0&navpanes=0&view=FitH`}
                      type="application/pdf"
                      className="min-h-0 flex-1 w-full bg-[var(--panel-muted)]"
                    >
                      <div className="flex h-full min-h-[560px] items-center justify-center p-6 text-center text-sm leading-7 text-[var(--muted)]">
                        <div>
                          <p>{copy.research.browserDidNotRender}</p>
                          <a
                            href={activePaper.downloadedPdfPath}
                            target="_blank"
                            rel="noreferrer"
                            className="mt-4 inline-flex rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 font-medium text-[var(--ink)] transition hover:border-[var(--primary)]"
                          >
                            {copy.research.openPdfNewTab}
                          </a>
                        </div>
                      </div>
                    </object>
                  </div>
                </div>
              ) : paperView === 'details' ? (
                <div className="grid flex-1 min-h-[520px] gap-4 p-4 xl:grid-cols-[minmax(0,1fr)_20rem] lg:min-h-0">
                  <div className="min-h-0 space-y-4 overflow-y-auto pr-1 app-scrollbar">
                    <div className="rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] p-5">
                      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.referenceDetails}</p>
                      <div className="mt-4 grid gap-3 sm:grid-cols-2">
                        <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--muted)]">
                          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.research.doi}</p>
                          <p className="mt-2 break-words">{activePaper.doi ?? copy.common.notResolved}</p>
                        </div>
                        <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--muted)]">
                          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.research.officialLink}</p>
                          <p className="mt-2 break-words">{activePaper.officialUrl ?? copy.common.notResolved}</p>
                        </div>
                        <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 text-sm text-[var(--muted)] sm:col-span-2">
                          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.research.openAccessPdfUrl}</p>
                          <p className="mt-2 break-words">{activePaper.openAccessPdfUrl ?? copy.common.notResolved}</p>
                        </div>
                      </div>
                    </div>

                    <div className="rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] p-5">
                      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.projectNote}</p>
                      <p className="mt-4 text-sm leading-7 text-[var(--muted)]">{activePaper.summary}</p>
                    </div>
                  </div>

                  <div className="min-h-0 space-y-4 overflow-y-auto pr-1 app-scrollbar">
                    <div className="rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] p-5 text-sm leading-7 text-[var(--muted)]">
                      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent-warm)]">{copy.research.availability}</p>
                      <p className="mt-4">
                        {activePaper.downloadedPdfPath
                          ? copy.research.availabilityLocal
                          : activePaper.openAccessPdfUrl
                            ? copy.research.availabilityExternal
                            : copy.research.availabilityNone}
                      </p>
                    </div>

                    <div className="rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] p-5 text-sm leading-7 text-[var(--muted)]">
                      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.sourceNote}</p>
                      <p className="mt-4 break-words">{activePaper.sourcePath}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="grid flex-1 min-h-[520px] gap-4 p-4 xl:grid-cols-[minmax(0,1.35fr)_20rem] lg:min-h-0">
                  <div className="min-h-0 space-y-4 overflow-y-auto pr-1 app-scrollbar">
                    <div className="rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] p-5">
                      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.whyPaperMattered}</p>
                      <p className="mt-4 text-sm leading-7 text-[var(--muted)] md:text-base">{activePaper.summary}</p>
                    </div>
                    <div className="rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] p-5 text-sm leading-7 text-[var(--muted)]">
                      {copy.research.sourceNote}: {activePaper.sourcePath}
                    </div>
                  </div>

                  <div className="min-h-0 space-y-4 overflow-y-auto pr-1 app-scrollbar">
                    <div className="rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] p-5">
                      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.research.referenceDetails}</p>
                      <div className="mt-4 space-y-3 text-sm leading-7 text-[var(--muted)]">
                        <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 break-words">{copy.research.doi}: {activePaper.doi ?? copy.common.notResolved}</div>
                        <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 break-words">{copy.research.officialLink}: {activePaper.officialUrl ?? copy.common.notResolved}</div>
                        <div className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] px-4 py-3 break-words">{copy.research.openAccessPdfUrl}: {activePaper.openAccessPdfUrl ?? copy.common.notResolved}</div>
                      </div>
                    </div>

                    <div className="rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] p-5">
                      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent-warm)]">{copy.research.pdfAvailabilityRule}</p>
                      <p className="mt-4 text-sm leading-7 text-[var(--muted)]">{copy.research.pdfAvailabilityRuleBody}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-6 text-base leading-8 text-[var(--muted)]">{copy.research.noPapers}</div>
          )}
        </div>
      </section>
    </div>
  )
}
