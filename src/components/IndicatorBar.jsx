import { INDICATORS, CHART_COLORS } from '../data'

export default function IndicatorBar({ regions, indicatorKey, highlight = false }) {
  const ind = INDICATORS[indicatorKey]
  if (!ind) return null

  const values = regions.map(r => r[indicatorKey] ?? 0)
  const maxVal = Math.max(...values) || 1

  return (
    <div className={`mb-3 px-4 py-3 bg-surface/60 rounded-xl border ${highlight ? 'border-indigo-500/50 ring-1 ring-indigo-500/20' : 'border-border'}`}>
      <div className="text-[11px] text-slate-500 uppercase tracking-widest font-bold mb-2.5">
        {ind.label}
      </div>
      {regions.map((r, i) => {
        const val = r[indicatorKey] ?? 0
        const pct = (val / maxVal) * 100
        const color = CHART_COLORS[i % CHART_COLORS.length]
        return (
          <div key={r.id} className="flex items-center gap-2 mb-1.5 last:mb-0">
            <span className="w-28 text-xs text-slate-300 text-right flex-shrink-0 truncate">
              {r.flag} {r.name}
            </span>
            <div className="flex-1 h-5 bg-midnight rounded overflow-hidden relative">
              <div
                className="h-full rounded flex items-center justify-end pr-2 transition-all duration-700 ease-out"
                style={{
                  width: `${Math.max(pct, 2)}%`,
                  background: `linear-gradient(90deg, ${color}66, ${color})`,
                }}
              >
                {pct > 30 && (
                  <span className="text-[11px] text-white font-semibold tabular-nums">
                    {ind.format(val)}
                  </span>
                )}
              </div>
              {pct <= 30 && (
                <span
                  className="absolute top-1/2 -translate-y-1/2 text-[11px] text-slate-400 font-semibold"
                  style={{ left: `calc(${pct}% + 6px)` }}
                >
                  {ind.format(val)}
                </span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
