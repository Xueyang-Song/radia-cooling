import { useEffect, useState } from 'react'
import { useI18n } from '../useI18n'

type ThemeMode = 'light' | 'dark'

function getPreferredTheme(): ThemeMode {
  if (typeof window === 'undefined') {
    return 'light'
  }

  const stored = window.localStorage.getItem('theme')
  if (stored === 'light' || stored === 'dark') {
    return stored
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function ThemeToggle() {
  const { copy } = useI18n()
  const [theme, setTheme] = useState<ThemeMode>(() => getPreferredTheme())

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    window.localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    const nextTheme: ThemeMode = theme === 'dark' ? 'light' : 'dark'
    setTheme(nextTheme)
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="inline-flex max-w-full shrink-0 items-center gap-2 rounded-full border border-[var(--line)] bg-[var(--panel-strong)] px-4 py-2.5 text-left text-sm font-semibold text-[var(--foreground)] shadow-[var(--panel-shadow)] transition hover:border-[var(--primary)] hover:text-[var(--foreground)] disabled:cursor-wait disabled:opacity-70"
      aria-label={copy.controls.toggleTheme}
      title={theme === 'dark' ? copy.controls.switchToLight : copy.controls.switchToDark}
    >
      <span className="text-base leading-none">{theme === 'dark' ? '◐' : '◑'}</span>
      <span className="truncate">{theme === 'dark' ? copy.controls.darkMode : copy.controls.lightMode}</span>
    </button>
  )
}