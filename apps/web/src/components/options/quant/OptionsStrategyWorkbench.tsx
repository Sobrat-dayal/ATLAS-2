"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Cpu,
  Layers,
  Activity,
  Grid,
  GitCompare,
  Plus,
  Trash2,
  AlertTriangle,
  RefreshCw,
  Bookmark,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import {
  OptionPricingResult,
  QuantModelGreeks,
  QuantPricingModelDefinition,
  QuantStrategyLeg,
  ScenarioMatrixResult,
  StrategyComparisonItem,
  StrategyValuationResult,
} from "@/lib/options/quant/types";
import {
  analyzeQuantStrategy,
  compareQuantStrategies,
  computeScenarioMatrix,
  listQuantModels,
  listQuantStrategyTemplates,
  priceSingleContract,
  saveUserStrategy,
} from "@/lib/options/quant/api";
import { StrategyTemplateDefinition } from "@/lib/options/types";
import { QuantPricingInspector } from "./QuantPricingInspector";
import { StrategyGreeksPanel } from "./StrategyGreeksPanel";
import { StrategyScenarioMatrix } from "./StrategyScenarioMatrix";
import { StrategyComparisonView } from "./StrategyComparisonView";
import { StrategyPayoffWithPreExpirationChart } from "./StrategyPayoffWithPreExpirationChart";

interface OptionsStrategyWorkbenchProps {
  initialSymbol?: string;
  initialSpot?: number;
}

export function OptionsStrategyWorkbench({
  initialSymbol = "SPY",
  initialSpot = 530.0,
}: OptionsStrategyWorkbenchProps) {
  // Underlying & Global Market Inputs
  const [symbol, setSymbol] = useState(initialSymbol);
  const [spotPrice, setSpotPrice] = useState(initialSpot);
  const [riskFreeRate, setRiskFreeRate] = useState(0.05);
  const [dividendYield, setDividendYield] = useState(0.0);
  const [volatility, setVolatility] = useState(0.18);
  const [evaluationDate, setEvaluationDate] = useState("2024-05-20");

  // Models & Templates
  const [models, setModels] = useState<QuantPricingModelDefinition[]>([]);
  const [selectedModelId, setSelectedModelId] = useState("BARONE_ADESI_WHALEY");
  const [templates, setTemplates] = useState<StrategyTemplateDefinition[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("BULL_CALL_SPREAD");

  // Strategy Builder State
  const [legs, setLegs] = useState<QuantStrategyLeg[]>([
    {
      contract_id: "leg_call_530",
      side: "LONG_CALL",
      quantity: 1,
      entry_premium: 8.5,
      multiplier: 100,
      strike_price: 530,
      expiration_date: "2024-06-21",
      option_type: "CALL",
      exercise_style: "AMERICAN",
      custom_fee: 1.0,
    },
    {
      contract_id: "leg_call_540",
      side: "SHORT_CALL",
      quantity: 1,
      entry_premium: 3.5,
      multiplier: 100,
      strike_price: 540,
      expiration_date: "2024-06-21",
      option_type: "CALL",
      exercise_style: "AMERICAN",
      custom_fee: 1.0,
    },
  ]);

  // Results State
  const [valuationResult, setValuationResult] = useState<StrategyValuationResult | null>(null);
  const [matrixResult, setMatrixResult] = useState<ScenarioMatrixResult | null>(null);
  const [comparisonItems, setComparisonItems] = useState<StrategyComparisonItem[]>([]);
  const [pricingInspectorResult, setPricingInspectorResult] = useState<OptionPricingResult | null>(null);

  // Active Sub-Tab
  const [activeTab, setActiveTab] = useState<"PAYOFF" | "GREEKS" | "SCENARIOS" | "COMPARE">("PAYOFF");

  // Loading & Error States
  const [isCalculating, setIsCalculating] = useState(false);
  const [isMatrixLoading, setIsMatrixLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // Load Models and Strategy Templates on mount
  useEffect(() => {
    async function loadMetadata() {
      try {
        const [loadedModels, loadedTemplates] = await Promise.all([
          listQuantModels().catch(() => []),
          listQuantStrategyTemplates().catch(() => []),
        ]);
        if (loadedModels.length > 0) setModels(loadedModels);
        if (loadedTemplates.length > 0) setTemplates(loadedTemplates);
      } catch (err) {
        console.error("Failed to load QuantLib metadata", err);
      }
    }
    loadMetadata();
  }, []);

  // Recalculate Strategy Valuation
  const handleRecalculate = useCallback(async () => {
    if (legs.length === 0) {
      setValuationResult(null);
      return;
    }

    setIsCalculating(true);
    setStatusMessage(null);

    try {
      const res = await analyzeQuantStrategy({
        legs,
        spot_price: spotPrice,
        evaluation_date: evaluationDate,
        risk_free_rate: riskFreeRate,
        dividend_yield: dividendYield,
        volatility,
        pricing_model_id: selectedModelId,
        generate_pre_expiration: true,
      });
      setValuationResult(res);

      // Also price leg 0 for QuantPricingInspector if available
      if (legs[0]) {
        try {
          const leg0Price = await priceSingleContract({
            contract_id: legs[0].contract_id,
            evaluation_date: evaluationDate,
            spot_price: spotPrice,
            risk_free_rate: riskFreeRate,
            dividend_yield: dividendYield,
            volatility,
            model_id: selectedModelId,
          });
          setPricingInspectorResult(leg0Price);
        } catch {
          // Fallback gracefully if single contract ID is purely synthetic
          setPricingInspectorResult(null);
        }
      }
    } catch (err: any) {
      setStatusMessage(err.message || "Valuation computation failed.");
    } finally {
      setIsCalculating(false);
    }
  }, [legs, spotPrice, evaluationDate, riskFreeRate, dividendYield, volatility, selectedModelId]);

  // Trigger recalculation when relevant inputs change
  useEffect(() => {
    handleRecalculate();
  }, [handleRecalculate]);

  // Compute 2D Scenario Matrix
  const handleComputeMatrix = async () => {
    if (legs.length === 0) return;
    setIsMatrixLoading(true);
    try {
      const mtx = await computeScenarioMatrix({
        legs,
        base_spot: spotPrice,
        base_vol: volatility,
        spot_shifts_pct: [-0.1, -0.05, 0.0, 0.05, 0.1],
        vol_shifts_pct: [-0.05, 0.0, 0.05],
        evaluation_date: evaluationDate,
        risk_free_rate: riskFreeRate,
        pricing_model_id: selectedModelId,
      });
      setMatrixResult(mtx);
      setActiveTab("SCENARIOS");
    } catch (err: any) {
      setStatusMessage(err.message || "Failed to compute 2D scenario matrix.");
    } finally {
      setIsMatrixLoading(false);
    }
  };

  // Compare Canonical Strategies
  const handleRunComparison = async () => {
    try {
      const cmp = await compareQuantStrategies({
        strategies: [
          {
            strategy_id: "curr_strategy",
            strategy_name: "Active Custom Strategy",
            legs,
            total_fees: 2.0,
          },
          {
            strategy_id: "benchmark_straddle",
            strategy_name: "Benchmark Long Straddle",
            legs: [
              {
                contract_id: "straddle_c",
                side: "LONG_CALL",
                quantity: 1,
                entry_premium: 8.0,
                multiplier: 100,
                strike_price: spotPrice,
                expiration_date: "2024-06-21",
                option_type: "CALL",
                exercise_style: "AMERICAN",
                custom_fee: 1.0,
              },
              {
                contract_id: "straddle_p",
                side: "LONG_PUT",
                quantity: 1,
                entry_premium: 7.5,
                multiplier: 100,
                strike_price: spotPrice,
                expiration_date: "2024-06-21",
                option_type: "PUT",
                exercise_style: "AMERICAN",
                custom_fee: 1.0,
              },
            ],
            total_fees: 2.0,
          },
        ],
        spot_price: spotPrice,
        evaluation_date: evaluationDate,
        volatility,
      });
      setComparisonItems(cmp);
      setActiveTab("COMPARE");
    } catch (err: any) {
      setStatusMessage(err.message || "Comparison failed.");
    }
  };

  // Add Leg
  const handleAddLeg = () => {
    const newLeg: QuantStrategyLeg = {
      contract_id: `custom_leg_${Date.now()}`,
      side: "LONG_CALL",
      quantity: 1,
      entry_premium: 5.0,
      multiplier: 100,
      strike_price: Math.round(spotPrice),
      expiration_date: "2024-06-21",
      option_type: "CALL",
      exercise_style: "AMERICAN",
      custom_fee: 1.0,
    };
    setLegs([...legs, newLeg]);
  };

  // Remove Leg
  const handleRemoveLeg = (idx: number) => {
    setLegs(legs.filter((_, i) => i !== idx));
  };

  // Update Leg
  const handleUpdateLeg = (idx: number, updates: Partial<QuantStrategyLeg>) => {
    setLegs(legs.map((leg, i) => (i === idx ? { ...leg, ...updates } : leg)));
  };

  // Apply Template
  const handleApplyTemplate = (templateId: string) => {
    setSelectedTemplateId(templateId);
    const baseStrike = Math.round(spotPrice);

    if (templateId === "BULL_CALL_SPREAD") {
      setLegs([
        {
          contract_id: `tmpl_${templateId}_c1`,
          side: "LONG_CALL",
          quantity: 1,
          entry_premium: 8.5,
          multiplier: 100,
          strike_price: baseStrike,
          expiration_date: "2024-06-21",
          option_type: "CALL",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
        {
          contract_id: `tmpl_${templateId}_c2`,
          side: "SHORT_CALL",
          quantity: 1,
          entry_premium: 3.5,
          multiplier: 100,
          strike_price: baseStrike + 10,
          expiration_date: "2024-06-21",
          option_type: "CALL",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
      ]);
    } else if (templateId === "BEAR_PUT_SPREAD") {
      setLegs([
        {
          contract_id: `tmpl_${templateId}_p1`,
          side: "LONG_PUT",
          quantity: 1,
          entry_premium: 7.0,
          multiplier: 100,
          strike_price: baseStrike,
          expiration_date: "2024-06-21",
          option_type: "PUT",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
        {
          contract_id: `tmpl_${templateId}_p2`,
          side: "SHORT_PUT",
          quantity: 1,
          entry_premium: 3.0,
          multiplier: 100,
          strike_price: baseStrike - 10,
          expiration_date: "2024-06-21",
          option_type: "PUT",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
      ]);
    } else if (templateId === "LONG_STRADDLE") {
      setLegs([
        {
          contract_id: `tmpl_${templateId}_c`,
          side: "LONG_CALL",
          quantity: 1,
          entry_premium: 8.0,
          multiplier: 100,
          strike_price: baseStrike,
          expiration_date: "2024-06-21",
          option_type: "CALL",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
        {
          contract_id: `tmpl_${templateId}_p`,
          side: "LONG_PUT",
          quantity: 1,
          entry_premium: 7.5,
          multiplier: 100,
          strike_price: baseStrike,
          expiration_date: "2024-06-21",
          option_type: "PUT",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
      ]);
    } else if (templateId === "IRON_CONDOR") {
      setLegs([
        {
          contract_id: `tmpl_${templateId}_p_short`,
          side: "SHORT_PUT",
          quantity: 1,
          entry_premium: 2.5,
          multiplier: 100,
          strike_price: baseStrike - 10,
          expiration_date: "2024-06-21",
          option_type: "PUT",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
        {
          contract_id: `tmpl_${templateId}_p_long`,
          side: "LONG_PUT",
          quantity: 1,
          entry_premium: 1.0,
          multiplier: 100,
          strike_price: baseStrike - 20,
          expiration_date: "2024-06-21",
          option_type: "PUT",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
        {
          contract_id: `tmpl_${templateId}_c_short`,
          side: "SHORT_CALL",
          quantity: 1,
          entry_premium: 2.5,
          multiplier: 100,
          strike_price: baseStrike + 10,
          expiration_date: "2024-06-21",
          option_type: "CALL",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
        {
          contract_id: `tmpl_${templateId}_c_long`,
          side: "LONG_CALL",
          quantity: 1,
          entry_premium: 1.0,
          multiplier: 100,
          strike_price: baseStrike + 20,
          expiration_date: "2024-06-21",
          option_type: "CALL",
          exercise_style: "AMERICAN",
          custom_fee: 1.0,
        },
      ]);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Header & Market Inputs Bar */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded-lg p-4 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800/80 pb-3">
          <div className="flex items-center gap-2.5">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <div>
              <h2 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
                QuantLib Quantitative Strategy Lab
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950 text-indigo-300 border border-indigo-800/60">
                  Stage 142
                </span>
              </h2>
              <p className="text-xs text-zinc-400">
                Multi-Model Derivatives Valuation, Greeks, 2D Scenario Stress & Payoff Curves
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleComputeMatrix}
              disabled={isMatrixLoading || legs.length === 0}
              className="px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-mono font-medium flex items-center gap-1.5 transition-colors"
            >
              <Grid className="w-3.5 h-3.5 text-indigo-400" />
              <span>{isMatrixLoading ? "Computing..." : "2D Stress Matrix"}</span>
            </button>
            <button
              onClick={handleRunComparison}
              disabled={legs.length === 0}
              className="px-3 py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-mono font-medium flex items-center gap-1.5 transition-colors"
            >
              <GitCompare className="w-3.5 h-3.5 text-emerald-400" />
              <span>Compare Strategies</span>
            </button>
            <button
              onClick={handleRecalculate}
              disabled={isCalculating}
              className="p-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
              title="Recalculate Mark-to-Market"
            >
              <RefreshCw className={`w-4 h-4 ${isCalculating ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        {/* Global Valuation Parameters */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-1 text-xs font-mono">
          <div>
            <label className="text-[10px] text-zinc-400 uppercase font-sans">Underlying</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              className="w-full mt-1 bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1 text-zinc-200 uppercase font-bold"
            />
          </div>

          <div>
            <label className="text-[10px] text-zinc-400 uppercase font-sans">Spot Price ($)</label>
            <input
              type="number"
              step="0.5"
              value={spotPrice}
              onChange={(e) => setSpotPrice(parseFloat(e.target.value) || 0)}
              className="w-full mt-1 bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1 text-zinc-200 font-bold"
            />
          </div>

          <div>
            <label className="text-[10px] text-zinc-400 uppercase font-sans">Risk-Free Rate</label>
            <input
              type="number"
              step="0.005"
              value={riskFreeRate}
              onChange={(e) => setRiskFreeRate(parseFloat(e.target.value) || 0)}
              className="w-full mt-1 bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1 text-zinc-200"
            />
          </div>

          <div>
            <label className="text-[10px] text-zinc-400 uppercase font-sans">Dividend Yield</label>
            <input
              type="number"
              step="0.005"
              value={dividendYield}
              onChange={(e) => setDividendYield(parseFloat(e.target.value) || 0)}
              className="w-full mt-1 bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1 text-zinc-200"
            />
          </div>

          <div>
            <label className="text-[10px] text-zinc-400 uppercase font-sans">Volatility (IV)</label>
            <input
              type="number"
              step="0.01"
              value={volatility}
              onChange={(e) => setVolatility(parseFloat(e.target.value) || 0)}
              className="w-full mt-1 bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1 text-zinc-200"
            />
          </div>

          <div>
            <label className="text-[10px] text-zinc-400 uppercase font-sans">Evaluation Date</label>
            <input
              type="date"
              value={evaluationDate}
              onChange={(e) => setEvaluationDate(e.target.value)}
              className="w-full mt-1 bg-zinc-950 border border-zinc-800 rounded px-2 py-1 text-zinc-200"
            />
          </div>
        </div>
      </div>

      {/* Model Inspector */}
      <QuantPricingInspector
        pricingResult={pricingInspectorResult}
        availableModels={models}
        selectedModelId={selectedModelId}
        onSelectModel={setSelectedModelId}
        isLoading={isCalculating}
        onRefresh={handleRecalculate}
      />

      {/* Template Picker & Leg Builder */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800 pb-2.5">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-zinc-400" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-200">
              Strategy Legs ({legs.length})
            </h3>
          </div>

          {/* Canonical Templates Dropdown */}
          <div className="flex items-center gap-2">
            <label className="text-[11px] text-zinc-400 font-sans">Load Template:</label>
            <select
              value={selectedTemplateId}
              onChange={(e) => handleApplyTemplate(e.target.value)}
              className="bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded px-2.5 py-1 font-mono focus:border-indigo-500"
            >
              {templates.map((t) => (
                <option key={t.template_id} value={t.template_id}>
                  {t.name}
                </option>
              ))}
            </select>
            <button
              onClick={handleAddLeg}
              className="px-2.5 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium flex items-center gap-1 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Leg</span>
            </button>
          </div>
        </div>

        {/* Legs Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono border-collapse min-w-[650px]">
            <thead>
              <tr className="border-b border-zinc-800 text-[10px] text-zinc-500 uppercase text-left">
                <th className="p-2">Side</th>
                <th className="p-2">Qty</th>
                <th className="p-2">Strike</th>
                <th className="p-2">Type</th>
                <th className="p-2">Style</th>
                <th className="p-2">Expiry</th>
                <th className="p-2">Entry Premium</th>
                <th className="p-2">Fee</th>
                <th className="p-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-850">
              {legs.map((leg, idx) => (
                <tr key={idx} className="hover:bg-zinc-950/40 transition-colors">
                  <td className="p-2">
                    <select
                      value={leg.side}
                      onChange={(e) => handleUpdateLeg(idx, { side: e.target.value as any })}
                      className={`bg-zinc-950 border rounded px-2 py-0.5 font-bold ${
                        leg.side.startsWith("LONG")
                          ? "text-emerald-400 border-emerald-900/60"
                          : "text-rose-400 border-rose-900/60"
                      }`}
                    >
                      <option value="LONG_CALL">LONG CALL</option>
                      <option value="SHORT_CALL">SHORT CALL</option>
                      <option value="LONG_PUT">LONG PUT</option>
                      <option value="SHORT_PUT">SHORT PUT</option>
                    </select>
                  </td>

                  <td className="p-2">
                    <input
                      type="number"
                      min="1"
                      value={leg.quantity}
                      onChange={(e) =>
                        handleUpdateLeg(idx, { quantity: parseInt(e.target.value) || 1 })
                      }
                      className="w-14 bg-zinc-950 border border-zinc-800 rounded px-2 py-0.5 text-zinc-200"
                    />
                  </td>

                  <td className="p-2">
                    <input
                      type="number"
                      step="0.5"
                      value={leg.strike_price}
                      onChange={(e) =>
                        handleUpdateLeg(idx, { strike_price: parseFloat(e.target.value) || 0 })
                      }
                      className="w-20 bg-zinc-950 border border-zinc-800 rounded px-2 py-0.5 text-zinc-200"
                    />
                  </td>

                  <td className="p-2">
                    <span className="text-zinc-300">{leg.option_type}</span>
                  </td>

                  <td className="p-2">
                    <span className="text-zinc-400">{leg.exercise_style}</span>
                  </td>

                  <td className="p-2">
                    <input
                      type="date"
                      value={leg.expiration_date}
                      onChange={(e) => handleUpdateLeg(idx, { expiration_date: e.target.value })}
                      className="bg-zinc-950 border border-zinc-800 rounded px-2 py-0.5 text-zinc-300"
                    />
                  </td>

                  <td className="p-2">
                    <div className="flex items-center gap-1">
                      <span>$</span>
                      <input
                        type="number"
                        step="0.05"
                        value={leg.entry_premium}
                        onChange={(e) =>
                          handleUpdateLeg(idx, { entry_premium: parseFloat(e.target.value) || 0 })
                        }
                        className="w-16 bg-zinc-950 border border-zinc-800 rounded px-2 py-0.5 text-zinc-200"
                      />
                    </div>
                  </td>

                  <td className="p-2">
                    <div className="flex items-center gap-1">
                      <span>$</span>
                      <input
                        type="number"
                        step="0.5"
                        value={leg.custom_fee}
                        onChange={(e) =>
                          handleUpdateLeg(idx, { custom_fee: parseFloat(e.target.value) || 0 })
                        }
                        className="w-14 bg-zinc-950 border border-zinc-800 rounded px-2 py-0.5 text-zinc-400"
                      />
                    </div>
                  </td>

                  <td className="p-2 text-right">
                    <button
                      onClick={() => handleRemoveLeg(idx)}
                      className="p-1 rounded text-zinc-500 hover:text-rose-400 hover:bg-rose-950/30 transition-colors"
                      title="Remove Leg"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Status or Risk Warnings */}
      {valuationResult?.risk_warnings && valuationResult.risk_warnings.length > 0 && (
        <div className="bg-amber-950/20 border border-amber-800/40 rounded-lg p-3 space-y-1 text-xs font-mono text-amber-300">
          <div className="flex items-center gap-1.5 font-bold">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Quantitative Risk Diagnostics ({valuationResult.risk_warnings.length}):</span>
          </div>
          <ul className="list-disc list-inside space-y-0.5 pl-2 text-[11px] text-amber-200/90">
            {valuationResult.risk_warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Sub-Tabs Navigation */}
      <div className="flex items-center gap-1 border-b border-zinc-800 pt-2">
        <button
          onClick={() => setActiveTab("PAYOFF")}
          className={`px-4 py-2 text-xs font-mono border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === "PAYOFF"
              ? "border-indigo-500 text-indigo-400 font-semibold"
              : "border-transparent text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Payoff & Pre-Expiration Curve</span>
        </button>

        <button
          onClick={() => setActiveTab("GREEKS")}
          className={`px-4 py-2 text-xs font-mono border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === "GREEKS"
              ? "border-indigo-500 text-indigo-400 font-semibold"
              : "border-transparent text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <Cpu className="w-3.5 h-3.5" />
          <span>Strategy Greeks</span>
        </button>

        <button
          onClick={() => setActiveTab("SCENARIOS")}
          className={`px-4 py-2 text-xs font-mono border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === "SCENARIOS"
              ? "border-indigo-500 text-indigo-400 font-semibold"
              : "border-transparent text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <Grid className="w-3.5 h-3.5" />
          <span>2D Scenario Matrix</span>
        </button>

        <button
          onClick={() => setActiveTab("COMPARE")}
          className={`px-4 py-2 text-xs font-mono border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === "COMPARE"
              ? "border-indigo-500 text-indigo-400 font-semibold"
              : "border-transparent text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <GitCompare className="w-3.5 h-3.5" />
          <span>Compare Strategies</span>
        </button>
      </div>

      {/* Sub-Tab Content */}
      {activeTab === "PAYOFF" && valuationResult && (
        <StrategyPayoffWithPreExpirationChart
          expirationCurve={valuationResult.expiration_payoff_curve}
          preExpirationCurve={valuationResult.pre_expiration_curve}
          currentSpot={spotPrice}
          breakEvenPoints={valuationResult.break_even_points}
          maxProfit={valuationResult.max_profit}
          maxLoss={valuationResult.max_loss}
          isUnboundedLoss={valuationResult.is_unbounded_loss}
        />
      )}

      {activeTab === "GREEKS" && valuationResult && (
        <StrategyGreeksPanel greeks={valuationResult.aggregate_greeks} />
      )}

      {activeTab === "SCENARIOS" && (
        <StrategyScenarioMatrix matrixResult={matrixResult} isLoading={isMatrixLoading} />
      )}

      {activeTab === "COMPARE" && (
        <StrategyComparisonView comparisonItems={comparisonItems} />
      )}

      {/* Disclaimers & Governance Footer */}
      <div className="bg-zinc-950/80 border border-zinc-850 rounded-lg p-3 text-[10px] text-zinc-500 font-mono space-y-1">
        <div className="flex items-center gap-2 text-zinc-400 font-semibold uppercase">
          <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
          <span>Computational Governance & Compliance Disclaimers</span>
        </div>
        <p>
          QuantLib calculations are for analytical and quantitative decision-support purposes only.
          No automated trade execution, broker order routing, or algorithmic order placement is
          permitted within this engine. All valuations reflect theoretical derivatives pricing
          models under specified evaluation date contexts.
        </p>
      </div>
    </div>
  );
}
