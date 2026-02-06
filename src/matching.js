// Smart matching engine - runs entirely in browser
import { REGIONS, INDICATOR_KEYS, MATCH_PRESETS } from './data';

// Compute normalization params once (lazy)
let NORM_PARAMS = null;

function computeNormParams() {
  if (NORM_PARAMS) return NORM_PARAMS;
  const params = {};
  for (const key of INDICATOR_KEYS) {
    const values = REGIONS.map(r => r[key]).filter(v => v != null && !isNaN(v));
    if (values.length) {
      params[key] = { min: Math.min(...values), max: Math.max(...values) };
    } else {
      params[key] = { min: 0, max: 1 };
    }
  }
  NORM_PARAMS = params;
  return params;
}

function normalize(value, min, max) {
  if (max === min) return 0.5;
  return (value - min) / (max - min);
}

function computeSimilarity(source, target, weights) {
  const params = computeNormParams();
  let totalWeight = 0;
  let totalScore = 0;

  for (const key of INDICATOR_KEYS) {
    const w = weights[key] || 0;
    if (w <= 0) continue;

    const sVal = source[key];
    const tVal = target[key];
    if (sVal == null || tVal == null || isNaN(sVal) || isNaN(tVal)) continue;

    const { min, max } = params[key];
    const sNorm = normalize(sVal, min, max);
    const tNorm = normalize(tVal, min, max);

    const distance = Math.abs(sNorm - tNorm);
    totalScore += w * (1 - distance);
    totalWeight += w;
  }

  if (totalWeight === 0) return 0;
  return Math.round((totalScore / totalWeight) * 1000) / 10; // One decimal
}

export function findMatches(sourceId, preset = 'comprehensive', customWeights = null, limit = 20) {
  const source = REGIONS.find(r => r.id === sourceId);
  if (!source) return [];

  const weights = customWeights || MATCH_PRESETS[preset]?.weights || MATCH_PRESETS.comprehensive.weights;

  const results = [];
  for (const region of REGIONS) {
    if (region.id === sourceId) continue;
    const score = computeSimilarity(source, region, weights);
    results.push({ ...region, score });
  }

  results.sort((a, b) => b.score - a.score);
  return results.slice(0, limit);
}

export function getRegion(id) {
  return REGIONS.find(r => r.id === id);
}

export function searchRegions(query) {
  if (!query?.trim()) return REGIONS.slice(0, 15);
  const q = query.toLowerCase();
  return REGIONS.filter(r => r.name.toLowerCase().includes(q)).slice(0, 15);
}

export function filterRegions({ type, parent, query }) {
  let results = REGIONS;
  if (type) results = results.filter(r => r.type === type);
  if (parent) results = results.filter(r => r.parent === parent);
  if (query) {
    const q = query.toLowerCase();
    results = results.filter(r => r.name.toLowerCase().includes(q));
  }
  return results;
}

export function aggregateRegions(componentIds, name) {
  const components = REGIONS.filter(r => componentIds.includes(r.id));
  if (!components.length) return null;

  const totalPop = components.reduce((sum, r) => sum + (r.population || 0), 0);
  const totalGdp = components.reduce((sum, r) => sum + (r.gdp || 0), 0);
  const totalArea = components.reduce((sum, r) => sum + (r.area || 0), 0);

  const weightedAvg = (key) => {
    const vals = components.filter(r => r[key] != null && r.population > 0);
    if (!vals.length) return null;
    const totalW = vals.reduce((sum, r) => sum + r.population, 0);
    return Math.round(vals.reduce((sum, r) => sum + r[key] * r.population, 0) / totalW * 100) / 100;
  };

  return {
    id: 'custom-' + componentIds.sort().join('-'),
    name,
    type: 'custom',
    parent: null,
    flag: '🔷',
    population: totalPop,
    gdp: totalGdp,
    gdpPerCapita: totalPop > 0 ? Math.round(totalGdp * 1000000 / totalPop) : null,
    area: totalArea,
    urbanization: weightedAvg('urbanization'),
    gini: weightedAvg('gini'),
    hdi: weightedAvg('hdi'),
    internetPenetration: weightedAvg('internetPenetration'),
    lifeExpectancy: weightedAvg('lifeExpectancy'),
    co2PerCapita: weightedAvg('co2PerCapita'),
  };
}
