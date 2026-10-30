/**
 * Historical Allocation Drift and Date-to-Date Changes Panel.
 */

'use client';

import React, { useState } from 'react';
import {
  formatBps,
  formatMonetaryValue,
  formatWeightPct,
} from '@/lib/portfolios/exposure/formatting';
import {
  AllocationChangeResponse,
  ExposureDimension,
} from '@/lib/portfolios/exposure/types';

interface HistoricalAllocationPanelProps {
  changes: AllocationChangeResponse[];
  loading?: boolean;
  onFetchChanges: (startDate: string, endDate: string, dimension: ExposureDimension) => void;
  baseCurrency?: string;
}

export const HistoricalAllocationPanel: React.FC<HistoricalAllocationPanelProps> = ({
  changes,
  loading,
  onFetchChanges,
  baseCurrency = 'USD',
}) => {
  const [dimension, setDimension] = useState<ExposureDimension>('ASSET_CLASS');
  const [startDate, setStartDate] = useState<string>(
    new Date(Date.now() - 30 * 86400000).toISOString().split('T')[0]
  );
  const [endDate, setEndDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );

  const handleApply = () => {
    onFetchChanges(startDate, endDate, dimension);
  };

  return (
    <div className="bg-[#0f1523] border border-slate-800 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Historical Allocation Drift</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Date-to-date allocation change (Δw = w_t2 - w_t1) in percentage points and basis points.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-2">
          <select
            value={dimension}
            onChange={(e) => setDimension(e.target.value as ExposureDimension)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded px-2.5 py-1 focus:outline-none"
          >
            <option value="ASSET_CLASS">Asset Class</option>
            <option value="SECTOR">GICS Sector</option>
            <option value="COUNTRY">Country</option>
            <option value="CURRENCY">Currency</option>
          </select>

          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded px-2 py-1 focus:outline-none"
          />
          <span className="text-slate-500 text-xs">to</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded px-2 py-1 focus:outline-none"
          />

          <button
            onClick={handleApply}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded transition-colors"
          >
            Compare
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-400">Loading historical drift comparison...</div>
      ) : changes.length === 0 ? (
        <div className="p-8 text-center text-slate-400">
          <p className="text-sm">No historical drift data computed for this period.</p>
          <p className="text-xs text-slate-500 mt-1">
            Select dates above and click Compare to evaluate date-to-date allocation drift.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#0a0e17] text-[11px] text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4 font-medium">Category</th>
                <th className="py-2.5 px-4 font-medium text-right">Start Weight ({startDate})</th>
                <th className="py-2.5 px-4 font-medium text-right">End Weight ({endDate})</th>
                <th className="py-2.5 px-4 font-medium text-right">Weight Change (pp)</th>
                <th className="py-2.5 px-4 font-medium text-right">Drift (bps)</th>
                <th className="py-2.5 px-4 font-medium text-right">Start Value</th>
                <th className="py-2.5 px-4 font-medium text-right">End Value</th>
                <th className="py-2.5 px-4 font-medium text-right">Value Change</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {changes.map((c) => {
                const bps = c.weight_change_bps;
                const isPositive = bps > 0;
                const isNegative = bps < 0;

                return (
                  <tr key={c.category_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-4 font-medium text-slate-200">
                      {c.category_label}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-400">
                      {formatWeightPct(c.start_weight)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-200 font-medium">
                      {formatWeightPct(c.end_weight)}
                    </td>
                    <td
                      className={`py-2.5 px-4 text-right font-mono font-bold ${
                        isPositive
                          ? 'text-emerald-400'
                          : isNegative
                          ? 'text-rose-400'
                          : 'text-slate-400'
                      }`}
                    >
                      {formatWeightPct(c.weight_change_pct)}
                    </td>
                    <td
                      className={`py-2.5 px-4 text-right font-mono font-bold ${
                        isPositive
                          ? 'text-emerald-400'
                          : isNegative
                          ? 'text-rose-400'
                          : 'text-slate-400'
                      }`}
                    >
                      {formatBps(c.weight_change_bps)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-400">
                      {formatMonetaryValue(c.start_value, baseCurrency)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-200">
                      {formatMonetaryValue(c.end_value, baseCurrency)}
                    </td>
                    <td
                      className={`py-2.5 px-4 text-right font-mono ${
                        parseFloat(c.value_change || '0') >= 0
                          ? 'text-emerald-400'
                          : 'text-rose-400'
                      }`}
                    >
                      {formatMonetaryValue(c.value_change, baseCurrency)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

