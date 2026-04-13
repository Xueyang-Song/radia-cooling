import Editor from '@monaco-editor/react'
import { useMemo, useState } from 'react'
import { SectionHeading } from '../components/SectionHeading'
import { useEditorTheme } from '../hooks/useEditorTheme'
import type { NotebookMetric, NotebookPanel, SiteData } from '../lib/types'
import { useI18n } from '../useI18n'

interface NotebookPageProps {
  siteData: SiteData
}

type NotebookWorkspaceTab = 'overview' | 'commands' | 'files'

function metricToneClasses(tone: NotebookMetric['tone']): string {
  switch (tone) {
    case 'warm':
      return 'border-[color:var(--accent-warm-soft)] bg-[color:var(--accent-warm-soft)] text-[var(--ink)]'
    case 'neutral':
      return 'border-[var(--line)] bg-[var(--panel-strong)] text-[var(--ink)]'
    default:
      return 'border-[color:var(--accent-soft)] bg-[color:var(--accent-soft)] text-[var(--ink)]'
  }
}

function panelKindClasses(kind: NotebookPanel['kind']): string {
  return kind === 'artifact'
    ? 'bg-[color:var(--accent-warm-soft)] text-[var(--ink)]'
    : 'bg-[color:var(--accent-soft)] text-[var(--ink)]'
}

export function NotebookPage({ siteData }: NotebookPageProps) {
  const { copy } = useI18n()
  const stages = siteData.labNotebook.stages
  const [activeStageId, setActiveStageId] = useState(stages[0]?.id ?? '')
  const activeStage = stages.find((stage) => stage.id === activeStageId) ?? stages[0]
  const [activePanelId, setActivePanelId] = useState(activeStage?.panels[0]?.id ?? '')
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<NotebookWorkspaceTab>('files')
  const editorTheme = useEditorTheme()

  const activePanel = useMemo(
    () => activeStage?.panels.find((panel) => panel.id === activePanelId) ?? activeStage?.panels[0],
    [activePanelId, activeStage],
  )

  if (!activeStage) {
    return null
  }

  const totalCommands = stages.reduce((total, stage) => total + stage.commands.length, 0)
  const totalPanels = stages.reduce((total, stage) => total + stage.panels.length, 0)

  return (
    <div className="space-y-4 lg:h-[calc(100vh-9.5rem)]">
      <div className="space-y-4 lg:hidden">
        <SectionHeading
          eyebrow={copy.notebook.eyebrow}
          title={copy.notebook.title}
          description={siteData.labNotebook.intro}
        />

        <div className="hidden flex-wrap gap-2 lg:flex">
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{copy.notebook.stageCount(stages.length)}</div>
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{copy.notebook.commandCount(totalCommands)}</div>
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{copy.notebook.panelCount(totalPanels)}</div>
          <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-4 py-2 text-sm text-[var(--muted)]">{copy.notebook.currentStageBadge(activeStage.eyebrow)}</div>
        </div>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4 lg:hidden">
          <article className="rounded-[1.8rem] border border-[var(--line)] bg-[var(--panel)] p-5 shadow-[var(--panel-shadow)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.notebook.stageCount(stages.length)}</p>
            <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{stages.length}</p>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.notebook.stageCardDescription}</p>
          </article>
          <article className="rounded-[1.8rem] border border-[var(--line)] bg-[var(--panel)] p-5 shadow-[var(--panel-shadow)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.notebook.commandCount(totalCommands)}</p>
            <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{totalCommands}</p>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.notebook.commandCardDescription}</p>
          </article>
          <article className="rounded-[1.8rem] border border-[var(--line)] bg-[var(--panel)] p-5 shadow-[var(--panel-shadow)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.notebook.panelCount(totalPanels)}</p>
            <p className="mt-3 text-3xl font-semibold text-[var(--ink)]">{totalPanels}</p>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{copy.notebook.panelCardDescription}</p>
          </article>
          <article className="rounded-[1.8rem] border border-[var(--line)] bg-[var(--panel)] p-5 shadow-[var(--panel-shadow)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.common.currentSelectedStage}</p>
            <p className="mt-3 text-2xl font-semibold text-[var(--ink)]">{activeStage.eyebrow}</p>
            <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{activeStage.title}</p>
          </article>
        </section>
      </div>

      <section className="grid gap-4 lg:h-full lg:min-h-0 lg:grid-cols-[18rem_minmax(0,1fr)]">
        <aside className="surface-card min-h-0 rounded-[1.8rem] p-4 lg:flex lg:flex-col">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
            <div className="surface-inset rounded-[1.2rem] px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.common.selected}</p>
              <p className="mt-2 text-lg font-semibold text-[var(--ink)]">{activeStage.eyebrow}</p>
            </div>
            <div className="surface-inset rounded-[1.2rem] px-4 py-3">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.common.openPanels}</p>
              <p className="mt-2 text-lg font-semibold text-[var(--ink)]">{activeStage.panels.length}</p>
            </div>
          </div>

          <div className="mt-4 min-h-0 space-y-2 lg:overflow-y-auto lg:pr-1 app-scrollbar">
            {stages.map((stage, index) => {
              const isActive = stage.id === activeStage.id
              return (
                <button
                  key={stage.id}
                  type="button"
                  onClick={() => {
                    setActiveStageId(stage.id)
                    setActivePanelId('')
                    setActiveWorkspaceTab('files')
                  }}
                  className={[
                    'w-full min-w-0 rounded-[1.25rem] border p-4 text-left transition',
                    isActive
                      ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)] shadow-[var(--panel-shadow)]'
                      : 'border-[var(--line)] bg-[var(--panel)] text-[var(--ink)] hover:border-[var(--primary)]',
                  ].join(' ')}
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.24em] opacity-75">{index + 1}. {stage.eyebrow}</p>
                  <h3 className="mt-3 text-base font-semibold leading-tight">{stage.title}</h3>
                  <p className="mt-3 text-sm leading-6 opacity-80">{stage.summary}</p>
                </button>
              )
            })}
          </div>
        </aside>

        <div className="surface-card min-h-0 overflow-hidden rounded-[1.8rem] p-0 lg:flex lg:flex-col">
          <div className="border-b border-[var(--line)] px-4 py-3">
            <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_18rem] xl:items-start">
              <div className="min-w-0">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.common.currentStage}</p>
                <h3 className="mt-2 font-serif text-2xl leading-tight text-[var(--ink)]">{activeStage.title}</h3>
                <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{activeStage.summary}</p>
              </div>
              <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                <div className="surface-inset rounded-[1.2rem] px-4 py-2.5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.common.commands}</p>
                  <p className="mt-1 text-lg font-semibold text-[var(--ink)]">{activeStage.commands.length}</p>
                </div>
                <div className="surface-inset rounded-[1.2rem] px-4 py-2.5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.common.files}</p>
                  <p className="mt-1 text-lg font-semibold text-[var(--ink)]">{activeStage.panels.length}</p>
                </div>
                <div className="surface-inset rounded-[1.2rem] px-4 py-2.5">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">{copy.common.metrics}</p>
                  <p className="mt-1 text-lg font-semibold text-[var(--ink)]">{activeStage.metrics.length}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 border-b border-[var(--line)] px-4 py-3">
            {([
              ['files', copy.notebook.workspaceTabs.files],
              ['commands', copy.notebook.workspaceTabs.commands],
              ['overview', copy.notebook.workspaceTabs.overview],
            ] as Array<[NotebookWorkspaceTab, string]>).map(([tab, label]) => {
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
            {activeWorkspaceTab === 'files' ? (
              <div className="flex h-full min-h-0 flex-col">
                <div className="flex flex-wrap gap-2">
                  {activeStage.panels.map((panel) => {
                    const isActive = panel.id === activePanel?.id
                    return (
                      <button
                        key={panel.id}
                        type="button"
                        onClick={() => setActivePanelId(panel.id)}
                        className={[
                          'rounded-full border px-4 py-2 text-sm font-medium transition',
                          isActive
                            ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)]'
                            : 'border-[var(--line)] bg-[var(--panel-strong)] text-[var(--muted)] hover:border-[var(--primary)] hover:text-[var(--foreground)]',
                        ].join(' ')}
                      >
                        {panel.title}
                      </button>
                    )
                  })}
                </div>

                {activePanel ? (
                  <div className="mt-3 flex min-h-[520px] flex-1 flex-col overflow-hidden rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-strong)] lg:min-h-0">
                    <div className="flex flex-col gap-2 border-b border-[var(--line)] px-4 py-3 md:flex-row md:items-center md:justify-between">
                      <div className="min-w-0">
                        <div className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] ${panelKindClasses(activePanel.kind)}`}>
                          {copy.enums.panelKind[activePanel.kind]}
                        </div>
                        <h4 className="mt-2 text-base font-semibold text-[var(--ink)]">{activePanel.title}</h4>
                        <p className="mt-1 break-words text-sm leading-6 text-[var(--muted)]">{activePanel.sourcePath}</p>
                      </div>
                      <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-3 py-2 text-sm text-[var(--muted)]">
                        {activePanel.language}
                      </div>
                    </div>
                    <div className="min-h-0 flex-1">
                      <Editor
                        height="100%"
                        language={activePanel.language}
                        value={activePanel.content}
                        theme={editorTheme}
                        options={{
                          readOnly: true,
                          minimap: { enabled: false },
                          automaticLayout: true,
                          scrollBeyondLastLine: false,
                          wordWrap: 'on',
                          lineNumbersMinChars: 3,
                          fontSize: 13,
                          tabSize: 2,
                          folding: true,
                          renderLineHighlight: 'line',
                        }}
                      />
                    </div>
                  </div>
                ) : (
                  <div className="surface-inset mt-4 rounded-[1.4rem] p-5 text-sm leading-7 text-[var(--muted)]">
                    {copy.notebook.noPanels}
                  </div>
                )}
              </div>
            ) : activeWorkspaceTab === 'commands' ? (
              <div className="h-full min-h-[520px] space-y-3 overflow-y-auto pr-1 app-scrollbar lg:min-h-0">
                {activeStage.commands.map((command) => (
                  <article key={command.label} className="surface-terminal overflow-hidden rounded-[1.3rem]">
                    <div className="flex items-center gap-2 border-b border-white/10 bg-[linear-gradient(90deg,rgba(56,189,248,0.16),rgba(94,234,212,0.06))] px-4 py-3 text-sm font-semibold text-[var(--terminal-foreground)]">
                      <span className="h-2.5 w-2.5 rounded-full bg-[#22c55e]" />
                      <span className="h-2.5 w-2.5 rounded-full bg-[#f59e0b]" />
                      <span className="h-2.5 w-2.5 rounded-full bg-[#ef4444]" />
                      <span className="ml-3">{command.label}</span>
                    </div>
                    <div className="space-y-3 px-4 py-4">
                      <pre className="overflow-x-auto whitespace-pre-wrap break-words font-mono text-sm leading-7 text-[var(--terminal-foreground)]">{command.command}</pre>
                      <p className="text-sm leading-7 text-[color:color-mix(in_oklab,var(--terminal-foreground)_72%,transparent)]">{command.note}</p>
                      <div className="rounded-[1rem] border border-white/10 bg-black/20 px-4 py-3 text-xs leading-6 text-[color:color-mix(in_oklab,var(--terminal-foreground)_60%,transparent)]">
                        {command.sourcePaths.map((sourcePath) => (
                          <div key={sourcePath} className="break-words">{sourcePath}</div>
                        ))}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="grid h-full min-h-[520px] gap-4 xl:grid-cols-[minmax(0,1fr)_20rem] lg:min-h-0">
                <div className="min-h-0 space-y-4 overflow-y-auto pr-1 app-scrollbar">
                  <div className="surface-inset rounded-[1.4rem] p-5 text-sm leading-7 text-[var(--muted)]">
                    <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.notebook.whatHappenedHere}</p>
                    <p className="mt-4">{activeStage.meaning}</p>
                  </div>

                  <div className="surface-card rounded-[1.6rem] p-5">
                    <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">{copy.notebook.whyItMatters}</p>
                    <div className="mt-4 space-y-3">
                      {activeStage.takeaways.map((takeaway, index) => (
                        <div key={takeaway} className="surface-inset flex gap-3 rounded-[1.2rem] px-4 py-4 text-sm leading-7 text-[var(--muted)]">
                          <span className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--accent)] text-xs font-semibold text-[var(--primary-foreground)]">{index + 1}</span>
                          <span>{takeaway}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="min-h-0 space-y-3 overflow-y-auto pr-1 app-scrollbar">
                  {activeStage.metrics.map((metric) => (
                    <div key={metric.label} className={`rounded-[1.4rem] border p-4 shadow-[var(--panel-shadow)] ${metricToneClasses(metric.tone)}`}>
                      <p className="text-xs font-semibold uppercase tracking-[0.22em] opacity-80">{metric.label}</p>
                      <p className="mt-3 font-serif text-3xl text-[var(--ink)]">{metric.value}</p>
                      <p className="mt-3 text-sm leading-7 opacity-85">{metric.detail}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
