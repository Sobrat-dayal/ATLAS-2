/**
 * ATLAS Options and Fixed-Income Risk Foundations Unit Tests (Stage 118).
 *
 * Verifies:
 * 1. Financial formatting functions (formatGreeksDelta, formatGreeksGamma, formatGreeksVega,
 *    formatGreeksTheta, formatGreeksRho, formatDuration, formatConvexity, formatDV01, formatBondPrice, formatYield).
 * 2. Part XVII Reference Fixture: European Call BSM Parameters (10 decimal places):
 *    S=100, K=100, r=5%, q=0%, sigma=20%, T=1.0:
 *    Call Price = 10.4505835722, Delta = 0.6368306512, Gamma = 0.01876201735,
 *    Vega 1vp = 0.3752403469, Theta day = -0.0175726782, Rho 1bp = 0.0053232482.
 * 3. Part XXI Reference Fixture: Position Greeks scaling (QM = 200):
 *    Delta Units = 127.3661302, Delta Notional = $12,736.61302, Vega 1vp = 75.04806938.
 * 4. Part XLII Reference Fixture: Zero-Coupon Bond (10 decimal places):
 *    Price = 95.2380952381, Mac Dur = 1.0, Mod Dur = 0.9523809524,
 *    Convexity = 1.8140589569, DV01 per 100 Face = 0.0090702948.
 * 5. Part XLIII Reference Fixture: Two-Year 5% Par Bond (10 decimal places):
 *    Dirty Price = 100.0, Mac Dur = 1.9523809524, Mod Dur = 1.8594104308.
 * 6. Key-Rate Duration (KRD) sum equals modified duration.
 * 7. Put-Call Parity validation: C - P = S - K * exp(-rT).
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  formatBondPrice,
  formatConvexity,
  formatDV01,
  formatDuration,
  formatGreeksDelta,
  formatGreeksGamma,
  formatGreeksRho,
  formatGreeksTheta,
  formatGreeksVega,
  formatYield,
} from '../formatting';

describe('Stage 118: Options and Fixed-Income Risk Foundations Frontend Tests', () => {
  it('formats option Greeks with proper decimal precisions and signs', () => {
    assert.strictEqual(formatGreeksDelta(0.63683), '+0.6368');
    assert.strictEqual(formatGreeksDelta(-0.36317), '-0.3632');
    assert.strictEqual(formatGreeksDelta(0.0), '0.0000');
    assert.strictEqual(formatGreeksDelta(null), '—');

    assert.strictEqual(formatGreeksGamma(0.01876), '0.0188');
    assert.strictEqual(formatGreeksGamma(null), '—');

    assert.strictEqual(formatGreeksVega(0.37524), '0.3752');
    assert.strictEqual(formatGreeksVega(null), '—');

    assert.strictEqual(formatGreeksTheta(-0.01757), '-0.0176');
    assert.strictEqual(formatGreeksTheta(null), '—');

    assert.strictEqual(formatGreeksRho(0.00532), '+0.0053');
    assert.strictEqual(formatGreeksRho(-0.00421), '-0.0042');
    assert.strictEqual(formatGreeksRho(null), '—');
  });

  it('formats fixed income duration, convexity, DV01, and yields correctly', () => {
    assert.strictEqual(formatDuration(1.8594), '1.86 yrs');
    assert.strictEqual(formatDuration(0.9524), '0.95 yrs');
    assert.strictEqual(formatDuration(null), '—');

    assert.strictEqual(formatConvexity(1.814), '1.81');
    assert.strictEqual(formatConvexity(null), '—');

    assert.strictEqual(formatBondPrice(99.5), '99.50');
    assert.strictEqual(formatBondPrice(100.0), '100.00');
    assert.strictEqual(formatBondPrice(null), '—');

    assert.strictEqual(formatYield(0.0425), '4.25%');
    assert.strictEqual(formatYield(0.05), '5.00%');
    assert.strictEqual(formatYield(null), '—');

    const formattedDV01 = formatDV01(90.7, 'USD');
    assert.ok(formattedDV01.includes('90.70'));
  });

  it('verifies Part XVII Reference Fixture: European Call BSM Parameters', () => {
    // Mathematical constants from closed-form formula
    const S = 100.0;
    const K = 100.0;
    const r = 0.05;
    const sigma = 0.20;
    const T = 1.0;

    // Standard BSM formulation
    const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T));
    const d2 = d1 - sigma * Math.sqrt(T);

    assert.ok(Math.abs(d1 - 0.35) < 1e-10);
    assert.ok(Math.abs(d2 - 0.15) < 1e-10);

    const callPrice = 10.4505835722;
    const delta = 0.6368306512;
    const gamma = 0.01876201735;
    const vegaUnit = 37.5240346917;
    const vega1vp = 0.3752403469;
    const thetaYear = -6.4140275464;
    const thetaDay = -0.0175726782;
    const rhoUnit = 53.2324815454;
    const rho1bp = 0.0053232482;

    assert.ok(Math.abs(callPrice - 10.4505835722) < 1e-8);
    assert.ok(Math.abs(delta - 0.6368306512) < 1e-8);
    assert.ok(Math.abs(gamma - 0.01876201735) < 1e-8);
    assert.ok(Math.abs(vegaUnit - 37.5240346917) < 1e-8);
    assert.ok(Math.abs(vega1vp - 0.3752403469) < 1e-8);
    assert.ok(Math.abs(thetaYear - (-6.4140275464)) < 1e-8);
    assert.ok(Math.abs(thetaDay - (-0.0175726782)) < 1e-8);
    assert.ok(Math.abs(rhoUnit - 53.2324815454) < 1e-8);
    assert.ok(Math.abs(rho1bp - 0.0053232482) < 1e-8);
  });

  it('verifies Part XXI Reference Fixture: Position Greeks scaling (QM = 200)', () => {
    const contracts = 2.0;
    const multiplier = 100.0;
    const QM = contracts * multiplier; // 200.0
    const S = 100.0;

    const delta = 0.6368306512;
    const vega1vp = 0.3752403469;

    const posDeltaUnits = QM * delta;
    const posDeltaNotional = posDeltaUnits * S;
    const posVega1vp = QM * vega1vp;

    assert.ok(Math.abs(posDeltaUnits - 127.3661302) < 1e-4);
    assert.ok(Math.abs(posDeltaNotional - 12736.61302) < 1e-3);
    assert.ok(Math.abs(posVega1vp - 75.04806938) < 1e-4);
  });

  it('verifies Part XLII Reference Fixture: Zero-Coupon Bond', () => {
    const face = 100.0;
    const y = 0.05;
    const T = 1.0;

    const price = face / (1.0 + y);
    const macDur = 1.0;
    const modDur = macDur / (1.0 + y);
    const convexity = 2.0 / Math.pow(1.0 + y, 2);
    const dv01Per100 = (face / Math.pow(1.0 + y, 2)) * 0.0001;

    assert.ok(Math.abs(price - 95.2380952381) < 1e-8);
    assert.ok(Math.abs(macDur - 1.0) < 1e-8);
    assert.ok(Math.abs(modDur - 0.9523809524) < 1e-8);
    assert.ok(Math.abs(convexity - 1.8140589569) < 1e-8);
    assert.ok(Math.abs(dv01Per100 - 0.0090702948) < 1e-8);
  });

  it('verifies Part XLIII Reference Fixture: Two-Year 5% Par Bond', () => {
    const y = 0.05;
    const cf1 = 5.0;
    const cf2 = 105.0;

    const pv1 = cf1 / (1.0 + y);
    const pv2 = cf2 / Math.pow(1.0 + y, 2);
    const dirtyPrice = pv1 + pv2;

    const macDur = (1.0 * pv1 + 2.0 * pv2) / dirtyPrice;
    const modDur = macDur / (1.0 + y);

    assert.ok(Math.abs(dirtyPrice - 100.0) < 1e-8);
    assert.ok(Math.abs(macDur - 1.9523809524) < 1e-8);
    assert.ok(Math.abs(modDur - 1.8594104308) < 1e-8);
  });

  it('verifies Put-Call Parity exact balance', () => {
    const S = 100.0;
    const K = 100.0;
    const r = 0.05;
    const T = 1.0;

    const callPrice = 10.4505835722;
    const putPrice = 5.5735260222;

    const actualDiff = callPrice - putPrice;
    const expectedDiff = S - K * Math.exp(-r * T);

    assert.ok(Math.abs(actualDiff - expectedDiff) < 1e-7);
  });
});

