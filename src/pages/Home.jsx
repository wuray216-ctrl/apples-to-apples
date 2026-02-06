import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import SearchInput from '../components/SearchInput'
import IndicatorBar from '../components/IndicatorBar'
import { REGIONS, INDICATORS, INDICATOR_KEYS, SHOWCASE_GROUPS } from '../data'

export default function Home() {
  const navigate = useNavigate()
  const [sourceId, setSourceId] = useState(null)
  const [compareToId, setCompareToId] = useState(null)
  const [selectedIndicator, setSelectedIndicator] = useState('all')
  const [showcaseIdx, setShowcaseIdx] = useState(0)
  const [fade, setFade] = useState('in')

  useEffect(() => {
    const timer = setInterval(() => {
      setFade('out')
      setTimeout(() => {
        setShowcaseIdx(prev => (prev + 1) % SHOWCASE_GROUPS.length)
        setFade('in')
      }, 400)
    }, 6000)
    return () => clearInterval(timer)
  }, [])

  const currentGroup = SHOWCASE_GROUPS[showcaseIdx]
  const showcaseRegions = currentGroup.ids
    .map(id => REGIONS.find(r => r.id === id))
    .filter(Boolean)

  const handleFind = () => {
    if (!sourceId) return
    const ids = [sourceId, compareToId].filter(Boolean)
    const params = new URLSearchParams({ ids: ids.join(',') })
    if (selectedIndicator !== 'all') params.set('indicator', selectedIndicator)
    navigate(`/compare?${params}`)
  }

  const stats = {
    regions: REGIONS.length,
    countries: REGIONS.filter(r => r.type === 'country').length,
    provinces: REGIONS.filter(r => r.type === 'province').length,
    states: REGIONS.filter(r => r.type === 'state').length,
    indicators: INDICATOR_KEYS.length,
  }

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <div className="max-w-4xl mx-auto px-6 pt-12 pb-8 text-center">
        <div className="text-xs tracking-[4px] text-indigo-400 font-bold uppercase mb-4">
          🍎 Apples to Apples
        </div>
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-mono font-bold leading-tight mb-5 bg-gradient-to-br from-slate-200 to-slate-500 bg-clip-text text-transparent">
          Compare what's actually comparable.
        </h1>
        <p className="text-base text-slate-500 max-w-xl mx-auto mb-8 leading-relaxed">
          Comparing Georgia (country) to China doesn't make sense. But Zhejiang, California, and Bavaria?
          Now you're comparing apples to apples.
        </p>

        {/* Stats */}
        <div className="flex justify-center gap-8 mb-10 text-center">
          <div>
            <div className="text-2xl font-bold text-slate-200">{stats.regions}</div>
            <div className="text-xs text-slate-600 uppercase tracking-wider">Regions</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-200">{stats.countries}</div>
            <div className="text-xs text-slate-600 uppercase tracking-wider">Countries</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-200">{stats.provinces + stats.states}</div>
            <div className="text-xs text-slate-600 uppercase tracking-wider">Provinces/States</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-200">{stats.indicators}</div>
            <div className="text-xs text-slate-600 uppercase tracking-wider">Indicators</div>
          </div>
        </div>

        {/* Search */}
        <div className="max-w-3xl mx-auto bg-surface/80 backdrop-blur-xl rounded-2xl p-6 border border-border">
          <div className="flex items-center gap-3 flex-wrap justify-center">
            <span className="text-slate-400 text-sm font-medium whitespace-nowrap">Compare</span>
            <div className="w-40">
              <SearchInput value={sourceId} onSelect={setSourceId} placeholder="e.g. Zhejiang" />
            </div>
            <span className="text-slate-400 text-sm font-medium">with</span>
            <div className="w-40">
              <SearchInput
                value={compareToId}
                onSelect={setCompareToId}
                placeholder="e.g. Bavaria"
                exclude={sourceId ? [sourceId] : []}
              />
            </div>
            <span className="text-slate-400 text-sm font-medium">on</span>
            <select
              value={selectedIndicator}
              onChange={e => setSelectedIndicator(e.target.value)}
              className="px-3 py-3 rounded-xl bg-surface text-slate-200 border-2 border-border font-sans text-sm cursor-pointer outline-none focus:border-indigo-500"
            >
              <option value="all">All Indicators</option>
              {INDICATOR_KEYS.map(k => (
                <option key={k} value={k}>{INDICATORS[k].label}</option>
              ))}
            </select>
          </div>
          <div className="text-center mt-5">
            <button
              onClick={handleFind}
              disabled={!sourceId}
              className={`px-10 py-3 rounded-xl text-base font-bold transition-all tracking-wide ${
                sourceId
                  ? 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white hover:from-indigo-400 hover:to-indigo-500 cursor-pointer'
                  : 'bg-border text-slate-600 cursor-not-allowed opacity-50'
              }`}
            >
              Find Similar Regions →
            </button>
          </div>
        </div>
      </div>

      {/* Carousel */}
      <div className="max-w-3xl mx-auto px-6 pb-12">
        <div className="text-center mb-5">
          <span
            className="text-sm font-semibold text-slate-300 transition-opacity duration-300"
            style={{ opacity: fade === 'in' ? 1 : 0 }}
          >
            {currentGroup.title}
          </span>
          <span
            className="text-sm text-slate-600 ml-2 transition-opacity duration-300"
            style={{ opacity: fade === 'in' ? 1 : 0 }}
          >
            — {currentGroup.subtitle}
          </span>
        </div>
        <div className="flex justify-center gap-2 mb-5">
          {SHOWCASE_GROUPS.map((_, i) => (
            <button
              key={i}
              onClick={() => {
                setFade('out')
                setTimeout(() => { setShowcaseIdx(i); setFade('in') }, 300)
              }}
              className={`h-2 rounded-full border-none transition-all duration-300 ${
                i === showcaseIdx ? 'w-6 bg-indigo-500' : 'w-2 bg-border hover:bg-slate-600'
              }`}
            />
          ))}
        </div>
        
        <div className="flex justify-center gap-4 mb-4">
          {showcaseRegions.map(r => (
            <span key={r.id} className="text-sm text-slate-400 transition-opacity duration-300" style={{ opacity: fade === 'in' ? 1 : 0 }}>
              {r.flag} {r.name}
            </span>
          ))}
        </div>

        <div
          className="transition-all duration-400"
          style={{
            opacity: fade === 'in' ? 1 : 0,
            transform: fade === 'in' ? 'translateY(0)' : 'translateY(12px)',
          }}
        >
          {['population', 'gdp', 'gdpPerCapita', 'hdi', 'lifeExpectancy', 'manufacturingPct', 'renewableEnergy'].map(key => (
            <IndicatorBar key={`${showcaseIdx}-${key}`} regions={showcaseRegions} indicatorKey={key} />
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-6 border-t border-border/30 text-slate-700 text-xs">
        Apples to Apples — Data from World Bank, UN, national statistics bureaus (2023)
        <br />
        <a href="https://github.com" className="text-indigo-500/70 hover:text-indigo-400 transition-colors">
          View on GitHub
        </a>
      </div>
    </div>
  )
}
