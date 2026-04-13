import Editor from '@monaco-editor/react'
import { useState } from 'react'
import type { EvidenceFile } from '../lib/types'
import { useEditorTheme } from '../hooks/useEditorTheme'
import { useI18n } from '../useI18n'

interface EvidenceAccordionProps {
  files: EvidenceFile[]
  emptyMessage?: string
  editorHeight?: number
}

export function EvidenceAccordion({ files, emptyMessage, editorHeight = 260 }: EvidenceAccordionProps) {
  const { copy } = useI18n()
  const [openFileId, setOpenFileId] = useState<string | null>(null)
  const editorTheme = useEditorTheme()
  const resolvedEmptyMessage = emptyMessage ?? copy.common.noEvidence

  if (!files.length) {
    return <p className="text-sm leading-7 text-[var(--muted)]">{resolvedEmptyMessage}</p>
  }

  return (
    <div className="space-y-3">
      {files.map((file) => {
        const isOpen = openFileId === file.id

        return (
          <div key={file.id} className="overflow-hidden rounded-[1.2rem] border border-[var(--line)] bg-[var(--panel)]">
            <button
              type="button"
              onClick={() => setOpenFileId((current) => current === file.id ? null : file.id)}
              className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left transition hover:bg-[var(--panel-strong)]"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-[var(--ink)]">{file.title}</p>
                <p className="mt-1 truncate text-xs leading-6 text-[var(--muted)]">{file.sourcePath}</p>
              </div>
              <span className="shrink-0 rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
                {isOpen ? copy.common.hide : copy.common.open}
              </span>
            </button>

            {isOpen ? (
              <div className="border-t border-[var(--line)] bg-[var(--panel-strong)]">
                <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
                  <p className="min-w-0 break-words text-xs font-semibold uppercase tracking-[0.2em] text-[var(--accent)]">
                    {file.sourcePath}
                  </p>
                  <div className="rounded-full border border-[var(--line)] bg-[var(--panel)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
                    {file.language}
                  </div>
                </div>
                <Editor
                  height={`${editorHeight}px`}
                  language={file.language}
                  value={file.content}
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
            ) : null}
          </div>
        )
      })}
    </div>
  )
}