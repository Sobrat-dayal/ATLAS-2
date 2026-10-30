/**
 * Frontend Unit Tests for Portfolio Allocation, Exposure & Concentration (Stage 112).
 */

import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  formatBps,
  formatHhi,
  formatMonetaryValue,
  formatWeightPct,
  getCompletenessBadge,
  getHhiConcentrationLevel,
  getLookThroughStatusBadge,
} from '../formatting';

test('Stage 112: formatWeightPct formats fractional decimal weights into percentage strings', () => {
  assert.equal(formatWeightPct('0.500000'), '50.00%');
  assert.equal(formatWeightPct(0.25), '25.00%');
  assert.equal(formatWeightPct('0.0725'), '7.25%');
  assert.equal(formatWeightPct(1.0), '100.00%');
  assert.equal(formatWeightPct(0), '0.00%');
  assert.equal(formatWeightPct(null), '—');
  assert.equal(formatWeightPct(undefined), '—');
  assert.equal(formatWeightPct('invalid'), '—');
});

test('Stage 112: formatMonetaryValue formats monetary numbers with appropriate currency symbols', () => {
  assert.equal(formatMonetaryValue('20000.00', 'USD'), '$20,000.00');
  assert.equal(formatMonetaryValue(5000, 'USD'), '$5,000.00');
  assert.equal(formatMonetaryValue(null), '—');
  assert.equal(formatMonetaryValue(undefined), '—');
});

test('Stage 112: formatBps formats basis points with signs', () => {
  assert.equal(formatBps(50), '+50 bps');
  assert.equal(formatBps(-25), '-25 bps');
  assert.equal(formatBps(0), '0 bps');
  assert.equal(formatBps(null), '—');
});

test('Stage 112: formatHhi formats raw decimal HHI and conventional index correctly', () => {
  assert.equal(formatHhi('0.375000'), '3,750');
  assert.equal(formatHhi(3750), '3,750');
  assert.equal(formatHhi(null), '—');
});

test('Stage 112: getHhiConcentrationLevel classifies diversification regimes', () => {
  assert.equal(getHhiConcentrationLevel(0.12).label, 'Diversified');
  assert.equal(getHhiConcentrationLevel(0.18).label, 'Moderately Concentrated');
  assert.equal(getHhiConcentrationLevel(0.375).label, 'Highly Concentrated');
});

test('Stage 112: getCompletenessBadge and getLookThroughStatusBadge return correct styles', () => {
  assert.equal(getCompletenessBadge('COMPLETE').variant, 'emerald');
  assert.equal(getCompletenessBadge('PARTIAL_VALUATION').variant, 'rose');
  assert.equal(getLookThroughStatusBadge('FULL_LOOK_THROUGH').variant, 'emerald');
  assert.equal(getLookThroughStatusBadge('UNSUPPORTED').variant, 'muted');
});

test('Stage 112: Part X Fixture math partitions $20,000 NAV into 75% Equity and 25% Cash', () => {
  const totalNav = 20000;
  const techValue = 10000;
  const finValue = 5000;
  const cashValue = 5000;

  const techWeight = techValue / totalNav;
  const finWeight = finValue / totalNav;
  const cashWeight = cashValue / totalNav;

  assert.equal(techWeight, 0.5);
  assert.equal(finWeight, 0.25);
  assert.equal(cashWeight, 0.25);
  assert.equal(techWeight + finWeight + cashWeight, 1.0);

  const equityWeight = (techValue + finValue) / totalNav;
  assert.equal(equityWeight, 0.75);
});

test('Stage 112: Part XXVIII Concentration Fixture math: 50%, 25%, 25% yields HHI = 0.375 and N_eff ≈ 2.67', () => {
  const weights = [0.5, 0.25, 0.25];
  const hhi = weights.reduce((acc, w) => acc + w * w, 0);
  assert.equal(hhi, 0.375);

  const conventionalHhi = hhi * 10000;
  assert.equal(conventionalHhi, 3750);

  const nEff = 1 / hhi;
  assert.equal(Math.round(nEff * 100) / 100, 2.67);
});

test('Stage 112: Part XXXII Look-Through Fixture math: $2,000 ETF with 60% Sec A, 30% Sec B, 10% Residual', () => {
  const fundNav = 2000;
  const secAWeight = 0.6;
  const secBWeight = 0.3;
  const residualWeight = 0.1;

  const secAValue = fundNav * secAWeight;
  const secBValue = fundNav * secBWeight;
  const residualValue = fundNav * residualWeight;

  assert.equal(secAValue, 1200);
  assert.equal(secBValue, 600);
  assert.equal(residualValue, 200);
  assert.equal(secAValue + secBValue + residualValue, 2000);
});
