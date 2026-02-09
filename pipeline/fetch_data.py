#!/usr/bin/env python3
"""
Apples to Apples — Automated Data Pipeline v3
Fetches country-level data from World Bank API with LOCAL CACHING.

Fixes from v2:
- Correct field index mapping (verified against actual data.js)
- Proper unit conversions (area ÷1000, pop ÷1e6, gdp ÷1e9)
- Skip fields where our definition != WB definition (exports, FDI as absolutes)
- Local JSON cache (only calls API once, reuse with --cache)
- co2PerCapita fallback to older data (WB often lags)

Usage:
  python3 fetch_data.py                # Fetch + cache + update (default year 2022)
  python3 fetch_data.py --cache        # Use cached data (no API calls)
  python3 fetch_data.py --refresh      # Force re-fetch even if cache exists
  python3 fetch_data.py --dry-run      # Preview changes without writing
  python3 fetch_data.py --year 2023    # Target different year
"""

import json
import time
import argparse
import os
import sys
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from collections import Counter

# ============================================================
# ACTUAL FIELD LAYOUT IN data.js (verified from source)
# ============================================================
# idx  0: id
# idx  1: name
# idx  2: type
# idx  3: parent
# idx  4: flag
# idx  5: pop(M)         — population in millions
# idx  6: gdp(B$)        — GDP in billions USD
# idx  7: gdpPC           — GDP per capita USD
# idx  8: area(k)         — area in THOUSANDS of sq km
# idx  9: urban%          — urbanization percentage
# idx 10: gini            — Gini coefficient
# idx 11: hdi             — Human Development Index (UNDP, not WB)
# idx 12: net%            — internet penetration % (WB: IT.NET.USER.ZS)
# idx 13: lifeExp         — life expectancy years
# idx 14: co2PC           — CO2 per capita tonnes
# idx 15: unis            — university count (manual, NOT WB)
# idx 16: lit%            — literacy rate %
# idx 17: pisa            — PISA score (OECD, NOT WB)
# idx 18: docs            — doctors per 1000
# idx 19: beds            — hospital beds per 1000
# idx 20: health%         — health expenditure % GDP
# idx 21: mfg%            — manufacturing % GDP
# idx 22: exp(B)          — exports in billions (absolute, NOT % — skip WB)
# idx 23: fdi(B)          — FDI inflow in billions (absolute, NOT % — skip WB)
# idx 24: forest%         — forest coverage %
# idx 25: pm25            — PM2.5 μg/m³
# idx 26: renew%          — renewable energy %
# idx 27: unemp%          — unemployment %
# idx 28: inflate%        — inflation %
# idx 29: rd%             — R&D expenditure % GDP
# idx 30: mil%            — military spending % GDP
# idx 31: popDens         — population density /km²
# idx 32: medAge          — median age (UN, NOT WB)
# idx 33: birthR          — birth rate per 1000
# idx 34: deathR          — death rate per 1000

# Only map fields where WB definition MATCHES our data definition
WB_FIELD_MAP = {
    # field_name:       (idx, wb_code,              transform)
    # transform: "direct" = use as-is, "div1e6" = ÷1M, "div1e9" = ÷1B, "div1e3" = ÷1K
    "population":       (5,  "SP.POP.TOTL",          "div1e6"),   # people → millions
    "gdpBillions":      (6,  "NY.GDP.MKTP.CD",       "div1e9"),   # USD → billions
    "gdpPerCapita":     (7,  "NY.GDP.PCAP.CD",       "direct"),   # USD per capita
    "area":             (8,  "AG.LND.TOTL.K2",       "div1e3"),   # sq km → thousands
    "urbanization":     (9,  "SP.URB.TOTL.IN.ZS",    "direct"),   # percentage
    "gini":             (10, "SI.POV.GINI",           "direct"),   # index
    # idx 11: hdi — UNDP only, skip
    # idx 12: internet — could add IT.NET.USER.ZS but skip for now
    "lifeExpectancy":   (13, "SP.DYN.LE00.IN",       "direct"),   # years
    "co2PerCapita":     (14, "EN.ATM.CO2E.PC",       "direct"),   # tonnes
    # idx 15: unis — manual count, skip
    "literacy":         (16, "SE.ADT.LITR.ZS",       "direct"),   # percentage
    # idx 17: pisa — OECD only, skip
    "doctors":          (18, "SH.MED.PHYS.ZS",       "direct"),   # per 1000
    "hospitalBeds":     (19, "SH.MED.BEDS.ZS",       "direct"),   # per 1000
    # idx 20: healthExpenditure — could add SH.XPD.CHEX.GD.ZS
    "manufacturing":    (21, "NV.IND.MANF.ZS",       "direct"),   # % of GDP ✓ matches
    # idx 22: exports(B) — WB has NE.EXP.GNFS.CD but our data is billions, need div1e9
    # idx 23: fdi(B) — WB has BX.KLT.DINV.CD.WD but our data is billions, need div1e9
    "forestCover":      (24, "AG.LND.FRST.ZS",       "direct"),   # percentage
    "pm25":             (25, "EN.ATM.PM25.MC.M3",    "direct"),   # μg/m³
    "renewableEnergy":  (26, "EG.FEC.RNEW.ZS",       "direct"),   # percentage
    "unemployment":     (27, "SL.UEM.TOTL.ZS",       "direct"),   # percentage
    "inflation":        (28, "FP.CPI.TOTL.ZG",       "direct"),   # percentage
    "rdExpenditure":    (29, "GB.XPD.RSDV.GD.ZS",    "direct"),   # % GDP
    "militarySpending": (30, "MS.MIL.XPND.GD.ZS",   "direct"),   # % GDP
    "populationDensity":(31, "EN.POP.DNST",          "direct"),   # per km²
    # idx 32: medianAge — UN only, skip
    "birthRate":        (33, "SP.DYN.CBRT.IN",       "direct"),   # per 1000
    "deathRate":        (34, "SP.DYN.CDRT.IN",       "direct"),   # per 1000
}

# Also fetch exports and FDI (absolute values in our data)
WB_FIELD_MAP["exports"] = (22, "NE.EXP.GNFS.CD", "div1e9")   # USD → billions
WB_FIELD_MAP["fdiInflow"] = (23, "BX.KLT.DINV.CD.WD", "div1e9")  # USD → billions
WB_FIELD_MAP["healthExpenditure"] = (20, "SH.XPD.CHEX.GD.ZS", "direct")  # % GDP

# Region ID → ISO3 code (country-level only)
REGION_TO_ISO3 = {
    "us": "USA", "cn": "CHN", "de": "DEU", "jp": "JPN", "gb": "GBR",
    "fr": "FRA", "in": "IND", "br": "BRA", "kr": "KOR", "it": "ITA",
    "ca": "CAN", "au": "AUS", "es": "ESP", "mx": "MEX", "id": "IDN",
    "nl": "NLD", "sa": "SAU", "ch": "CHE", "se": "SWE", "pl": "POL",
    "th": "THA", "tr": "TUR", "ng": "NGA", "ar": "ARG", "za": "ZAF",
    "my": "MYS", "bd": "BGD", "vn": "VNM", "ph": "PHL", "eg": "EGY",
    "sg": "SGP", "ie": "IRL", "dk": "DNK", "fi": "FIN", "no": "NOR",
    "nz": "NZL", "il": "ISR", "hk": "HKG", "tw": "TWN", "pt": "PRT",
    "cz": "CZE", "ro": "ROU", "hu": "HUN", "at": "AUT", "be": "BEL",
    "cl": "CHL", "co": "COL", "pe": "PER", "ec": "ECU", "uy": "URY",
    "pa": "PAN", "cr": "CRI",
    "pk": "PAK", "et": "ETH", "ke": "KEN", "gh": "GHA", "tz": "TZA",
    "ru": "RUS",
    "ae": "ARE", "qa": "QAT", "kw": "KWT", "jo": "JOR",
    "bg": "BGR", "hr": "HRV", "rs": "SRB", "lt": "LTU", "lv": "LVA", "ee": "EST",
    "ma": "MAR", "tn": "TUN", "rw": "RWA", "sn": "SEN", "ci": "CIV",
    "lk": "LKA", "mm": "MMR", "kh": "KHM", "np": "NPL",
    "gr": "GRC", "ua": "UKR",
}

# ============================================================
# CACHING
# ============================================================
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

def get_cache_path(year):
    return os.path.join(CACHE_DIR, f"wb_data_{year}.json")

def save_cache(all_data, year):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = get_cache_path(year)
    with open(path, 'w') as f:
        json.dump({
            "fetchedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            "targetYear": year,
            "data": all_data
        }, f, indent=2)
    size_kb = os.path.getsize(path) / 1024
    print(f"  💾 Cache saved: {path} ({size_kb:.0f} KB)")

def load_cache(year):
    path = get_cache_path(year)
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        cached = json.load(f)
    print(f"  📦 Cache loaded: {path}")
    print(f"     Fetched at: {cached['fetchedAt']}")
    return cached["data"]


# ============================================================
# DATA FETCHING
# ============================================================

def fetch_wb_indicator(indicator_code, year, fallback_range=2):
    """Fetch one indicator for all countries. Uses date range, picks closest year."""
    start_year = year - fallback_range
    end_year = year + fallback_range

    results = {}
    page = 1
    total_pages = 1

    while page <= total_pages:
        url = (
            f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}"
            f"?date={start_year}:{end_year}&format=json&per_page=1000&page={page}"
        )
        try:
            req = Request(url, headers={"User-Agent": "ApplesToApples/3.0"})
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            if not data or len(data) < 2 or not data[1]:
                break

            total_pages = data[0].get("pages", 1)

            for entry in data[1]:
                iso3 = entry.get("countryiso3code", "")
                value = entry.get("value")
                date_str = entry.get("date", "")

                if not iso3 or value is None:
                    continue
                try:
                    entry_year = int(date_str)
                except (ValueError, TypeError):
                    continue

                # Keep closest to target year
                if iso3 not in results:
                    results[iso3] = {"value": float(value), "year": entry_year}
                else:
                    if abs(entry_year - year) < abs(results[iso3]["year"] - year):
                        results[iso3] = {"value": float(value), "year": entry_year}

            page += 1
            time.sleep(0.25)

        except (HTTPError, URLError) as e:
            print(f"    ⚠️  Error: {e}")
            # Fallback: try mrv=5
            if page == 1:
                return fetch_wb_fallback(indicator_code, year, fallback_range)
            break
        except json.JSONDecodeError as e:
            print(f"    ⚠️  JSON error: {e}")
            break

    return results


def fetch_wb_fallback(indicator_code, year, fallback_range):
    """Fallback using mrv parameter."""
    url = (
        f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}"
        f"?mrv=5&format=json&per_page=1000"
    )
    results = {}
    page = 1
    total_pages = 1

    while page <= total_pages:
        page_url = f"{url}&page={page}"
        try:
            req = Request(page_url, headers={"User-Agent": "ApplesToApples/3.0"})
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            if not data or len(data) < 2 or not data[1]:
                break
            total_pages = data[0].get("pages", 1)

            for entry in data[1]:
                iso3 = entry.get("countryiso3code", "")
                value = entry.get("value")
                date_str = entry.get("date", "")
                if not iso3 or value is None:
                    continue
                try:
                    entry_year = int(date_str)
                except (ValueError, TypeError):
                    continue
                if abs(entry_year - year) > fallback_range:
                    continue
                if iso3 not in results or abs(entry_year - year) < abs(results[iso3]["year"] - year):
                    results[iso3] = {"value": float(value), "year": entry_year}

            page += 1
            time.sleep(0.25)
        except Exception as e:
            print(f"    ⚠️  Fallback error: {e}")
            break

    return results


def fetch_all_indicators(target_year, fallback_range):
    """Fetch all WB indicators."""
    all_data = {}
    wb_codes = {name: info[1] for name, info in WB_FIELD_MAP.items()}
    total = len(wb_codes)

    for i, (name, code) in enumerate(wb_codes.items(), 1):
        print(f"  [{i}/{total}] {name} ({code})...")
        data = fetch_wb_indicator(code, target_year, fallback_range)
        all_data[name] = data
        count = len(data)
        icon = "✅" if count > 100 else ("⚠️" if count > 0 else "❌")
        print(f"    {icon} {count} countries")

    return all_data


# ============================================================
# VALUE TRANSFORMATION
# ============================================================

def transform_value(field_name, raw_value, transform):
    """Apply unit conversion."""
    if raw_value is None:
        return None

    if transform == "div1e6":
        v = raw_value / 1_000_000
    elif transform == "div1e9":
        v = raw_value / 1_000_000_000
    elif transform == "div1e3":
        v = raw_value / 1_000
    else:  # "direct"
        v = raw_value

    # Format based on field
    if field_name in ("population",):
        return round(v, 1)  # 335.0 million
    elif field_name in ("gdpBillions", "exports", "fdiInflow"):
        return int(round(v, 0))  # 27360 billion
    elif field_name in ("gdpPerCapita",):
        return int(round(v, 0))  # 81695
    elif field_name in ("area",):
        return int(round(v, 0))  # 9833 thousand km²
    elif field_name in ("populationDensity",):
        return int(round(v, 0))  # 34 /km²
    elif field_name == "gini":
        return round(v, 1)
    elif field_name in ("lifeExpectancy", "birthRate", "deathRate",
                        "urbanization", "literacy", "manufacturing",
                        "forestCover", "renewableEnergy", "pm25",
                        "unemployment", "inflation", "rdExpenditure",
                        "militarySpending", "co2PerCapita", "doctors",
                        "hospitalBeds", "healthExpenditure"):
        return round(v, 1)
    else:
        return round(v, 1)


def format_value(v):
    """Format number for CSV output."""
    if v is None:
        return ""
    if isinstance(v, int):
        return str(v)
    if v == int(v):
        return str(int(v))
    return str(v)


# ============================================================
# DATA.JS PARSING & UPDATE
# ============================================================

def parse_data_js(filepath):
    """Parse data.js RAW lines."""
    import re
    with open(filepath, 'r') as f:
        content = f.read()

    match = re.search(r'const RAW = `(.*?)`', content, re.DOTALL)
    if not match:
        print("ERROR: Could not find RAW template literal")
        sys.exit(1)

    raw_text = match.group(1).strip()
    regions = []

    for line in raw_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('//'):
            continue
        parts = line.split(',')
        if len(parts) >= 5:
            regions.append({
                "raw": line,
                "id": parts[0].strip(),
                "name": parts[1].strip() if len(parts) > 1 else "",
                "type": parts[2].strip() if len(parts) > 2 else "",
                "parts": parts,
                "num_fields": len(parts)
            })

    return regions, content


def update_countries(regions, all_data, target_year):
    """Update country data with WB values. Returns changes."""
    changes = []
    updated_ids = set()

    for reg in regions:
        if reg["type"] != "country":
            continue

        iso3 = REGION_TO_ISO3.get(reg["id"])
        if not iso3:
            continue

        parts = reg["parts"][:]
        changed = False

        for field_name, (field_idx, wb_code, transform) in WB_FIELD_MAP.items():
            if field_name not in all_data:
                continue

            wb_entry = all_data[field_name].get(iso3)
            if not wb_entry:
                continue

            new_val = transform_value(field_name, wb_entry["value"], transform)
            if new_val is None:
                continue

            # Ensure list is long enough
            while len(parts) <= field_idx:
                parts.append("")

            old_str = parts[field_idx].strip()
            new_str = format_value(new_val)

            # Skip if same value
            if old_str == new_str:
                continue

            # Sanity check: reject obviously wrong changes
            # e.g., US population shouldn't jump from 335 to 33500
            if old_str:
                try:
                    old_num = float(old_str)
                    if old_num != 0 and abs(new_val / old_num) > 100:
                        print(f"    ⚠️  SKIP {reg['id']}.{field_name}: "
                              f"{old_str} → {new_str} (>100x change, likely unit mismatch)")
                        continue
                except ValueError:
                    pass

            changes.append({
                "region": reg["id"],
                "field": field_name,
                "idx": field_idx,
                "old": old_str,
                "new": new_str,
                "year": wb_entry["year"],
            })
            parts[field_idx] = new_str
            changed = True

        if changed:
            reg["parts"] = parts
            reg["raw"] = ",".join(parts)
            updated_ids.add(reg["id"])

    return changes, len(updated_ids)


def write_data_js(filepath, content, regions, target_year):
    """Write updated data.js."""
    import re
    new_raw = "\n".join(r["raw"] for r in regions)

    content = re.sub(
        r'(const RAW = `\s*\n?)(.*?)(\n?\s*`\.trim\(\);)',
        lambda m: m.group(1) + new_raw + m.group(3),
        content,
        flags=re.DOTALL
    )

    # Update comment
    content = re.sub(
        r'// Sources:.*',
        f'// Sources: World Bank API (country data unified to {target_year}), national statistics bureaus',
        content,
        count=1
    )

    with open(filepath, 'w') as f:
        f.write(content)


# ============================================================
# REPORTING
# ============================================================

def print_report(all_data, target_year):
    print(f"\n{'='*60}")
    print(f"DATA QUALITY REPORT — Target Year: {target_year}")
    print(f"{'='*60}\n")

    for name in sorted(all_data.keys()):
        cdata = all_data[name]
        if not cdata:
            print(f"  ❌ {name}: NO DATA")
            continue
        years = [d["year"] for d in cdata.values()]
        on_target = sum(1 for y in years if y == target_year)
        yc = Counter(years)
        ys = ", ".join(f"{y}:{c}" for y, c in sorted(yc.items()))
        icon = "✅" if on_target > len(years) * 0.5 else "⚠️"
        print(f"  {icon} {name}: {len(years)} countries, {on_target} on target | {ys}")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Apples to Apples Data Pipeline v3")
    parser.add_argument("--year", type=int, default=2022)
    parser.add_argument("--fallback", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--cache", action="store_true", help="Use cached data (no API)")
    parser.add_argument("--refresh", action="store_true", help="Force re-fetch")
    parser.add_argument("--data-file", type=str,
                        default=os.path.expanduser("~/Desktop/apples-to-apples/src/data.js"))
    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════╗
║  🍎 Apples to Apples — Data Pipeline v3             ║
║  Target Year: {args.year}                               ║
║  Fallback: ±{args.fallback} years                            ║
║  Mode: {'CACHE' if args.cache else 'REFRESH' if args.refresh else 'AUTO'}{'  (dry run)' if args.dry_run else ''}                           ║
╚══════════════════════════════════════════════════════╝
""")

    # 1. Get data (cache or fetch)
    all_data = None
    if not args.refresh:
        all_data = load_cache(args.year)

    if all_data is None:
        if args.cache:
            print("  ❌ No cache found. Run without --cache first.")
            sys.exit(1)
        print("📡 Fetching from World Bank API...\n")
        all_data = fetch_all_indicators(args.year, args.fallback)
        save_cache(all_data, args.year)
    else:
        print("  Using cached data (add --refresh to re-fetch)\n")

    print_report(all_data, args.year)

    # 2. Parse data.js
    print(f"\n📂 Parsing {args.data_file}...")
    if not os.path.exists(args.data_file):
        print(f"  ❌ Not found: {args.data_file}")
        sys.exit(1)

    regions, content = parse_data_js(args.data_file)
    countries = [r for r in regions if r["type"] == "country"]
    sub = [r for r in regions if r["type"] != "country"]
    print(f"  {len(regions)} regions: {len(countries)} countries, {len(sub)} subnational")

    # 3. Update
    print(f"\n🔄 Updating countries to {args.year}...")
    changes, num_updated = update_countries(regions, all_data, args.year)
    print(f"\n  ✅ {num_updated} countries updated, {len(changes)} field changes")

    if changes:
        print(f"\n  Changes (first 30):")
        for ch in changes[:30]:
            print(f"    {ch['region']:6s} | {ch['field']:20s} | "
                  f"{ch['old']:>12s} → {ch['new']:>12s}  (yr:{ch['year']})")
        if len(changes) > 30:
            print(f"    ... and {len(changes) - 30} more")

    # 4. Write
    if args.dry_run:
        print(f"\n🔍 DRY RUN — no files modified")
    else:
        print(f"\n💾 Writing...")
        write_data_js(args.data_file, content, regions, args.year)
        print(f"  ✅ data.js updated")

        # Metadata
        meta = {
            "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            "targetYear": args.year,
            "source": "World Bank API v2",
            "fieldsUpdated": list(WB_FIELD_MAP.keys()),
            "fieldsSkipped": ["hdi (UNDP)", "pisaScore (OECD)", "universities (manual)", "medianAge (UN)"],
            "indicators": {}
        }
        for name, cdata in all_data.items():
            if cdata:
                years = [d["year"] for d in cdata.values()]
                meta["indicators"][name] = {
                    "coverage": len(cdata),
                    "primaryYear": Counter(years).most_common(1)[0][0]
                }
        meta_path = os.path.join(os.path.dirname(args.data_file), "data_metadata.json")
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        print(f"  ✅ Metadata: {meta_path}")

        # Changelog
        log_path = os.path.join(os.path.dirname(args.data_file), "data_changelog.json")
        with open(log_path, 'w') as f:
            json.dump({
                "date": time.strftime("%Y-%m-%d"),
                "targetYear": args.year,
                "updated": num_updated,
                "totalChanges": len(changes),
                "changes": changes
            }, f, indent=2)
        print(f"  ✅ Changelog: {log_path}")

    print(f"""
╔══════════════════════════════════════════════════════╗
║  ✅ Pipeline complete                                ║
║  Countries: {num_updated:>3} updated                            ║
║  Changes:  {len(changes):>4} fields                            ║
║  Year:     {args.year}                                  ║
║  Cache:    pipeline/cache/wb_data_{args.year}.json       ║
║                                                      ║
║  Next: cd ~/Desktop/apples-to-apples                 ║
║        npm run build && npx gh-pages -d dist         ║
╚══════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
