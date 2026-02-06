import { useState, useEffect, useMemo } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend,
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, Cell, ResponsiveContainer,
} from 'recharts'
import { REGIONS, INDICATORS, INDICATOR_KEYS, CHART_COLORS, MATCH_PRESETS, TYPE_STYLES, INDICATOR_CATEGORIES } from '../data'
import { findMatches, getRegion } from '../matching'
import SearchInput from '../components/SearchInput'
import IndicatorBar from '../components/IndicatorBar'
import ScoreBar from '../components/ScoreBar'

export default function Compare() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  const initialIds = (searchParams.get('ids') || '').split(',').filter(Boolean)
  const initialIndicator = searchParams.get('indicator') || 'all'

  const [sourceId, setSourceId] = useState(initialIds[0] || null)
  const [selectedIds, setSelectedIds] = useState(initialIds.slice(1))
  const [focusIndicator, setFocusIndicator] = useState(initialIndicator)
  const [preset, setPreset] = useState('comprehensive')
  const [customWeights, setCustomWeights] = useState(null)
  const [showWeights, setShowWeights] = useState(false)
  const [tab, setTab] = useState('bars')
  const [category, setCategory] = useState('all')

  const source = sourceId ? getRegion(sourceId) : null
  
  const matches = useMemo(() => {
    if (!sourceId) return []
    return findMatches(sourceId, preset, customWeights, 20)
  }, [sourceId, preset, customWeights])

  const compareRegions = useMemo(() => {
    const ids = [sourceId, ...selectedIds].filter(Boolean)
    return ids.map(id => getRegion(id)).filter(Boolean)
  }, [sourceId, selectedIds])

  const toggleSelected = (id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : prev.length < 4 ? [...prev, id] : prev
    )
  }

  // Radar data
  const radarData = useMemo(() => {
    if (compareRegions.length < 2) return []
    const keys = ['gdpPerCapita', 'urbanization', 'hdi', 'internetPenetration', 'lifeExpectancy', 'gini']
    const allVals = {}
    keys.forEach(k => {
      const vals = REGIONS.map(r => r[k]).filter(v => v != null)
      allVals[k] = { min: Math.min(...vals), max: Math.max(...vals) }
    })
    return keys.map(k => {
      const entry = { indicator: INDICATORS[k].label }
      compareRegions.forEach(r => {
        const { min, max } = allVals[k]
        const range = max - min || 1
        entry[r.name] = Math.round(((r[k] - min) / range) * 100)
      })
      return entry
    })
  }, [compareRegions])

  // Scatter data
  const scatterData = useMemo(() =>
    REGIONS.map(r => ({
      name: r.name, x: r.gdpPerCapita, y: r.lifeExpectancy, z: r.population, id: r.id,
    })),
  [])

  const orderedIndicators = useMemo(() => {
    let keys = INDICATOR_KEYS;
    if (category !== 'all') {
      keys = INDICATOR_CATEGORIES[category]?.keys || INDICATOR_KEYS;
    }
    if (focusIndicator !== 'all' && keys.includes(focusIndicator)) {
      return [focusIndicator, ...keys.filter(k => k !== focusIndicator)];
    }
    return keys;
  }, [focusIndicator, category]);

  const weights = customWeights || MATCH_PRESETS[preset]?.weights || MATCH_PRESETS.comprehensive.weights

  return (
    <div className="min-h-screen flex flex-col">
      {/* Nav */}
      <div className="flex items-center gap-4 px-6 py-4 border-b border-border/30">
        <button onClick={() => navigate('/')} className="text-indigo-400 hover:text-indigo-300 text-sm font-semibold transition-colors">
          ← Back
        </button>
        <span className="text-xs tracking-[3px] text-indigo-400 font-bold uppercase">🍎 Apples to Apples</span>
        <div className="ml-auto text-xs text-slate-600">
          {REGIONS.length} regions • 10 indicators
        </div>
      </div>

      <div className="flex flex-1 max-w-[1400px] mx-auto w-full">
        {/* LEFT SIDEBAR */}
        <div className="w-80 border-r border-border/30 p-5 overflow-y-auto flex-shrink-0">
          {/* Source */}
          <div className="mb-5">
            <div className="text-[11px] text-slate-600 uppercase tracking-widest font-bold mb-2">Comparing</div>
            {source ? (
              <div className="flex items-center gap-3 p-3 bg-surface rounded-xl border-2 border-indigo-500/50">
                <span className="text-2xl">{source.flag}</span>
                <div>
                  <div className="font-bold text-sm">{source.name}</div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold uppercase tracking-wider ${TYPE_STYLES[source.type]?.bg} ${TYPE_STYLES[source.type]?.border} ${TYPE_STYLES[source.type]?.text}`}>
                    {TYPE_STYLES[source.type]?.label}
                  </span>
                </div>
                <button onClick={() => { setSourceId(null); setSelectedIds([]) }} className="ml-auto text-slate-600 hover:text-slate-300 text-xs">✕</button>
              </div>
            ) : (
              <SearchInput value={null} onSelect={setSourceId} placeholder="Choose a region..." />
            )}
          </div>

          {/* Preset selector */}
          <div className="mb-4">
            <div className="text-[11px] text-slate-600 uppercase tracking-widest font-bold mb-2">Match Mode</div>
            <div className="flex gap-1.5">
              {Object.entries(MATCH_PRESETS).map(([key, { label }]) => (
                <button
                  key={key}
                  onClick={() => { setPreset(key); setCustomWeights(null) }}
                  className={`flex-1 py-2 px-1 rounded-lg border text-[11px] font-semibold transition-all ${
                    preset === key && !customWeights
                      ? 'border-indigo-500 bg-indigo-500/10 text-indigo-300'
                      : 'border-border text-slate-600 hover:text-slate-400'
                  }`}
                >{label}</button>
              ))}
            </div>
          </div>

          {/* Custom weights */}
          <div className="mb-5">
            <button
              onClick={() => setShowWeights(!showWeights)}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold transition-colors"
            >
              {showWeights ? '▾ Hide' : '▸ Show'} Custom Weights
            </button>
            {showWeights && (
              <div className="mt-3 space-y-1">
                {INDICATOR_KEYS.map(k => (
                  <div key={k} className="flex items-center gap-2">
                    <span className="w-24 text-xs text-slate-500 text-right truncate">{INDICATORS[k].label}</span>
                    <input
                      type="range" min="0" max="100"
                      value={Math.round((weights[k] || 0) * 100)}
                      onChange={e => {
                        const newW = { ...weights, [k]: parseInt(e.target.value) / 100 }
                        setCustomWeights(newW)
                      }}
                      className="flex-1"
                    />
                    <span className="w-8 text-xs text-slate-400 text-right tabular-nums">
                      {Math.round((weights[k] || 0) * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Match results */}
          <div className="text-[11px] text-slate-600 uppercase tracking-widest font-bold mb-3">
            Best Matches
          </div>
          <div className="space-y-1">
            {matches.map(m => (
              <div
                key={m.id}
                onClick={() => toggleSelected(m.id)}
                className={`flex items-center gap-2.5 px-3 py-2.5 rounded-lg cursor-pointer transition-all ${
                  selectedIds.includes(m.id)
                    ? 'bg-indigo-500/10 border border-indigo-500/30'
                    : 'border border-transparent hover:bg-surface'
                }`}
              >
                <span className="text-lg">{m.flag}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold text-slate-200 truncate">{m.name}</div>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded-full border font-semibold uppercase ${TYPE_STYLES[m.type]?.bg} ${TYPE_STYLES[m.type]?.border} ${TYPE_STYLES[m.type]?.text}`}>
                    {TYPE_STYLES[m.type]?.label}
                  </span>
                </div>
                <ScoreBar score={m.score} />
              </div>
            ))}
          </div>
        </div>

        {/* MAIN CONTENT */}
        <div className="flex-1 p-6 overflow-y-auto">
          {compareRegions.length <= 1 ? (
            <div className="flex items-center justify-center h-96 text-slate-600">
              ← Click regions on the left to compare (up to 5)
            </div>
          ) : (
            <>
              {/* Selected chips */}
              <div className="flex gap-2 mb-5 flex-wrap">
                {compareRegions.map((r, i) => (
                  <div
                    key={r.id}
                    className="flex items-center gap-2 px-3.5 py-2 rounded-full border"
                    style={{
                      background: `${CHART_COLORS[i % CHART_COLORS.length]}10`,
                      borderColor: `${CHART_COLORS[i % CHART_COLORS.length]}40`,
                    }}
                  >
                    <span>{r.flag}</span>
                    <span className="text-xs font-semibold" style={{ color: CHART_COLORS[i % CHART_COLORS.length] }}>
                      {r.name}
                    </span>
                    {r.id !== sourceId && (
                      <button onClick={() => toggleSelected(r.id)} className="text-slate-600 hover:text-slate-300 text-xs ml-1">✕</button>
                    )}
                  </div>
                ))}
              </div>

              {/* Tab switcher */}
              <div className="flex gap-1 mb-4 bg-surface rounded-xl p-1 w-fit">
                {[['bars', '📊 Bars'], ['radar', '🕸️ Radar'], ['scatter', '⬡ Scatter']].map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => setTab(key)}
                    className={`px-5 py-2 rounded-lg text-xs font-semibold transition-all ${
                      tab === key ? 'bg-border text-slate-200' : 'text-slate-600 hover:text-slate-400'
                    }`}
                  >{label}</button>
                ))}
              </div>

              {/* Category filter */}
              {tab === 'bars' && (
                <div className="flex gap-1.5 mb-6 flex-wrap">
                  <button
                    onClick={() => setCategory('all')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      category === 'all' ? 'bg-indigo-500/20 border border-indigo-500/50 text-indigo-300' : 'border border-border text-slate-600 hover:text-slate-400'
                    }`}
                  >📊 All (18)</button>
                  {Object.entries(INDICATOR_CATEGORIES).map(([key, { label, keys }]) => (
                    <button
                      key={key}
                      onClick={() => setCategory(key)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        category === key ? 'bg-indigo-500/20 border border-indigo-500/50 text-indigo-300' : 'border border-border text-slate-600 hover:text-slate-400'
                      }`}
                    >{label} ({keys.length})</button>
                  ))}
                </div>
              )}

              {/* BARS */}
              {tab === 'bars' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                  {orderedIndicators.map((key, i) => (
                    <div key={key} className={focusIndicator !== 'all' && i === 0 ? 'lg:col-span-2' : ''}>
                      <IndicatorBar regions={compareRegions} indicatorKey={key} highlight={focusIndicator !== 'all' && i === 0} />
                    </div>
                  ))}
                </div>
              )}

              {/* RADAR */}
              {tab === 'radar' && (
                <div className="bg-surface/60 rounded-2xl border border-border p-6">
                  <div className="text-[11px] text-slate-600 uppercase tracking-widest font-bold mb-4">
                    Normalized Multi-Dimensional Comparison
                  </div>
                  <ResponsiveContainer width="100%" height={420}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="#1e293b" />
                      <PolarAngleAxis dataKey="indicator" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#475569', fontSize: 10 }} />
                      {compareRegions.map((r, i) => (
                        <Radar
                          key={r.id} name={r.name} dataKey={r.name}
                          stroke={CHART_COLORS[i % CHART_COLORS.length]}
                          fill={CHART_COLORS[i % CHART_COLORS.length]}
                          fillOpacity={0.12} strokeWidth={2}
                        />
                      ))}
                      <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* SCATTER */}
              {tab === 'scatter' && (
                <div className="bg-surface/60 rounded-2xl border border-border p-6">
                  <div className="text-[11px] text-slate-600 uppercase tracking-widest font-bold mb-1">
                    GDP per Capita vs Life Expectancy
                  </div>
                  <div className="text-[11px] text-slate-700 mb-4">Bubble size = population, selected regions highlighted</div>
                  <ResponsiveContainer width="100%" height={420}>
                    <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 10 }}>
                      <XAxis dataKey="x" name="GDP/capita" tick={{ fill: '#64748b', fontSize: 10 }}
                        tickFormatter={v => '$' + Math.round(v / 1000) + 'k'}
                        label={{ value: 'GDP per Capita (USD)', position: 'bottom', fill: '#64748b', fontSize: 11 }}
                      />
                      <YAxis dataKey="y" name="Life Expectancy" tick={{ fill: '#64748b', fontSize: 10 }} domain={[50, 90]}
                        label={{ value: 'Life Expectancy', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }}
                      />
                      <ZAxis dataKey="z" range={[30, 400]} name="Population" />
                      <Tooltip content={({ active, payload }) => {
                        if (!active || !payload?.length) return null
                        const d = payload[0].payload
                        return (
                          <div className="bg-surface border border-border rounded-lg px-3 py-2 text-xs shadow-xl">
                            <div className="font-bold mb-1">{d.name}</div>
                            <div className="text-slate-400">GDP/cap: ${d.x?.toLocaleString()}</div>
                            <div className="text-slate-400">Life Exp: {d.y} yrs</div>
                            <div className="text-slate-400">Pop: {d.z >= 1e9 ? (d.z / 1e9).toFixed(1) + 'B' : (d.z / 1e6).toFixed(1) + 'M'}</div>
                          </div>
                        )
                      }} />
                      <Scatter data={scatterData}>
                        {scatterData.map((entry, i) => {
                          const isSelected = compareRegions.some(r => r.id === entry.id)
                          return (
                            <Cell
                              key={i}
                              fill={isSelected ? '#6366f1' : '#1e293b'}
                              stroke={isSelected ? '#6366f1' : '#334155'}
                              strokeWidth={isSelected ? 2 : 1}
                              fillOpacity={isSelected ? 0.8 : 0.4}
                            />
                          )
                        })}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
