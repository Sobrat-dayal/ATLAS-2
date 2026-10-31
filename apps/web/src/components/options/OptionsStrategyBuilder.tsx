"use client";

import React, { useState } from "react";
import {
  LegSide,
  OptionChainResponse,
  OptionStrategyAnalysisResult,
  OptionStrategyLeg,
  StrategyTemplateDefinition,
} from "@/lib/options/types";
import { formatCurrency } from "@/lib/options/formatters";
import { StrategyPayoffChart } from "./StrategyPayoffChart";
import {
  AlertTriangle,
  Bookmark,
  CheckCircle2,
  DollarSign,
  Plus,
  RefreshCw,
  Sliders,
  Trash2,
} from "lucide-react";

interface OptionsStrategyBuilderProps {
  legs: OptionStrategyLeg[];
  onUpdateLegs: (legs: OptionStrategyLeg[]) => void;
  templates: StrategyTemplateDefinition[];
  chain: OptionChainResponse | null;
  currency?: string;
  analysisResult: OptionStrategyAnalysisResult | null;
  onAnalyze: (legs: OptionStrategyLeg[]) => void;
  isAnalyzing?: boolean;
}

export function OptionsStrategyBuilder({
  legs,
  onUpdateLegs,
  templates,
  chain,
  currency = "USD",
  analysisResult,
  onAnalyze,
  isAnalyzing,
}: OptionsStrategyBuilderProps) {
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("");

  const handleApplyTemplate = (templateId: string) => {
    setSelectedTemplateId(templateId);
    if (!chain || chain.rows.length === 0) return;

    const atmRow =
      chain.rows.find((r) => r.moneyness === "AT_THE_MONEY") ||
      chain.rows[Math.floor(chain.rows.length / 2)];

    const higherRow =
      chain.rows.find((r) => r.strike_price > atmRow.strike_price) || atmRow;
    const lowerRow =
      [...chain.rows].reverse().find((r) => r.strike_price < atmRow.strike_price) || atmRow;

    let newLegs: OptionStrategyLeg[] = [];

    switch (templateId) {
      case "BULL_CALL_SPREAD":
        if (atmRow.call_contract && higherRow.call_contract) {
          newLegs = [
            {
              contract_id: atmRow.call_contract.option_contract_id,
              side: "LONG_CALL",
              quantity: 1,
              entry_premium: atmRow.call_quote?.ask || 5.0,
              multiplier: atmRow.call_contract.contract_multiplier,
            },
            {
              contract_id: higherRow.call_contract.option_contract_id,
              side: "SHORT_CALL",
              quantity: 1,
              entry_premium: higherRow.call_quote?.bid || 2.0,
              multiplier: higherRow.call_contract.contract_multiplier,
            },
          ];
        }
        break;

      case "LONG_STRADDLE":
        if (atmRow.call_contract && atmRow.put_contract) {
          newLegs = [
            {
              contract_id: atmRow.call_contract.option_contract_id,
              side: "LONG_CALL",
              quantity: 1,
              entry_premium: atmRow.call_quote?.ask || 4.5,
              multiplier: atmRow.call_contract.contract_multiplier,
            },
            {
              contract_id: atmRow.put_contract.option_contract_id,
              side: "LONG_PUT",
              quantity: 1,
              entry_premium: atmRow.put_quote?.ask || 4.5,
              multiplier: atmRow.put_contract.contract_multiplier,
            },
          ];
        }
        break;

      case "LONG_CALL":
        if (atmRow.call_contract) {
          newLegs = [
            {
              contract_id: atmRow.call_contract.option_contract_id,
              side: "LONG_CALL",
              quantity: 1,
              entry_premium: atmRow.call_quote?.ask || 5.0,
              multiplier: atmRow.call_contract.contract_multiplier,
            },
          ];
        }
        break;

      case "BEAR_PUT_SPREAD":
        if (atmRow.put_contract && lowerRow.put_contract) {
          newLegs = [
            {
              contract_id: atmRow.put_contract.option_contract_id,
              side: "LONG_PUT",
              quantity: 1,
              entry_premium: atmRow.put_quote?.ask || 5.0,
              multiplier: atmRow.put_contract.contract_multiplier,
            },
            {
              contract_id: lowerRow.put_contract.option_contract_id,
              side: "SHORT_PUT",
              quantity: 1,
              entry_premium: lowerRow.put_quote?.bid || 2.0,
              multiplier: lowerRow.put_contract.contract_multiplier,
            },
          ];
        }
        break;

      case "SHORT_CALL":
        if (higherRow.call_contract) {
          newLegs = [
            {
              contract_id: higherRow.call_contract.option_contract_id,
              side: "SHORT_CALL",
              quantity: 1,
              entry_premium: higherRow.call_quote?.bid || 3.0,
              multiplier: higherRow.call_contract.contract_multiplier,
            },
          ];
        }
        break;

      default:
        // Default to long call
        if (atmRow.call_contract) {
          newLegs = [
            {
              contract_id: atmRow.call_contract.option_contract_id,
              side: "LONG_CALL",
              quantity: 1,
              entry_premium: atmRow.call_quote?.ask || 5.0,
              multiplier: atmRow.call_contract.contract_multiplier,
            },
          ];
        }
        break;
    }

    if (newLegs.length > 0) {
      onUpdateLegs(newLegs);
      onAnalyze(newLegs);
    }
  };

  const handleUpdateLeg = (index: number, updates: Partial<OptionStrategyLeg>) => {
    const updated = [...legs];
    updated[index] = { ...updated[index], ...updates };
    onUpdateLegs(updated);
  };

  const handleRemoveLeg = (index: number) => {
    const updated = legs.filter((_, i) => i !== index);
    onUpdateLegs(updated);
    if (updated.length > 0) {
      onAnalyze(updated);
    }
  };

  const handleAddDefaultLeg = () => {
    if (!chain || chain.rows.length === 0) return;
    const atmRow =
      chain.rows.find((r) => r.moneyness === "AT_THE_MONEY") || chain.rows[0];
    if (atmRow.call_contract) {
      const leg: OptionStrategyLeg = {
        contract_id: atmRow.call_contract.option_contract_id,
        side: "LONG_CALL",
        quantity: 1,
        entry_premium: atmRow.call_quote?.ask || 5.0,
        multiplier: atmRow.call_contract.contract_multiplier,
      };
      const updated = [...legs, leg];
      onUpdateLegs(updated);
      onAnalyze(updated);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-4 p-4 h-full overflow-y-auto bg-zinc-950">
      {/* Left Column: Strategy Configuration & Legs */}
      <div className="w-full lg:w-1/2 space-y-4">
        {/* Templates Selector */}
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-zinc-300 flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-cyan-400" />
              Pre-Configured Strategy Templates
            </span>
            <span className="text-[10px] text-zinc-500">{templates.length} Available</span>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={selectedTemplateId}
              onChange={(e) => handleApplyTemplate(e.target.value)}
              className="flex-1 bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="">Select a strategy template...</option>
              {templates.map((t) => (
                <option key={t.template_id} value={t.template_id}>
                  {t.name} ({t.directional_bias} • {t.max_risk_profile})
                </option>
              ))}
            </select>
            {legs.length > 0 && (
              <button
                onClick={() => {
                  onUpdateLegs([]);
                  setSelectedTemplateId("");
                }}
                className="px-2.5 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded text-xs transition-colors"
                title="Clear all legs"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Legs Table */}
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-lg p-3">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-zinc-300">Strategy Legs ({legs.length})</span>
            <button
              onClick={handleAddDefaultLeg}
              className="flex items-center gap-1 text-[11px] font-medium text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Custom Leg</span>
            </button>
          </div>

          {legs.length === 0 ? (
            <div className="p-6 text-center text-xs text-zinc-500 border border-dashed border-zinc-800 rounded-lg">
              No strategy legs added. Click Bid/Ask in the Options Chain or pick a strategy template above.
            </div>
          ) : (
            <div className="space-y-2">
              {legs.map((leg, idx) => (
                <div
                  key={idx}
                  className="bg-zinc-950 border border-zinc-850 rounded-lg p-3 flex flex-wrap items-center justify-between gap-2"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-zinc-500">#{idx + 1}</span>
                    <select
                      value={leg.side}
                      onChange={(e) =>
                        handleUpdateLeg(idx, { side: e.target.value as LegSide })
                      }
                      className="bg-zinc-900 border border-zinc-800 rounded px-2 py-1 text-xs font-bold text-white focus:outline-none"
                    >
                      <option value="LONG_CALL">BUY CALL</option>
                      <option value="SHORT_CALL">SELL CALL</option>
                      <option value="LONG_PUT">BUY PUT</option>
                      <option value="SHORT_PUT">SELL PUT</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-2 text-xs">
                    <div className="flex items-center gap-1">
                      <span className="text-zinc-500 text-[10px]">Qty:</span>
                      <input
                        type="number"
                        min="1"
                        max="1000"
                        value={leg.quantity}
                        onChange={(e) =>
                          handleUpdateLeg(idx, {
                            quantity: Math.max(1, parseInt(e.target.value, 10) || 1),
                          })
                        }
                        className="w-14 bg-zinc-900 border border-zinc-800 rounded px-1.5 py-1 text-xs text-right font-mono text-white"
                      />
                    </div>

                    <div className="flex items-center gap-1">
                      <span className="text-zinc-500 text-[10px]">Price:</span>
                      <input
                        type="number"
                        step="0.05"
                        min="0"
                        value={leg.entry_premium}
                        onChange={(e) =>
                          handleUpdateLeg(idx, {
                            entry_premium: parseFloat(e.target.value) || 0,
                          })
                        }
                        className="w-16 bg-zinc-900 border border-zinc-800 rounded px-1.5 py-1 text-xs text-right font-mono text-white"
                      />
                    </div>

                    <div className="text-[10px] text-zinc-500 font-mono">
                      Lot: {leg.multiplier}
                    </div>

                    <button
                      onClick={() => handleRemoveLeg(idx)}
                      className="p-1 text-zinc-500 hover:text-rose-400 transition-colors ml-1"
                      title="Remove leg"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}

              <div className="pt-2 flex justify-end">
                <button
                  onClick={() => onAnalyze(legs)}
                  disabled={isAnalyzing}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs rounded transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? "animate-spin" : ""}`} />
                  <span>Recalculate Payoff</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Risk Warnings Banner */}
        {analysisResult?.risk_warnings && analysisResult.risk_warnings.length > 0 && (
          <div className="bg-rose-500/10 border border-rose-500/30 rounded-lg p-3 space-y-1.5">
            <div className="flex items-center gap-1.5 text-rose-400 text-xs font-bold">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>Risk Warning</span>
            </div>
            {analysisResult.risk_warnings.map((w, i) => (
              <p key={i} className="text-[11px] text-rose-300 leading-relaxed">
                {w}
              </p>
            ))}
          </div>
        )}
      </div>

      {/* Right Column: Mathematical Analysis & Expiration Payoff Diagram */}
      <div className="w-full lg:w-1/2 space-y-4">
        {/* Cash Flow and Analytics Summary */}
        {analysisResult && (
          <div className="bg-zinc-900/70 border border-zinc-800 rounded-lg p-3">
            <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-wider mb-3">
              Strategy Payoff & Breakeven Analytics
            </h3>

            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="bg-zinc-950 p-2.5 rounded border border-zinc-850">
                <div className="text-zinc-500 text-[10px]">Opening Cash Flow</div>
                <div
                  className={`font-mono text-sm font-bold mt-0.5 ${
                    analysisResult.is_net_debit ? "text-rose-400" : "text-emerald-400"
                  }`}
                >
                  {formatCurrency(analysisResult.net_opening_cash_flow, currency)}
                </div>
                <div className="text-[10px] text-zinc-500">
                  {analysisResult.is_net_debit ? "Net Debit Paid" : "Net Credit Collected"}
                </div>
              </div>

              <div className="bg-zinc-950 p-2.5 rounded border border-zinc-850">
                <div className="text-zinc-500 text-[10px]">Breakeven Price(s)</div>
                <div className="font-mono text-sm font-bold text-amber-300 mt-0.5">
                  {analysisResult.breakevens.length > 0
                    ? analysisResult.breakevens.map((b) => formatCurrency(b, currency)).join(", ")
                    : "None"}
                </div>
                <div className="text-[10px] text-zinc-500">Exact Root Finding</div>
              </div>

              <div className="bg-zinc-950 p-2.5 rounded border border-zinc-850">
                <div className="text-zinc-500 text-[10px]">Risk Profile</div>
                <div className="font-mono text-xs font-bold text-white mt-0.5">
                  {analysisResult.is_unbounded_loss ? (
                    <span className="text-rose-400 font-bold">Unbounded Upside Risk</span>
                  ) : (
                    <span className="text-emerald-400 font-bold">Defined Risk</span>
                  )}
                </div>
                <div className="text-[10px] text-zinc-500">
                  {analysisResult.is_unbounded_profit ? "Uncapped Profit" : "Defined Profit"}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Visual Chart */}
        <StrategyPayoffChart
          coordinates={analysisResult?.payoff_curve || []}
          breakevens={analysisResult?.breakevens || []}
          currency={currency}
          maxProfit={analysisResult?.max_profit}
          maxLoss={analysisResult?.max_loss}
          isUnboundedProfit={analysisResult?.is_unbounded_profit}
          isUnboundedLoss={analysisResult?.is_unbounded_loss}
        />

        {/* Analytical Payoff Disclaimer */}
        <div className="p-2.5 bg-zinc-900/40 rounded border border-zinc-850 text-[10px] text-zinc-500 leading-relaxed">
          <span className="font-semibold text-zinc-400">Expiration Boundary Notice:</span> This payoff model represents deterministic piecewise-linear intrinsic value at expiration settlement (T = Expiration Cutoff). It does NOT model prior-to-expiration mark-to-market Black-Scholes / QuantLib pricing (scheduled for Stage 142) or early assignment risk on American options.
        </div>
      </div>
    </div>
  );
}
