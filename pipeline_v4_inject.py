#!/usr/bin/env python3
"""
Pipeline v4: Multi-Source Data Integration
Injects IMF WEO Oct 2024 + UNDP HDI 2023/24 data into data.js
Each data point carries: value + year + source
"""

import json
import re
import sys
import os

def load_lookup(path='pipeline_v4_lookup.json'):
    with open(path) as f:
        return json.load(f)

def inject_into_datajs(datajs_path, lookup):
    with open(datajs_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Mapping from data.js indicator keys to our lookup keys
    INDICATOR_MAP = {
        'gdp': 'gdp',              # GDP in billions USD
        'gdpPerCapita': 'gdpPerCapita',  # GDP per capita USD
        'population': 'population',      # Population in millions
        'unemployment': 'unemployment',  # Unemployment %
        'hdi': 'hdi',                    # Human Development Index
        'lifeExpectancy': 'lifeExpectancy',  # Life expectancy (years)
        'medianAge': 'medianAge',            # Median age (years)
        'fertilityRate': 'fertilityRate',    # Fertility rate
        'populationDensity': 'populationDensity',  # Pop density
    }

    # Find all region objects in the REGIONS array
    # Pattern: { id: "xxx", ... iso: "XXX" or iso3: "XXX" ... indicators: { ... } }
    
    # We need to find each region's ISO code and update its indicators
    # Strategy: find each region block, extract iso/iso3, match to lookup, update values
    
    updated_count = 0
    skipped = []
    changelog = []

    # Find region blocks - they start with { id: " and contain indicators: {
    # We'll use a regex to find iso codes and indicator values
    
    # First, find all ISO codes in the data.js
    iso_pattern = re.compile(r'''(?:iso3?|code)\s*:\s*['"]([A-Z]{2,3})['"]''')
    
    # For each country in our lookup, find and update its indicators
    for iso, indicators in lookup.items():
        # Search for this ISO in data.js
        # Could be iso: "CHN" or iso3: "CHN" or code: "CN"
        patterns_to_try = [
            rf'iso3?\s*:\s*[\'"]({re.escape(iso)})[\'"]',
            rf'code\s*:\s*[\'"]({re.escape(iso)})[\'"]',
        ]
        # Also try 2-letter code
        iso2_map = {
            'CHN': 'CN', 'USA': 'US', 'JPN': 'JP', 'DEU': 'DE', 'GBR': 'GB',
            'FRA': 'FR', 'IND': 'IN', 'BRA': 'BR', 'KOR': 'KR', 'AUS': 'AU',
            'CAN': 'CA', 'ITA': 'IT', 'ESP': 'ES', 'MEX': 'MX', 'IDN': 'ID',
            'TUR': 'TR', 'SAU': 'SA', 'CHE': 'CH', 'NLD': 'NL', 'SWE': 'SE',
            'POL': 'PL', 'NOR': 'NO', 'AUT': 'AT', 'BEL': 'BE', 'ISR': 'IL',
            'THA': 'TH', 'ARE': 'AE', 'SGP': 'SG', 'MYS': 'MY', 'PHL': 'PH',
            'ZAF': 'ZA', 'EGY': 'EG', 'NGA': 'NG', 'ARG': 'AR', 'CHL': 'CL',
            'COL': 'CO', 'PER': 'PE', 'VNM': 'VN', 'NZL': 'NZ', 'IRL': 'IE',
            'DNK': 'DK', 'FIN': 'FI', 'PRT': 'PT', 'CZE': 'CZ', 'GRC': 'GR',
            'ROU': 'RO', 'HUN': 'HU', 'UKR': 'UA', 'RUS': 'RU', 'KAZ': 'KZ',
            'PAK': 'PK', 'BGD': 'BD', 'ETH': 'ET', 'KEN': 'KE', 'TZA': 'TZ',
            'GHA': 'GH', 'MAR': 'MA', 'TUN': 'TN', 'IRQ': 'IQ', 'QAT': 'QA',
            'KWT': 'KW', 'OMN': 'OM', 'BHR': 'BH', 'JOR': 'JO', 'LBN': 'LB',
            'HKG': 'HK', 'TWN': 'TW', 'ISL': 'IS', 'LUX': 'LU', 'SVN': 'SI',
            'SVK': 'SK', 'HRV': 'HR', 'BGR': 'BG', 'SRB': 'RS', 'LTU': 'LT',
            'LVA': 'LV', 'EST': 'EE',
        }
        if iso in iso2_map:
            patterns_to_try.append(rf'code\s*:\s*[\'"]({re.escape(iso2_map[iso])})[\'"]')
        
        found = False
        for pat_str in patterns_to_try:
            pat = re.compile(pat_str)
            match = pat.search(content)
            if match:
                found = True
                # Found this country in data.js
                # Now find and update each indicator value
                # We need to find the indicators block near this match
                pos = match.start()
                
                # Search for indicators: { ... } block within ~2000 chars after the match
                block = content[max(0,pos-200):pos+3000]
                
                for our_key, lookup_key in INDICATOR_MAP.items():
                    if lookup_key not in indicators:
                        continue
                    
                    new_val = indicators[lookup_key]['value']
                    new_year = indicators[lookup_key]['year']
                    new_source = indicators[lookup_key]['source']
                    
                    # Find pattern like: gdp: 1234.5  or  gdp: 1234
                    ind_pattern = re.compile(
                        rf'({re.escape(our_key)}\s*:\s*)([-\d.,]+)',
                    )
                    
                    # Search in the block near this region
                    ind_match = ind_pattern.search(block)
                    if ind_match:
                        old_val_str = ind_match.group(2)
                        try:
                            old_val = float(old_val_str.replace(',', ''))
                        except:
                            old_val = None
                        
                        # Format new value
                        if our_key == 'hdi':
                            new_val_str = f"{new_val:.3f}"
                        elif our_key == 'population':
                            new_val_str = f"{new_val:.2f}"
                        elif our_key in ('gdp', 'gdpPerCapita'):
                            new_val_str = f"{new_val:.1f}"
                        elif our_key == 'unemployment':
                            new_val_str = f"{new_val:.1f}"
                        else:
                            new_val_str = f"{new_val}"
                        
                        # Calculate the absolute position in content
                        block_start = max(0, pos - 200)
                        abs_start = block_start + ind_match.start()
                        abs_end = block_start + ind_match.end()
                        
                        old_text = content[abs_start:abs_end]
                        new_text = f"{ind_match.group(1)}{new_val_str}"
                        
                        content = content[:abs_start] + new_text + content[abs_end:]
                        
                        if old_val is not None and abs(old_val - new_val) > 0.01:
                            changelog.append({
                                'iso': iso,
                                'indicator': our_key,
                                'old': old_val,
                                'new': new_val,
                                'year': new_year,
                                'source': new_source,
                            })
                        
                        updated_count += 1
                
                break
        
        if not found and iso in ['CHN', 'USA', 'JPN', 'DEU', 'GBR', 'FRA', 'IND', 'BRA']:
            skipped.append(iso)

    # Write updated content
    with open(datajs_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Save changelog
    with open('pipeline_v4_changelog.json', 'w') as f:
        json.dump({
            'total_updates': updated_count,
            'changes': changelog[:200],  # limit size
            'skipped_major': skipped,
        }, f, indent=2, ensure_ascii=False)
    
    return updated_count, len(changelog), skipped

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 pipeline_v4_inject.py <path_to_data.js>")
        print("Example: python3 pipeline_v4_inject.py src/data.js")
        sys.exit(1)
    
    datajs_path = sys.argv[1]
    if not os.path.exists(datajs_path):
        print(f"Error: {datajs_path} not found")
        sys.exit(1)
    
    # Check for lookup file
    lookup_path = 'pipeline_v4_lookup.json'
    if not os.path.exists(lookup_path):
        print(f"Error: {lookup_path} not found. Run data extraction first.")
        sys.exit(1)
    
    lookup = load_lookup(lookup_path)
    
    print(f"Injecting data from {len(lookup)} countries into {datajs_path}...")
    updates, changes, skipped = inject_into_datajs(datajs_path, lookup)
    
    print(f"\n✅ Pipeline v4 complete!")
    print(f"   Total field updates: {updates}")
    print(f"   Values changed: {changes}")
    if skipped:
        print(f"   ⚠️  Major countries not found in data.js: {skipped}")
    print(f"\nChangelog saved to pipeline_v4_changelog.json")
    print(f"\nNext steps:")
    print(f"  1. Review changelog")
    print(f"  2. npm run build")
    print(f"  3. npx gh-pages -d dist")
