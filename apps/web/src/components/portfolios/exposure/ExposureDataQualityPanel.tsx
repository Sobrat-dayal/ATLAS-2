/**
 * Exposure Data Quality, Completeness & Reconciliation Audit Diagnostics Panel.
 */

'use client';

import React from 'react';
import { formatWeightPct, getCompletenessBadge } from '@/lib/portfolios/exposure/formatting';
import { ExposureDataQualityResponse } from '@/lib/portfolios/exposure/types';

interface ExposureDataQualityPanelProps {
  dataQuality: ExposureDataQualityResponse | null;
  inputHash?: string;
  calculationVersion?: string;
  loading?: boolean;
}

export const ExposureDataQualityPanel: React.FC<ExposureDataQualityPanelProps> = ({
  dataQuality,
  inputHash,
  calculationVersion = '1.0.0',
  loading,
}) => {
  if (loading || !dataQuality) {
    return (
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-4 animate-pulse h-64" />
    );
  }

  const badge = getCompletenessBadge(dataQuality.completeness);

  return (
    <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-4 space-y-4">
      <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">
            Data Quality & Reconciliation Audit
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Invariant verification, classification coverage, and reproducible execution hash.
          </p>
        </div>
        <span
          className={`text-xs px-2.5 py-1 rounded font-medium border ${
            badge.variant === 'emerald'
              ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800'
              : badge.variant === 'amber'
              ? 'bg-amber-950/60 text-amber-400 border-amber-800'
              : 'bg-rose-950/60 text-rose-400 border-rose-800'
          }`}
        >
          {badge.label}
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-slate-900/60 border border-slate-800 p-3 rounded">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">
            Classification Coverage
          </div>
          <div className="text-base font-bold text-slate-100 font-mono mt-1">
            {formatWeightPct(dataQuality.classification_coverage_ratio)}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            {dataQuality.classified_positions} of {dataQuality.total_positions} positions
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-3 rounded">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">
            Valuation Coverage
          </div>
          <div className="text-base font-bold text-slate-100 font-mono mt-1">
            {formatWeightPct(dataQuality.valuation_coverage_ratio)}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Canonical exchange marks</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-3 rounded">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">
            FX Rate Coverage
          </div>
          <div className="text-base font-bold text-slate-100 font-mono mt-1">
            {formatWeightPct(dataQuality.fx_coverage_ratio)}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">Verified currency conversion</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 p-3 rounded">
          <div className="text-[10px] text-slate-400 uppercase tracking-wider">
            Partition Invariant
          </div>
          <div className="text-base font-bold text-emerald-400 font-mono mt-1">
            {dataQuality.reconciled ? 'Reconciled (100%)' : 'Discrepancy'}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5 font-mono">
            Δ = {dataQuality.reconciliation_discrepancy || '0.000000'}
          </div>
        </div>
      </div>

      {/* Warnings & Diagnostics */}
      {dataQuality.warnings.length > 0 && (
        <div className="bg-amber-950/20 border border-amber-800/60 rounded p-3 text-xs text-amber-300">
          <div className="font-semibold text-amber-200 mb-1">Audit Warnings:</div>
          <ul className="list-disc pl-4 space-y-0.5">
            {dataQuality.warnings.map((w, idx) => (
              <li key={idx}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Reproducibility Manifest */}
      <div className="bg-slate-900/40 border border-slate-800 rounded p-3 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="text-slate-400">
          Calculation Version: <span className="font-mono text-slate-200">{calculationVersion}</span>
        </div>
        {inputHash && (
          <div className="text-slate-400 flex items-center space-x-2">
            <span>Input Hash (SHA-256):</span>
            <span className="font-mono text-slate-300 text-[11px] bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
              {inputHash.substring(0, 16)}...
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

