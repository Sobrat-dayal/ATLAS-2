/**
 * Currency Denomination Exposure Panel.
 */

'use client';

import React from 'react';
import { formatMonetaryValue, formatWeightPct } from '@/lib/portfolios/exposure/formatting';
import { ExposureDimensionResponse } from '@/lib/portfolios/exposure/types';

interface CurrencyExposurePanelProps {
  data: ExposureDimensionResponse | null;
  baseCurrency?: string;
  loading?: boolean;
}

export const CurrencyExposurePanel: React.FC<CurrencyExposurePanelProps> = ({
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
          <h3 className="text-sm font-semibold text-slate-200">Currency Denomination Exposure</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Valuation denomination in base currency ({baseCurrency}) via canonical spot rates.
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
            Total: {formatWeightPct(data.total_weight)}
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-[#0a0e17] text-[11px] text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-4 font-medium">Currency Code</th>
              <th className="py-2.5 px-4 font-medium text-right">Value ({baseCurrency})</th>
              <th className="py-2.5 px-4 font-medium text-right">Portfolio Weight</th>
              <th className="py-2.5 px-4 font-medium">Relative Share</th>
              <th className="py-2.5 px-4 font-medium text-right">Holdings</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {data.categories.map((cat) => {
              const weightVal = parseFloat(cat.weight);
              const widthPct = Math.min(100, Math.max(1, weightVal * 100));

              return (
                <tr key={cat.category_id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5 px-4 font-medium text-slate-200 flex items-center space-x-2">
                    <span className="px-1.5 py-0.5 bg-slate-800 font-mono text-[11px] font-semibold text-amber-400 rounded border border-slate-700">
                      {cat.category_id}
                    </span>
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
                        className="bg-amber-500 h-full rounded-full"
                        style={{ width: `${widthPct}%` }}
                      />
                    </div>
                  </td>
                  <td className="py-2.5 px-4 text-right font-mono text-slate-400">
                    {cat.position_count}
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

