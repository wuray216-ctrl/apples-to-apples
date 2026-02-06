# 🍎 Apples to Apples

**Compare regions that are actually comparable.**

Comparing Georgia (3.7M people) to China (1.4B people) doesn't make sense. But Zhejiang, California, and Bavaria? Now you're comparing apples to apples.

🌐 **Live Demo**: https://yourusername.github.io/apples-to-apples

## Features

- **150+ Regions** — 70+ countries, all 31 Chinese provinces, all 50 US states, major metro areas
- **18 Indicators** across 5 categories:
  - 📊 **Basic**: Population, GDP, GDP/capita, Area, Urbanization, HDI, Internet
  - 💰 **Economic**: GDP, GDP/capita, Gini, Manufacturing %, Exports, FDI
  - 🎓 **Education**: Universities, Literacy Rate, PISA Score
  - 🏥 **Healthcare**: Life Expectancy, Doctors/1000, Hospital Beds, Health Spending
  - 🌿 **Environment**: CO₂/capita, Forest Coverage, PM2.5, Renewable Energy
- **Smart Matching** — Find the most similar regions based on weighted multi-dimensional similarity
- **Rich Visualizations** — Bar charts, radar charts, scatter plots
- **100% Static** — No backend needed, deploys free on GitHub Pages

## Data Sources

- World Bank Open Data
- UN Human Development Reports
- WHO Global Health Observatory
- UNESCO Institute for Statistics
- IEA Energy Statistics
- National Statistics Bureaus (China NBS, US Census, Eurostat)

Data is from 2023 where available.

## Quick Start

### Local Development

```bash
npm install
npm run dev
```

Open http://localhost:5173

### Build for Production

```bash
npm run build
```

Output is in `dist/` folder.

## Deploy to GitHub Pages

### Option 1: Using gh-pages (Recommended)

1. **Create a GitHub repo** named `apples-to-apples`

2. **Update vite.config.js** with your repo name:
   ```js
   base: '/apples-to-apples/'
   ```

3. **Push your code**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/apples-to-apples.git
   git push -u origin main
   ```

4. **Deploy**:
   ```bash
   npm run deploy
   ```

5. **Enable GitHub Pages**:
   - Go to repo Settings → Pages
   - Source: Deploy from branch
   - Branch: `gh-pages` / `/ (root)`
   - Save

Your site will be live at `https://YOUR_USERNAME.github.io/apples-to-apples`

### Option 2: GitHub Actions (Auto-deploy on push)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- Recharts
- React Router (HashRouter for GitHub Pages)

## Project Structure

```
src/
├── data.js          # All regions data + constants
├── matching.js      # Similarity algorithm
├── components/
│   ├── SearchInput.jsx
│   ├── IndicatorBar.jsx
│   └── ScoreBar.jsx
└── pages/
    ├── Home.jsx
    └── Compare.jsx
```

## License

MIT

## Contributing

PRs welcome! Especially for:
- More regions (provinces of other countries)
- More indicators
- Data corrections
- Translations
