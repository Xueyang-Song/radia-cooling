import { useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { Locale } from './lib/locale'
import { I18nContext, type I18nContextValue, getPreferredLocale, LOCALE_STORAGE_KEY } from './useI18n'
import { copy } from './uiCopy'

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(() => getPreferredLocale())

  useEffect(() => {
    document.documentElement.lang = locale === 'zh-Hans' ? 'zh-Hans' : 'en'
    document.documentElement.dataset.locale = locale
    window.localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  }, [locale])

  const value = useMemo<I18nContextValue>(
    () => ({
      locale,
      setLocale,
      copy: copy[locale],
    }),
    [locale],
  )

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}
