export const supportedLocales = ['en', 'zh-Hans'] as const

export type Locale = (typeof supportedLocales)[number]

export const localeNumberFormats: Record<Locale, string> = {
  en: 'en-US',
  'zh-Hans': 'zh-CN',
}

export function isLocale(value: string | null | undefined): value is Locale {
  return value === 'en' || value === 'zh-Hans'
}
