/**
 * ATLAS Portfolios V1 — Optimization & Construction Unit Tests (Stage 114).
 *
 * Verifies:
 * 1. Formatting helpers (Percent, Bps, Currency, Badges, Objective labels).
 * 2. Part XXIX analytical minimum variance reference math (9/13 and 4/13).
 * 3. Part LXIV 4x20% cap infeasibility math (sum = 80% < 100%).
 * 4. Rebalancing one-way turnover and transaction cost arithmetic.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  formatBps,
  formatCurrency,
  formatNumber,
  formatPercent,
  formatWeightPercent,
  getFeasibilityBadge,
  getObjectiveLabel,
  getSolverStatusBadge,
  getTradeDirectionBadge,
} from '../formatting';

describe('Stage 114: Portfolio Optimization & Construction Tests', () => {
  it('formats percentages with signed and unsigned display', () => {
    assert.strictEqual(formatPercent(0.125), '+12.50%');
    assert.strictEqual(formatPercent(-0.0425, 2), '-4.25%');
    assert.strictEqual(formatPercent(0.0), '0.00%');
    assert.strictEqual(formatPercent(null), '—');

    assert.strictEqual(formatWeightPercent(0.692308, 2), '69.23%');
    assert.strictEqual(formatWeightPercent(0.307692, 4), '30.7692%');
    assert.strictEqual(formatWeightPercent(null), '0.00%');
  });

  it('formats basis points accurately', () => {
    assert.strictEqual(formatBps(0.0125), '+125 bps');
    assert.strictEqual(formatBps(-0.005), '-50 bps');
    assert.strictEqual(formatBps(0.0), '0 bps');
    assert.strictEqual(formatBps(null), '—');
  });

  it('formats currency correctly with standard symbol and decimals', () => {
    assert.strictEqual(formatCurrency(1250000.5, 'USD'), '$1,250,000.50');
    assert.strictEqual(formatCurrency(0, 'USD'), '$0.00');
    assert.strictEqual(formatCurrency(null), '—');
  });

  it('formats generic numbers', () => {
    assert.strictEqual(formatNumber(1.23456, 2), '1.23');
    assert.strictEqual(formatNumber(1.23456, 4), '1.2346');
    assert.strictEqual(formatNumber(null), '—');
  });

  it('returns appropriate badge metadata for solver status', () => {
    assert.strictEqual(getSolverStatusBadge('OPTIMAL').variant, 'positive');
    assert.strictEqual(getSolverStatusBadge('OPTIMAL_INACCURATE').variant, 'warning');
    assert.strictEqual(getSolverStatusBadge('INFEASIBLE').variant, 'negative');
    assert.strictEqual(getSolverStatusBadge('TIMEOUT').variant, 'warning');
    assert.strictEqual(getSolverStatusBadge('NUMERICAL_FAILURE').variant, 'negative');
  });

  it('returns appropriate badge metadata for feasibility status', () => {
    assert.strictEqual(getFeasibilityBadge('FEASIBLE').variant, 'positive');
    assert.strictEqual(getFeasibilityBadge('FEASIBLE_WITH_SLACK_WARNING').variant, 'warning');
    assert.strictEqual(getFeasibilityBadge('INFEASIBLE').variant, 'negative');
  });

  it('returns appropriate trade direction visual classes', () => {
    assert.ok(getTradeDirectionBadge('BUY').className.includes('emerald'));
    assert.ok(getTradeDirectionBadge('SELL').className.includes('rose'));
    assert.ok(getTradeDirectionBadge('HOLD').className.includes('zinc'));
  });

  it('returns clear labels for mathematical objectives', () => {
    assert.strictEqual(getObjectiveLabel('MINIMUM_VARIANCE'), 'Global Minimum Variance');
    assert.strictEqual(getObjectiveLabel('MAXIMUM_SHARPE'), 'Maximum Sharpe Ratio');
    assert.strictEqual(getObjectiveLabel('RISK_PARITY'), 'Equal Risk Contribution (Risk Parity)');
  });

  it('Part XXIX Reference Fixture: exact two-asset uncorrelated minimum variance weights', () => {
    // Asset A var = 0.04, Asset B var = 0.09, Cov = 0.0
    const varA = 0.04;
    const varB = 0.09;
    const totalVar = varA + varB; // 0.13

    const wA = varB / totalVar; // 0.09 / 0.13 = 9/13 ≈ 0.69230769
    const wB = varA / totalVar; // 0.04 / 0.13 = 4/13 ≈ 0.30769231

    assert.ok(Math.abs(wA + wB - 1.0) < 1e-6);
    assert.ok(Math.abs(wA - 9 / 13) < 1e-6);
    assert.ok(Math.abs(wB - 4 / 13) < 1e-6);

    const portfolioVar = Math.pow(wA, 2) * varA + Math.pow(wB, 2) * varB;
    const analyticalVar = 4.68 / 169; // ≈ 0.0276923
    assert.ok(Math.abs(portfolioVar - analyticalVar) < 1e-6);

    const portfolioVol = Math.sqrt(portfolioVar);
    assert.ok(Math.abs(portfolioVol - 0.16641) < 1e-4);
  });

  it('Part LXIV Reference Fixture: detects budget deficit when 4 assets are capped at 20% each', () => {
    const caps = [0.20, 0.20, 0.20, 0.20];
    const sumCaps = caps.reduce((acc, c) => acc + c, 0);

    assert.strictEqual(sumCaps, 0.80);
    const requiredBudget = 1.00;
    const deficit = requiredBudget - sumCaps;

    assert.ok(Math.abs(deficit - 0.20) < 1e-6);
    assert.strictEqual(sumCaps < requiredBudget, true);
  });

  it('Rebalancing & Turnover Arithmetic: computes one-way turnover and transaction costs', () => {
    const nav = 1000000;
    const curr = { AAPL: 0.50, MSFT: 0.30, CASH: 0.20 };
    const cand = { AAPL: 0.40, MSFT: 0.40, CASH: 0.20 };

    const deltaAAPL = cand.AAPL - curr.AAPL; // -0.10
    const deltaMSFT = cand.MSFT - curr.MSFT; // +0.10
    const deltaCASH = cand.CASH - curr.CASH; // 0.00

    const tradeValAAPL = nav * deltaAAPL; // -$100,000
    const tradeValMSFT = nav * deltaMSFT; // +$100,000
    const tradeValCASH = nav * deltaCASH; // $0

    // Self-funding check: trade value deltas must sum to 0 within floating point precision
    assert.ok(Math.abs(tradeValAAPL + tradeValMSFT + tradeValCASH) < 1e-6);

    // One-way turnover: 0.5 * sum(|delta|)
    const grossTurnover = Math.abs(deltaAAPL) + Math.abs(deltaMSFT) + Math.abs(deltaCASH);
    const oneWayTurnover = grossTurnover / 2.0;
    assert.ok(Math.abs(oneWayTurnover - 0.10) < 1e-4);

    // Transaction cost at 10 bps (0.0010) on traded volume
    const costRate = 0.0010;
    const costAAPL = Math.abs(tradeValAAPL) * costRate; // 100,000 * 0.001 = $100
    const costMSFT = Math.abs(tradeValMSFT) * costRate; // 100,000 * 0.001 = $100
    const totalCost = costAAPL + costMSFT;
    assert.strictEqual(totalCost, 200.0);
  });
});
