#!/bin/bash
# Apples-to-Apples i18n patch script
# This script makes MINIMAL changes to existing files, only adding i18n support
# Run from the project root: ~/Desktop/apples-to-apples

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT=~/Desktop/apples-to-apples

echo "📦 Step 1: Installing i18next dependencies..."
cd "$PROJECT"
npm install i18next react-i18next

echo "📁 Step 2: Copying new i18n files..."
cp -r "$DIR/src/i18n" "$PROJECT/src/"
cp "$DIR/src/components/LanguageSwitcher.jsx" "$PROJECT/src/components/"

echo "✏️  Step 3: Patching main.jsx (add 1 import line)..."
# Add i18n import before index.css import
sed -i.bak "s|import './index.css'|import './i18n/i18n'\nimport './index.css'|" "$PROJECT/src/main.jsx"

echo "✏️  Step 4: Patching Home.jsx..."
cd "$PROJECT/src/pages"

# Create patched Home.jsx from original
python3 -c "
import re
with open('Home.jsx', 'r') as f:
    code = f.read()

# Add imports
code = code.replace(
    \"import { useState, useEffect } from 'react'\",
    \"import { useState, useEffect } from 'react'\\nimport { useTranslation } from 'react-i18next'\"
)
code = code.replace(
    \"import { REGIONS, INDICATORS, INDICATOR_KEYS, SHOWCASE_GROUPS } from '../data'\",
    \"import { REGIONS, INDICATORS, INDICATOR_KEYS, SHOWCASE_GROUPS } from '../data'\\nimport LanguageSwitcher from '../components/LanguageSwitcher'\"
)

# Add const t
code = code.replace(
    'export default function Home() {',
    'export default function Home() {\\n  const { t } = useTranslation()'
)

# Add LanguageSwitcher before Hero
code = code.replace(
    '    <div className=\"min-h-screen\">\\n      {/* Hero */}',
    '''    <div className=\"min-h-screen\">
      {/* Language Switcher */}
      <div className=\"absolute top-4 right-6 z-50\">
        <LanguageSwitcher />
      </div>

      {/* Hero */}'''
)

# Translate texts
code = code.replace(
    \"Compare what's actually comparable.\",
    \"{t('home.hero_title')}\"
)
code = code.replace(
    \"Comparing Georgia (country) to China doesn't make sense. But Zhejiang, California, and Bavaria?\\n          Now you're comparing apples to apples.\",
    \"{t('home.hero_desc')}\"
)
code = code.replace(
    '<span className=\"text-slate-400 text-sm font-medium whitespace-nowrap\">Compare</span>',
    '<span className=\"text-slate-400 text-sm font-medium whitespace-nowrap\">{t(\"home.compare\")}</span>'
)
code = code.replace(
    '<span className=\"text-slate-400 text-sm font-medium\">with</span>',
    '<span className=\"text-slate-400 text-sm font-medium\">{t(\"home.with\")}</span>'
)
code = code.replace(
    '<span className=\"text-slate-400 text-sm font-medium\">on</span>',
    '<span className=\"text-slate-400 text-sm font-medium\">{t(\"home.on\")}</span>'
)
code = code.replace(
    '<option value=\"all\">All Indicators</option>',
    '<option value=\"all\">{t(\"home.all_indicators\")}</option>'
)
code = code.replace(
    'Find Similar Regions →',
    '{t(\"home.find_btn\")}'
)
code = code.replace(
    'placeholder=\"e.g. Zhejiang\"',
    'placeholder={t(\"home.placeholder_source\")}'
)
code = code.replace(
    'placeholder=\"e.g. Bavaria\"',
    'placeholder={t(\"home.placeholder_target\")}'
)
code = code.replace(
    '<div className=\"text-xs text-slate-600 uppercase tracking-wider\">Regions</div>',
    '<div className=\"text-xs text-slate-600 uppercase tracking-wider\">{t(\"home.regions\")}</div>'
)
code = code.replace(
    '<div className=\"text-xs text-slate-600 uppercase tracking-wider\">Countries</div>',
    '<div className=\"text-xs text-slate-600 uppercase tracking-wider\">{t(\"home.countries\")}</div>'
)
code = code.replace(
    '<div className=\"text-xs text-slate-600 uppercase tracking-wider\">Provinces/States</div>',
    '<div className=\"text-xs text-slate-600 uppercase tracking-wider\">{t(\"home.provinces_states\")}</div>'
)
code = code.replace(
    '<div className=\"text-xs text-slate-600 uppercase tracking-wider\">Indicators</div>',
    '<div className=\"text-xs text-slate-600 uppercase tracking-wider\">{t(\"home.indicators\")}</div>'
)
code = code.replace(
    'Apples to Apples — Data from World Bank, UN, national statistics bureaus (2023)',
    '{t(\"home.footer\")}'
)
code = code.replace(
    'View on GitHub',
    '{t(\"home.github\")}'
)

with open('Home.jsx', 'w') as f:
    f.write(code)
print('  Home.jsx patched successfully')
"

echo "✏️  Step 5: Patching Compare.jsx..."
python3 -c "
with open('Compare.jsx', 'r') as f:
    code = f.read()

# Add imports
code = code.replace(
    \"import { useState, useEffect, useMemo } from 'react'\",
    \"import { useState, useEffect, useMemo } from 'react'\\nimport { useTranslation } from 'react-i18next'\"
)
code = code.replace(
    \"import ScoreBar from '../components/ScoreBar'\",
    \"import ScoreBar from '../components/ScoreBar'\\nimport LanguageSwitcher from '../components/LanguageSwitcher'\"
)

# Add const t
code = code.replace(
    'export default function Compare() {',
    'export default function Compare() {\\n  const { t } = useTranslation()'
)

# Nav bar: add LanguageSwitcher, translate Back
code = code.replace(
    '''        <span className=\"text-xs tracking-[3px] text-indigo-400 font-bold uppercase\">🍎 Apples to Apples</span>
        <div className=\"ml-auto text-xs text-slate-600\">
          {REGIONS.length} regions • 10 indicators
        </div>''',
    '''        <span className=\"text-xs tracking-[3px] text-indigo-400 font-bold uppercase\">🍎 Apples to Apples</span>
        <div className=\"ml-auto flex items-center gap-3\">
          <LanguageSwitcher />
          <span className=\"text-xs text-slate-600\">{t('compare.region_count', { count: REGIONS.length })}</span>
        </div>'''
)
code = code.replace('← Back', '{t(\"compare.back\")}')

# Sidebar texts
code = code.replace(
    '>Comparing</div>',
    '>{t(\"compare.comparing\")}</div>'
)
code = code.replace(
    'placeholder=\"Choose a region...\"',
    'placeholder={t(\"compare.choose_region\")}'
)
code = code.replace(
    '>Match Mode</div>',
    '>{t(\"compare.match_mode\")}</div>'
)
code = code.replace(
    \"{showWeights ? '▾ Hide' : '▸ Show'} Custom Weights\",
    \"{showWeights ? t('compare.hide_weights') : t('compare.show_weights')}\"
)
code = code.replace(
    'Best Matches',
    '{t(\"compare.best_matches\")}'
)
code = code.replace(
    '← Click regions on the left to compare (up to 5)',
    '{t(\"compare.hint_select\")}'
)

# Tab labels
code = code.replace(
    \"[['bars', '📊 Bars'], ['radar', '🕸️ Radar'], ['scatter', '⬡ Scatter']]\",
    \"[['bars', t('compare.tab_bars')], ['radar', t('compare.tab_radar')], ['scatter', t('compare.tab_scatter')]]\"
)

# Category all button
code = code.replace(
    '>📊 All (18)</button>',
    '>{t(\"compare.all_count\")}</button>'
)

# Chart titles
code = code.replace(
    'Normalized Multi-Dimensional Comparison',
    '{t(\"compare.radar_title\")}'
)
code = code.replace(
    'GDP per Capita vs Life Expectancy',
    '{t(\"compare.scatter_title\")}'
)
code = code.replace(
    'Bubble size = population, selected regions highlighted',
    '{t(\"compare.scatter_subtitle\")}'
)

with open('Compare.jsx', 'w') as f:
    f.write(code)
print('  Compare.jsx patched successfully')
"

# Clean up backup files
rm -f "$PROJECT/src/main.jsx.bak"

echo ""
echo "✅ Done! All patches applied. Run 'npm run dev' to test."
echo ""
echo "Language switcher will appear in the top-right corner."
echo "Supports: 🇺🇸 English | 🇨🇳 中文 | 🇪🇸 Español"
