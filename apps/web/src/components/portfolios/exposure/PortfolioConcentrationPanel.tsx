/**
 * Portfolio Concentration & Position Weights Panel.
 */

'use client';

import React, { useState } from 'react';
import {
  formatHhi,
  formatMonetaryValue,
  formatWeightPct,
  getHhiConcentrationLevel,
} from '@/lib/portfolios/exposure/formatting';
import {
  ConcentrationSummaryResponse,
  IssuerWeightResponse,
  SecurityWeightResponse,
} from '@/lib/portfolios/exposure/types';

interface PortfolioConcentrationPanelProps {
  concentration: ConcentrationSummaryResponse | null;
  securities: SecurityWeightResponse[];
  issuers: IssuerWeightResponse[];
  baseCurrency?: string;
  loading?: boolean;
}

export const PortfolioConcentrationPanel: React.FC<PortfolioConcentrationPanelProps> = ({
  concentration,
  securities,
  issuers,
  baseCurrency = 'USD',
  loading,
}) => {
  const [scope, setScope] = useState<'SECURITIES' | 'ISSUERS'>('SECURITIES');

  if (loading || !concentration) {
    return (
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-4 animate-pulse h-64" />
    );
  }

  const hhiNum = parseFloat(concentration.herfindahl_index);
  const hhiLevel = getHhiConcentrationLevel(hhiNum);

  return (
    <div className="space-y-4">
      {/* Concentration Ladder */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Concentration Profile</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Herfindahl-Hirschman Index, Effective Holdings (N_eff), and Cumulative Quantile Ladders.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span
              className={`text-xs px-2 py-0.5 rounded font-medium border ${hhiLevel.bg} ${hhiLevel.color} ${hhiLevel.border}`}
            >
              HHI: {formatHhi(concentration.herfindahl_index)} ({hhiLevel.label})
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="bg-slate-900/60 border border-slate-800 p-2.5 rounded text-center">
            <div className="text-[10px] uppercase tracking-wider text-slate-400">Top 1 Weight</div>
            <div className="text-base font-bold text-slate-100 font-mono mt-1">
              {formatWeightPct(concentration.top1_weight)}
            </div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 p-2.5 rounded text-center">
            <div className="text-[10px] uppercase tracking-wider text-slate-400">Top 3 Weight</div>
            <div className="text-base font-bold text-slate-100 font-mono mt-1">
              {formatWeightPct(concentration.top3_weight)}
            </div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 p-2.5 rounded text-center">
            <div className="text-[10px] uppercase tracking-wider text-slate-400">Top 5 Weight</div>
            <div className="text-base font-bold text-slate-100 font-mono mt-1">
              {formatWeightPct(concentration.top5_weight)}
            </div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 p-2.5 rounded text-center">
            <div className="text-[10px] uppercase tracking-wider text-slate-400">Top 10 Weight</div>
            <div className="text-base font-bold text-slate-100 font-mono mt-1">
              {formatWeightPct(concentration.top10_weight)}
            </div>
          </div>
          <div className="bg-slate-900/60 border border-slate-800 p-2.5 rounded text-center">
            <div className="text-[10px] uppercase tracking-wider text-slate-400">Effective N</div>
            <div className="text-base font-bold text-emerald-400 font-mono mt-1">
              {parseFloat(concentration.effective_number_of_holdings || '0').toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Holdings List with Scope Toggle */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h3 className="text-sm font-semibold text-slate-200">Concentration Rankings</h3>
            <div className="flex items-center bg-slate-900 border border-slate-800 rounded p-0.5 text-xs">
              <button
                onClick={() => setScope('SECURITIES')}
                className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                  scope === 'SECURITIES'
                    ? 'bg-slate-800 text-slate-100'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Individual Securities ({securities.length})
              </button>
              <button
                onClick={() => setScope('ISSUERS')}
                className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                  scope === 'ISSUERS'
                    ? 'bg-slate-800 text-slate-100'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Economic Issuers ({issuers.length})
              </button>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          {scope === 'SECURITIES' ? (
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-[#0a0e17] text-[11px] text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4 font-medium w-12 text-center">#</th>
                  <th className="py-2.5 px-4 font-medium">Security</th>
                  <th className="py-2.5 px-4 font-medium text-right">Shares</th>
                  <th className="py-2.5 px-4 font-medium text-right">Base Value</th>
                  <th className="py-2.5 px-4 font-medium text-right">Direct Wt</th>
                  <th className="py-2.5 px-4 font-medium text-right">Look-Through Wt</th>
                  <th className="py-2.5 px-4 font-medium text-right">Total Weight</th>
                  <th className="py-2.5 px-4 font-medium">Weight Bar</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {securities.slice(0, 25).map((sec, idx) => {
                  const weightVal = parseFloat(sec.weight);
                  const widthPct = Math.min(100, Math.max(1, weightVal * 100));

                  return (
                    <tr key={sec.instrument_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-2.5 px-4 text-center font-mono text-slate-500">
                        {idx + 1}
                      </td>
                      <td className="py-2.5 px-4 font-medium text-slate-200">
                        <div className="flex items-baseline space-x-2">
                          <span className="font-mono text-slate-100 font-bold">{sec.symbol}</span>
                          <span className="text-[11px] text-slate-400 truncate max-w-[160px]">
                            {sec.name}
                          </span>
                        </div>
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono text-slate-400">
                        {parseFloat(sec.effective_shares).toLocaleString('en-US')}
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono text-slate-200">
                        {formatMonetaryValue(sec.base_value, baseCurrency)}
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono text-slate-300">
                        {formatWeightPct(sec.direct_weight)}
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono text-slate-400">
                        {parseFloat(sec.look_through_weight || '0') > 0
                          ? formatWeightPct(sec.look_through_weight)
                          : '—'}
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono font-bold text-slate-100">
                        {formatWeightPct(sec.weight)}
                      </td>
                      <td className="py-2.5 px-4 min-w-[120px]">
                        <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
                          <div
                            className="bg-blue-500 h-full rounded-full"
                            style={{ width: `${widthPct}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-[#0a0e17] text-[11px] text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4 font-medium w-12 text-center">#</th>
                  <th className="py-2.5 px-4 font-medium">Ultimate Economic Issuer</th>
                  <th className="py-2.5 px-4 font-medium">Country</th>
                  <th className="py-2.5 px-4 font-medium text-right">Consolidated Value</th>
                  <th className="py-2.5 px-4 font-medium text-right">Issuer Weight</th>
                  <th className="py-2.5 px-4 font-medium">Weight Bar</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {issuers.slice(0, 25).map((iss, idx) => {
                  const weightVal = parseFloat(iss.weight);
                  const widthPct = Math.min(100, Math.max(1, weightVal * 100));

                  return (
                    <tr key={iss.issuer_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-2.5 px-4 text-center font-mono text-slate-500">
                        {idx + 1}
                      </td>
                      <td className="py-2.5 px-4 font-medium text-slate-200">
                        <div className="font-semibold text-slate-100">{iss.issuer_name}</div>
                        <div className="text-[10px] text-slate-500 font-mono">
                          {iss.constituent_instruments.join(', ')}
                        </div>
                      </td>
                      <td className="py-2.5 px-4">
                        <span className="px-1.5 py-0.5 bg-slate-800 text-[10px] font-mono rounded text-slate-400">
                          {iss.country_code}
                        </span>
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono text-slate-200">
                        {formatMonetaryValue(iss.base_value, baseCurrency)}
                      </td>
                      <td className="py-2.5 px-4 text-right font-mono font-bold text-slate-100">
                        {formatWeightPct(iss.weight)}
                      </td>
                      <td className="py-2.5 px-4 min-w-[120px]">
                        <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
                          <div
                            className="bg-indigo-500 h-full rounded-full"
                            style={{ width: `${widthPct}%` }}
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};
