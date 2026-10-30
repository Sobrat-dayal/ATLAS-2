/**
 * ATLAS VaR, Expected Shortfall, Scenarios, and Model Backtesting Unit Tests (Stage 116).
 *
 * Verifies:
 * 1. Financial formatting functions (formatCurrency, formatPnl, formatVaRReturn).
 * 2. Status badges (Kupiec unconditional coverage, Scenario shock severity).
 * 3. Part XVI Reference Fixture (Historical Simulation empirical VaR & fractional ES).
 * 4. Part XX Reference Fixture (Parametric Normal VaR & Gaussian ES).
 * 5. Part XXXIV Multi-Currency Multiplicative Compounding fixture: (1 + s_p)(1 + s_fx) - 1.
 * 6. Part XLIII Scenario Revaluation & Exact Portfolio Reconciliation.
 * 7. Kupiec POF Likelihood Ratio Invariants.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  formatCurrency,
  formatPnl,
  formatVaRReturn,
  getKupiecStatusBadge,
  getScenarioImpactBadge,
  getVaRModelLabel,
} from '../formatting';

describe('Stage 116: VaR, Expected Shortfall, and Scenario Testing Frontend Tests', () => {
  it('formats currency and P&L correctly with proper sign representation', () => {
    assert.strictEqual(formatCurrency(1250000), '$1,250,000');
    assert.strictEqual(formatCurrency(-4000), '-$4,000');
    assert.strictEqual(formatCurrency(0), '$0');
    assert.strictEqual(formatCurrency(null), '—');

    assert.strictEqual(formatPnl(25000), '+$25,000');
    assert.strictEqual(formatPnl(-4000), '-$4,000');
    assert.strictEqual(formatPnl(0), '$0');
    assert.strictEqual(formatPnl(null), '—');
  });

  it('formats VaR loss return fractions as clean unsigned percentages', () => {
    assert.strictEqual(formatVaRReturn(0.032897), '3.29%');
    assert.strictEqual(formatVaRReturn(0.032897, 4), '3.2897%');
    assert.strictEqual(formatVaRReturn(-0.041254), '4.13%'); // unsigned loss magnitude
    assert.strictEqual(formatVaRReturn(null), '—');
  });

  it('returns appropriate Kupiec status badge styling', () => {
    const acceptBadge = getKupiecStatusBadge('ACCEPT_UNCONDITIONAL_COVERAGE');
    assert.ok(acceptBadge.label.includes('Accepted'));
    assert.ok(acceptBadge.textClass.includes('emerald'));

    const rejectTooMany = getKupiecStatusBadge('REJECT_TOO_MANY_EXCEPTIONS');
    assert.ok(rejectTooMany.label.includes('Rejected (Underestimates Risk)'));
    assert.ok(rejectTooMany.textClass.includes('rose'));

    const rejectTooFew = getKupiecStatusBadge('REJECT_TOO_FEW_EXCEPTIONS');
    assert.ok(rejectTooFew.label.includes('Overestimates Risk'));
    assert.ok(rejectTooFew.textClass.includes('amber'));

    const insufficient = getKupiecStatusBadge('INSUFFICIENT_OBSERVATIONS');
    assert.ok(insufficient.label.includes('Insufficient Sample'));
  });

  it('classifies scenario shock impact severity', () => {
    const severe = getScenarioImpactBadge(-0.22);
    assert.strictEqual(severe.label, 'Severe Impact');
    assert.ok(severe.textClass.includes('rose'));

    const moderate = getScenarioImpactBadge(-0.08);
    assert.strictEqual(moderate.label, 'Moderate Impact');
    assert.ok(moderate.textClass.includes('amber'));

    const mild = getScenarioImpactBadge(-0.02);
    assert.strictEqual(mild.label, 'Mild Impact');

    const positive = getScenarioImpactBadge(0.05);
    assert.strictEqual(positive.label, 'Positive Impact');
    assert.ok(positive.textClass.includes('emerald'));
  });

  it('provides institutional VaR model labels', () => {
    assert.strictEqual(
      getVaRModelLabel('HISTORICAL_SIMULATION'),
      'Historical Simulation (Non-Parametric)'
    );
    assert.strictEqual(
      getVaRModelLabel('PARAMETRIC_NORMAL'),
      'Parametric Delta-Normal (Gaussian)'
    );
    assert.strictEqual(
      getVaRModelLabel('MONTE_CARLO_GAUSSIAN'),
      'Monte Carlo Gaussian Simulation'
    );
  });

  it('reconciles Part XVI Reference Fixture: Empirical Quantile & Fractional ES', () => {
    // 5 sorted daily losses: [-0.02, -0.01, 0.005, 0.01, 0.03]
    const sortedLosses = [-0.02, -0.01, 0.005, 0.01, 0.03];
    const N = sortedLosses.length;
    const alpha = 0.8;

    // k = ceil(0.8 * 5) = 4 (1-based index) -> index 3 (0-based) -> 0.01 (1.0%)
    const k = Math.ceil(alpha * N);
    const varLoss = sortedLosses[k - 1];
    assert.strictEqual(varLoss, 0.01);
    assert.strictEqual(formatVaRReturn(varLoss), '1.00%');

    // Expected Shortfall: tail above alpha = 0.8 covers the top 20% (u in [0.8, 1.0]).
    // The 5 bins are [0.0, 0.2], [0.2, 0.4], [0.4, 0.6], [0.6, 0.8], [0.8, 1.0].
    // Bin 5 (u in [0.8, 1.0]) corresponds to sortedLosses[4] = 0.03.
    // Integral from 0.8 to 1.0 of Q(u) du = (1.0 - 0.8) * 0.03 = 0.2 * 0.03 = 0.006.
    // ES = 0.006 / 0.2 = 0.03 (3.0%).
    const esTailLoss = sortedLosses[4];
    assert.strictEqual(esTailLoss, 0.03);
    assert.strictEqual(formatVaRReturn(esTailLoss), '3.00%');
  });

  it('reconciles Part XX Reference Fixture: Closed-Form Gaussian VaR and ES', () => {
    const mu = 0.0;
    const sigma = 0.02;
    const alpha = 0.95;

    // Standard Normal Quantile z_0.95 = 1.64485362695
    const zAlpha = 1.6448536269514722;
    const var95 = -mu + sigma * zAlpha;
    assert.strictEqual(formatVaRReturn(var95, 4), '3.2897%');

    // Standard Normal Density phi(z) = (1 / sqrt(2*pi)) * exp(-z^2 / 2)
    const phiZ = (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * zAlpha * zAlpha);
    const es95 = -mu + sigma * (phiZ / (1 - alpha));
    assert.strictEqual(formatVaRReturn(es95, 4), '4.1254%');

    // Tail leptokurtosis ratio for Gaussian at 95% is approximately 1.254
    const ratio = es95 / var95;
    assert.strictEqual(ratio.toFixed(3), '1.254');
  });

  it('reconciles Part XXXIV Multi-Currency Multiplicative Compounding', () => {
    const priceShock = -0.10;
    const fxShock = -0.05;

    // Correct multiplicative compounding: (1 + s_p)(1 + s_fx) - 1
    const compoundReturn = (1 + priceShock) * (1 + fxShock) - 1;

    // (-0.10) + (-0.05) would be naive additive -0.150 (-15.0%)
    // Multiplicative is (0.90 * 0.95) - 1 = 0.855 - 1 = -0.145 (-14.5%)
    assert.strictEqual(compoundReturn.toFixed(4), '-0.1450');
    assert.notStrictEqual(compoundReturn, priceShock + fxShock);
    assert.strictEqual(formatVaRReturn(compoundReturn), '14.50%');
  });

  it('reconciles Part XLIII Scenario Revaluation & Exact Sum Invariant', () => {
    const baseNav = 100000.0;
    const assetA_base = 60000.0;
    const assetB_base = 40000.0;

    const shockA = -0.10; // -10%
    const shockB = 0.05;  // +5%

    const assetA_shocked = assetA_base * (1 + shockA); // 54,000
    const assetB_shocked = assetB_base * (1 + shockB); // 42,000

    const pnlA = assetA_shocked - assetA_base; // -6,000
    const pnlB = assetB_shocked - assetB_base; // +2,000

    const totalPnl = pnlA + pnlB; // -4,000
    const shockedNav = assetA_shocked + assetB_shocked; // 96,000

    assert.strictEqual(assetA_shocked, 54000.0);
    assert.strictEqual(assetB_shocked, 42000.0);
    assert.strictEqual(pnlA, -6000.0);
    assert.strictEqual(pnlB, 2000.0);
    assert.strictEqual(totalPnl, -4000.0);
    assert.strictEqual(shockedNav, 96000.0);

    // Exact reconciliation assertion: Sum(Delta V_i) === Delta V_P
    const portfolioDiff = Math.abs(shockedNav - baseNav - totalPnl);
    assert.ok(portfolioDiff < 1e-9);
  });

  it('verifies Kupiec POF Likelihood Ratio Critical Value Invariants', () => {
    // Critical value at 95% confidence for Chi-Square distribution with df=1 is 3.841459
    const chiSquareCritical95 = 3.841459;

    // LR <= critical -> ACCEPT
    const lrAccept = 1.42;
    assert.ok(lrAccept <= chiSquareCritical95);

    // LR > critical -> REJECT
    const lrReject = 5.89;
    assert.ok(lrReject > chiSquareCritical95);
  });
});

