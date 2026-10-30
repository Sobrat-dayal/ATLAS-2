/**
 * ATLAS Portfolios V1 — Formatting Utilities for Attribution Analytics (Stage 113).
 */

import { AttributionCompleteness, ReconciliationStatus } from './types';

export function formatPercent(
  value: string | number | null | undefined,
  decimals = 2,
  includeSign = false
): string {
  if (value === null || value === undefined) return '—';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  const pct = Math.abs(num) <= 1.0 && num !== 0 ? num * 100 : num;
  const sign = includeSign && pct > 0 ? '+' : '';
  return `${sign}${pct.toFixed(decimals)}%`;
}

export function formatWeight(
  value: string | number | null | undefined,
  decimals = 2
): string {
  if (value === null || value === undefined) return '0.00%';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0.00%';
  const pct = Math.abs(num) <= 1.0 && num !== 0 ? num * 100 : num;
  return `${pct.toFixed(decimals)}%`;
}

export function formatBps(
  value: string | number | null | undefined,
  decimals = 1
): string {
  if (value === null || value === undefined) return '—';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  // If decimal e.g. 0.0040 -> 40.0 bps. If already in bps e.g. 40, check magnitude.
  const bps = Math.abs(num) < 1.0 && num !== 0 ? num * 10000 : num;
  const prefix = bps > 0 ? '+' : '';
  return `${prefix}${bps.toFixed(decimals)} bps`;
}

export function getEffectColorClass(
  value: string | number | null | undefined
): string {
  if (value === null || value === undefined) return 'text-atlas-text-muted';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num) || Math.abs(num) < 0.00001) return 'text-atlas-text-secondary';
  return num > 0 ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium';
}

export function getEffectBgClass(
  value: string | number | null | undefined
): string {
  if (value === null || value === undefined) return 'bg-atlas-surface-2';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num) || Math.abs(num) < 0.00001) return 'bg-atlas-surface-2';
  return num > 0 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20';
}

export function getReconciliationBadge(status: ReconciliationStatus): {
  label: string;
  variant: 'default' | 'outline' | 'secondary' | 'destructive';
  colorClass: string;
} {
  switch (status) {
    case 'RECONCILED':
      return {
        label: 'Exact Reconciled',
        variant: 'default',
        colorClass: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      };
    case 'RECONCILED_WITH_ROUNDING_TOLERANCE':
      return {
        label: 'Reconciled (Tolerance)',
        variant: 'default',
        colorClass: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      };
    case 'PARTIAL_COVERAGE':
      return {
        label: 'Partial Coverage',
        variant: 'secondary',
        colorClass: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      };
    case 'UNRECONCILED':
    default:
      return {
        label: 'Unreconciled Residual',
        variant: 'destructive',
        colorClass: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
      };
  }
}

export function getCompletenessBadge(completeness: AttributionCompleteness): {
  label: string;
  colorClass: string;
} {
  switch (completeness) {
    case 'FULL_COVERAGE':
      return {
        label: '100% GICS & Benchmark Coverage',
        colorClass: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      };
    case 'PARTIAL_COVERAGE':
      return {
        label: 'Partial Holdings Coverage',
        colorClass: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      };
    case 'BENCHMARK_CONSTITUENTS_MISSING':
      return {
        label: 'Benchmark Constituents Missing',
        colorClass: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      };
    case 'UNMAPPED_CATEGORIES':
    default:
      return {
        label: 'Unmapped Categories Present',
        colorClass: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
      };
  }
}

export function formatDateRange(startDate: string, endDate: string): string {
  try {
    const s = new Date(startDate).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
    const e = new Date(endDate).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
    return `${s} — ${e}`;
  } catch {
    return `${startDate} — ${endDate}`;
  }
}

