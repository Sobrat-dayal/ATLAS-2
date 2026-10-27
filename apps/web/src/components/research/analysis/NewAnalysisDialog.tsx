"use client";

import React, { useState } from "react";
import {
  CreateResearchAnalysisDTO,
  ResearchAnalysisSpecification,
  ResearchAnalysisType,
  ResearchInvestigation,
} from "@/lib/research/types";
import { Button } from "@/design-system";
import * as api from "@/lib/research/api";

interface NewAnalysisDialogProps {
  isOpen: boolean;
  investigations: ResearchInvestigation[];
  onClose: () => void;
  onSubmit: (data: CreateResearchAnalysisDTO) => Promise<unknown>;
}

export function NewAnalysisDialog({
  isOpen,
  investigations,
  onClose,
  onSubmit,
}: NewAnalysisDialogProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [researchObjective, setResearchObjective] = useState("");
  const [analysisType, setAnalysisType] = useState<ResearchAnalysisType>("COMPANY_FINANCIAL_TREND");
  const [primaryEntityId, setPrimaryEntityId] = useState("AAPL");
  const [metricId, setMetricId] = useState("operating_income");
  const [frequency, setFrequency] = useState<"ANNUAL" | "QUARTERLY">("ANNUAL");
  const [selectedInvestigationId, setSelectedInvestigationId] = useState<string>("");
  const [inputPolicy, setInputPolicy] = useState<"PINNED_SOURCE_VERSION" | "LATEST_AUTHORIZED_DATA">("PINNED_SOURCE_VERSION");

  const [validationState, setValidationState] = useState<{
    tested: boolean;
    valid: boolean;
    errors: string[];
    warnings: string[];
  }>({ tested: false, valid: true, errors: [], warnings: [] });
  const [isValidating, setIsValidating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const buildSpec = (): ResearchAnalysisSpecification => ({
    analysis_type: analysisType,
    primary_entity_id: primaryEntityId.trim().toUpperCase(),
    metric_ids: [metricId.trim()],
    frequency,
    input_version_policy: inputPolicy,
    outlier_policy: "INCLUDE_ALL",
    currency: "USD",
    methodology_version: 1,
  });

  const handleValidate = async () => {
    setIsValidating(true);
    try {
      const res = await api.validateAnalysisSpecification({ specification: buildSpec() });
      setValidationState({
        tested: true,
        valid: res.is_valid,
        errors: res.errors,
        warnings: res.warnings,
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Validation call failed.";
      setValidationState({
        tested: true,
        valid: false,
        errors: [msg],
        warnings: [],
      });
    } finally {
      setIsValidating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !primaryEntityId.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        research_objective: researchObjective.trim() || undefined,
        analysis_type: analysisType,
        primary_subject_entity_id: primaryEntityId.trim().toUpperCase(),
        primary_subject_type: "COMPANY",
        secondary_entity_ids: [],
        specification: buildSpec(),
        investigation_id: selectedInvestigationId || undefined,
      });
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
      <div className="w-full max-w-xl rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-5 shadow-xl animate-in fade-in zoom-in-95">
        <div className="mb-4 flex items-center justify-between border-b border-atlas-border-subtle pb-3">
          <div>
            <h2 className="text-sm font-semibold text-atlas-text-primary">
              Create Research Analysis Workbench
            </h2>
            <p className="text-xs text-atlas-text-muted">
              Configure a reproducible quantitative financial study grounded in verified data.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Analysis Title *
            </label>
            <input
              type="text"
              placeholder="e.g. Apple Operating Profitability Multi-Year Trend"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-accent focus:outline-hidden"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Analysis Type
              </label>
              <select
                value={analysisType}
                onChange={(e) => setAnalysisType(e.target.value as ResearchAnalysisType)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
              >
                <option value="COMPANY_FINANCIAL_TREND">Company Financial Trend</option>
                <option value="COMPANY_RATIO_ANALYSIS">Company Ratio Analysis</option>
                <option value="PEER_BENCHMARKING">Cross-Sectional Peer Benchmarking</option>
                <option value="CASH_FLOW_ANALYSIS">Cash Flow Dynamics</option>
                <option value="CAPITAL_STRUCTURE_ANALYSIS">Capital Structure & Leverage</option>
                <option value="MACROECONOMIC_TIME_SERIES">Macroeconomic Time Series</option>
                <option value="HYPOTHESIS_EVALUATION">Deterministic Hypothesis Evaluation</option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Target Entity Ticker / ID *
              </label>
              <input
                type="text"
                placeholder="AAPL, MSFT, NVDA, GOOGL"
                value={primaryEntityId}
                onChange={(e) => setPrimaryEntityId(e.target.value)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs font-mono uppercase text-atlas-text-primary"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Canonical Metric ID
              </label>
              <select
                value={metricId}
                onChange={(e) => setMetricId(e.target.value)}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs font-mono text-atlas-text-primary"
              >
                <option value="operating_income">operating_income</option>
                <option value="revenue">revenue</option>
                <option value="net_income">net_income</option>
                <option value="gross_profit">gross_profit</option>
                <option value="operating_cash_flow">operating_cash_flow</option>
                <option value="free_cash_flow">free_cash_flow</option>
                <option value="operating_margin">operating_margin (%)</option>
                <option value="net_margin">net_margin (%)</option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Frequency
              </label>
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value as "ANNUAL" | "QUARTERLY")}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
              >
                <option value="ANNUAL">Annual (10-K)</option>
                <option value="QUARTERLY">Quarterly (10-Q)</option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
                Data Version Policy
              </label>
              <select
                value={inputPolicy}
                onChange={(e) => setInputPolicy(e.target.value as "PINNED_SOURCE_VERSION" | "LATEST_AUTHORIZED_DATA")}
                className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
              >
                <option value="PINNED_SOURCE_VERSION">Pinned Filing Version</option>
                <option value="LATEST_AUTHORIZED_DATA">Latest Authorized Data</option>
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Description (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. Multi-year profitability analysis"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Link to Research Investigation (Optional)
            </label>
            <select
              value={selectedInvestigationId}
              onChange={(e) => setSelectedInvestigationId(e.target.value)}
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-3 py-1.5 text-xs text-atlas-text-primary"
            >
              <option value="">Standalone Analysis (No Investigation Link)</option>
              {investigations.map((inv) => (
                <option key={inv.investigation_id} value={inv.investigation_id}>
                  {inv.title} ({inv.investigation_id})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Research Objective
            </label>
            <textarea
              rows={2}
              placeholder="State the core hypothesis or analytical inquiry..."
              value={researchObjective}
              onChange={(e) => setResearchObjective(e.target.value)}
              className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 p-2 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted"
            />
          </div>

          {/* Validation Feedback */}
          {validationState.tested && (
            <div
              className={`rounded-xs border p-2 text-xs ${
                validationState.valid
                  ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-500"
                  : "border-rose-500/30 bg-rose-500/10 text-rose-500"
              }`}
            >
              {validationState.valid
                ? "✓ Specification is valid and ready for execution."
                : `✕ Validation failed: ${validationState.errors.join(", ")}`}
            </div>
          )}

          <div className="flex items-center justify-between border-t border-atlas-border-subtle pt-3">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={handleValidate}
              disabled={isValidating}
            >
              {isValidating ? "Validating..." : "Pre-Validate"}
            </Button>

            <div className="flex gap-2">
              <Button type="button" variant="secondary" size="sm" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
                {isSubmitting ? "Creating..." : "Create Analysis"}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
