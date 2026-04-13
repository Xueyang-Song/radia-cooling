import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { DatasetSample, DesignSpace } from '../lib/types'
import { formatValue } from '../lib/format'
import { useI18n } from '../useI18n'

interface SpectrumChartProps {
  sample: DatasetSample
  wavelengths: number[]
  designSpace: DesignSpace
}

export function SpectrumChart({ sample, wavelengths, designSpace }: SpectrumChartProps) {
  const { copy, locale } = useI18n()
  const points = wavelengths.map((wavelength, index) => ({
    wavelength,
    reflectance: sample.reflectance[index],
    emissivity: sample.emissivity[index],
  }))

  return (
    <div className="surface-card-strong rounded-[1.6rem] p-5">
      <div className="mb-4 flex flex-wrap items-center gap-3 text-sm text-[var(--muted)]">
        <span className="inline-flex items-center gap-2 rounded-full bg-[var(--accent-soft)] px-3 py-1 text-[var(--accent)]">
          <span className="h-2.5 w-2.5 rounded-full bg-[var(--accent)]" /> {copy.explore.reflectance}
        </span>
        <span className="inline-flex items-center gap-2 rounded-full bg-[var(--accent-warm-soft)] px-3 py-1 text-[var(--accent-warm)]">
          <span className="h-2.5 w-2.5 rounded-full bg-[var(--accent-warm)]" /> {copy.explore.emissivity}
        </span>
      </div>
      <div className="h-[340px] w-full">
        <ResponsiveContainer>
          <LineChart data={points} margin={{ top: 10, right: 18, bottom: 12, left: 0 }}>
            <CartesianGrid stroke="var(--line)" strokeOpacity={0.55} strokeDasharray="4 4" />
            <ReferenceArea x1={designSpace.solarBand[0]} x2={designSpace.solarBand[1]} fill="var(--accent)" fillOpacity={0.08} />
            <ReferenceArea x1={designSpace.windowBand[0]} x2={designSpace.windowBand[1]} fill="var(--accent-warm)" fillOpacity={0.1} />
            <XAxis
              dataKey="wavelength"
              tick={{ fill: 'var(--muted)', fontSize: 12 }}
              tickFormatter={(value: number) => formatValue(value, 1, locale)}
              stroke="var(--line)"
            />
            <YAxis domain={[0, 1]} tick={{ fill: 'var(--muted)', fontSize: 12 }} stroke="var(--line)" />
            <Tooltip
              formatter={(value, key) => [
                formatValue(Number(value ?? 0), 3, locale),
                key === 'reflectance' ? copy.explore.reflectance : copy.explore.emissivity,
              ]}
              labelFormatter={(value) => `${formatValue(Number(value), 2, locale)} μm`}
              contentStyle={{ borderRadius: '1rem', border: '1px solid var(--line)', background: 'var(--panel)', color: 'var(--ink)' }}
              itemStyle={{ color: 'var(--ink)' }}
              labelStyle={{ color: 'var(--muted)' }}
            />
            <Line type="monotone" dataKey="reflectance" stroke="var(--accent)" strokeWidth={2.6} dot={false} />
            <Line type="monotone" dataKey="emissivity" stroke="var(--accent-warm)" strokeWidth={2.6} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}