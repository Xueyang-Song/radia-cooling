import { useI18n } from '../useI18n'
import { useTheme, type ThemeMode } from '../theme'

interface ThemeToggleProps {
  compact?: boolean
}

export function ThemeToggle({ compact = false }: ThemeToggleProps) {
  const { copy } = useI18n()
  const { resolvedTheme, systemTheme, themePreference, setThemePreference } = useTheme()
  const isFollowingSystem = themePreference === 'system'

  const toggleTheme = () => {
    const nextTheme: ThemeMode = resolvedTheme === 'dark' ? 'light' : 'dark'

    if (themePreference !== 'system' && nextTheme === systemTheme) {
      setThemePreference('system')
      return
    }

    setThemePreference(nextTheme)
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={[
        'window-no-drag inline-flex max-w-full shrink-0 items-center gap-2 rounded-full border border-[var(--line)] bg-[var(--panel-strong)] text-left font-semibold text-[var(--foreground)] shadow-[var(--panel-shadow)] transition hover:border-[var(--primary)] hover:text-[var(--foreground)] disabled:cursor-wait disabled:opacity-70',
        compact ? 'px-3 py-2 text-xs' : 'px-4 py-2.5 text-sm',
      ].join(' ')}
      aria-label={copy.controls.toggleTheme}
      title={isFollowingSystem
        ? copy.controls.followSystem
        : resolvedTheme === 'dark'
          ? copy.controls.switchToLight
          : copy.controls.switchToDark}
    >
      <span className={`${compact ? 'text-sm' : 'text-base'} leading-none`}>
        {resolvedTheme === 'dark' ? '◐' : '◑'}
      </span>
      <span className="truncate">{resolvedTheme === 'dark' ? copy.controls.darkMode : copy.controls.lightMode}</span>
      {isFollowingSystem ? (
        <span className="inline-flex items-center justify-center rounded-full bg-[var(--accent-soft)] px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.14em] text-[var(--accent)]">
          {copy.controls.systemShort}
        </span>
      ) : null}
    </button>
  )
}
