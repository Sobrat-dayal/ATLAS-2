/**
 * ATLAS Financial Risk Foundation — Formatting Utilities (Stage 115).
 *
 * Provides institutional formatting for risk metrics: volatility, variance,
 * drawdowns, beta, tracking error, condition numbers, and status badges.
 */

import {
  DataCoverageStatus,
  DrawdownEpisodeStatus,
  ModelDiagnosticStatus,
  RiskCalculationStatus,
  RiskMetricStatus,
  RiskModelType,
  RiskReturnFrequency,
} from './types';

/**
 * Formats a decimal risk metric (e.g. 0.1833) into an unsigned percentage string (e.g. "18.33%").
 */
export function formatVolPercent(
  val: number | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return `${(val * 100).toFixed(decimals)}%`;
}

/**
 * Formats a signed return or drawdown percentage (e.g. -0.25 -> "-25.00%").
 */
export function formatSignedPercent(
  val: number | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  const sign = val > 0 ? '+' : '';
  return `${sign}${(val * 100).toFixed(decimals)}%`;
}

/**
 * Formats portfolio allocation / risk contribution weight (e.g. 0.50 -> "50.00%").
 */
export function formatWeight(
  val: number | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || isNaN(val)) return '0.00%';
  return `${(val * 100).toFixed(decimals)}%`;
}

/**
 * Formats a decimal basis point value (e.g. 0.0125 -> "125 bps").
 */
export function formatBps(
  val: number | null | undefined,
  decimals: number = 0
): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  const bps = val * 10000;
  return `${bps.toFixed(decimals)} bps`;
}

/**
 * Formats a ratio, such as Beta or Correlation (e.g. 1.042 -> "1.04").
 */
export function formatRatio(
  val: number | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return val.toFixed(decimals);
}

/**
 * Formats days duration (e.g. 42 -> "42 days").
 */
export function formatDays(val: number | null | undefined): string {
  if (val === null || val === undefined) return '—';
  return `${val} ${val === 1 ? 'day' : 'days'}`;
}

/**
 * Formats an ISO date string into standard display (e.g. "2026-03-31").
 */
export function formatDate(isoStr: string | null | undefined): string {
  if (!isoStr) return '—';
  return isoStr.substring(0, 10);
}

export interface StatusBadgeConfig {
  label: string;
  bgClass: string;
  textClass: string;
  borderClass: string;
}

/**
 * Returns badge styling for calculation runs.
 */
export function getCalculationStatusBadge(status: RiskCalculationStatus): StatusBadgeConfig {
  switch (status) {
    case 'COMPLETED':
      return {
        label: 'Calculated',
        bgClass: 'bg-emerald-500/10',
        textClass: 'text-emerald-400',
        borderClass: 'border-emerald-500/30',
      };
    case 'CALCULATING':
    case 'PENDING':
      return {
        label: 'Computing...',
        bgClass: 'bg-amber-500/10',
        textClass: 'text-amber-400',
        borderClass: 'border-amber-500/30',
      };
    case 'FAILED':
      return {
        label: 'Failed',
        bgClass: 'bg-rose-500/10',
        textClass: 'text-rose-400',
        borderClass: 'border-rose-500/30',
      };
    case 'STALE':
      return {
        label: 'Stale',
        bgClass: 'bg-yellow-500/10',
        textClass: 'text-yellow-400',
        borderClass: 'border-yellow-500/30',
      };
    default:
      return {
        label: status,
        bgClass: 'bg-zinc-800',
        textClass: 'text-zinc-400',
        borderClass: 'border-zinc-700',
      };
  }
}

/**
 * Returns badge styling for data coverage health.
 */
export function getDataCoverageBadge(status: DataCoverageStatus): StatusBadgeConfig {
  switch (status) {
    case 'FULL':
      return {
        label: '100% Coverage',
        bgClass: 'bg-emerald-500/10',
        textClass: 'text-emerald-400',
        borderClass: 'border-emerald-500/30',
      };
    case 'ACCEPTABLE':
      return {
        label: 'Acceptable',
        bgClass: 'bg-blue-500/10',
        textClass: 'text-blue-400',
        borderClass: 'border-blue-500/30',
      };
    case 'DEGRADED':
      return {
        label: 'Degraded',
        bgClass: 'bg-amber-500/10',
        textClass: 'text-amber-400',
        borderClass: 'border-amber-500/30',
      };
    case 'CRITICAL_GAPS':
      return {
        label: 'Critical Gaps',
        bgClass: 'bg-rose-500/10',
        textClass: 'text-rose-400',
        borderClass: 'border-rose-500/30',
      };
    default:
      return {
        label: status,
        bgClass: 'bg-zinc-800',
        textClass: 'text-zinc-400',
        borderClass: 'border-zinc-700',
      };
  }
}

/**
 * Returns badge styling for drawdown episode status.
 */
export function getDrawdownEpisodeBadge(status: DrawdownEpisodeStatus): StatusBadgeConfig {
  switch (status) {
    case 'RECOVERED':
      return {
        label: 'Recovered',
        bgClass: 'bg-emerald-500/10',
        textClass: 'text-emerald-400',
        borderClass: 'border-emerald-500/30',
      };
    case 'ONGOING':
      return {
        label: 'Under Water',
        bgClass: 'bg-rose-500/10',
        textClass: 'text-rose-400',
        borderClass: 'border-rose-500/30',
      };
    default:
      return {
        label: status,
        bgClass: 'bg-zinc-800',
        textClass: 'text-zinc-400',
        borderClass: 'border-zinc-700',
      };
  }
}

/**
 * Friendly label for Model Type.
 */
export function getModelTypeLabel(type: RiskModelType): string {
  switch (type) {
    case 'HISTORICAL_SAMPLE':
      return 'Historical Sample';
    case 'ROLLING_SAMPLE':
      return 'Rolling Sample';
    case 'CASH_FLOW_ADJUSTED_WEALTH':
      return 'Cash-Flow-Neutral Wealth';
    case 'COVARIANCE_PARAMETRIC':
      return 'Covariance Parametric (Euler)';
    case 'MULTI_CURRENCY_FACTOR':
      return 'Multi-Currency Multi-Factor';
    case 'EXPONENTIALLY_WEIGHTED':
      return 'Exponentially Weighted (EWMA)';
    case 'MONTE_CARLO':
      return 'Monte Carlo Simulation';
    default:
      return type;
  }
}

/**
 * Friendly label for Return Frequency.
 */
export function getFrequencyLabel(freq: RiskReturnFrequency): string {
  switch (freq) {
    case 'DAILY':
      return 'Daily (252x)';
    case 'WEEKLY':
      return 'Weekly (52x)';
    case 'MONTHLY':
      return 'Monthly (12x)';
    default:
      return freq;
  }
}


// ---------------------------------------------------------------------------
// Stage 116: VaR, Expected Shortfall, Scenarios, and Kupiec Formatting
// ---------------------------------------------------------------------------

import type {
  KupiecTestStatus,
  VaRModelType,
} from './types';

/**
 * Formats monetary amounts with thousands separators and currency symbol.
 */
export function formatCurrency(
  val: number | null | undefined,
  currency: string = 'USD',
  decimals: number = 0
): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  const prefix = currency === 'USD' ? '$' : `${currency} `;
  const absVal = Math.abs(val);
  const formatted = absVal.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return val < 0 ? `-${prefix}${formatted}` : `${prefix}${formatted}`;
}

/**
 * Formats signed monetary P&L e.g. "+$25,000" or "-$40,000".
 */
export function formatPnl(
  val: number | null | undefined,
  currency: string = 'USD',
  decimals: number = 0
): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  const prefix = currency === 'USD' ? '$' : `${currency} `;
  const sign = val > 0 ? '+' : val < 0 ? '-' : '';
  const formatted = Math.abs(val).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return `${sign}${prefix}${formatted}`;
}

/**
 * Formats a decimal VaR or ES loss fraction into an unsigned percentage string.
 */
export function formatVaRReturn(
  val: number | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return `${(Math.abs(val) * 100).toFixed(decimals)}%`;
}

/**
 * Returns badge styling for Kupiec POF unconditional coverage tests.
 */
export function getKupiecStatusBadge(status: KupiecTestStatus): StatusBadgeConfig {
  switch (status) {
    case 'ACCEPT_UNCONDITIONAL_COVERAGE':
      return {
        label: 'Accepted (Accurate VaR)',
        bgClass: 'bg-emerald-500/10',
        textClass: 'text-emerald-400',
        borderClass: 'border-emerald-500/30',
      };
    case 'REJECT_TOO_MANY_EXCEPTIONS':
      return {
        label: 'Rejected (Underestimates Risk)',
        bgClass: 'bg-rose-500/10',
        textClass: 'text-rose-400',
        borderClass: 'border-rose-500/30',
      };
    case 'REJECT_TOO_FEW_EXCEPTIONS':
      return {
        label: 'Rejected (Overestimates Risk)',
        bgClass: 'bg-amber-500/10',
        textClass: 'text-amber-400',
        borderClass: 'border-amber-500/30',
      };
    case 'INSUFFICIENT_OBSERVATIONS':
      return {
        label: 'Insufficient Sample (<30)',
        bgClass: 'bg-slate-500/10',
        textClass: 'text-slate-400',
        borderClass: 'border-slate-500/30',
      };
    default:
      return {
        label: status,
        bgClass: 'bg-slate-500/10',
        textClass: 'text-slate-400',
        borderClass: 'border-slate-500/30',
      };
  }
}

/**
 * Returns badge styling for scenario shock impact severity.
 */
export function getScenarioImpactBadge(returnPct: number): StatusBadgeConfig {
  if (returnPct <= -0.15) {
    return {
      label: 'Severe Impact',
      bgClass: 'bg-rose-500/15',
      textClass: 'text-rose-400',
      borderClass: 'border-rose-500/40',
    };
  } else if (returnPct <= -0.05) {
    return {
      label: 'Moderate Impact',
      bgClass: 'bg-amber-500/15',
      textClass: 'text-amber-400',
      borderClass: 'border-amber-500/40',
    };
  } else if (returnPct < 0) {
    return {
      label: 'Mild Impact',
      bgClass: 'bg-yellow-500/10',
      textClass: 'text-yellow-400',
      borderClass: 'border-yellow-500/30',
    };
  } else {
    return {
      label: 'Positive Impact',
      bgClass: 'bg-emerald-500/10',
      textClass: 'text-emerald-400',
      borderClass: 'border-emerald-500/30',
    };
  }
}

/**
 * Formats a VaR Model Type into human readable title.
 */
export function getVaRModelLabel(model: VaRModelType): string {
  switch (model) {
    case 'HISTORICAL_SIMULATION':
      return 'Historical Simulation (Non-Parametric)';
    case 'PARAMETRIC_NORMAL':
      return 'Parametric Delta-Normal (Gaussian)';
    case 'MONTE_CARLO_GAUSSIAN':
      return 'Monte Carlo Gaussian Simulation';
    default:
      return model;
  }
}

// ---------------------------------------------------------------------------
// Stage 117: Factor, Concentration, Currency, and Sector Risk Formatters
// ---------------------------------------------------------------------------

/**
 * Formats a factor loading beta (e.g. 1.042 -> "1.04", -0.22 -> "-0.22").
 */
export function formatFactorLoading(
  val: number | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  const sign = val > 0 ? '+' : '';
  return `${sign}${val.toFixed(decimals)}`;
}

/**
 * Formats Herfindahl-Hirschman Index (e.g. 0.3800 -> "0.3800").
 */
export function formatHHI(val: number | null | undefined, decimals: number = 4): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return val.toFixed(decimals);
}

/**
 * Formats effective number of holdings (e.g. 2.63158 -> "2.6").
 */
export function formatEffectiveHoldings(
  val: number | null | undefined,
  decimals: number = 1
): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return val.toFixed(decimals);
}

/**
 * Interprets concentration level based on standard antitrust / institutional thresholds.
 */
export function getConcentrationClassification(hhi: number): {
  label: string;
  badgeClass: string;
  description: string;
} {
  if (hhi < 0.15) {
    return {
      label: 'Diversified',
      badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      description: 'HHI < 0.15: Well diversified across holdings.',
    };
  }
  if (hhi <= 0.25) {
    return {
      label: 'Moderate',
      badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      description: '0.15 <= HHI <= 0.25: Moderate concentration.',
    };
  }
  return {
    label: 'High Concentration',
    badgeClass: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    description: 'HHI > 0.25: Significant capital concentration in top holdings.',
  };
}

/**
 * Returns badge styling for regression diagnostics.
 */
export function getModelDiagnosticStatusBadge(status: ModelDiagnosticStatus): StatusBadgeConfig {
  switch (status) {
    case 'HEALTHY':
      return {
        label: 'Healthy',
        bgClass: 'bg-emerald-500/10',
        textClass: 'text-emerald-400',
        borderClass: 'border-emerald-500/30',
      };
    case 'WARNING_COLLINEARITY':
      return {
        label: 'Collinear',
        bgClass: 'bg-amber-500/10',
        textClass: 'text-amber-400',
        borderClass: 'border-amber-500/30',
      };
    case 'WARNING_RANK_DEFICIENT':
      return {
        label: 'Rank Deficient',
        bgClass: 'bg-rose-500/10',
        textClass: 'text-rose-400',
        borderClass: 'border-rose-500/30',
      };
    case 'CRITICAL':
    default:
      return {
        label: 'Critical',
        bgClass: 'bg-rose-500/10',
        textClass: 'text-rose-400',
        borderClass: 'border-rose-500/30',
      };
  }
}
