#!/bin/bash
# Apples to Apples — Data Pipeline v3
#
# Usage:
#   bash run_pipeline.sh              # Fetch + update + build (year 2022)
#   bash run_pipeline.sh 2023         # Different year
#   bash run_pipeline.sh 2022 --dry-run   # Preview only
#   bash run_pipeline.sh 2022 --cache     # Use cached data (instant)
#   bash run_pipeline.sh 2022 --refresh   # Force re-fetch

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
YEAR=${1:-2022}
shift 2>/dev/null || true
EXTRA_ARGS="$@"

echo ""
echo "🍎 Apples to Apples — Data Pipeline v3"
echo "========================================="
echo "  Target year: $YEAR"
echo "  Args: $EXTRA_ARGS"
echo ""

# Step 1: Fetch & update data.js
cd "$SCRIPT_DIR"
python3 fetch_data.py --year "$YEAR" $EXTRA_ARGS

# Check if dry-run
if echo "$EXTRA_ARGS" | grep -q "dry-run"; then
    exit 0
fi

# Step 2: Update disclaimers
echo "📝 Updating disclaimers..."
COMPARE=~/Desktop/apples-to-apples/src/pages/Compare.jsx
HOME_PAGE=~/Desktop/apples-to-apples/src/pages/Home.jsx

# Update Compare disclaimer (try multiple possible strings)
python3 -c "
import sys
for filepath in ['$COMPARE', '$HOME_PAGE']:
    try:
        with open(filepath, 'r') as f:
            code = f.read()

        # Replace various disclaimer patterns
        for old in [
            'Data approximate, primarily 2022–2023',
            'Data approximate, primarily 2022-2023',
            'Country data unified to',
        ]:
            if old in code:
                start = code.index(old)
                # Find end of the string (next quote)
                end = code.index(\"'\", start) if \"'\" in code[start:start+200] else code.index('\"', start)
                old_text = code[start:end]
                new_text = 'Country data unified to $YEAR via World Bank API. Subnational data from 2021–2023. For reference only.'
                code = code.replace(old_text, new_text)
                break

        with open(filepath, 'w') as f:
            f.write(code)
        print(f'  ✅ {filepath}')
    except Exception as e:
        print(f'  ⚠️  {filepath}: {e}')
"

# Step 3: Build
echo ""
echo "🔨 Building..."
cd ~/Desktop/apples-to-apples
npm run build

echo ""
echo "✅ Done! Data unified to $YEAR."
echo "   Deploy: npx gh-pages -d dist"
