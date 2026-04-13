import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { LanguageToggle } from './LanguageToggle'
import { ThemeToggle } from './ThemeToggle'
import type { ProjectInfo, ResearchLibraryMeta } from '../lib/types'
import { useI18n } from '../useI18n'

interface AppShellProps {
  project: ProjectInfo
  researchLibrary: ResearchLibraryMeta
}

export function AppShell({ project, researchLibrary }: AppShellProps) {
  const { copy } = useI18n()
  const location = useLocation()
  const navItems = [
    { to: '/', ...copy.shell.nav.story },
    { to: '/pipeline', ...copy.shell.nav.pipeline },
    { to: '/compare', ...copy.shell.nav.compare },
    { to: '/explore', ...copy.shell.nav.explore },
    { to: '/notebook', ...copy.shell.nav.notebook },
    { to: '/research', ...copy.shell.nav.research },
    { to: '/audit', ...copy.shell.nav.audit },
  ]
  const activeItem = navItems.find((item) => item.to === '/' ? location.pathname === '/' : location.pathname.startsWith(item.to)) ?? navItems[0]

  return (
    <div className="relative min-h-screen overflow-hidden bg-[var(--app-frame)]">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-80 bg-[radial-gradient(circle_at_top,_color-mix(in_oklab,var(--primary)_18%,transparent),_transparent_56%)]" />
      <div className="pointer-events-none absolute right-[-8rem] top-28 h-72 w-72 rounded-full bg-[color:color-mix(in_oklab,var(--accent-warm)_18%,transparent)] blur-3xl" />

      <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col lg:h-screen lg:flex-row lg:gap-3 lg:p-3">
        <aside className="hidden lg:grid lg:w-[18.5rem] lg:shrink-0 lg:grid-rows-[auto_minmax(0,1fr)_auto] lg:overflow-hidden lg:rounded-[1.8rem] lg:border lg:border-[var(--sidebar-border)] lg:bg-[var(--sidebar)] lg:p-3 lg:text-[var(--sidebar-foreground)] lg:shadow-[var(--panel-shadow)]">
          <div className="border-b border-[var(--sidebar-border)] px-3 pb-4 pt-2">
            <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[var(--sidebar-primary)]">{copy.shell.appName}</p>
            <h1 className="mt-3 font-serif text-2xl leading-tight">{project.title}</h1>
            <p className="mt-3 text-sm leading-7 opacity-75">{project.subtitle}</p>
          </div>

          <nav className="mt-3 min-h-0 space-y-1 overflow-y-auto px-1 app-scrollbar">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  [
                    'block rounded-[1.25rem] border px-3 py-3 transition',
                    isActive
                      ? 'border-transparent bg-[var(--sidebar-accent)] text-[var(--sidebar-accent-foreground)] shadow-[0_0_0_1px_var(--sidebar-border)]'
                      : 'border-transparent text-[var(--sidebar-foreground)] opacity-80 hover:border-[var(--sidebar-border)] hover:bg-[var(--sidebar-accent)] hover:opacity-100',
                  ].join(' ')
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center justify-between gap-3">
                      <span className="font-semibold">{item.label}</span>
                      <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] ${isActive ? 'bg-[color:color-mix(in_oklab,var(--sidebar-primary)_20%,transparent)] text-[var(--sidebar-accent-foreground)]' : 'bg-[color:color-mix(in_oklab,var(--sidebar-primary)_12%,transparent)] text-[var(--sidebar-primary)]'}`}>
                        {item.eyebrow}
                      </span>
                    </div>
                    <p className={`mt-2 text-xs leading-6 ${isActive ? 'opacity-80' : 'opacity-65'}`}>{item.detail}</p>
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          <div className="mt-3 min-w-0 border-t border-[var(--sidebar-border)] px-2 pt-4">
            <div className="grid min-w-0 gap-3">
              <div className="w-full min-w-0 overflow-hidden rounded-[1.4rem] border border-[var(--sidebar-border)] bg-[color:color-mix(in_oklab,var(--sidebar-accent)_62%,var(--sidebar))] p-4">
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[var(--sidebar-primary)]">{copy.shell.evidenceLoaded}</p>
              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                <div>
                  <p className="text-xl font-semibold">{researchLibrary.docCount}</p>
                  <p className="text-[10px] uppercase tracking-[0.18em] opacity-65">{copy.shell.guides}</p>
                </div>
                <div>
                  <p className="text-xl font-semibold">{researchLibrary.paperCount}</p>
                  <p className="text-[10px] uppercase tracking-[0.18em] opacity-65">{copy.shell.papers}</p>
                </div>
                <div>
                  <p className="text-xl font-semibold">{researchLibrary.pdfCount}</p>
                  <p className="text-[10px] uppercase tracking-[0.18em] opacity-65">{copy.shell.oaPdfs}</p>
                </div>
              </div>
              </div>
              <div className="w-full min-w-0 overflow-hidden rounded-[1.4rem] border border-[var(--sidebar-border)] bg-[color:color-mix(in_oklab,var(--sidebar)_80%,white)] p-4">
                <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[var(--sidebar-primary)]">{copy.shell.shellIntent}</p>
                <p className="mt-3 max-w-full break-words text-sm leading-6 opacity-75">{copy.shell.shellIntentBody}</p>
              </div>
            </div>
          </div>
        </aside>

        <div className="flex min-h-screen flex-1 flex-col lg:min-h-0 lg:overflow-hidden lg:rounded-[1.8rem] lg:border lg:border-[var(--line)] lg:bg-[var(--app-shell)] lg:shadow-[var(--panel-shadow)]">
          <header className="sticky top-0 z-30 border-b border-[var(--line)] bg-[var(--app-shell)] backdrop-blur-xl">
            <div className="mx-auto flex max-w-[1300px] flex-col gap-5 px-4 py-4 md:px-6 lg:px-8">
              <div className="flex items-start justify-between gap-4 lg:hidden">
                <div className="min-w-0">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[var(--accent)]">{copy.shell.appName}</p>
                  <h1 className="mt-2 truncate font-serif text-2xl text-[var(--ink)]">{project.title}</h1>
                </div>
                <div className="flex shrink-0 flex-wrap justify-end gap-2">
                  <LanguageToggle />
                  <ThemeToggle />
                </div>
              </div>

              <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                <div className="max-w-3xl">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-[var(--accent)]">{activeItem.eyebrow}</p>
                  <h2 className="mt-2 font-serif text-3xl leading-tight text-[var(--ink)] md:text-4xl">{activeItem.label}</h2>
                  <p className="mt-3 text-sm leading-7 text-[var(--muted)] md:text-base">{activeItem.detail}</p>
                </div>
                <div className="hidden items-center gap-2 md:flex md:flex-wrap md:justify-end">
                  <div className="rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-4 py-2 text-sm text-[var(--muted)]">
                    {copy.shell.openAccessResolved(researchLibrary.openAccessCount)}
                  </div>
                  <div className="rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-4 py-2 text-sm text-[var(--muted)]">
                    {copy.shell.realEvidence}
                  </div>
                  <LanguageToggle />
                  <ThemeToggle />
                </div>
              </div>

              <nav className="flex gap-2 overflow-x-auto pb-1 lg:hidden">
                {navItems.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/'}
                    className={({ isActive }) =>
                      [
                        'shrink-0 rounded-full border px-4 py-2 text-sm font-medium transition',
                        isActive
                          ? 'border-transparent bg-[var(--primary)] text-[var(--primary-foreground)] shadow-[var(--panel-shadow)]'
                          : 'border-[var(--line)] bg-[var(--panel-strong)] text-[var(--ink)] hover:border-[var(--primary)]',
                      ].join(' ')
                    }
                  >
                    {item.label}
                  </NavLink>
                ))}
              </nav>
            </div>
          </header>

          <div className="flex-1 lg:overflow-y-auto app-scrollbar">
            <main className="mx-auto w-full max-w-[1300px] px-4 py-6 md:px-6 lg:px-8 lg:py-8">
              <Outlet />
            </main>
          </div>
        </div>
      </div>
    </div>
  )
}