"use client";

import React, { useState } from "react";
import { useAiActionPlan } from "@/hooks/ai/actions/useAiActionPlan";
import { AiActionCard } from "./AiActionCard";

const QUICK_ACTIONS = [
  {
    label: "Add 20 & 50 SMA (Chart)",
    prompt: "Add 20-period SMA and 50-period SMA to active chart",
    hints: { chart_id: "chart_fixture_a" },
  },
  {
    label: "India Tech Growth Screen (Screener)",
    prompt: "Find Indian companies with positive net profit, revenue growth above 15%, and market cap above 10,000 crore",
    hints: { screener_id: "screener_fixture_b" },
  },
  {
    label: "50/50 Equity/Bonds Scenario (Portfolio)",
    prompt: "Shift portfolio allocation to 50% Equity and 50% Bonds",
    hints: { portfolio_id: "TEST_P" },
  },
  {
    label: "99% 1-Day Historical VaR (Risk)",
    prompt: "Calculate historical Value at Risk for my selected Portfolio using a one-day horizon and 99% confidence level",
    hints: { portfolio_id: "TEST_P" },
  },
];

export function AiActionPanel() {
  const [prompt, setPrompt] = useState("");
  const {
    plan,
    receipts,
    isLoading,
    isExecuting,
    error,
    generatePlan,
    approve,
    deny,
    execute,
    undo,
    clear,
  } = useAiActionPlan();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    generatePlan(prompt);
  };

  const handleQuickAction = (item: (typeof QUICK_ACTIONS)[0]) => {
    setPrompt(item.prompt);
    generatePlan(item.prompt, item.hints);
  };

  const hasApprovedActions =
    plan &&
    plan.actions.some(
      (a) => a.action_status === "APPROVED" || a.approval_policy === "AUTO_READ_ONLY"
    );

  const canExecute =
    plan &&
    plan.status !== "COMPLETED" &&
    plan.status !== "EXECUTING" &&
    hasApprovedActions;

  return (
    <div className="space-y-4">
      {/* Header and natural language intent input */}
      <div className="p-4 rounded-xl border border-neutral-800 bg-neutral-900/60 shadow-sm space-y-3">
        <div>
          <h3 className="text-sm font-semibold text-neutral-100">
            Institutional AI Financial Action Engine
          </h3>
          <p className="text-xs text-neutral-400">
            Natural-language control for Charts, Screeners, Portfolios, and Risk with strict preview,
            human approval, and zero unauthorized trading.
          </p>
        </div>

        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Add 20-period SMA to chart, or Shift portfolio allocation to 50/50 Equity/Bonds..."
            className="flex-1 px-3 py-2 rounded-lg border border-neutral-700 bg-neutral-850 text-neutral-100 placeholder-neutral-500 text-xs focus:outline-none focus:border-cyan-500 transition-colors"
          />
          <button
            type="submit"
            disabled={isLoading || !prompt.trim()}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs transition-colors disabled:opacity-50"
          >
            {isLoading ? "Planning..." : "Propose Action"}
          </button>
        </form>

        {/* Quick Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          <span className="text-[10px] text-neutral-500 uppercase font-semibold mr-1">
            Presets:
          </span>
          {QUICK_ACTIONS.map((item, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleQuickAction(item)}
              className="px-2.5 py-1 rounded-md border border-neutral-800 bg-neutral-850 hover:bg-neutral-800 text-neutral-300 text-[11px] transition-colors"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-3 rounded-lg border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs flex items-center justify-between">
          <span>{error}</span>
          <button
            type="button"
            onClick={clear}
            className="text-neutral-400 hover:text-neutral-200 text-xs underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Action Plan View */}
      {plan && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-neutral-200">
                Action Plan ({plan.actions.length} step{plan.actions.length > 1 ? "s" : ""}):
              </span>
              <span className="font-mono text-neutral-500 text-[11px]">{plan.plan_id}</span>
            </div>

            <div className="flex items-center gap-2">
              {canExecute && (
                <button
                  type="button"
                  onClick={execute}
                  disabled={isExecuting}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-sm transition-colors disabled:opacity-50 flex items-center gap-1.5"
                >
                  {isExecuting ? "Executing Services..." : "Execute Approved Operations"}
                </button>
              )}
              <button
                type="button"
                onClick={clear}
                className="px-2.5 py-1.5 rounded border border-neutral-800 hover:bg-neutral-850 text-neutral-400 hover:text-neutral-200 text-xs"
              >
                Clear Plan
              </button>
            </div>
          </div>

          <div className="space-y-3">
            {plan.actions.map((act) => {
              const matchedReceipt = receipts.find((r) => r.action_id === act.action_id);
              return (
                <AiActionCard
                  key={act.action_id}
                  action={act}
                  receipt={matchedReceipt}
                  onApprove={approve}
                  onDeny={deny}
                  onUndo={undo}
                  isLoading={isLoading || isExecuting}
                />
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

