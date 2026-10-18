import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

export type ThemeMode = 'light' | 'dark'
export type ThemePreference = ThemeMode | 'system'

const THEME_STORAGE_KEY = 'theme-preference'

interface ThemeContextValue {
  resolvedTheme: ThemeMode
  systemTheme: ThemeMode
  themePreference: ThemePreference
  setThemePreference: (preference: ThemePreference) => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

function isThemePreference(value: string | null): value is ThemePreference {
  return value === 'system' || value === 'light' || value === 'dark'
}

function getSystemTheme(): ThemeMode {
  if (typeof window === 'undefined') {
    return 'light'
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function getPreferredThemePreference(): ThemePreference {
  if (typeof window === 'undefined') {
    return 'system'
  }

  const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
  return isThemePreference(stored) ? stored : 'system'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [systemTheme, setSystemTheme] = useState<ThemeMode>(() => getSystemTheme())
  const [themePreference, setThemePreference] = useState<ThemePreference>(() => getPreferredThemePreference())
  const resolvedTheme = themePreference === 'system' ? systemTheme : themePreference

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    const updateSystemTheme = (matches: boolean) => {
      setSystemTheme(matches ? 'dark' : 'light')
    }

    updateSystemTheme(mediaQuery.matches)

    const handleChange = (event: MediaQueryListEvent) => {
      updateSystemTheme(event.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', resolvedTheme === 'dark')
    document.documentElement.dataset.theme = resolvedTheme
    document.documentElement.dataset.themePreference = themePreference

    if (themePreference === 'system') {
      window.localStorage.removeItem(THEME_STORAGE_KEY)
    } else {
      window.localStorage.setItem(THEME_STORAGE_KEY, themePreference)
    }

    window.rcDesktop?.setWindowTheme(resolvedTheme)
  }, [resolvedTheme, themePreference])

  const value = useMemo<ThemeContextValue>(
    () => ({
      resolvedTheme,
      systemTheme,
      themePreference,
      setThemePreference,
    }),
    [resolvedTheme, systemTheme, themePreference],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const context = useContext(ThemeContext)

  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }

  return context
}
