"use client";

import React, { useState } from "react";
import { Cpu, CheckCircle2, AlertTriangle, ArrowRight, RefreshCw } from "lucide-react";
import { OptionPricingResult, QuantPricingModelDefinition } from "@/lib/options/quant/types";

interface QuantPricingInspectorProps {
  pricingResult?: OptionPricingResult | null;
  availableModels: QuantPricingModelDefinition[];
  selectedModelId: string;
  onSelectModel: (modelId: string) => void;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export function QuantPricingInspector({
  pricingResult,
  availableModels,
  selectedModelId,
  onSelectModel,
  isLoading = false,
  onRefresh,
}: QuantPricingInspectorProps) {
  const currentModel = availableModels.find((m) => m.model_id === selectedModelId);

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          <div>
            <h3 className="text-sm font-semibold text-zinc-100">QuantLib Valuation Engine</h3>
            <p className="text-xs text-zinc-400">Institutional Multi-Model Derivatives Pricing</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-indigo-950/80 text-indigo-300 border border-indigo-800/60">
            QuantLib v1.44
          </span>
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 disabled:opacity-50 transition-colors"
              title="Recalculate Theoretical Price"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
            </button>
          )}
        </div>
      </div>

      {/* Model Selector Bar */}
      <div>
        <label className="text-xs text-zinc-400 mb-1.5 block font-medium">Pricing Model</label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {availableModels.map((model) => {
            const isSelected = model.model_id === selectedModelId;
            return (
              <button
                key={model.model_id}
                onClick={() => onSelectModel(model.model_id)}
                className={`flex flex-col text-left p-2 rounded border text-xs transition-colors ${
                  isSelected
                    ? "bg-indigo-950/50 border-indigo-500 text-zinc-100 font-medium"
                    : "bg-zinc-950/40 border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
                }`}
              >
                <span className="font-semibold truncate">{model.name}</span>
                <span className="text-[10px] text-zinc-500 font-mono mt-0.5">
                  {model.is_closed_form ? "Analytic" : `Numerical (${model.default_steps} steps)`}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Price vs Market Mark Inspection */}
      {pricingResult ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
          <div className="bg-zinc-950/60 border border-zinc-800/80 rounded p-3">
            <span className="text-[11px] text-zinc-400 uppercase font-mono tracking-wider">
              Theoretical Price (QuantLib)
            </span>
            <div className="text-xl font-bold font-mono text-indigo-300 mt-1">
              ${pricingResult.theoretical_price.toFixed(4)}
            </div>
            <div className="text-[10px] text-zinc-500 mt-1 flex items-center gap-1 font-mono">
              <span className="capitalize">{pricingResult.exercise_style.toLowerCase()}</span> exercise •
              Multiplier: {pricingResult.contract_multiplier}
            </div>
          </div>

          <div className="bg-zinc-950/60 border border-zinc-800/80 rounded p-3">
            <span className="text-[11px] text-zinc-400 uppercase font-mono tracking-wider">
              Observed Market Mark
            </span>
            <div className="text-xl font-bold font-mono text-zinc-200 mt-1">
              {pricingResult.observed_market_mark !== null && pricingResult.observed_market_mark !== undefined
                ? `$${pricingResult.observed_market_mark.toFixed(2)}`
                : "No Market Quote"}
            </div>
            <div className="text-[10px] text-zinc-500 mt-1 font-mono">
              Bid:{" "}
              {pricingResult.observed_market_bid !== null && pricingResult.observed_market_bid !== undefined
                ? `$${pricingResult.observed_market_bid.toFixed(2)}`
                : "—"}{" "}
              | Ask:{" "}
              {pricingResult.observed_market_ask !== null && pricingResult.observed_market_ask !== undefined
                ? `$${pricingResult.observed_market_ask.toFixed(2)}`
                : "—"}
            </div>
          </div>

          <div className="bg-zinc-950/60 border border-zinc-800/80 rounded p-3">
            <span className="text-[11px] text-zinc-400 uppercase font-mono tracking-wider">
              Theoretical vs Market Edge
            </span>
            {pricingResult.model_market_difference !== null &&
            pricingResult.model_market_difference !== undefined ? (
              <>
                <div
                  className={`text-xl font-bold font-mono mt-1 ${
                    pricingResult.model_market_difference > 0
                      ? "text-emerald-400"
                      : pricingResult.model_market_difference < 0
                      ? "text-rose-400"
                      : "text-zinc-300"
                  }`}
                >
                  {pricingResult.model_market_difference > 0 ? "+" : ""}
                  ${pricingResult.model_market_difference.toFixed(4)}
                </div>
                <div className="text-[10px] text-zinc-500 mt-1 font-mono">
                  {pricingResult.model_market_difference > 0
                    ? "Theoretical > Market (Potential Underpriced)"
                    : "Theoretical < Market (Potential Overpriced)"}
                </div>
              </>
            ) : (
              <div className="text-sm text-zinc-500 font-mono mt-2">Unavailable</div>
            )}
          </div>
        </div>
      ) : (
        <div className="text-center py-6 text-zinc-500 text-xs font-mono">
          Select or configure an option contract to evaluate theoretical pricing.
        </div>
      )}

      {/* Diagnostics Footer */}
      {pricingResult?.diagnostics && (
        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-zinc-800/60 pt-2 text-[10px] text-zinc-500 font-mono">
          <div className="flex items-center gap-3">
            <span>Engine: {pricingResult.diagnostics.engine_class_name}</span>
            <span>Calc Time: {pricingResult.diagnostics.elapsed_calculation_ms.toFixed(2)}ms</span>
            <span>TTE: {pricingResult.diagnostics.time_to_expiration_years.toFixed(4)}y</span>
          </div>
          <div className="flex items-center gap-1.5 text-zinc-400">
            <CheckCircle2 className="w-3 h-3 text-emerald-500" />
            <span>Thread-safe isolated date evaluation</span>
          </div>
        </div>
      )}
    </div>
  );
}

