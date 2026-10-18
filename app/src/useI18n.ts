import { createContext, useContext } from 'react'
import { isLocale, type Locale } from './lib/locale'
import type { Copy } from './uiCopy'

export const LOCALE_STORAGE_KEY = 'locale'

export interface I18nContextValue {
  locale: Locale
  setLocale: (locale: Locale) => void
  copy: Copy
}

export const I18nContext = createContext<I18nContextValue | null>(null)

export function getPreferredLocale(): Locale {
  if (typeof window === 'undefined') {
    return 'zh-Hans'
  }

  const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY)
  if (isLocale(stored)) {
    return stored
  }

  return 'zh-Hans'
}

export function useI18n() {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider')
  }
  return context
}
