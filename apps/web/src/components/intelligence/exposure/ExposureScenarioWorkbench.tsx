"use client";

import React, { useState } from "react";
import { ExposureScenarioShock, ExposureScenarioRun } from "@/lib/intelligence/exposure/types";
import { formatCurrencyAmount, formatPercentage } from "@/lib/intelligence/exposure/units";
import { runScenarioShock } from "@/lib/intelligence/exposure/api";
import { Play, AlertTriangle, Sliders, DollarSign, RotateCcw } from "lucide-react";

interface ExposureScenarioWorkbenchProps {
  baseCurrency?: string;
  positions?: Array<Record<string, unknown>>;
}

export function ExposureScenarioWorkbench({
  baseCurrency = "USD",
  positions = []
}: ExposureScenarioWorkbenchProps) {
  const [targetDimension, setTargetDimension] = useState<string>("SECTOR");
  const [targetIdentifier, setTargetIdentifier] = useState<string>("Information Technology");
  const [shockValue, setShockValue] = useState<number>(-10.0);
  const [running, setRunning] = useState<boolean>(false);
  const [scenarioRun, setScenarioRun] = useState<ExposureScenarioRun | null>(null);

  // Default sample positions if none provided
  const activePositions = positions.length > 0 ? positions : [
    {
      id: "pos_tech",
      symbol: "AAPL",
      market_value: 500000.0,
      sector: "Information Technology",
      country: "US",
      node_ref: { node_type: "COMPANY", entity_id: "COMP_AAPL", canonical_name: "Apple Inc." }
    },
    {
      id: "pos_fin",
      symbol: "JPM",
      market_value: 300000.0,
      sector: "Financials",
      country: "US",
      node_ref: { node_type: "COMPANY", entity_id: "COMP_JPM", canonical_name: "JPMorgan Chase & Co." }
    },
    {
      id: "pos_ind",
      symbol: "CAT",
      market_value: 200000.0,
      sector: "Industrials",
      country: "US",
      node_ref: { node_type: "COMPANY", entity_id: "COMP_CAT", canonical_name: "Caterpillar Inc." }
    }
  ];

  const handleRunScenario = async () => {
    setRunning(true);
    const shock: ExposureScenarioShock = {
      shock_id: `shk_${Date.now()}`,
      target_dimension: targetDimension,
      target_identifier: targetIdentifier,
      shock_value: shockValue,
      shock_unit: "PERCENT"
    };

    try {
      const res = await runScenarioShock(
        `scen_${Date.now()}`,
        `${targetDimension} ${shockValue}% Shock`,
        [shock],
        activePositions,
        baseCurrency
      );
      setScenarioRun(res);
    } catch (err) {
      console.error("Scenario execution failed:", err);
      // Fallback deterministic local evaluation
      let totalPnl = 0;
      const results = activePositions.map((pos) => {
        const mv = Number(pos.market_value) || 0;
        let match = false;
        if (targetDimension === "SECTOR" && String(pos.sector).toLowerCase() === targetIdentifier.toLowerCase()) match = true;
        if (targetDimension === "SECURITY" && String(pos.symbol).toLowerCase() === targetIdentifier.toLowerCase()) match = true;
        if (targetDimension === "COUNTRY" && String(pos.country).toLowerCase() === targetIdentifier.toLowerCase()) match = true;

        const condPnl = match ? mv * (shockValue / 100.0) : 0;
        totalPnl += condPnl;

        return {
          exposure_id: `exp_scen_${pos.id}`,
          analysis_run_id: `run_fallback_${Date.now()}`,
          subject_entity_ref: (pos.node_ref as any) || { node_type: "PORTFOLIO", entity_id: "PORT", canonical_name: "Portfolio" },
          target_entity_ref: (pos.node_ref as any) || { node_type: "COMPANY", entity_id: String(pos.symbol), canonical_name: String(pos.symbol) },
          exposure_domain: "PORTFOLIO" as const,
          exposure_type: "SCENARIO_EXPOSURE" as const,
          exposure_measure_id: "SCENARIO_CONDITIONAL_PNL_V1",
          evidence_class: "USER_DEFINED_SCENARIO" as const,
          relationship_strength: "ASSUMPTION_DEPENDENT" as const,
          amount: condPnl,
          currency: baseCurrency,
          unit: "CURRENCY",
          percentage: match ? shockValue : 0,
          calculation_method_id: "DETERMINISTIC_SHOCK_APPLICATION",
          calculation_version: "v1.0",
          input_lineage_ids: [],
          graph_path_ids: [],
          coverage_status: "COMPLETE" as const,
          uncertainty_class: "SCENARIO_ASSUMPTION" as const,
          explanation: match
            ? `Hypothetical ${shockValue}% shock on ${pos.symbol} (${mv} ${baseCurrency}) yields conditional P&L of ${condPnl.toFixed(2)} ${baseCurrency}.`
            : `Position unaffected by ${targetIdentifier} shock.`,
          limitations_disclaimer: "HYPOTHETICAL SCENARIO RESULT. Computed strictly from user-supplied assumptions.",
          warnings: [],
          known_as_of: new Date().toISOString(),
          created_at: new Date().toISOString()
        };
      });

      setScenarioRun({
        run_id: `scen_local_${Date.now()}`,
        scenario_id: `scen_user`,
        status: "COMPLETED",
        subject_entity_ref: { node_type: "OTHER_SUPPORTED_CANONICAL_ENTITY", entity_id: "PORT_ROOT", canonical_name: "Target Portfolio" },
        results: results.filter(r => r.amount !== 0),
        total_conditional_pnl: totalPnl,
        base_currency: baseCurrency,
        warnings: [],
        assumptions_notice: "HYPOTHETICAL SCENARIO RESULT. Computed strictly from user-supplied assumptions.",
        generated_at: new Date().toISOString()
      });
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-4 font-mono text-xs space-y-4">
      {/* Configuration Box */}
      <div className="bg-zinc-900/60 border border-zinc-800 rounded p-4 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-sky-400" />
            <span className="font-semibold text-zinc-100 uppercase tracking-wider">
              DETERMINISTIC SCENARIO WORKBENCH
            </span>
          </div>
          <span className="text-[11px] text-zinc-400">
            Portfolio: {activePositions.length} positions
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Target Dimension */}
          <div>
            <label className="text-[10px] text-zinc-400 block mb-1">TARGET DIMENSION</label>
            <select
              value={targetDimension}
              onChange={(e) => {
                setTargetDimension(e.target.value);
                if (e.target.value === "SECTOR") setTargetIdentifier("Information Technology");
                if (e.target.value === "SECURITY") setTargetIdentifier("AAPL");
                if (e.target.value === "COUNTRY") setTargetIdentifier("US");
              }}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
            >
              <option value="SECTOR">SECTOR</option>
              <option value="SECURITY">SECURITY</option>
              <option value="COUNTRY">COUNTRY</option>
            </select>
          </div>

          {/* Target Identifier */}
          <div>
            <label className="text-[10px] text-zinc-400 block mb-1">TARGET IDENTIFIER</label>
            <input
              type="text"
              value={targetIdentifier}
              onChange={(e) => setTargetIdentifier(e.target.value)}
              placeholder="e.g. Information Technology, AAPL, US"
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Shock Value */}
          <div>
            <label className="text-[10px] text-zinc-400 block mb-1">HYPOTHETICAL SHOCK (%)</label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                step="1"
                value={shockValue}
                onChange={(e) => setShockValue(parseFloat(e.target.value) || 0)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-sky-500"
              />
              <button
                onClick={handleRunScenario}
                disabled={running}
                className="px-4 py-1.5 rounded bg-sky-600 hover:bg-sky-500 text-white font-bold flex items-center gap-1.5 transition-colors shrink-0 disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{running ? "EVALUATING..." : "RUN"}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory Prominent Scenario Notice */}
      <div className="p-3 bg-amber-950/20 border border-amber-800/80 rounded flex items-start gap-2.5 text-amber-300">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-[11px] leading-relaxed">
          <span className="font-bold uppercase tracking-wider block">HYPOTHETICAL SCENARIO RESULT</span>
          Computed strictly from user-supplied assumptions. Does not constitute a financial forecast, probability estimate, or realized market outcome.
        </div>
      </div>

      {/* Scenario Evaluation Results */}
      {scenarioRun && (
        <div className="space-y-3">
          <div className="p-3 bg-zinc-900/60 border border-zinc-800 rounded flex items-center justify-between">
            <span className="text-zinc-400">TOTAL CONDITIONAL P&L:</span>
            <span className={`text-base font-bold ${Number(scenarioRun.total_conditional_pnl) < 0 ? "text-rose-400" : "text-emerald-400"}`}>
              {formatCurrencyAmount(scenarioRun.total_conditional_pnl, baseCurrency)}
            </span>
          </div>

          <div className="overflow-x-auto border border-zinc-800 rounded">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-zinc-900 border-b border-zinc-800 text-zinc-400">
                  <th className="p-2">HOLDING</th>
                  <th className="p-2 text-right">SHOCK APPLIED</th>
                  <th className="p-2 text-right">CONDITIONAL P&L</th>
                  <th className="p-2">EXPLANATION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {scenarioRun.results.map((res) => (
                  <tr key={res.exposure_id} className="hover:bg-zinc-900/40">
                    <td className="p-2 font-medium text-zinc-200">
                      {res.target_entity_ref.canonical_name}
                    </td>
                    <td className="p-2 text-right font-bold text-amber-400">
                      {res.percentage}%
                    </td>
                    <td className={`p-2 text-right font-bold ${Number(res.amount) < 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {formatCurrencyAmount(res.amount, baseCurrency)}
                    </td>
                    <td className="p-2 text-zinc-400 text-[11px]">
                      {res.explanation}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
