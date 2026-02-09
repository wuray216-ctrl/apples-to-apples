#!/usr/bin/env python3
"""
Add 'year' property to each indicator in the INDICATORS object in data.js.
This enables IndicatorBar to show a superscript year tag next to each indicator label.

Usage: python3 add_indicator_years.py
Then: npm run build
"""
import os, re

DATA_FILE = os.path.expanduser('~/Desktop/apples-to-apples/src/data.js')

# Year mapping for each indicator
# Country-level data updated to 2022 via World Bank API (pipeline v3)
# Subnational data is mixed-year estimates
INDICATOR_YEARS = {
    'population': '2022',
    'gdp': '2022',
    'gdpPerCapita': '2022',
    'area': '2022',
    'urbanization': '2022',
    'gini': '2022',
    'hdi': '2021',          # UNDP HDI latest available is usually 1 year behind
    'internetPenetration': None,  # mixed sources, no single year
    'lifeExpectancy': '2022',
    'co2PerCapita': None,    # WB data gap noted in pipeline
    'universityCount': None, # static/estimated
    'literacyRate': '2022',
    'pisaScore': '2022',     # PISA 2022 round
    'doctorsPer1000': '2022',
    'hospitalBeds': '2022',
    'healthExpenditure': '2022',
    'manufacturingPct': '2022',
    'exports': '2022',
    'fdiInflow': '2022',
    'forestCoverage': '2022',
    'airQualityPM25': None,  # mixed sources
    'renewableEnergy': '2022',
    'unemployment': '2022',
    'inflation': '2022',
    'rdExpenditure': '2022',
    'militarySpending': '2022',
    'populationDensity': '2022',
    'medianAge': '2022',
    'birthRate': '2022',
    'deathRate': '2022',
}

with open(DATA_FILE, 'r') as f:
    content = f.read()

# For each indicator, add year property after the existing properties
# Pattern: indicatorKey: { label: '...', ... },
changes = 0
for key, year in INDICATOR_YEARS.items():
    if year is None:
        continue
    
    # Find the indicator definition line and add year property
    # Match pattern like: key: { label: '...', ... format: v => ... },
    # We'll insert year: '2022', right after the opening {
    pattern = rf"(\s+{key}:\s*\{{)"
    replacement = rf"\1 year: '{year}',"
    
    new_content = re.sub(pattern, replacement, content, count=1)
    if new_content != content:
        changes += 1
        content = new_content

with open(DATA_FILE, 'w') as f:
    f.write(content)

print(f"✅ Added year tags to {changes} indicators in data.js")
print(f"   Indicators with year: {sum(1 for v in INDICATOR_YEARS.values() if v)}")
print(f"   Indicators without year (mixed sources): {sum(1 for v in INDICATOR_YEARS.values() if not v)}")
print()
print("Next steps:")
print("1. Copy updated IndicatorBar.jsx to src/components/")
print("2. Run: npm run build")
