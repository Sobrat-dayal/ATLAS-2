/**
 * ATLAS Portfolios V1 — Formatting Utilities for Allocation & Exposure (Stage 112).
 */

import { ExposureDataCompleteness, LookThroughStatus } from './types';

export function formatWeightPct(value: string | number | null | undefined, decimals = 2): string {
  if (value === null || value === undefined) return '—';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  // If value is fractional (e.g. 0.50), convert to percentage
  const pct = Math.abs(num) <= 1.0 && num !== 0 ? num * 100 : num;
  return `${pct.toFixed(decimals)}%`;
}

export function formatMonetaryValue(
  value: string | number | null | undefined,
  currency = 'USD',
  decimals = 2
): string {
  if (value === null || value === undefined) return '—';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
}

export function formatBps(bps: number | null | undefined): string {
  if (bps === null || bps === undefined) return '—';
  const prefix = bps > 0 ? '+' : '';
  return `${prefix}${bps} bps`;
}

export function formatHhi(value: string | number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '—';
  // Standard index is between 0 and 10,000
  const indexVal = num <= 1.0 ? num * 10000 : num;
  return Math.round(indexVal).toLocaleString('en-US');
}

export function getHhiConcentrationLevel(hhiNum: number): {
  label: string;
  color: string;
  bg: string;
  border: string;
} {
  const normalized = hhiNum <= 1.0 ? hhiNum * 10000 : hhiNum;
  if (normalized < 1500) {
    return {
      label: 'Diversified',
      color: 'text-emerald-400',
      bg: 'bg-emerald-950/40',
      border: 'border-emerald-800/60',
    };
  }
  if (normalized <= 2500) {
    return {
      label: 'Moderately Concentrated',
      color: 'text-amber-400',
      bg: 'bg-amber-950/40',
      border: 'border-amber-800/60',
    };
  }
  return {
    label: 'Highly Concentrated',
    color: 'text-rose-400',
    bg: 'bg-rose-950/40',
    border: 'border-rose-800/60',
  };
}

export function getCompletenessBadge(status: ExposureDataCompleteness): {
  label: string;
  variant: 'emerald' | 'amber' | 'rose' | 'muted';
} {
  switch (status) {
    case 'COMPLETE':
      return { label: 'Verified Complete', variant: 'emerald' };
    case 'COMPLETE_WITH_WARNINGS':
      return { label: 'Complete (Warnings)', variant: 'amber' };
    case 'PARTIAL_CLASSIFICATION':
      return { label: 'Partial Classification', variant: 'amber' };
    case 'PARTIAL_VALUATION':
      return { label: 'Missing Valuation', variant: 'rose' };
    case 'PARTIAL_FX':
      return { label: 'Missing FX', variant: 'rose' };
    case 'EMPTY':
    default:
      return { label: 'Uncomputed', variant: 'muted' };
  }
}

export function getLookThroughStatusBadge(status: LookThroughStatus): {
  label: string;
  variant: 'emerald' | 'amber' | 'rose' | 'muted';
} {
  switch (status) {
    case 'FULL_LOOK_THROUGH':
      return { label: 'Full Look-Through', variant: 'emerald' };
    case 'PARTIAL_LOOK_THROUGH':
      return { label: 'Partial Look-Through', variant: 'amber' };
    case 'DEPTH_EXCEEDED':
      return { label: 'Max Depth Exceeded', variant: 'amber' };
    case 'DATA_UNAVAILABLE':
      return { label: 'Holdings Unavailable', variant: 'rose' };
    case 'UNSUPPORTED':
    default:
      return { label: 'Direct Only', variant: 'muted' };
  }
}

