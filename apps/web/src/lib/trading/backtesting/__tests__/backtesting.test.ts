import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  formatCurrency,
  formatPercent,
  formatRatio,
  formatNumber,
  isOptionStrategy,
  validateBacktestConfig,
  calculateClientDrawdowns,
  computeTradeRatios,
} from "../formatters";
import { TradeRecord } from "../types";

describe("ATLAS Stage 143: Backtesting Formatters & Calculations", () => {
  it("formats currency correctly for USD and custom currencies", () => {
    assert.equal(formatCurrency(10000), "$10,000.00");
    assert.equal(formatCurrency(-250.5), "-$250.50");
    assert.equal(formatCurrency(null), "—");
    assert.equal(formatCurrency(undefined), "—");
  });

  it("formats percentages and ratios cleanly", () => {
    assert.equal(formatPercent(12.345), "+12.35%");
    assert.equal(formatPercent(-4.2), "-4.20%");
    assert.equal(formatPercent(null), "—");
    assert.equal(formatRatio(1.854), "1.85");
    assert.equal(formatNumber(125000), "125,000");
  });

  it("identifies options strategies correctly", () => {
    assert.equal(isOptionStrategy("BUY_AND_HOLD"), false);
    assert.equal(isOptionStrategy("MA_CROSSOVER"), false);
    assert.equal(isOptionStrategy("OPTIONS_LONG_CALL"), true);
    assert.equal(isOptionStrategy("OPTIONS_IRON_CONDOR"), true);
  });

  it("validates backtest configuration accurately", () => {
    const invalidConfig = {
      strategy_id: "",
      dataset_id: "",
      initial_cash: -100,
    };
    const res1 = validateBacktestConfig(invalidConfig);
    assert.equal(res1.isValid, false);
    assert.equal(res1.errors.length, 3);

    const maCrossInvalid = {
      strategy_id: "MA_CROSSOVER",
      dataset_id: "ds_spy_daily_2024",
      strategy_parameters: { fast_period: 30, slow_period: 10 },
    };
    const res2 = validateBacktestConfig(maCrossInvalid);
    assert.equal(res2.isValid, false);
    assert.match(res2.errors[0], /Fast MA period must be strictly less/);

    const validConfig = {
      strategy_id: "MA_CROSSOVER",
      dataset_id: "ds_spy_daily_2024",
      initial_cash: 50000,
      strategy_parameters: { fast_period: 10, slow_period: 50 },
    };
    const res3 = validateBacktestConfig(validConfig);
    assert.equal(res3.isValid, true);
    assert.equal(res3.errors.length, 0);
  });

  it("calculates peak-to-trough drawdowns correctly", () => {
    const series = [
      { timestamp: "2024-01-01", equity: 100 },
      { timestamp: "2024-01-02", equity: 120 }, // Peak
      { timestamp: "2024-01-03", equity: 90 },  // Drawdown of (120-90)/120 = 25%
      { timestamp: "2024-01-04", equity: 110 },
      { timestamp: "2024-01-05", equity: 130 }, // Recovered
    ];

    const result = calculateClientDrawdowns(series);
    assert.equal(result.metrics.peak_equity, 130);
    assert.equal(result.metrics.max_drawdown_dollar, 30);
    assert.equal(result.metrics.max_drawdown_pct, 25.0);
    assert.equal(result.metrics.is_recovered, true);
    assert.equal(result.drawdowns[2], 25.0);
  });

  it("computes trade ratios and profit factor with zero-division safety", () => {
    const trades: TradeRecord[] = [
      {
        trade_id: "t1",
        instrument_id: "SPY",
        direction: "LONG",
        entry_time: "2024-01-01",
        entry_price: 100,
        exit_time: "2024-01-05",
        exit_price: 110,
        quantity: 10,
        gross_pnl: 100,
        commissions: 2,
        slippage_cost: 1,
        net_pnl: 97,
        holding_period_days: 4,
        exit_reason: "SIGNAL",
      },
      {
        trade_id: "t2",
        instrument_id: "SPY",
        direction: "LONG",
        entry_time: "2024-01-06",
        entry_price: 110,
        exit_time: "2024-01-08",
        exit_price: 105,
        quantity: 10,
        gross_pnl: -50,
        commissions: 2,
        slippage_cost: 1,
        net_pnl: -53,
        holding_period_days: 2,
        exit_reason: "STOP",
      },
    ];

    const ratios = computeTradeRatios(trades);
    assert.equal(ratios.winningCount, 1);
    assert.equal(ratios.losingCount, 1);
    assert.equal(ratios.winRatePct, 50.0);
    assert.equal(ratios.profitFactor, Number((97 / 53).toFixed(2)));

    // Edge case: 0 trades
    const zeroTradeRatios = computeTradeRatios([]);
    assert.equal(zeroTradeRatios.winRatePct, 0);
    assert.equal(zeroTradeRatios.profitFactor, null);
  });
});
