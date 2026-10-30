/**
 * ATLAS Multi-Factor, Concentration, Currency, and Sector Risk Unit Tests (Stage 117).
 *
 * Verifies:
 * 1. Financial formatting functions (formatFactorLoading, formatHHI, formatEffectiveHoldings, formatVolPercent, formatWeight).
 * 2. Status badges (getModelDiagnosticStatusBadge, getConcentrationClassification).
 * 3. Part XIV Reference Fixture: Factor loading aggregation b = B^T w = [1.04, 0.22].
 * 4. Part XXII Reference Fixture: Factor risk decomposition and exact Euler reconciliation:
 *    V_sys = 0.043748, V_spec = 0.009700, V_total = 0.053448, sigma_P ~= 23.11882%,
 *    VC_MKT = 0.043264, VC_HML = 0.000484.
 * 5. Part XXXI Reference Fixture: HHI = 0.3800, N_eff ~= 2.63158, Top 1 = 50%, Top 2 = 80%.
 * 6. Part XLIV Reference Fixture: Discrete FX multiplicative compounding interaction:
 *    Local +10%, FX -5% -> Interaction -0.5%, Base +4.5%.
 * 7. Part LVII Reference Fixture: Sector Euler risk attribution:
 *    Tech 50%, Fin 50%, Sigma=diag(0.04, 0.09) -> V_P = 0.0325, VC_Tech = 0.0100, VC_Fin = 0.0225.
 * 8. Cross-exposure 2D matrix row-sum reconciliation: sum_s b_{s,k} == b_k.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  formatEffectiveHoldings,
  formatFactorLoading,
  formatHHI,
  formatSignedPercent,
  formatVolPercent,
  formatWeight,
  getConcentrationClassification,
  getModelDiagnosticStatusBadge,
} from '../formatting';

describe('Stage 117: Multi-Factor, Concentration, Currency, and Sector Risk Frontend Tests', () => {
  it('formats factor loadings correctly with explicit plus/minus signs', () => {
    assert.strictEqual(formatFactorLoading(1.04), '+1.04');
    assert.strictEqual(formatFactorLoading(-0.22), '-0.22');
    assert.strictEqual(formatFactorLoading(0.0), '0.00');
    assert.strictEqual(formatFactorLoading(null), '—');
    assert.strictEqual(formatFactorLoading(undefined), '—');
  });

  it('formats Herfindahl-Hirschman Index (HHI) with four decimals', () => {
    assert.strictEqual(formatHHI(0.38), '0.3800');
    assert.strictEqual(formatHHI(0.125), '0.1250');
    assert.strictEqual(formatHHI(1.0), '1.0000');
    assert.strictEqual(formatHHI(null), '—');
  });

  it('formats effective number of holdings with one decimal place', () => {
    assert.strictEqual(formatEffectiveHoldings(2.6315789), '2.6');
    assert.strictEqual(formatEffectiveHoldings(10.0), '10.0');
    assert.strictEqual(formatEffectiveHoldings(1.0), '1.0');
    assert.strictEqual(formatEffectiveHoldings(null), '—');
  });

  it('evaluates antitrust concentration classifications correctly', () => {
    const diversified = getConcentrationClassification(0.12);
    assert.strictEqual(diversified.label, 'Diversified');
    assert.ok(diversified.badgeClass.includes('emerald'));

    const moderate = getConcentrationClassification(0.20);
    assert.strictEqual(moderate.label, 'Moderate');
    assert.ok(moderate.badgeClass.includes('amber'));

    const high = getConcentrationClassification(0.38);
    assert.strictEqual(high.label, 'High Concentration');
    assert.ok(high.badgeClass.includes('rose'));
  });

  it('returns appropriate model diagnostic status badges', () => {
    const healthy = getModelDiagnosticStatusBadge('HEALTHY');
    assert.strictEqual(healthy.label, 'Healthy');
    assert.ok(healthy.textClass.includes('emerald'));

    const collinear = getModelDiagnosticStatusBadge('WARNING_COLLINEARITY');
    assert.strictEqual(collinear.label, 'Collinear');
    assert.ok(collinear.textClass.includes('amber'));

    const rankDef = getModelDiagnosticStatusBadge('WARNING_RANK_DEFICIENT');
    assert.strictEqual(rankDef.label, 'Rank Deficient');
    assert.ok(rankDef.textClass.includes('rose'));
  });

  it('verifies Part XIV Reference Fixture: b = B^T w = [1.04, 0.22]', () => {
    const w = [0.6, 0.4];
    const B = [
      [1.2, 0.5],
      [0.8, -0.2],
    ];

    const b_mkt = w[0] * B[0][0] + w[1] * B[1][0];
    const b_hml = w[0] * B[0][1] + w[1] * B[1][1];

    assert.ok(Math.abs(b_mkt - 1.04) < 1e-9);
    assert.ok(Math.abs(b_hml - 0.22) < 1e-9);
  });

  it('verifies Part XXII Reference Fixture: Systematic vs Specific Risk & Euler Reconciliation', () => {
    const w = [0.6, 0.4];
    const b = [1.04, 0.22];
    const F = [
      [0.04, 0.0],
      [0.0, 0.01],
    ];
    const d = [0.0225, 0.01];

    // Systematic variance: b^T F b
    const v_sys = b[0] * (F[0][0] * b[0] + F[0][1] * b[1]) + b[1] * (F[1][0] * b[0] + F[1][1] * b[1]);
    assert.ok(Math.abs(v_sys - 0.043748) < 1e-6);

    // Specific variance: w^T D w
    const v_spec = w[0] * w[0] * d[0] + w[1] * w[1] * d[1];
    assert.ok(Math.abs(v_spec - 0.009700) < 1e-6);

    // Total variance & volatility
    const v_tot = v_sys + v_spec;
    assert.ok(Math.abs(v_tot - 0.053448) < 1e-6);
    const sigma_p = Math.sqrt(v_tot);
    assert.ok(Math.abs(sigma_p - 0.231188235) < 1e-6);

    // Factor Euler variance contributions
    const vc_mkt = b[0] * (F[0][0] * b[0] + F[0][1] * b[1]);
    const vc_hml = b[1] * (F[1][0] * b[0] + F[1][1] * b[1]);

    assert.ok(Math.abs(vc_mkt - 0.043264) < 1e-6);
    assert.ok(Math.abs(vc_hml - 0.000484) < 1e-6);

    // Reconciliation invariants
    assert.ok(Math.abs(vc_mkt + vc_hml - v_sys) < 1e-9);
    assert.ok(Math.abs(vc_mkt + vc_hml + v_spec - v_tot) < 1e-9);

    // Volatility contributions
    const rc_mkt = vc_mkt / sigma_p;
    const rc_hml = vc_hml / sigma_p;
    const rc_spec = v_spec / sigma_p;
    assert.ok(Math.abs(rc_mkt + rc_hml + rc_spec - sigma_p) < 1e-7);
  });

  it('verifies Part XXXI Reference Fixture: w = [0.5, 0.3, 0.2] -> HHI = 0.3800, N_eff = 2.63158', () => {
    const w = [0.5, 0.3, 0.2];
    const hhi = w.reduce((acc, weight) => acc + weight * weight, 0);
    assert.ok(Math.abs(hhi - 0.38) < 1e-9);

    const n_eff = 1 / hhi;
    assert.ok(Math.abs(n_eff - 2.631578947) < 1e-6);

    // Top-N sums
    const top1 = w[0];
    const top2 = w[0] + w[1];
    assert.strictEqual(top1, 0.5);
    assert.strictEqual(top2, 0.8);
  });

  it('verifies Part XLIV Reference Fixture: Local +10%, FX -5% -> Interaction -0.5%, Base +4.5%', () => {
    const r_local = 0.10;
    const r_fx = -0.05;
    const interaction = r_local * r_fx;
    const r_base = r_local + r_fx + interaction;

    assert.ok(Math.abs(interaction - (-0.005)) < 1e-9);
    assert.ok(Math.abs(r_base - 0.045) < 1e-9);
    // Exact compounding verification: (1 + 0.10)(1 - 0.05) - 1
    assert.ok(Math.abs((1 + r_local) * (1 + r_fx) - 1 - 0.045) < 1e-9);
  });

  it('verifies Part LVII Reference Fixture: Sector Euler Risk Attribution', () => {
    const w = [0.5, 0.5];
    const Sigma = [
      [0.04, 0.0],
      [0.0, 0.09],
    ];

    // Sigma * w
    const sw0 = Sigma[0][0] * w[0] + Sigma[0][1] * w[1];
    const sw1 = Sigma[1][0] * w[0] + Sigma[1][1] * w[1];

    // Portfolio Variance
    const v_p = w[0] * sw0 + w[1] * sw1;
    assert.ok(Math.abs(v_p - 0.0325) < 1e-9);

    // Sector Variance Contributions
    const vc_tech = w[0] * sw0; // 0.5 * 0.02 = 0.0100
    const vc_fin = w[1] * sw1;  // 0.5 * 0.045 = 0.0225

    assert.ok(Math.abs(vc_tech - 0.0100) < 1e-9);
    assert.ok(Math.abs(vc_fin - 0.0225) < 1e-9);
    assert.ok(Math.abs(vc_tech + vc_fin - v_p) < 1e-9);
  });

  it('verifies Cross-Exposure 2D Matrix row-sum reconciliation: sum_s b_{s,k} == b_k', () => {
    const weights = [0.4, 0.3, 0.3];
    const techBetas = [1.2, 1.1]; // AAPL, MSFT in Tech
    const finBetas = [0.9];       // JPM in Fin

    const b_tech = weights[0] * techBetas[0] + weights[1] * techBetas[1]; // 0.4(1.2) + 0.3(1.1) = 0.81
    const b_fin = weights[2] * finBetas[0];                               // 0.3(0.9) = 0.27
    const b_total = b_tech + b_fin;                                      // 1.08

    assert.ok(Math.abs(b_tech - 0.81) < 1e-9);
    assert.ok(Math.abs(b_fin - 0.27) < 1e-9);
    assert.ok(Math.abs(b_total - 1.08) < 1e-9);
  });
});
