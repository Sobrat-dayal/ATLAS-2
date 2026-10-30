"use client";

import React, { useState } from "react";
import {
  ConstraintType,
  ConstraintValidationResultDTO,
  OptimizationConstraintRequestDTO,
  UniverseAssetDTO,
} from "@/lib/portfolios/optimization/types";
import { formatPercent } from "@/lib/portfolios/optimization/formatting";
import { AlertCircle, CheckCircle2, Plus, ShieldAlert, Sliders, Trash2 } from "lucide-react";

interface OptimizationConstraintBuilderProps {
  constraints: OptimizationConstraintRequestDTO[];
  universe: UniverseAssetDTO[];
  validationResult: ConstraintValidationResultDTO | null;
  onAddConstraint: (c: OptimizationConstraintRequestDTO) => void;
  onRemoveConstraint: (index: number) => void;
  onValidate: () => Promise<void>;
  onApplyPreset?: (preset: string) => void;
}

export function OptimizationConstraintBuilder({
  constraints,
  universe,
  validationResult,
  onAddConstraint,
  onRemoveConstraint,
  onValidate,
}: OptimizationConstraintBuilderProps) {
  const [constraintType, setConstraintType] = useState<ConstraintType>("SECURITY_WEIGHT_BOUND");
  const [scope, setScope] = useState<string>("SECURITY");
  const [targetId, setTargetId] = useState<string>(universe[0]?.symbol || "");
  const [lowerBound, setLowerBound] = useState<string>("");
  const [upperBound, setUpperBound] = useState<string>("0.20");
  const [isHard, setIsHard] = useState<boolean>(true);
  const [validating, setValidating] = useState<boolean>(false);

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();

    let resolvedScope = scope;
    let resolvedTarget = targetId;

    if (constraintType === "LONG_ONLY") {
      resolvedScope = "PORTFOLIO";
      resolvedTarget = "";
    } else if (constraintType === "FULLY_INVESTED") {
      resolvedScope = "PORTFOLIO";
      resolvedTarget = "";
    } else if (constraintType === "TURNOVER_LIMIT") {
      resolvedScope = "PORTFOLIO";
      resolvedTarget = "";
    } else if (constraintType === "CASH_WEIGHT_BOUND") {
      resolvedScope = "PORTFOLIO";
      resolvedTarget = "CASH";
    }

    const newConstraint: OptimizationConstraintRequestDTO = {
      constraint_type: constraintType,
      scope: resolvedScope,
      target_id: resolvedTarget || undefined,
      lower_bound: lowerBound ? parseFloat(lowerBound) : undefined,
      upper_bound: upperBound ? parseFloat(upperBound) : undefined,
      is_hard: isHard,
    };

    onAddConstraint(newConstraint);
    setLowerBound("");
  };

  const handleValidateClick = async () => {
    setValidating(true);
    try {
      await onValidate();
    } finally {
      setValidating(false);
    }
  };

  // Quick Preset Helper
  const applyPreset = (presetName: string) => {
    if (presetName === "MAX_20_PCT_SECURITY") {
      universe.forEach((u) => {
        onAddConstraint({
          constraint_type: "SECURITY_WEIGHT_BOUND",
          scope: "SECURITY",
          target_id: u.symbol,
          lower_bound: 0.0,
          upper_bound: 0.2,
          is_hard: true,
        });
      });
    } else if (presetName === "MIN_2_PCT_CASH") {
      onAddConstraint({
        constraint_type: "CASH_WEIGHT_BOUND",
        scope: "PORTFOLIO",
        target_id: "CASH",
        lower_bound: 0.02,
        upper_bound: 0.5,
        is_hard: true,
      });
    } else if (presetName === "MAX_30_TURNOVER") {
      onAddConstraint({
        constraint_type: "TURNOVER_LIMIT",
        scope: "PORTFOLIO",
        target_id: undefined,
        upper_bound: 0.3,
        is_hard: true,
      });
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Banner & Quick Presets */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Sliders className="h-4 w-4 text-atlas-accent" />
              <h3 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
                Optimization Constraint Engine
              </h3>
            </div>
            <p className="mt-0.5 text-xs text-atlas-text-muted">
              Define regulatory, concentration, and turnover bounds. Verified for mathematical feasibility before solving.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => applyPreset("MAX_20_PCT_SECURITY")}
              className="rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-secondary hover:border-atlas-accent hover:text-atlas-text-primary"
            >
              + Preset: Max 20% Security
            </button>
            <button
              type="button"
              onClick={() => applyPreset("MIN_2_PCT_CASH")}
              className="rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-secondary hover:border-atlas-accent hover:text-atlas-text-primary"
            >
              + Preset: Min 2% Cash
            </button>
            <button
              type="button"
              onClick={() => applyPreset("MAX_30_TURNOVER")}
              className="rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-secondary hover:border-atlas-accent hover:text-atlas-text-primary"
            >
              + Preset: Max 30% Turnover
            </button>
          </div>
        </div>
      </div>

      {/* Add Constraint Form */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-atlas-text-secondary">
          Add Portfolio Constraint
        </h4>

        <form onSubmit={handleAdd} className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-6">
          {/* Constraint Type */}
          <div className="space-y-1">
            <label className="text-[11px] text-atlas-text-muted">Type</label>
            <select
              value={constraintType}
              onChange={(e) => {
                const val = e.target.value as ConstraintType;
                setConstraintType(val);
                if (val === "SECTOR_WEIGHT_BOUND") setScope("SECTOR");
                else if (val === "SECURITY_WEIGHT_BOUND") setScope("SECURITY");
                else setScope("PORTFOLIO");
              }}
              className="w-full rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            >
              <option value="SECURITY_WEIGHT_BOUND">Security Weight Bound</option>
              <option value="SECTOR_WEIGHT_BOUND">Sector Weight Bound</option>
              <option value="CASH_WEIGHT_BOUND">Cash Weight Bound</option>
              <option value="TURNOVER_LIMIT">Turnover Limit</option>
              <option value="VOLATILITY_LIMIT">Volatility Limit</option>
              <option value="LONG_ONLY">Long Only (0% - 100%)</option>
              <option value="FULLY_INVESTED">Fully Invested</option>
            </select>
          </div>

          {/* Target / Identifier */}
          <div className="space-y-1">
            <label className="text-[11px] text-atlas-text-muted">Target / Asset</label>
            {constraintType === "SECURITY_WEIGHT_BOUND" ? (
              <select
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                className="w-full rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              >
                {universe.map((u) => (
                  <option key={u.symbol} value={u.symbol}>
                    {u.symbol} ({u.name})
                  </option>
                ))}
              </select>
            ) : constraintType === "SECTOR_WEIGHT_BOUND" ? (
              <input
                type="text"
                placeholder="e.g. Information Technology"
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                className="w-full rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
              />
            ) : (
              <input
                type="text"
                disabled
                value={constraintType === "CASH_WEIGHT_BOUND" ? "CASH" : "PORTFOLIO"}
                className="w-full rounded border border-atlas-border-default/40 bg-atlas-surface-2/40 px-2 py-1.5 text-xs text-atlas-text-muted"
              />
            )}
          </div>

          {/* Lower Bound */}
          <div className="space-y-1">
            <label className="text-[11px] text-atlas-text-muted">Min Weight / Val (e.g. 0.05)</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              value={lowerBound}
              onChange={(e) => setLowerBound(e.target.value)}
              className="w-full rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2 py-1.5 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            />
          </div>

          {/* Upper Bound */}
          <div className="space-y-1">
            <label className="text-[11px] text-atlas-text-muted">Max Weight / Val (e.g. 0.20)</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.25"
              value={upperBound}
              onChange={(e) => setUpperBound(e.target.value)}
              className="w-full rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2 py-1.5 text-xs font-mono text-atlas-text-primary focus:border-atlas-accent focus:outline-none"
            />
          </div>

          {/* Hard / Soft Constraint */}
          <div className="flex flex-col justify-end pb-1.5">
            <label className="flex items-center gap-2 cursor-pointer text-xs text-atlas-text-secondary">
              <input
                type="checkbox"
                checked={isHard}
                onChange={(e) => setIsHard(e.target.checked)}
                className="rounded border-atlas-border-default bg-atlas-surface-2 text-atlas-accent focus:ring-0"
              />
              <span>Hard Constraint</span>
            </label>
          </div>

          {/* Submit Button */}
          <div className="flex items-end">
            <button
              type="submit"
              className="flex w-full items-center justify-center gap-1.5 rounded bg-atlas-accent px-3 py-1.5 text-xs font-semibold text-atlas-surface-0 hover:bg-atlas-accent/90 transition-colors"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>Add Constraint</span>
            </button>
          </div>
        </form>
      </div>

      {/* Constraints List & Feasibility Checker */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-secondary">
              Active Constraints ({constraints.length})
            </h4>
          </div>

          <button
            type="button"
            onClick={handleValidateClick}
            disabled={validating || constraints.length === 0}
            className="flex items-center gap-1.5 rounded border border-cyan-500/40 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-300 hover:bg-cyan-500/20 disabled:opacity-50 transition-colors"
          >
            <ShieldAlert className="h-3.5 w-3.5" />
            <span>{validating ? "Validating Feasibility..." : "Validate Feasibility"}</span>
          </button>
        </div>

        {/* Validation Result Banner */}
        {validationResult && (
          <div
            className={`mb-4 flex items-start gap-2.5 rounded border p-3 text-xs ${
              validationResult.is_feasible
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                : "border-rose-500/30 bg-rose-500/10 text-rose-300"
            }`}
          >
            {validationResult.is_feasible ? (
              <CheckCircle2 className="h-4 w-4 mt-0.5 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="h-4 w-4 mt-0.5 text-rose-400 shrink-0" />
            )}
            <div className="space-y-1">
              <p className="font-semibold">{validationResult.message}</p>
              {validationResult.conflicts && validationResult.conflicts.length > 0 && (
                <ul className="list-disc pl-4 space-y-0.5 text-[11px] opacity-90">
                  {validationResult.conflicts.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}

        {/* Constraints Table */}
        {constraints.length === 0 ? (
          <div className="p-6 text-center text-xs text-atlas-text-muted">
            No custom constraints added. Unconstrained / standard long-only budget constraints will be applied by default.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-atlas-border-default/60 text-atlas-text-muted">
                  <th className="py-2 font-medium">Type</th>
                  <th className="py-2 font-medium">Scope</th>
                  <th className="py-2 font-medium">Target</th>
                  <th className="py-2 font-medium text-right">Min Bound</th>
                  <th className="py-2 font-medium text-right">Max Bound</th>
                  <th className="py-2 font-medium text-center">Enforcement</th>
                  <th className="py-2 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default/40">
                {constraints.map((c, idx) => (
                  <tr key={idx} className="hover:bg-atlas-surface-2/40">
                    <td className="py-2.5 font-medium text-atlas-text-primary">
                      {c.constraint_type}
                    </td>
                    <td className="py-2.5 text-atlas-text-secondary">{c.scope}</td>
                    <td className="py-2.5 font-mono text-cyan-300">
                      {c.target_id || "—"}
                    </td>
                    <td className="py-2.5 text-right font-mono text-atlas-text-primary">
                      {c.lower_bound !== undefined && c.lower_bound !== null
                        ? `${(Number(c.lower_bound) * 100).toFixed(1)}%`
                        : "—"}
                    </td>
                    <td className="py-2.5 text-right font-mono text-atlas-text-primary">
                      {c.upper_bound !== undefined && c.upper_bound !== null
                        ? `${(Number(c.upper_bound) * 100).toFixed(1)}%`
                        : "—"}
                    </td>
                    <td className="py-2.5 text-center">
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                          c.is_hard
                            ? "bg-slate-700 text-slate-200"
                            : "bg-amber-500/10 text-amber-400"
                        }`}
                      >
                        {c.is_hard ? "HARD" : "SOFT"}
                      </span>
                    </td>
                    <td className="py-2.5 text-right">
                      <button
                        type="button"
                        onClick={() => onRemoveConstraint(idx)}
                        className="rounded p-1 text-atlas-text-muted hover:bg-rose-500/10 hover:text-rose-400 transition-colors"
                        title="Remove constraint"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
