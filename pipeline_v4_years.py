#!/usr/bin/env python3
"""
Pipeline v4: Update INDICATORS year metadata based on actual data sources.
Updates the year property in each indicator definition to reflect the primary data source year.
"""

import re
import sys
import os

# Indicator year mapping based on Pipeline v4 sources
INDICATOR_YEARS = {
    # From IMF WEO Oct 2024 → mostly 2024 data
    'gdp':              {'year': '2024', 'source': 'IMF WEO'},
    'gdpPerCapita':     {'year': '2024', 'source': 'IMF WEO'},
    'population':       {'year': '2024', 'source': 'IMF WEO'},
    'unemployment':     {'year': '2024', 'source': 'IMF WEO'},
    'inflation':        {'year': '2024', 'source': 'IMF WEO'},
    'govDebt':          {'year': '2024', 'source': 'IMF WEO'},
    
    # From UNDP HDR 2023/24 → 2022 data
    'hdi':              {'year': '2022', 'source': 'UNDP'},
    
    # Still from World Bank (Pipeline v3) → 2022 data
    'lifeExpectancy':   {'year': '2023', 'source': 'UN WPP'},
    'medianAge':        {'year': '2023', 'source': 'UN WPP'},
    'fertilityRate':    {'year': '2023', 'source': 'UN WPP'},
    'area':             {'year': '2022', 'source': 'World Bank'},
    'populationDensity':{'year': '2023', 'source': 'UN WPP'},
    'urbanization':     {'year': '2022', 'source': 'World Bank'},
    'gpiIndex':         {'year': '2022', 'source': 'IEP'},
    'giniCoefficient':  {'year': '2022', 'source': 'World Bank'},
    'manufacturingPct': {'year': '2022', 'source': 'World Bank'},
    'forestCoverage':   {'year': '2022', 'source': 'World Bank'},
    'renewableEnergy':  {'year': '2022', 'source': 'World Bank'},
    'fdiInflow':        {'year': '2022', 'source': 'World Bank'},
    'exportsOfGDP':     {'year': '2022', 'source': 'World Bank'},
    'healthExpenditure':{'year': '2022', 'source': 'World Bank'},
    'physiciansPer1000':{'year': '2022', 'source': 'World Bank'},
    'hospitalBedsPer1000':{'year': '2022', 'source': 'World Bank'},
    'educationExpenditure':{'year': '2022', 'source': 'World Bank'},
    'researchExpenditure':{'year': '2022', 'source': 'World Bank'},
    'militaryExpenditure':{'year': '2022', 'source': 'World Bank'},
    
    # Mixed sources - no year tag
    'internetPenetration': None,
    'co2PerCapita': None,
    'airQualityPM25': None,
    'universityCount': None,
}

def update_indicator_years(datajs_path):
    with open(datajs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updated = 0
    for indicator, meta in INDICATOR_YEARS.items():
        if meta is None:
            # Remove year tag if exists
            pattern = re.compile(
                rf'({indicator}\s*:\s*\{{)\s*year:\s*[\'"][^\'"]*[\'"]\s*,\s*'
            )
            if pattern.search(content):
                content = pattern.sub(r'\1 ', content)
            continue
        
        year_str = meta['year']
        source = meta['source']
        
        # Check if year property already exists
        has_year = re.search(
            rf'{indicator}\s*:\s*\{{[^}}]*?year\s*:', content
        )
        
        if has_year:
            # Update existing year
            pattern = re.compile(
                rf'({indicator}\s*:\s*\{{[^}}]*?)year\s*:\s*[\'"][^\'"]*[\'"]'
            )
            replacement = rf"\1year: '{year_str}'"
            new_content = pattern.sub(replacement, content)
            if new_content != content:
                content = new_content
                updated += 1
        else:
            # Add year property after the opening brace
            pattern = re.compile(
                rf'({indicator}\s*:\s*\{{)'
            )
            match = pattern.search(content)
            if match:
                content = pattern.sub(
                    rf"\1 year: '{year_str}',", content, count=1
                )
                updated += 1
    
    with open(datajs_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return updated

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 pipeline_v4_years.py <path_to_data.js>")
        sys.exit(1)
    
    datajs_path = sys.argv[1]
    if not os.path.exists(datajs_path):
        print(f"Error: {datajs_path} not found")
        sys.exit(1)
    
    updated = update_indicator_years(datajs_path)
    print(f"✅ Updated year metadata for {updated} indicators")
    print(f"   GDP, population, unemployment etc → 2024 (IMF WEO)")
    print(f"   HDI → 2022 (UNDP)")
    print(f"   Other indicators → 2022 (World Bank)")
