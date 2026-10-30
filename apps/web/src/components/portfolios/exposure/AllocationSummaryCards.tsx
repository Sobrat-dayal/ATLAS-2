/**
 * Top institutional KPI summary cards for portfolio allocation & concentration.
 */

'use client';

import React from 'react';
import {
  formatHhi,
  formatMonetaryValue,
  formatWeightPct,
  getCompletenessBadge,
  getHhiConcentrationLevel,
} from '@/lib/portfolios/exposure/formatting';
import { PortfolioExposureRunResponse } from '@/lib/portfolios/exposure/types';

interface AllocationSummaryCardsProps {
  run: PortfolioExposureRunResponse | null;
  loading?: boolean;
}

export const AllocationSummaryCards: React.FC<AllocationSummaryCardsProps> = ({ run, loading }) => {
  if (loading || !run) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="bg-[#0f1523] border border-slate-800 rounded-lg p-3 animate-pulse h-20"
          />
        ))}
      </div>
    );
  }

  const hhiNum = parseFloat(run.concentration.herfindahl_index);
  const hhiLevel = getHhiConcentrationLevel(hhiNum);
  const completenessBadge = getCompletenessBadge(run.data_quality.completeness);

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
      {/* 1. Net Asset Value */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-3">
        <div className="text-[11px] font-medium tracking-wide uppercase text-slate-400">
          Portfolio NAV
        </div>
        <div className="text-lg font-bold text-slate-100 mt-1 font-mono">
          {formatMonetaryValue(run.total_nav, run.base_currency)}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">
          Gross: {formatMonetaryValue(run.gross_exposure, run.base_currency)}
        </div>
      </div>

      {/* 2. Cash Weight */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-3">
        <div className="text-[11px] font-medium tracking-wide uppercase text-slate-400">
          Cash & Equivalents
        </div>
        <div className="text-lg font-bold text-amber-400 mt-1 font-mono">
          {formatWeightPct(run.cash_weight)}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">
          {formatMonetaryValue(run.cash_value, run.base_currency)}
        </div>
      </div>

      {/* 3. Top 1 Holding Weight */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-3">
        <div className="text-[11px] font-medium tracking-wide uppercase text-slate-400">
          Top 1 Holding
        </div>
        <div className="text-lg font-bold text-slate-100 mt-1 font-mono">
          {formatWeightPct(run.concentration.top1_weight)}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">
          {run.security_weights[0] ? run.security_weights[0].symbol : '—'}
        </div>
      </div>

      {/* 4. Top 5 Holdings Weight */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-3">
        <div className="text-[11px] font-medium tracking-wide uppercase text-slate-400">
          Top 5 Concentration
        </div>
        <div className="text-lg font-bold text-slate-100 mt-1 font-mono">
          {formatWeightPct(run.concentration.top5_weight)}
        </div>
        <div className="text-[10px] text-slate-500 mt-0.5">
          Top 10: {formatWeightPct(run.concentration.top10_weight)}
        </div>
      </div>

      {/* 5. HHI & Effective Holdings */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-3">
        <div className="text-[11px] font-medium tracking-wide uppercase text-slate-400">
          HHI / Effective N
        </div>
        <div className="flex items-baseline space-x-2 mt-1">
          <span className="text-lg font-bold text-slate-100 font-mono">
            {formatHhi(run.concentration.herfindahl_index)}
          </span>
          <span className="text-xs text-slate-400 font-mono">
            (N={parseFloat(run.concentration.effective_number_of_holdings || '0').toFixed(1)})
          </span>
        </div>
        <div className="mt-1">
          <span
            className={`text-[9px] px-1.5 py-0.5 rounded font-medium border ${hhiLevel.bg} ${hhiLevel.color} ${hhiLevel.border}`}
          >
            {hhiLevel.label}
          </span>
        </div>
      </div>

      {/* 6. Audit & Reconciliation */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-3">
        <div className="text-[11px] font-medium tracking-wide uppercase text-slate-400">
          Audit Status
        </div>
        <div className="mt-1.5">
          <span
            className={`text-[10px] px-2 py-0.5 rounded font-medium ${
              run.reconciled
                ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/80'
                : 'bg-rose-950/60 text-rose-400 border border-rose-800/80'
            }`}
          >
            {run.reconciled ? '✓ 100% Reconciled' : '⚠ Discrepancy'}
          </span>
        </div>
        <div className="text-[10px] text-slate-500 mt-1 truncate">
          {completenessBadge.label}
        </div>
      </div>
    </div>
  );
};
