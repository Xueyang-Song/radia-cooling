import type { ProjectInfo } from '../lib/types'
import { useI18n } from '../useI18n'

interface WindowTitleBarProps {
  project: ProjectInfo
  activeItem: {
    label: string
    eyebrow: string
  }
  visible: boolean
}

export function WindowTitleBar({ project, activeItem, visible }: WindowTitleBarProps) {
  const { copy } = useI18n()

  if (!visible) {
    return null
  }

  return (
    <div className="window-drag relative z-50 h-[var(--titlebar-height)] shrink-0 border-b border-[var(--line)] bg-[var(--app-shell)] select-none">
      <div className="grid h-full min-w-0 lg:grid-cols-[18.75rem_minmax(0,1fr)]">
        <div className="hidden h-full border-r border-[var(--sidebar-border)] bg-[var(--sidebar)] lg:block" />
        <div className="flex min-w-0 items-center px-4 md:px-6 lg:px-8" style={{ paddingRight: 'calc(var(--window-controls-width) + 0.75rem)' }}>
          <div className="min-w-0">
            <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-[var(--accent)]">
              {copy.shell.appName}
            </p>
            <div className="mt-1 flex min-w-0 items-center gap-2 text-sm text-[var(--muted)]">
              <span className="truncate font-semibold text-[var(--ink)]">{project.title}</span>
              <span className="shrink-0 opacity-45">/</span>
              <span className="truncate">{activeItem.label}</span>
              <span className="hidden rounded-full bg-[var(--accent-soft)] px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.18em] text-[var(--accent)] xl:inline-flex">
                {activeItem.eyebrow}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
