/**
 * Asset-Class Allocation Panel (Equities, Funds, Fixed Income, Cash).
 */

'use client';

import React from 'react';
import { formatMonetaryValue, formatWeightPct } from '@/lib/portfolios/exposure/formatting';
import { ExposureDimensionResponse } from '@/lib/portfolios/exposure/types';

interface AssetClassAllocationPanelProps {
  data: ExposureDimensionResponse | null;
  baseCurrency?: string;
  loading?: boolean;
}

export const AssetClassAllocationPanel: React.FC<AssetClassAllocationPanelProps> = ({
  data,
  baseCurrency = 'USD',
  loading,
}) => {
  if (loading || !data) {
    return (
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-4 animate-pulse h-64" />
    );
  }

  return (
    <div className="bg-[#0f1523] border border-slate-800 rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Asset-Class Allocation</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Canonical classification into distinct macro asset categories.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span
            className={`text-[10px] px-2 py-0.5 rounded font-mono ${
              data.reconciled
                ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800'
                : 'bg-rose-950/60 text-rose-400 border border-rose-800'
            }`}
          >
            Sum: {formatWeightPct(data.total_weight)}
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-[#0a0e17] text-[11px] text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-4 font-medium">Asset Class</th>
              <th className="py-2.5 px-4 font-medium text-right">Base Value</th>
              <th className="py-2.5 px-4 font-medium text-right">Weight</th>
              <th className="py-2.5 px-4 font-medium">Allocation Share</th>
              <th className="py-2.5 px-4 font-medium text-right">Holdings</th>
              <th className="py-2.5 px-4 font-medium text-right">Look-Through</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {data.categories.map((cat) => {
              const weightVal = parseFloat(cat.weight);
              const widthPct = Math.min(100, Math.max(1, weightVal * 100));

              return (
                <tr key={cat.category_id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5 px-4 font-medium text-slate-200 flex items-center space-x-2">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        cat.category_id === 'EQUITY'
                          ? 'bg-blue-400'
                          : cat.category_id === 'FUND'
                          ? 'bg-indigo-400'
                          : cat.category_id === 'FIXED_INCOME'
                          ? 'bg-cyan-400'
                          : cat.category_id === 'CASH'
                          ? 'bg-amber-400'
                          : 'bg-slate-500'
                      }`}
                    />
                    <span>{cat.category_label}</span>
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono text-slate-200">
                    {formatMonetaryValue(cat.base_value, baseCurrency)}
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono font-medium text-slate-100">
                    {formatWeightPct(cat.weight)}
                  </td>
                  <td className="py-2.5 px-4 min-w-[140px]">
                    <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                      <div
                        className={`h-full rounded-full ${
                          cat.category_id === 'EQUITY'
                            ? 'bg-blue-500'
                            : cat.category_id === 'FUND'
                            ? 'bg-indigo-500'
                            : cat.category_id === 'FIXED_INCOME'
                            ? 'bg-cyan-500'
                            : cat.category_id === 'CASH'
                            ? 'bg-amber-500'
                            : 'bg-slate-500'
                        }`}
                        style={{ width: `${widthPct}%` }}
                      />
                    </div>
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono text-slate-400">
                    {cat.position_count}
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono text-slate-400">
                    {parseFloat(cat.look_through_value || '0') > 0
                      ? formatMonetaryValue(cat.look_through_value, baseCurrency)
                      : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

