/**
 * ATLAS Financial Risk Foundation — Formatting Utilities (Stage 115).
 *
 * Provides institutional formatting for risk metrics: volatility, variance,
 * drawdowns, beta, tracking error, condition numbers, and status badges.
 */

import {
  DataCoverageStatus,
  DrawdownEpisodeStatus,
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

