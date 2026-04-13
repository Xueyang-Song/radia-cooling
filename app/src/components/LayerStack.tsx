import { useI18n } from '../useI18n'
import { formatValue } from '../lib/format'

const materialColors: Record<string, string> = {
  SiO2: '#cddff4',
  TiO2: '#d5c4f0',
  HfO2: '#c0e7d8',
  Al2O3: '#f4d7bf',
  Si3N4: '#f2e8b8',
  Ag: '#d8dde4',
}

interface LayerStackProps {
  materials: string[]
  thicknessesNm: number[]
  reflectorMaterial: string
  reflectorThicknessNm: number
}

export function LayerStack({ materials, thicknessesNm, reflectorMaterial, reflectorThicknessNm }: LayerStackProps) {
  const { copy, locale } = useI18n()
  const totalThickness = thicknessesNm.reduce((sum, value) => sum + value, 0) + reflectorThicknessNm
  const segmentTextClass = 'text-[#12202d]'

  return (
    <div className="surface-card-strong space-y-4 rounded-[1.6rem] p-5">
      <div className="surface-inset flex h-14 overflow-hidden rounded-full">
        {materials.map((material, index) => (
          <div
            key={`${material}-${index}`}
            className={`flex items-center justify-center px-1 text-[10px] font-semibold uppercase tracking-[0.2em] ${segmentTextClass}`}
            style={{
              width: `${(thicknessesNm[index] / totalThickness) * 100}%`,
              backgroundColor: materialColors[material] ?? '#d8dde4',
            }}
            title={`${material} at ${formatValue(thicknessesNm[index], 1, locale)} nm`}
          >
            {material}
          </div>
        ))}
        <div
          className={`flex items-center justify-center px-1 text-[10px] font-semibold uppercase tracking-[0.2em] ${segmentTextClass}`}
          style={{
            width: `${(reflectorThicknessNm / totalThickness) * 100}%`,
            backgroundColor: materialColors[reflectorMaterial] ?? '#d8dde4',
          }}
          title={copy.common.reflectorAt(reflectorMaterial, formatValue(reflectorThicknessNm, 1, locale))}
        >
          {reflectorMaterial}
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {materials.map((material, index) => (
          <div key={`${material}-${index}-detail`} className="surface-inset rounded-2xl px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">{copy.common.layer(index + 1)}</p>
            <div className="mt-2 flex items-center justify-between gap-3">
              <span className="font-semibold text-[var(--ink)]">{material}</span>
              <span className="text-sm text-[var(--muted)]">{formatValue(thicknessesNm[index], 1, locale)} nm</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}