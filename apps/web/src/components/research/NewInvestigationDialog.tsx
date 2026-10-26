"use client";

import React, { useState } from "react";
import { Badge, Button, Input } from "@/design-system";
import { CreateResearchInvestigationDTO, ResearchType } from "@/lib/research/types";

interface NewInvestigationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateResearchInvestigationDTO) => Promise<any>;
}

const COMMON_ENTITIES = [
  { id: "AAPL", label: "Apple Inc. (AAPL)", type: "COMPANY" },
  { id: "MSFT", label: "Microsoft Corp. (MSFT)", type: "COMPANY" },
  { id: "NVDA", label: "NVIDIA Corp. (NVDA)", type: "COMPANY" },
  { id: "US_CPI", label: "U.S. Consumer Price Index", type: "MACROECONOMIC" },
  { id: "FED", label: "Federal Reserve Board", type: "MACROECONOMIC" },
  { id: "SPY", label: "SPDR S&P 500 ETF Trust", type: "INSTRUMENT" },
];

const RESEARCH_TYPES: { type: ResearchType; label: string }[] = [
  { type: "COMPANY_RESEARCH", label: "Company Research" },
  { type: "SECURITY_RESEARCH", label: "Security & Instrument Research" },
  { type: "INDUSTRY_RESEARCH", label: "Industry & Sector Analysis" },
  { type: "MACROECONOMIC_RESEARCH", label: "Macroeconomic & Monetary Policy" },
  { type: "MARKET_RESEARCH", label: "Market Microstructure & Liquidity" },
  { type: "FINANCIAL_EVENT_RESEARCH", label: "Financial Event Investigation" },
  { type: "GENERAL_FINANCIAL_RESEARCH", label: "General Quantitative Research" },
];

export function NewInvestigationDialog({ isOpen, onClose, onSubmit }: NewInvestigationDialogProps) {
  const [title, setTitle] = useState("");
  const [researchType, setResearchType] = useState<ResearchType>("COMPANY_RESEARCH");
  const [primaryEntity, setPrimaryEntity] = useState("AAPL");
  const [primaryType, setPrimaryType] = useState("COMPANY");
  const [objective, setObjective] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError("Investigation title is required.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit({
        title: title.trim(),
        research_type: researchType,
        primary_subject_entity_id: primaryEntity || undefined,
        primary_subject_type: primaryType,
        research_objective: objective.trim() || undefined,
        description: description.trim() || undefined,
      });
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to create investigation.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
      <div className="w-full max-w-xl rounded-sm border border-atlas-border-strong bg-atlas-surface-1 p-5 shadow-2xl">
        <div className="mb-4 flex items-center justify-between border-b border-atlas-border-default pb-3">
          <div>
            <h2 className="text-base font-semibold text-atlas-text-primary">New Research Investigation</h2>
            <p className="text-xs text-atlas-text-muted">
              Initialize a source-grounded, revision-tracked financial investigation.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary text-sm font-mono"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="mb-3 rounded-xs border border-atlas-negative/30 bg-atlas-negative/10 p-2 text-xs text-atlas-negative">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">
              Investigation Title <span className="text-atlas-negative">*</span>
            </label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Apple Inc. FY2024 Gross Margin & Supply Chain Sourcing"
              className="w-full"
              autoFocus
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">Research Type</label>
              <select
                value={researchType}
                onChange={(e) => setResearchType(e.target.value as ResearchType)}
                className="w-full rounded-sm border border-atlas-border-default bg-atlas-surface-0 px-2 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              >
                {RESEARCH_TYPES.map((rt) => (
                  <option key={rt.type} value={rt.type}>
                    {rt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">Primary Subject Entity</label>
              <select
                value={primaryEntity}
                onChange={(e) => {
                  setPrimaryEntity(e.target.value);
                  const matched = COMMON_ENTITIES.find((x) => x.id === e.target.value);
                  if (matched) setPrimaryType(matched.type);
                }}
                className="w-full rounded-sm border border-atlas-border-default bg-atlas-surface-0 px-2 py-1.5 text-xs text-atlas-text-primary focus:border-atlas-accent focus:outline-hidden"
              >
                {COMMON_ENTITIES.map((ent) => (
                  <option key={ent.id} value={ent.id}>
                    {ent.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">Core Objective / Thesis</label>
            <Input
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="What core financial question is being answered?"
              className="w-full"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-atlas-text-secondary">Detailed Scope (Markdown)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Scope details, target time horizon, relevant regulatory frameworks..."
              rows={3}
              className="w-full rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-2 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-accent focus:outline-hidden"
            />
          </div>

          <div className="flex items-center justify-end gap-2 border-t border-atlas-border-default pt-3">
            <Button type="button" variant="secondary" size="sm" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
              {isSubmitting ? "Creating..." : "Initialize Investigation"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
