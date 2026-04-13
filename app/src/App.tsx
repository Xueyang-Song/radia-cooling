import { Suspense, lazy, useEffect, useState } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import type { Locale } from './lib/locale'
import type { ResearchPayload, SiteData } from './lib/types'
import { useI18n } from './useI18n'

const HomePage = lazy(async () => ({ default: (await import('./pages/HomePage')).HomePage }))
const PipelinePage = lazy(async () => ({ default: (await import('./pages/PipelinePage')).PipelinePage }))
const ComparePage = lazy(async () => ({ default: (await import('./pages/ComparePage')).ComparePage }))
const ExplorePage = lazy(async () => ({ default: (await import('./pages/ExplorePage')).ExplorePage }))
const NotebookPage = lazy(async () => ({ default: (await import('./pages/NotebookPage')).NotebookPage }))
const ResearchPage = lazy(async () => ({ default: (await import('./pages/ResearchPage')).ResearchPage }))
const AuditPage = lazy(async () => ({ default: (await import('./pages/AuditPage')).AuditPage }))

function contentUrl(path: string): string {
  const normalizedBase = import.meta.env.BASE_URL.endsWith('/')
    ? import.meta.env.BASE_URL
    : `${import.meta.env.BASE_URL}/`
  return new URL(path.replace(/^\//, ''), window.location.origin + normalizedBase).toString()
}

async function loadLocalizedJson<T>(baseName: string, locale: Locale): Promise<T> {
  const candidates = locale === 'en'
    ? [`/content/${baseName}.en.json`, `/content/${baseName}.json`]
    : [`/content/${baseName}.${locale}.json`, `/content/${baseName}.json`, `/content/${baseName}.en.json`]

  for (const path of candidates) {
    const response = await fetch(contentUrl(path), {
      headers: { Accept: 'application/json' },
    })

    if (!response.ok) {
      continue
    }

    const contentType = response.headers.get('content-type')?.toLowerCase() ?? ''
    if (!contentType.includes('json')) {
      continue
    }

    return response.json() as Promise<T>
  }

  throw new Error('content-load-failed')
}

function App() {
  const { locale, copy } = useI18n()
  const [siteData, setSiteData] = useState<SiteData | null>(null)
  const [researchPayload, setResearchPayload] = useState<ResearchPayload | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function load() {
      try {
        setError(null)
        setSiteData(null)
        setResearchPayload(null)

        const [nextSiteData, nextDocs] = await Promise.all([
          loadLocalizedJson<SiteData>('site-data', locale),
          loadLocalizedJson<ResearchPayload>('research-docs', locale),
        ])

        if (!active) {
          return
        }

        setSiteData(nextSiteData)
        setResearchPayload(nextDocs)
      } catch (caughtError) {
        if (!active) {
          return
        }
        const message = caughtError instanceof Error
          ? caughtError.message === 'content-load-failed'
            ? copy.app.contentLoadError
            : caughtError.message
          : copy.app.unknownStartupError
        setError(message)
      }
    }

    void load()

    return () => {
      active = false
    }
  }, [copy.app.contentLoadError, copy.app.unknownStartupError, locale])

  if (error) {
    return (
      <div className="mx-auto flex min-h-screen max-w-4xl items-center px-6 py-24">
        <div className="surface-card rounded-[2rem] p-8">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
            {copy.app.startupIssue}
          </p>
          <h1 className="mt-4 font-serif text-4xl text-[var(--ink)]">{copy.app.startupTitle}</h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--muted)]">{error}</p>
        </div>
      </div>
    )
  }

  if (!siteData || !researchPayload) {
    return (
      <div className="mx-auto flex min-h-screen max-w-4xl items-center justify-center px-6 py-24">
        <div className="surface-card rounded-[2rem] px-8 py-10 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
            {copy.app.loadingStory}
          </p>
          <h1 className="mt-4 font-serif text-4xl text-[var(--ink)]">{copy.app.loadingTitle}</h1>
          <p className="mt-4 max-w-xl text-base leading-7 text-[var(--muted)]">
            {copy.app.loadingDescription}
          </p>
        </div>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell project={siteData.project} researchLibrary={siteData.researchLibrary} />}>
          <Route index element={<LazyRoute label={copy.app.routeLabels.story}><HomePage siteData={siteData} /></LazyRoute>} />
          <Route path="pipeline" element={<LazyRoute label={copy.app.routeLabels.pipeline}><PipelinePage siteData={siteData} /></LazyRoute>} />
          <Route path="compare" element={<LazyRoute label={copy.app.routeLabels.comparison}><ComparePage siteData={siteData} /></LazyRoute>} />
          <Route path="explore" element={<LazyRoute label={copy.app.routeLabels.explorer}><ExplorePage siteData={siteData} /></LazyRoute>} />
          <Route path="notebook" element={<LazyRoute label={copy.app.routeLabels.notebook}><NotebookPage siteData={siteData} /></LazyRoute>} />
          <Route
            path="research"
            element={
              <LazyRoute label={copy.app.routeLabels.research}>
                <ResearchPage siteData={siteData} researchPayload={researchPayload} />
              </LazyRoute>
            }
          />
          <Route path="audit" element={<LazyRoute label={copy.app.routeLabels.audit}><AuditPage siteData={siteData} /></LazyRoute>} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

function LazyRoute({ children, label }: { children: React.ReactNode; label: string }) {
  return (
    <Suspense fallback={<RouteLoading label={label} />}>
      {children}
    </Suspense>
  )
}

function RouteLoading({ label }: { label: string }) {
  const { copy } = useI18n()

  return (
    <div className="surface-card rounded-[2rem] p-8">
      <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.app.loadingRoute}</p>
      <h2 className="mt-4 font-serif text-4xl text-[var(--ink)]">{copy.app.preparingRoute(label)}</h2>
      <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--muted)]">
        {copy.app.routeDescription}
      </p>
    </div>
  )
}

export default App
