#!/bin/bash
# Adds 73 new regions to data.js
# Run from anywhere: bash ~/Desktop/add-regions/add-regions.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_FILE=~/Desktop/apples-to-apples/src/data.js

echo "📊 Adding 73 new regions to Apples to Apples..."
echo ""

# Step 1: Insert new region data before the closing backtick of RAW
# Find the line with `.trim();` and insert new data before it
python3 -c "
import os

data_file = os.path.expanduser('~/Desktop/apples-to-apples/src/data.js')
new_regions_file = os.path.join('$SCRIPT_DIR', 'new_regions.txt')

with open(data_file, 'r') as f:
    content = f.read()

with open(new_regions_file, 'r') as f:
    new_data = f.read().strip()

# Insert before the closing backtick+.trim()
old = '\`.trim();'
new_insert = new_data + '\n\`.trim();'
content = content.replace(old, new_insert)

# Update SHOWCASE_GROUPS to include new regions
old_showcase = '''export const SHOWCASE_GROUPS = [
  { title: 'Industrial Powerhouses', subtitle: 'Manufacturing giants', ids: ['de-by', 'cn-zj', 'us-tx'] },
  { title: 'City-States & Hubs', subtitle: 'Financial centers', ids: ['sg', 'kr-sl', 'cn-sh'] },
  { title: 'Tech & Innovation', subtitle: 'Silicon Valleys', ids: ['us-ca', 'gb-ln', 'cn-js'] },
  { title: 'Emerging Economies', subtitle: 'Rising powers', ids: ['in-mh', 'br-sp', 'vn'] },
  { title: 'Small but Mighty', subtitle: 'High GDP/capita', ids: ['nl', 'ch', 'us-ma'] },
  { title: 'Population Giants', subtitle: '100M+ people', ids: ['cn-gd', 'us-ca', 'in-mh'] },
  { title: 'Green Leaders', subtitle: 'Renewable energy', ids: ['no', 'us-vt', 'cr'] },
  { title: 'Healthcare Excellence', subtitle: 'Best health', ids: ['jp', 'ch', 'es'] },
];'''

new_showcase = '''export const SHOWCASE_GROUPS = [
  { title: 'Industrial Powerhouses', subtitle: 'Manufacturing giants', ids: ['de-by', 'cn-zj', 'us-tx', 'jp-ai'] },
  { title: 'City-States & Hubs', subtitle: 'Financial centers', ids: ['sg', 'kr-sl', 'cn-sh', 'de-hh'] },
  { title: 'Tech & Innovation', subtitle: 'Silicon Valleys', ids: ['us-ca', 'gb-ln', 'cn-js', 'se-st'] },
  { title: 'Emerging Economies', subtitle: 'Rising powers', ids: ['in-mh', 'br-sp', 'vn', 'co'] },
  { title: 'Small but Mighty', subtitle: 'High GDP/capita', ids: ['nl', 'ch', 'us-ma', 'es-pv'] },
  { title: 'European Regions', subtitle: 'Cross-border comparison', ids: ['de-bw', 'fr-ra', 'it-lm', 'es-ct'] },
  { title: 'Global Capitals', subtitle: 'Metro areas', ids: ['jp-tk', 'gb-ln', 'fr-pr', 'ru-ms'] },
  { title: 'Canadian Provinces', subtitle: 'North American diversity', ids: ['ca-on', 'ca-bc', 'ca-ab', 'ca-qc'] },
  { title: 'Green Leaders', subtitle: 'Renewable energy', ids: ['no', 'us-vt', 'cr', 'ca-qc'] },
  { title: 'Healthcare Excellence', subtitle: 'Best health outcomes', ids: ['jp', 'ch', 'es', 'it-lm'] },
];'''

content = content.replace(old_showcase, new_showcase)

# Update comment at top
content = content.replace('// 250+ regions, 18 indicators', '// 320+ regions, 22 indicators')

with open(data_file, 'w') as f:
    f.write(content)

print('  ✅ data.js updated successfully')
"

# Step 2: Rebuild and deploy
echo ""
echo "🔨 Rebuilding..."
cd ~/Desktop/apples-to-apples
npm run build

echo ""
echo "✅ Done! New regions added:"
echo "   🇩🇪 13 German states (full coverage)"
echo "   🇫🇷 7 French regions"
echo "   🇮🇹 7 Italian regions"
echo "   🇪🇸 5 Spanish communities"
echo "   🇬🇧 5 UK nations/cities"
echo "   🇯🇵 4 Japanese prefectures"
echo "   🇨🇦 7 Canadian provinces"
echo "   🇳🇱 2 Dutch provinces"
echo "   🇸🇪 1 Swedish region"
echo "   🇷🇺 3 Russian regions"
echo "   🇵🇱🇨🇿🇭🇺🇷🇴🇦🇹 5 European capitals"
echo "   🇨🇱🇨🇴🇵🇪🇪🇨🇺🇾🇵🇦🇨🇷 7 Latin American countries"
echo "   🇵🇰🇧🇩🇪🇹🇰🇪🇬🇭🇹🇿 6 developing nations"
echo ""
echo "Run 'npm run dev' to preview, or 'npx gh-pages -d dist' to deploy."
