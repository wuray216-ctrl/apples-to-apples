import { useState, useRef, useEffect } from 'react'
import { REGIONS, TYPE_STYLES } from '../data'

export default function SearchInput({ value, onSelect, placeholder = 'Search regions...', exclude = [] }) {
  const [focused, setFocused] = useState(false)
  const [inputVal, setInputVal] = useState('')
  const ref = useRef(null)

  useEffect(() => {
    if (value) {
      const r = REGIONS.find(r => r.id === value)
      if (r) setInputVal(r.name)
    } else {
      setInputVal('')
    }
  }, [value])

  const filtered = (() => {
    let results = REGIONS.filter(r => !exclude.includes(r.id))
    if (inputVal.trim()) {
      const q = inputVal.toLowerCase()
      results = results.filter(r => r.name.toLowerCase().includes(q))
    }
    return results.slice(0, 12)
  })()

  return (
    <div className="relative">
      <input
        ref={ref}
        value={inputVal}
        onChange={e => setInputVal(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setTimeout(() => setFocused(false), 200)}
        placeholder={placeholder}
        className="w-full px-4 py-3 text-base rounded-xl bg-surface text-slate-200 border-2 border-border focus:border-indigo-500 outline-none transition-colors font-sans"
      />
      {focused && filtered.length > 0 && (
        <div className="absolute top-full mt-1 left-0 right-0 z-50 bg-surface border border-border rounded-xl max-h-72 overflow-y-auto shadow-2xl">
          {filtered.map(r => {
            const style = TYPE_STYLES[r.type] || TYPE_STYLES.country
            return (
              <div
                key={r.id}
                onMouseDown={() => {
                  onSelect(r.id)
                  setInputVal(r.name)
                  setFocused(false)
                }}
                className="flex items-center gap-3 px-4 py-2.5 cursor-pointer hover:bg-border/50 transition-colors"
              >
                <span className="text-lg">{r.flag}</span>
                <span className="text-sm font-medium text-slate-200">{r.name}</span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold uppercase tracking-wider ${style.bg} ${style.border} ${style.text}`}>
                  {style.label}
                </span>
                {r.parent && (
                  <span className="text-xs text-slate-600 ml-auto">
                    {REGIONS.find(p => p.id === r.parent)?.name}
                  </span>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
