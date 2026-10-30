/**
 * Fund & ETF Look-Through Decomposition and Cross-Fund Overlap Panel.
 */

'use client';

import React, { useState } from 'react';
import {
  formatMonetaryValue,
  formatWeightPct,
  getLookThroughStatusBadge,
} from '@/lib/portfolios/exposure/formatting';
import {
  CrossFundOverlapResponse,
  FundLookThroughResponse,
} from '@/lib/portfolios/exposure/types';

interface FundLookThroughPanelProps {
  funds: FundLookThroughResponse[];
  overlaps: CrossFundOverlapResponse[];
  baseCurrency?: string;
  loading?: boolean;
}

export const FundLookThroughPanel: React.FC<FundLookThroughPanelProps> = ({
  funds,
  overlaps,
  baseCurrency = 'USD',
  loading,
}) => {
  const [selectedFundId, setSelectedFundId] = useState<string | null>(
    funds.length > 0 ? funds[0].fund_instrument_id : null
  );

  if (loading) {
    return (
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-4 animate-pulse h-64" />
    );
  }

  if (funds.length === 0) {
    return (
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg p-8 text-center text-slate-400">
        <p className="text-sm">No funds or ETFs detected in this portfolio.</p>
        <p className="text-xs text-slate-500 mt-1">
          Add an ETF holding (e.g. SPY, QQQ) to view constituent look-through decomposition and cross-fund overlap.
        </p>
      </div>
    );
  }

  const selectedFund =
    funds.find((f) => f.fund_instrument_id === selectedFundId) || funds[0];

  return (
    <div className="space-y-4">
      {/* 1. Cross-Fund Constituent Overlap Analysis */}
      {overlaps.length > 0 && (
        <div className="bg-[#0f1523] border border-slate-800 rounded-lg overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">
                Cross-Fund Constituent Overlap
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Underlying securities held simultaneously across multiple ETF/mutual fund positions.
              </p>
            </div>
            <span className="text-xs bg-indigo-950/60 text-indigo-400 border border-indigo-800 px-2 py-0.5 rounded font-mono">
              {overlaps.length} Overlapping Positions
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-[#0a0e17] text-[11px] text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4 font-medium">Underlying Security</th>
                  <th className="py-2.5 px-4 font-medium">Funds Involved</th>
                  <th className="py-2.5 px-4 font-medium text-right">Combined Effective Value</th>
                  <th className="py-2.5 px-4 font-medium text-right">Effective Portfolio Weight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {overlaps.slice(0, 15).map((ov) => (
                  <tr key={ov.constituent_symbol} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-4 font-medium text-slate-200">
                      <span className="font-bold font-mono text-slate-100">{ov.constituent_symbol}</span>
                      <span className="ml-2 text-slate-400 text-[11px]">{ov.constituent_name}</span>
                    </td>
                    <td className="py-2.5 px-4">
                      <div className="flex items-center space-x-1.5">
                        {ov.funds_involved.map((f) => (
                          <span
                            key={f}
                            className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 text-[10px] font-mono rounded text-slate-300"
                          >
                            {f}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-200">
                      {formatMonetaryValue(ov.total_effective_value, baseCurrency)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono font-bold text-indigo-400">
                      {formatWeightPct(ov.total_effective_weight)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 2. Individual Fund Constituent Expansion */}
      <div className="bg-[#0f1523] border border-slate-800 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h3 className="text-sm font-semibold text-slate-200">Constituent Look-Through</h3>
            <div className="flex items-center bg-slate-900 border border-slate-800 rounded p-0.5 text-xs">
              {funds.map((f) => (
                <button
                  key={f.fund_instrument_id}
                  onClick={() => setSelectedFundId(f.fund_instrument_id)}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                    selectedFund.fund_instrument_id === f.fund_instrument_id
                      ? 'bg-slate-800 text-slate-100'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {f.fund_symbol}
                </button>
              ))}
            </div>
          </div>
          {selectedFund && (
            <div className="flex items-center space-x-3">
              <span className="text-xs text-slate-400">
                Fund NAV: <strong className="font-mono text-slate-200">{formatMonetaryValue(selectedFund.fund_base_value, baseCurrency)}</strong> ({formatWeightPct(selectedFund.fund_weight_in_portfolio)})
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800 font-mono">
                {getLookThroughStatusBadge(selectedFund.status).label}
              </span>
            </div>
          )}
        </div>

        {selectedFund && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-[#0a0e17] text-[11px] text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4 font-medium">Constituent</th>
                  <th className="py-2.5 px-4 font-medium">Sector</th>
                  <th className="py-2.5 px-4 font-medium">Country</th>
                  <th className="py-2.5 px-4 font-medium text-right">Weight in Fund</th>
                  <th className="py-2.5 px-4 font-medium text-right">Effective Value</th>
                  <th className="py-2.5 px-4 font-medium text-right">Portfolio Weight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {selectedFund.constituents.map((c) => (
                  <tr key={c.constituent_instrument_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-4 font-medium text-slate-200">
                      <span className="font-bold font-mono text-slate-100">{c.constituent_symbol}</span>
                      <span className="ml-2 text-slate-400 text-[11px]">{c.constituent_name}</span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-300">{c.constituent_sector}</td>
                    <td className="py-2.5 px-4">
                      <span className="px-1.5 py-0.5 bg-slate-800 text-[10px] font-mono rounded text-slate-400">
                        {c.constituent_country}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-300">
                      {formatWeightPct(c.constituent_weight_in_fund)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono text-slate-200">
                      {formatMonetaryValue(c.effective_base_value, baseCurrency)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono font-bold text-blue-400">
                      {formatWeightPct(c.effective_portfolio_weight)}
                    </td>
                  </tr>
                ))}
                {parseFloat(selectedFund.residual_weight || '0') > 0 && (
                  <tr className="bg-amber-950/20 text-amber-300">
                    <td className="py-2.5 px-4 font-medium italic">Unclassified Residual Bucket</td>
                    <td className="py-2.5 px-4 text-slate-400">—</td>
                    <td className="py-2.5 px-4 text-slate-400">—</td>
                    <td className="py-2.5 px-4 text-right font-mono">
                      {formatWeightPct(selectedFund.residual_weight)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono">
                      {formatMonetaryValue(selectedFund.residual_base_value, baseCurrency)}
                    </td>
                    <td className="py-2.5 px-4 text-right font-mono font-bold">
                      {formatWeightPct(selectedFund.residual_weight)}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

