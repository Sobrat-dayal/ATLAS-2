/**
 * ATLAS Portfolios V1 — Optimization Formatting & Display Utilities (Stage 114).
 *
 * Provides institutionally precise formatting for percentages, basis points,
 * currencies, status badges, and objective descriptions.
 */

import { FeasibilityStatus, OptimizationObjective, SolverStatus } from './types';

/**
 * Formats a decimal return or weight (e.g., 0.1250) into percentage string (e.g., "12.50%").
 */
export function formatPercent(
  val: string | number | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || val === '') return '—';
  const num = typeof val === 'number' ? val : parseFloat(val);
  if (isNaN(num)) return '—';
  const sign = num > 0 ? '+' : '';
  return `${sign}${(num * 100).toFixed(decimals)}%`;
}

/**
 * Formats a decimal return into unsigned percentage string (e.g. for weights "12.50%").
 */
export function formatWeightPercent(
  val: string | number | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || val === '') return '0.00%';
  const num = typeof val === 'number' ? val : parseFloat(val);
  if (isNaN(num)) return '0.00%';
  return `${(num * 100).toFixed(decimals)}%`;
}

/**
 * Formats a decimal value into Basis Points (e.g. 0.0125 -> "+125 bps").
 */
export function formatBps(val: string | number | null | undefined): string {
  if (val === null || val === undefined || val === '') return '—';
  const num = typeof val === 'number' ? val : parseFloat(val);
  if (isNaN(num)) return '—';
  const bps = Math.round(num * 10000);
  const sign = bps > 0 ? '+' : '';
  return `${sign}${bps.toLocaleString()} bps`;
}

/**
 * Formats a monetary amount into localized currency (e.g. "$1,250,000.00").
 */
export function formatCurrency(
  val: string | number | null | undefined,
  currency: string = 'USD'
): string {
  if (val === null || val === undefined || val === '') return '—';
  const num = typeof val === 'number' ? val : parseFloat(val);
  if (isNaN(num)) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

/**
 * Formats a generic float number.
 */
export function formatNumber(
  val: string | number | null | undefined,
  decimals: number = 2
): string {
  if (val === null || val === undefined || val === '') return '—';
  const num = typeof val === 'number' ? val : parseFloat(val);
  if (isNaN(num)) return '—';
  return num.toFixed(decimals);
}

/**
 * Returns UI badge metadata for Solver convergence status.
 */
export function getSolverStatusBadge(status: SolverStatus): {
  label: string;
  variant: 'positive' | 'warning' | 'negative' | 'default';
  className: string;
  description: string;
} {
  switch (status) {
    case 'OPTIMAL':
      return {
        label: 'OPTIMAL',
        variant: 'positive',
        className: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        description: 'Solver converged successfully to global optimum satisfying all constraints.',
      };
    case 'OPTIMAL_INACCURATE':
      return {
        label: 'CONVERGED (INACCURATE)',
        variant: 'warning',
        className: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        description: 'Solver converged within relaxed numerical tolerances.',
      };
    case 'INFEASIBLE':
      return {
        label: 'INFEASIBLE',
        variant: 'negative',
        className: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
        description: 'No portfolio exists that satisfies all active constraints.',
      };
    case 'UNBOUNDED':
      return {
        label: 'UNBOUNDED',
        variant: 'negative',
        className: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
        description: 'Optimization problem formulation has an unbounded solution.',
      };
    case 'TIMEOUT':
      return {
        label: 'TIMEOUT',
        variant: 'warning',
        className: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        description: 'Solver time limit exceeded before convergence.',
      };
    case 'NUMERICAL_FAILURE':
    case 'MAX_ITERATIONS_EXCEEDED':
    default:
      return {
        label: status || 'NUMERICAL_FAILURE',
        variant: 'negative',
        className: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
        description: 'Solver encountered numerical singularity or exceeded iteration limits.',
      };
  }
}

/**
 * Returns UI badge metadata for constraint feasibility status.
 */
export function getFeasibilityBadge(status: FeasibilityStatus): {
  label: string;
  variant: 'positive' | 'warning' | 'negative';
  className: string;
} {
  switch (status) {
    case 'FEASIBLE':
      return {
        label: 'FEASIBLE',
        variant: 'positive',
        className: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      };
    case 'FEASIBLE_WITH_SLACK_WARNING':
      return {
        label: 'TIGHT SLACK',
        variant: 'warning',
        className: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      };
    case 'INFEASIBLE':
    default:
      return {
        label: 'INFEASIBLE',
        variant: 'negative',
        className: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      };
  }
}

/**
 * Returns trade direction visual badge properties.
 */
export function getTradeDirectionBadge(direction: string): {
  label: string;
  className: string;
} {
  switch (direction) {
    case 'BUY':
      return {
        label: 'BUY',
        className: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      };
    case 'SELL':
      return {
        label: 'SELL',
        className: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      };
    case 'HOLD':
    default:
      return {
        label: 'HOLD',
        className: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
      };
  }
}

/**
 * User-facing canonical name for mathematical objective.
 */
export function getObjectiveLabel(objective: OptimizationObjective): string {
  switch (objective) {
    case 'MINIMUM_VARIANCE':
      return 'Global Minimum Variance';
    case 'MEAN_VARIANCE_UTILITY':
      return 'Mean-Variance Utility';
    case 'TARGET_RETURN_MIN_VARIANCE':
      return 'Target Return Min Variance';
    case 'MAXIMUM_EXPECTED_RETURN':
      return 'Maximum Expected Return';
    case 'MAXIMUM_SHARPE':
      return 'Maximum Sharpe Ratio';
    case 'EFFICIENT_FRONTIER':
      return 'Efficient Frontier Generator';
    case 'BENCHMARK_TRACKING_ERROR':
      return 'Tracking Error Minimization';
    case 'RISK_PARITY':
      return 'Equal Risk Contribution (Risk Parity)';
    default:
      return objective;
  }
}
