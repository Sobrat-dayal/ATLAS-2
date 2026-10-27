"use client";

import React, { useState } from "react";
import {
  CreateResearchAssumptionDTO,
  ResearchAnalysis,
  ResearchAssumption,
  SensitivityAnalysisRequest,
  SensitivityAnalysisResponse,
} from "@/lib/research/types";
import { Badge, Button } from "@/design-system";

interface ScenarioSensitivityWorkspaceProps {
  analysis: ResearchAnalysis;
  assumptions: ResearchAssumption[];
  sensitivityResult?: SensitivityAnalysisResponse | null;
  isLoading: boolean;
  onCreateAssumption: (data: CreateResearchAssumptionDTO) => Promise<unknown>;
  onDeleteAssumption: (assumptionId: string) => Promise<unknown>;
  onExecuteSensitivity: (data: SensitivityAnalysisRequest) => Promise<unknown>;
}

export function ScenarioSensitivityWorkspace({
  analysis,
  assumptions,
  sensitivityResult,
  isLoading,
  onCreateAssumption,
  onDeleteAssumption,
  onExecuteSensitivity,
}: ScenarioSensitivityWorkspaceProps) {
  // New assumption inputs
  const [isAddingAssumption, setIsAddingAssumption] = useState(false);
  const [label, setLabel] = useState("");
  const [parameterId, setParameterId] = useState("");
  const [value, setValue] = useState<number>(5.0);
  const [unit, setUnit] = useState("%");
  const [sourceType, setSourceType] = useState<"ANALYST_ASSUMED" | "SOURCE_REPORTED" | "DERIVED">("ANALYST_ASSUMED");
  const [analystNote, setAnalystNote] = useState("");

  // Sensitivity matrix inputs
  const [baseMetricValue, setBaseMetricValue] = useState<number>(100000.0);
  const [metricName, setMetricName] = useState<string>("Operating Profit");
  const matrixUnit = "$M";
  const [growthRatesStr, setGrowthRatesStr] = useState<string>("-0.05, 0.0, 0.05, 0.10");
  const [marginRatesStr, setMarginRatesStr] = useState<string>("0.28, 0.30, 0.32, 0.34");

  const handleAddAssumption = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!label.trim() || !parameterId.trim()) return;

    await onCreateAssumption({
      label: label.trim(),
      parameter_id: parameterId.trim(),
      value: Number(value),
      unit: unit.trim(),
      source_type: sourceType,
      analyst_note: analystNote.trim() || undefined,
    });

    setLabel("");
    setParameterId("");
    setValue(5.0);
    setAnalystNote("");
    setIsAddingAssumption(false);
  };

  const handleRunSensitivity = async (e: React.FormEvent) => {
    e.preventDefault();
    const growthRates = growthRatesStr
      .split(",")
      .map((s) => parseFloat(s.trim()))
      .filter((n) => !isNaN(n));

    const marginRates = marginRatesStr
      .split(",")
      .map((s) => parseFloat(s.trim()))
      .filter((n) => !isNaN(n));

    await onExecuteSensitivity({
      base_metric_value: Number(baseMetricValue),
      metric_name: metricName,
      unit: matrixUnit,
      growth_rates: growthRates,
      margin_rates: marginRates,
    });
  };

  return (
    <div className="space-y-6">
      {/* 1. Analyst Assumptions Registry */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-subtle pb-3">
          <div>
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Analyst Assumptions Registry
            </h3>
            <p className="text-xs text-atlas-text-muted">
              Explicitly managed scenario inputs for {analysis.primary_subject_entity_id || "target entity"} distinguishing hypothetical bounds from verified historical facts.
            </p>
          </div>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => setIsAddingAssumption(!isAddingAssumption)}
          >
            {isAddingAssumption ? "Cancel" : "Add Assumption"}
          </Button>
        </div>

        {isAddingAssumption && (
          <form onSubmit={handleAddAssumption} className="mb-4 rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-3 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                  Assumption Label
                </label>
                <input
                  type="text"
                  placeholder="e.g. Long-Term Tax Rate"
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                  className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-primary"
                  required
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                  Parameter ID
                </label>
                <input
                  type="text"
                  placeholder="e.g. tax_rate"
                  value={parameterId}
                  onChange={(e) => setParameterId(e.target.value)}
                  className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs font-mono text-atlas-text-primary"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                    Value
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={value}
                    onChange={(e) => setValue(Number(e.target.value))}
                    className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs font-mono text-atlas-text-primary"
                    required
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                    Unit
                  </label>
                  <input
                    type="text"
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-primary"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                  Source Epistemic Type
                </label>
                <select
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value as "ANALYST_ASSUMED" | "SOURCE_REPORTED" | "DERIVED")}
                  className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-primary"
                >
                  <option value="ANALYST_ASSUMED">Analyst Assumed (Hypothetical)</option>
                  <option value="SOURCE_REPORTED">Source Reported (Official Guidance)</option>
                  <option value="DERIVED">Derived from Ratio Registry</option>
                </select>
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                  Rationale / Note
                </label>
                <input
                  type="text"
                  placeholder="Brief note on why this value was selected"
                  value={analystNote}
                  onChange={(e) => setAnalystNote(e.target.value)}
                  className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-primary"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-1">
              <Button type="submit" variant="primary" size="sm">
                Persist Assumption
              </Button>
            </div>
          </form>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-atlas-border-default bg-atlas-surface-1 font-mono text-[11px] text-atlas-text-secondary uppercase">
              <tr>
                <th className="px-3 py-2">Parameter</th>
                <th className="px-3 py-2">Label</th>
                <th className="px-3 py-2 text-right">Value</th>
                <th className="px-3 py-2">Unit</th>
                <th className="px-3 py-2">Category</th>
                <th className="px-3 py-2">Analyst Note</th>
                <th className="px-3 py-2 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle font-mono text-atlas-text-primary">
              {assumptions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-3 py-4 text-center text-xs text-atlas-text-muted italic">
                    No custom assumptions defined. Defaulting to historical baseline.
                  </td>
                </tr>
              ) : (
                assumptions.map((a) => (
                  <tr key={a.assumption_id} className="hover:bg-atlas-surface-1/50">
                    <td className="px-3 py-2 font-semibold text-atlas-accent">{a.parameter_id}</td>
                    <td className="px-3 py-2 font-sans">{a.label}</td>
                    <td className="px-3 py-2 text-right font-semibold">{a.value.toLocaleString()}</td>
                    <td className="px-3 py-2 text-atlas-text-muted">{a.unit}</td>
                    <td className="px-3 py-2">
                      <Badge variant={a.source_type === "SOURCE_REPORTED" ? "positive" : "outline"} className="text-[10px]">
                        {a.source_type}
                      </Badge>
                    </td>
                    <td className="px-3 py-2 text-atlas-text-secondary font-sans text-[11px] max-w-xs truncate">
                      {a.analyst_note || "—"}
                    </td>
                    <td className="px-3 py-2 text-center">
                      <button
                        type="button"
                        onClick={() => onDeleteAssumption(a.assumption_id)}
                        className="text-xs text-atlas-text-muted hover:text-rose-500"
                        title="Delete Assumption"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 2. Deterministic Sensitivity Matrix */}
      <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-4">
        <div className="mb-4 border-b border-atlas-border-subtle pb-3">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Bounded Sensitivity Matrix (What-If Arithmetic)
            </h3>
            <Badge variant="outline" className="font-mono text-[10px]">
              DETERMINISTIC
            </Badge>
          </div>
          <p className="text-xs text-atlas-text-muted">
            Evaluates mathematical outcomes under dual parameter grids without simulating unverified probabilities or forecast returns.
          </p>
        </div>

        <form onSubmit={handleRunSensitivity} className="mb-4 grid grid-cols-1 md:grid-cols-5 gap-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Base Metric Value
            </label>
            <input
              type="number"
              step="any"
              value={baseMetricValue}
              onChange={(e) => setBaseMetricValue(Number(e.target.value))}
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs font-mono text-atlas-text-primary"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Metric Name
            </label>
            <input
              type="text"
              value={metricName}
              onChange={(e) => setMetricName(e.target.value)}
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Growth Rates Grid (comma)
            </label>
            <input
              type="text"
              value={growthRatesStr}
              onChange={(e) => setGrowthRatesStr(e.target.value)}
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs font-mono text-atlas-text-primary"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Margin Rates Grid (comma)
            </label>
            <input
              type="text"
              value={marginRatesStr}
              onChange={(e) => setMarginRatesStr(e.target.value)}
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs font-mono text-atlas-text-primary"
              required
            />
          </div>

          <div className="flex items-end">
            <Button
              type="submit"
              variant="primary"
              size="sm"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? "Calculating..." : "Compute Matrix"}
            </Button>
          </div>
        </form>

        {/* Sensitivity Grid Table */}
        {sensitivityResult && (
          <div className="space-y-3">
            <div className="overflow-x-auto rounded-xs border border-atlas-border-default bg-atlas-surface-1">
              <table className="w-full text-center text-xs">
                <thead className="border-b border-atlas-border-default bg-atlas-surface-2 font-mono text-[11px] text-atlas-text-secondary uppercase">
                  <tr>
                    <th className="px-3 py-2 text-left">Growth \ Margin</th>
                    {sensitivityResult.margin_rates.map((m, idx) => (
                      <th key={idx} className="px-3 py-2">
                        {(m * 100).toFixed(1)}% Margin
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-atlas-border-subtle font-mono">
                  {sensitivityResult.growth_rates.map((g, rIdx) => (
                    <tr key={rIdx} className="hover:bg-atlas-surface-0/60 transition-colors">
                      <td className="px-3 py-2.5 text-left font-semibold text-atlas-text-primary bg-atlas-surface-2/40">
                        {g > 0 ? "+" : ""}{(g * 100).toFixed(1)}% Growth
                      </td>
                      {sensitivityResult.scenario_matrix[rIdx].map((val, cIdx) => (
                        <td
                          key={cIdx}
                          className="px-3 py-2.5 font-medium text-atlas-text-primary"
                        >
                          {val.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })} {sensitivityResult.unit}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Non-Predictive Illustrative Institutional Notice */}
            <div className="rounded-xs border border-atlas-border-subtle bg-atlas-surface-1 p-3 text-[11px] text-atlas-text-muted">
              <span className="font-semibold text-atlas-text-secondary">Institutional Disclosure: </span>
              {sensitivityResult.qualification_notice}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
