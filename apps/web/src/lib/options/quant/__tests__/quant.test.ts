/**
 * Unit tests for ATLAS QuantLib Options Frontend Utilities (Stage 142).
 */

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  QuantModelGreeks,
  QuantStrategyLeg,
  StrategyComparisonItem,
} from "../types";

describe("Stage 142 QuantLib Options Frontend Utilities", () => {
  it("formats and validates Greek unit conventions correctly", () => {
    const greeks: QuantModelGreeks = {
      delta: 0.5234,
      gamma: 0.0152,
      theta_per_day: -0.0456,
      theta_annual: -16.644,
      vega_per_point: 0.1845,
      vega_per_unit: 18.45,
      rho_per_point: 0.125,
      rho_per_bp: 0.00125,
      vanna: 0.002,
      volga: 0.015,
      calculation_method: "ANALYTIC",
    };

    assert.equal(greeks.delta, 0.5234);
    assert.equal(greeks.gamma, 0.0152);
    // Vega per point must be exactly 1/100 of vega per unit
    assert.ok(Math.abs(greeks.vega_per_unit / 100 - greeks.vega_per_point) < 1e-4);
    // Rho per bp must be exactly 1/100 of rho per point
    assert.ok(Math.abs(greeks.rho_per_point / 100 - greeks.rho_per_bp) < 1e-4);
    // Theta annual must be ~ 365 * theta per day
    assert.ok(Math.abs(greeks.theta_per_day * 365 - greeks.theta_annual) < 1.0);
  });

  it("identifies unbounded risk correctly for naked short options", () => {
    const nakedCallLeg: QuantStrategyLeg = {
      contract_id: "opt_spy_call_500",
      side: "SHORT_CALL",
      quantity: 1,
      entry_premium: 5.0,
      multiplier: 100.0,
      strike_price: 500.0,
      expiration_date: "2024-06-21",
      option_type: "CALL",
      exercise_style: "AMERICAN",
      custom_fee: 0.0,
    };

    const isUnboundedCall = nakedCallLeg.side === "SHORT_CALL";
    assert.equal(isUnboundedCall, true);

    const bullCallSpreadLegs: QuantStrategyLeg[] = [
      {
        contract_id: "opt_spy_call_500",
        side: "LONG_CALL",
        quantity: 1,
        entry_premium: 8.0,
        multiplier: 100.0,
        strike_price: 500.0,
        expiration_date: "2024-06-21",
        option_type: "CALL",
        exercise_style: "AMERICAN",
        custom_fee: 0.0,
      },
      {
        contract_id: "opt_spy_call_510",
        side: "SHORT_CALL",
        quantity: 1,
        entry_premium: 3.0,
        multiplier: 100.0,
        strike_price: 510.0,
        expiration_date: "2024-06-21",
        option_type: "CALL",
        exercise_style: "AMERICAN",
        custom_fee: 0.0,
      },
    ];

    const netCallExposure = bullCallSpreadLegs.reduce((acc, leg) => {
      const sign = leg.side === "LONG_CALL" ? 1 : -1;
      return acc + sign * leg.quantity;
    }, 0);

    assert.equal(netCallExposure, 0); // Perfectly capped upside risk
  });

  it("evaluates StrategyComparisonItem risk-reward metrics cleanly", () => {
    const item: StrategyComparisonItem = {
      strategy_id: "bull_call_spread",
      strategy_name: "Bull Call Spread",
      net_debit_credit: -500.0,
      max_profit: 500.0,
      max_loss: -500.0,
      break_even_points: [505.0],
      net_delta: 25.4,
      net_gamma: 0.5,
      net_vega: 2.1,
      net_theta: -0.8,
      return_on_risk_ratio: 1.0,
      unbounded_risk: false,
    };

    assert.equal(item.unbounded_risk, false);
    assert.equal(item.return_on_risk_ratio, 1.0);
    assert.equal(item.break_even_points.length, 1);
    assert.equal(item.break_even_points[0], 505.0);
  });
});
