#!/bin/bash
# Adds 142 Chinese prefecture-level cities to Apples to Apples
# Run: bash add-cn-cities.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_FILE=~/Desktop/apples-to-apples/src/data.js

echo "🇨🇳 Adding 142 Chinese cities to Apples to Apples..."

# Combine all city files
cat "$SCRIPT_DIR"/cn_cities_*.txt | sed '/^$/d' > "$SCRIPT_DIR/all_cn_cities.txt"
TOTAL=$(wc -l < "$SCRIPT_DIR/all_cn_cities.txt")
echo "   Found $TOTAL cities to add"

# Check if data.js has 35 fields (new indicators already applied) or 27 (old)
SAMPLE_FIELDS=$(grep "^us," "$DATA_FILE" | head -1 | awk -F',' '{print NF}')
echo "   Current field count: $SAMPLE_FIELDS"

if [ "$SAMPLE_FIELDS" -eq 27 ]; then
    echo ""
    echo "⚠️  ERROR: You need to run the data-expansion patch first!"
    echo "   The 8 new indicators (unemployment, inflation, etc.) must be"
    echo "   added before the city data, since cities include those fields."
    echo ""
    echo "   Run: cd ~/Desktop/expansion && bash run.sh"
    echo "   Then run this script again."
    exit 1
fi

# Insert city data before closing backtick
python3 -c "
import os
data_file = os.path.expanduser('~/Desktop/apples-to-apples/src/data.js')
cities_file = os.path.join('$SCRIPT_DIR', 'all_cn_cities.txt')

with open(data_file, 'r') as f:
    content = f.read()

with open(cities_file, 'r') as f:
    cities = f.read().strip()

# Insert before closing backtick
content = content.replace('\`.trim();', cities + '\n\`.trim();')

# Update region count comment
import re
content = re.sub(r'// \d+ regions', '// 520+ regions', content, count=1)

# Add China-focused showcase groups
old_end = '];'  # end of SHOWCASE_GROUPS
# We need to find the SHOWCASE_GROUPS and add entries
if 'China Deep Dive' not in content:
    content = content.replace(
        \"  { title: 'Healthcare Excellence'\",
        \"\"\"  { title: 'China: Economic Powerhouses', subtitle: 'Top GDP cities', ids: ['cn-sz', 'cn-gz2', 'cn-su', 'cn-cd'] },
  { title: 'China: Western Development', subtitle: 'Go West strategy', ids: ['cn-cd', 'cn-km', 'cn-gy', 'cn-ls'] },
  { title: 'China: Tech Hubs', subtitle: 'Innovation cities', ids: ['cn-sz', 'cn-hz', 'cn-hf', 'cn-wh'] },
  { title: 'China: Ancient Capitals', subtitle: 'Historic cities', ids: ['cn-nj', 'cn-xm', 'cn-jn', 'cn-cs'] },
  { title: 'Healthcare Excellence'\"\"\"
    )

with open(data_file, 'w') as f:
    f.write(content)

print(f'  ✅ Added {len(cities.splitlines())} Chinese cities')
"

echo ""
echo "🔨 Rebuilding..."
cd ~/Desktop/apples-to-apples
npm run build

echo ""
echo "✅ Done! 142 Chinese cities added, covering:"
echo "   📍 All 4 直辖市 capital cities"
echo "   📍 All 26 省会/自治区首府"
echo "   📍 5 计划单列市 (深圳、大连、青岛、宁波、厦门)"
echo "   📍 ~105 地级市 across all provinces"
echo "   📍 From Kashgar in the west to Shanghai in the east"
echo "   📍 From Harbin in the north to Beihai in the south"
echo ""
echo "Total regions now: ~520+"
echo "Run 'npm run dev' to preview, or 'npx gh-pages -d dist' to deploy."
