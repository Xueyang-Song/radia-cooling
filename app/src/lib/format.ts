import { localeNumberFormats, type Locale } from './locale'

const metricLabels: Record<string, Record<Locale, string>> = {
  solar_reflectance: { en: 'solar reflectance', 'zh-Hans': '太阳反射率' },
  window_emissivity: { en: 'window emissivity', 'zh-Hans': '大气窗口发射率' },
  cooling_power_proxy_w_m2: { en: 'cooling power proxy (W/m2)', 'zh-Hans': '冷却功率代理值 (W/m2)' },
  cooling_power_proxy_w_m2_mae: { en: 'cooling power proxy MAE (W/m2)', 'zh-Hans': '冷却功率代理值 MAE (W/m2)' },
  layer_material_accuracy: { en: 'layer material accuracy', 'zh-Hans': '层材料准确率' },
  total_thickness_mae_nm: { en: 'total thickness MAE (nm)', 'zh-Hans': '总厚度 MAE (nm)' },
  feature_rmse: { en: 'feature RMSE', 'zh-Hans': '特征 RMSE' },
}

export function formatValue(value: number, digits = 3, locale: Locale = 'en'): string {
  return new Intl.NumberFormat(localeNumberFormats[locale], {
    maximumFractionDigits: digits,
    minimumFractionDigits: 0,
  }).format(value)
}

export function formatFixed(value: number, digits = 4, locale: Locale = 'en'): string {
  return new Intl.NumberFormat(localeNumberFormats[locale], {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  }).format(value)
}

export function formatBytes(value: number, locale: Locale = 'en'): string {
  if (value < 1024) {
    return `${value} B`
  }

  const kilobytes = value / 1024
  if (kilobytes < 1024) {
    return `${formatFixed(kilobytes, 1, locale)} KB`
  }

  return `${formatFixed(kilobytes / 1024, 1, locale)} MB`
}

export function labelFromMetric(key: string, locale: Locale = 'en'): string {
  return metricLabels[key]?.[locale] ?? key.replaceAll('_', ' ').replaceAll('w m2', 'W/m2')
}