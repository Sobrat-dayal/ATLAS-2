/**
 * ATLAS Financial Risk Foundation — Frontend Unit Tests (Stage 115).
 *
 * Verifies:
 * 1. Financial formatting functions (Vol, Signed %, Weight, Bps, Ratio, Days).
 * 2. Status badge configurations and institutional theme classes.
 * 3. Part XV Reference Mathematical Fixture (Alternating returns annualized vol).
 * 4. Part XXI Reference Drawdown Fixture (Peak, Trough, Max Drawdown, Recovery).
 * 5. Part XXXV & XL Euler Risk Decomposition Reconciliation.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  formatBps,
  formatDate,
  formatDays,
  formatRatio,
  formatSignedPercent,
  formatVolPercent,
  formatWeight,
  getCalculationStatusBadge,
  getDataCoverageBadge,
  getDrawdownEpisodeBadge,
  getFrequencyLabel,
  getModelTypeLabel,
} from '../formatting';

describe('Stage 115: Financial Risk Foundation Frontend Tests', () => {
  it('formats volatility percentages cleanly and handles edge cases', () => {
    assert.strictEqual(formatVolPercent(0.183303), '18.33%');
    assert.strictEqual(formatVolPercent(0.183303, 4), '18.3303%');
    assert.strictEqual(formatVolPercent(0.0), '0.00%');
    assert.strictEqual(formatVolPercent(null), '—');
    assert.strictEqual(formatVolPercent(undefined), '—');
    assert.strictEqual(formatVolPercent(NaN), '—');
  });

  it('formats signed returns and drawdown percentages with sign preservation', () => {
    assert.strictEqual(formatSignedPercent(-0.25), '-25.00%');
    assert.strictEqual(formatSignedPercent(0.085), '+8.50%');
    assert.strictEqual(formatSignedPercent(0.0), '0.00%');
    assert.strictEqual(formatSignedPercent(null), '—');
  });

  it('formats allocation weights and basis points correctly', () => {
    assert.strictEqual(formatWeight(0.5), '50.00%');
    assert.strictEqual(formatWeight(0.307692, 4), '30.7692%');
    assert.strictEqual(formatWeight(null), '0.00%');

    assert.strictEqual(formatBps(0.0125), '125 bps');
    assert.strictEqual(formatBps(0.0004), '4 bps');
    assert.strictEqual(formatBps(null), '—');
  });

  it('formats numerical ratios and durations', () => {
    assert.strictEqual(formatRatio(1.0542, 2), '1.05');
    assert.strictEqual(formatRatio(12.456, 1), '12.5');
    assert.strictEqual(formatRatio(null), '—');

    assert.strictEqual(formatDays(42), '42 days');
    assert.strictEqual(formatDays(1), '1 day');
    assert.strictEqual(formatDays(null), '—');
    assert.strictEqual(formatDate('2026-03-31T16:00:00Z'), '2026-03-31');
  });

  it('returns valid badge configurations for status indicators', () => {
    const calcBadge = getCalculationStatusBadge('COMPLETED');
    assert.strictEqual(calcBadge.label, 'Calculated');
    assert.ok(calcBadge.textClass.includes('emerald'));

    const covBadge = getDataCoverageBadge('FULL');
    assert.strictEqual(covBadge.label, '100% Coverage');

    const ddBadge = getDrawdownEpisodeBadge('RECOVERED');
    assert.strictEqual(ddBadge.label, 'Recovered');

    const ongoingBadge = getDrawdownEpisodeBadge('ONGOING');
    assert.strictEqual(ongoingBadge.label, 'Under Water');
  });

  it('provides friendly labels for model types and frequencies', () => {
    assert.strictEqual(getModelTypeLabel('COVARIANCE_PARAMETRIC'), 'Covariance Parametric (Euler)');
    assert.strictEqual(getModelTypeLabel('HISTORICAL_SAMPLE'), 'Historical Sample');
    assert.strictEqual(getFrequencyLabel('DAILY'), 'Daily (252x)');
  });

  it('reconciles Part XV Reference Fixture: alternating returns volatility', () => {
    // 4 returns: [+1%, -1%, +1%, -1%]
    const returns = [0.01, -0.01, 0.01, -0.01];
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
    assert.strictEqual(mean, 0.0);

    const sumSq = returns.reduce((acc, r) => acc + Math.pow(r - mean, 2), 0);
    const sampleVariance = sumSq / (returns.length - 1); // 0.0004 / 3
    const periodVol = Math.sqrt(sampleVariance);
    const annualizedVol = periodVol * Math.sqrt(252);

    assert.strictEqual(formatVolPercent(annualizedVol, 4), '18.3303%');
  });

  it('reconciles Part XXI Reference Fixture: drawdown series, max drawdown, and recovery', () => {
    // Wealth index: [100, 120, 90, 99, 130]
    const wealthIndex = [100, 120, 90, 99, 130];
    let peak = wealthIndex[0];
    const drawdowns: number[] = [];

    for (const w of wealthIndex) {
      if (w > peak) peak = w;
      drawdowns.push(w / peak - 1.0);
    }

    assert.strictEqual(drawdowns[0], 0);
    assert.strictEqual(drawdowns[1], 0);
    assert.strictEqual(drawdowns[2], -0.25); // 90 / 120 - 1 = -25%
    assert.ok(Math.abs(drawdowns[3] - (-0.175)) < 1e-9); // 99 / 120 - 1 = -17.5%
    assert.strictEqual(drawdowns[4], 0); // 130 > 120 -> new peak

    const maxDrawdown = Math.min(...drawdowns);
    assert.strictEqual(maxDrawdown, -0.25);
    assert.strictEqual(formatSignedPercent(maxDrawdown), '-25.00%');
  });

  it('reconciles Part XXXV & XL Reference Fixture: Euler risk decomposition additivity', () => {
    // 2 uncorrelated assets: var1 = 0.04 (vol 20%), var2 = 0.09 (vol 30%)
    // weights: w1 = 0.5, w2 = 0.5
    const w1 = 0.5;
    const w2 = 0.5;
    const var1 = 0.04;
    const var2 = 0.09;

    const portVariance = Math.pow(w1, 2) * var1 + Math.pow(w2, 2) * var2; // 0.25*0.04 + 0.25*0.09 = 0.01 + 0.0225 = 0.0325
    assert.strictEqual(portVariance, 0.0325);

    const portVol = Math.sqrt(portVariance); // ~0.18027756

    // Marginal Volatilities: (Sigma * w) / portVol
    const mvc1 = (var1 * w1) / portVol;
    const mvc2 = (var2 * w2) / portVol;

    // Component Volatilities: w_i * mvc_i
    const cvc1 = w1 * mvc1;
    const cvc2 = w2 * mvc2;

    // Euler identity: cvc1 + cvc2 === portVol
    const sumCvc = cvc1 + cvc2;
    assert.ok(Math.abs(sumCvc - portVol) < 1e-9);

    // Percentage contribution: cvc_i / portVol
    const pcr1 = cvc1 / portVol;
    const pcr2 = cvc2 / portVol;
    assert.ok(Math.abs(pcr1 + pcr2 - 1.0) < 1e-9);

    assert.strictEqual(formatWeight(pcr1, 4), '30.7692%');
    assert.strictEqual(formatWeight(pcr2, 4), '69.2308%');
  });
});
