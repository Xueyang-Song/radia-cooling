import { useI18n } from '../useI18n'

interface LanguageToggleProps {
  compact?: boolean
}

export function LanguageToggle({ compact = false }: LanguageToggleProps) {
  const { locale, setLocale, copy } = useI18n()
  const nextLocale = locale === 'en' ? 'zh-Hans' : 'en'
  const nextLabel = nextLocale === 'en' ? copy.controls.english : copy.controls.chinese
  const nextShort = nextLocale === 'en' ? copy.controls.englishShort : copy.controls.chineseShort

  return (
    <button
      type="button"
      onClick={() => setLocale(nextLocale)}
      className={[
        'window-no-drag inline-flex max-w-full shrink-0 items-center gap-2 rounded-full border border-[var(--line)] bg-[var(--panel-strong)] text-left font-semibold text-[var(--foreground)] shadow-[var(--panel-shadow)] transition hover:border-[var(--primary)] hover:text-[var(--foreground)]',
        compact ? 'px-3 py-2 text-xs' : 'px-4 py-2.5 text-sm',
      ].join(' ')}
      aria-label={nextLocale === 'en' ? copy.controls.switchToEnglish : copy.controls.switchToChinese}
      title={copy.controls.toggleLanguage}
    >
      <span className="inline-flex min-w-[2.35rem] items-center justify-center rounded-full bg-[var(--accent-soft)] px-2 py-1 text-[10px] font-bold text-[var(--accent)]">
        {nextShort}
      </span>
      <span className="truncate">{nextLabel}</span>
    </button>
  )
}
