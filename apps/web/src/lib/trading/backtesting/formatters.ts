/**
 * Utility functions, formatters, and client-side numerical validation
 * for ATLAS NautilusTrader Historical Backtesting (Stage 143).
 */

import { AtlasBacktestConfig, DrawdownMetrics, TradeRecord } from "./types";

export function formatCurrency(
  val: number | null | undefined,
  currency: string = "USD",
): string {
  if (val === null || val === undefined || isNaN(val)) return "—";
  const prefix = currency === "USD" ? "$" : `${currency} `;
  const isNegative = val < 0;
  const absVal = Math.abs(val);
  return `${isNegative ? "-" : ""}${prefix}${absVal.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatPercent(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "—";
  return `${val >= 0 ? "+" : ""}${val.toFixed(2)}%`;
}

export function formatRatio(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "—";
  return val.toFixed(2);
}

export function formatNumber(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return "—";
  return val.toLocaleString("en-US");
}

export function isOptionStrategy(strategyId: string): boolean {
  return strategyId.toUpperCase().includes("OPTION");
}

export function validateBacktestConfig(config: Partial<AtlasBacktestConfig>): {
  isValid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (!config.strategy_id) {
    errors.push("Strategy ID is required.");
  }
  if (!config.dataset_id) {
    errors.push("Historical dataset ID is required.");
  }
  if (config.initial_cash !== undefined && config.initial_cash <= 0) {
    errors.push("Initial capital must be greater than zero.");
  }
  if (config.max_position_size !== undefined && config.max_position_size <= 0) {
    errors.push("Max position size must be greater than zero.");
  }

  // Parameter validations
  if (config.strategy_parameters) {
    const params = config.strategy_parameters;
    if (params.fast_period && params.slow_period) {
      if (params.fast_period >= params.slow_period) {
        errors.push("Fast MA period must be strictly less than Slow MA period.");
      }
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

export function calculateClientDrawdowns(
  equitySeries: Array<{ timestamp: string; equity: number }>,
): {
  drawdowns: number[];
  metrics: DrawdownMetrics;
} {
  if (equitySeries.length === 0) {
    return {
      drawdowns: [],
      metrics: {
        max_drawdown_pct: 0.0,
        max_drawdown_dollar: 0.0,
        peak_equity: 0.0,
        trough_equity: 0.0,
        is_recovered: true,
      },
    };
  }

  let peak = equitySeries[0].equity;
  let maxDdPct = 0.0;
  let maxDdDollar = 0.0;
  let peakTime = equitySeries[0].timestamp;
  let troughTime = equitySeries[0].timestamp;
  let troughEquity = equitySeries[0].equity;
  const drawdowns: number[] = [];

  for (const item of equitySeries) {
    if (item.equity > peak) {
      peak = item.equity;
      peakTime = item.timestamp;
    }
    const ddDollar = peak - item.equity;
    const ddPct = peak > 0 ? (ddDollar / peak) * 100 : 0.0;
    drawdowns.push(Number(ddPct.toFixed(2)));

    if (ddPct > maxDdPct) {
      maxDdPct = ddPct;
      maxDdDollar = ddDollar;
      troughTime = item.timestamp;
      troughEquity = item.equity;
    }
  }

  const finalEquity = equitySeries[equitySeries.length - 1].equity;
  const isRecovered = finalEquity >= peak;

  return {
    drawdowns,
    metrics: {
      max_drawdown_pct: Number(maxDdPct.toFixed(2)),
      max_drawdown_dollar: Number(maxDdDollar.toFixed(2)),
      peak_equity: peak,
      trough_equity: troughEquity,
      peak_timestamp: peakTime,
      trough_timestamp: troughTime,
      is_recovered: isRecovered,
    },
  };
}

export function computeTradeRatios(trades: TradeRecord[]): {
  winRatePct: number;
  profitFactor: number | null;
  winningCount: number;
  losingCount: number;
} {
  if (trades.length === 0) {
    return {
      winRatePct: 0,
      profitFactor: null,
      winningCount: 0,
      losingCount: 0,
    };
  }

  let grossGains = 0;
  let grossLosses = 0;
  let winCount = 0;
  let lossCount = 0;

  for (const t of trades) {
    if (t.net_pnl > 0) {
      grossGains += t.net_pnl;
      winCount++;
    } else if (t.net_pnl < 0) {
      grossLosses += Math.abs(t.net_pnl);
      lossCount++;
    }
  }

  const winRatePct = Number(((winCount / trades.length) * 100).toFixed(2));
  const profitFactor =
    grossLosses > 0
      ? Number((grossGains / grossLosses).toFixed(2))
      : grossGains > 0
      ? null
      : 0.0;

  return {
    winRatePct,
    profitFactor,
    winningCount: winCount,
    losingCount: lossCount,
  };
}
