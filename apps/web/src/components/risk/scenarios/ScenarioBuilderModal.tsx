"use client";

import React, { useState } from "react";
import {
  CreateScenarioRequest,
  RiskScenarioDTO,
  ScenarioShockDTO,
  ScenarioShockType,
  ScenarioType,
  ShockTargetType,
} from "@/lib/risk/types";
import { AlertCircle, Plus, Trash2, X, Zap } from "lucide-react";

interface ScenarioBuilderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateScenario: (req: CreateScenarioRequest) => Promise<RiskScenarioDTO>;
}

export function ScenarioBuilderModal({
  isOpen,
  onClose,
  onCreateScenario,
}: ScenarioBuilderModalProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [scenarioType, setScenarioType] = useState<ScenarioType>("HYPOTHETICAL_STRESS");
  const [shocks, setShocks] = useState<ScenarioShockDTO[]>([
    {
      target_type: "PORTFOLIO_WIDE",
      target_identifier: "ALL",
      shock_type: "PRICE_SHOCK",
      magnitude: -0.1,
    },
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAddShock = () => {
    setShocks((prev) => [
      ...prev,
      {
        target_type: "SECURITY",
        target_identifier: "AAPL",
        shock_type: "PRICE_SHOCK",
        magnitude: -0.05,
      },
    ]);
  };

  const handleRemoveShock = (idx: number) => {
    setShocks((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleShockChange = (
    idx: number,
    field: keyof ScenarioShockDTO,
    value: unknown
  ) => {
    setShocks((prev) => {
      const updated = [...prev];
      updated[idx] = { ...updated[idx], [field]: value };
      return updated;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Scenario name is required.");
      return;
    }
    if (shocks.length === 0) {
      setError("At least one shock definition is required.");
      return;
    }

    // Check magnitude >= -1.0
    for (const sh of shocks) {
      if (sh.magnitude < -1.0) {
        setError(`Shock for ${sh.target_identifier} cannot exceed -100% loss.`);
        return;
      }
    }

    setSubmitting(true);
    setError(null);
    try {
      await onCreateScenario({
        name,
        description,
        scenario_type: scenarioType,
        shocks,
      });
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl rounded-lg border border-atlas-border-default bg-atlas-surface-1 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-atlas-border-default/60 bg-atlas-surface-2 px-4 py-3">
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-amber-400" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Construct Custom Risk Scenario
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-atlas-text-secondary hover:text-atlas-text-primary transition"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {error && (
            <div className="flex items-start gap-2 rounded border border-rose-500/30 bg-rose-500/10 p-2.5 text-rose-300">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Basic Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-medium text-atlas-text-secondary uppercase mb-1">
                Scenario Name *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. 2026 Energy Shock & High Inflation"
                className="w-full rounded border border-atlas-border-default bg-atlas-surface-2 px-2.5 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent-blue focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-[11px] font-medium text-atlas-text-secondary uppercase mb-1">
                Scenario Type
              </label>
              <select
                value={scenarioType}
                onChange={(e) => setScenarioType(e.target.value as ScenarioType)}
                className="w-full rounded border border-atlas-border-default bg-atlas-surface-2 px-2.5 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent-blue focus:outline-none"
              >
                <option value="HYPOTHETICAL_STRESS">Hypothetical Stress</option>
                <option value="FACTOR_SHOCK">Factor Shock</option>
                <option value="MACRO_REGIME">Macro Regime</option>
                <option value="HISTORICAL_EPISODE">Historical Episode</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-atlas-text-secondary uppercase mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe macroeconomic drivers, interest rate assumptions, and shock transmission channels..."
              rows={2}
              className="w-full rounded border border-atlas-border-default bg-atlas-surface-2 px-2.5 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent-blue focus:outline-none"
            />
          </div>

          {/* Shock List */}
          <div className="border-t border-atlas-border-default/40 pt-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-semibold text-atlas-text-secondary uppercase tracking-wider">
                Configured Shocks ({shocks.length})
              </span>
              <button
                type="button"
                onClick={handleAddShock}
                className="flex items-center gap-1 text-[11px] font-medium text-atlas-accent-blue hover:underline"
              >
                <Plus className="h-3 w-3" />
                Add Shock
              </button>
            </div>

            <div className="space-y-2 max-h-56 overflow-y-auto">
              {shocks.map((sh, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-2"
                >
                  {/* Target Type */}
                  <select
                    value={sh.target_type}
                    onChange={(e) =>
                      handleShockChange(idx, "target_type", e.target.value as ShockTargetType)
                    }
                    className="rounded border border-atlas-border-default bg-atlas-surface-3 px-2 py-1 text-[11px] text-atlas-text-primary"
                  >
                    <option value="SECURITY">Security</option>
                    <option value="SECTOR">Sector</option>
                    <option value="INDUSTRY">Industry</option>
                    <option value="CURRENCY">Currency</option>
                    <option value="PORTFOLIO_WIDE">Portfolio Wide</option>
                  </select>

                  {/* Identifier */}
                  <input
                    type="text"
                    value={sh.target_identifier}
                    onChange={(e) => handleShockChange(idx, "target_identifier", e.target.value)}
                    placeholder="Ticker / Sector / ALL"
                    className="w-28 rounded border border-atlas-border-default bg-atlas-surface-3 px-2 py-1 text-[11px] font-mono text-atlas-text-primary"
                  />

                  {/* Shock Type */}
                  <select
                    value={sh.shock_type}
                    onChange={(e) =>
                      handleShockChange(idx, "shock_type", e.target.value as ScenarioShockType)
                    }
                    className="rounded border border-atlas-border-default bg-atlas-surface-3 px-2 py-1 text-[11px] text-atlas-text-primary"
                  >
                    <option value="PRICE_SHOCK">Price Shock</option>
                    <option value="FX_SHOCK">FX Shock</option>
                    <option value="VOLATILITY_EXPANSION">Vol Expansion</option>
                  </select>

                  {/* Magnitude % */}
                  <div className="flex items-center gap-1 font-mono">
                    <input
                      type="number"
                      step="0.1"
                      value={(sh.magnitude * 100).toFixed(1)}
                      onChange={(e) =>
                        handleShockChange(
                          idx,
                          "magnitude",
                          parseFloat(e.target.value || "0") / 100
                        )
                      }
                      className="w-16 rounded border border-atlas-border-default bg-atlas-surface-3 px-1.5 py-1 text-[11px] text-right text-atlas-text-primary"
                    />
                    <span className="text-[11px] text-atlas-text-muted">%</span>
                  </div>

                  {/* Remove Button */}
                  <button
                    type="button"
                    onClick={() => handleRemoveShock(idx)}
                    className="text-atlas-text-muted hover:text-rose-400 transition p-1"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Footer Actions */}
          <div className="border-t border-atlas-border-default/60 pt-3 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded bg-atlas-surface-2 px-3 py-1.5 text-xs font-medium text-atlas-text-secondary hover:bg-atlas-surface-3 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded bg-atlas-accent-blue px-4 py-1.5 text-xs font-medium text-white hover:bg-atlas-accent-blue/90 disabled:opacity-50 transition shadow-sm"
            >
              {submitting ? "Saving..." : "Save & Register Scenario"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

