"use client";

import React, { useState } from "react";
import { Badge, Button, Input } from "@/design-system";
import {
  ResearchInvestmentThesis,
  ResearchThesisArgument,
  ThesisArgumentType,
  CreateThesisArgumentDTO,
} from "@/lib/research/types";
import {
  formatResearchDate,
  getThesisStatusDisplay,
  getThesisArgumentTypeDisplay,
} from "@/lib/research/formatting";

interface ResearchThesisWorkspaceProps {
  theses: ResearchInvestmentThesis[];
  selectedThesisId: string | null;
  currentThesis: ResearchInvestmentThesis | null;
  argumentsList: ResearchThesisArgument[];
  isLoading: boolean;
  onSelectThesis: (id: string) => void;
  onNewThesis: () => void;
  onDeleteThesis: (id: string) => void;
  onCreateArgument: (thesisId: string, data: CreateThesisArgumentDTO) => Promise<any>;
  onDeleteArgument: (argumentId: string) => Promise<any>;
  onOpenSource?: (sourceId: string) => void;
}

export function ResearchThesisWorkspace({
  theses,
  selectedThesisId,
  currentThesis,
  argumentsList,
  isLoading,
  onSelectThesis,
  onNewThesis,
  onDeleteThesis,
  onCreateArgument,
  onDeleteArgument,
  onOpenSource,
}: ResearchThesisWorkspaceProps) {
  const [isAddingArg, setIsAddingArg] = useState(false);
  const [argType, setArgType] = useState<ThesisArgumentType>("BULL_CASE");
  const [argStatement, setArgStatement] = useState("");
  const [argStrength, setArgStrength] = useState<number>(80);
  const [argCitations, setArgCitations] = useState("");
  const [isSubmittingArg, setIsSubmittingArg] = useState(false);

  const handleAddArgSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentThesis || !argStatement.trim()) return;
    setIsSubmittingArg(true);
    try {
      const citations = argCitations
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      await onCreateArgument(currentThesis.thesis_id, {
        argument_type: argType,
        statement: argStatement.trim(),
        evidence_citations: citations,
        strength_score: Number(argStrength) / 100,
      });
      setArgStatement("");
      setArgCitations("");
      setIsAddingArg(false);
    } finally {
      setIsSubmittingArg(false);
    }
  };

  const statusMeta = currentThesis ? getThesisStatusDisplay(currentThesis.status) : null;

  // Group arguments
  const bullArgs = argumentsList.filter((a) => a.argument_type === "BULL_CASE");
  const bearArgs = argumentsList.filter((a) => a.argument_type === "BEAR_CASE");
  const catalysts = argumentsList.filter((a) => a.argument_type === "CATALYST");
  const risks = argumentsList.filter((a) => a.argument_type === "KEY_RISK");
  const assumptions = argumentsList.filter(
    (a) => a.argument_type === "CORE_ASSUMPTION" || a.argument_type === "BASE_CASE"
  );

  return (
    <div className="flex h-full overflow-hidden bg-atlas-surface-0">
      {/* Left List of Theses */}
      <div className="w-72 shrink-0 border-r border-atlas-border-default bg-atlas-surface-1/40 flex flex-col">
        <div className="flex items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-3 py-2.5">
          <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
            Investment Theses
          </span>
          <Button variant="primary" size="xs" onClick={onNewThesis}>
            + New Thesis
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-atlas-border-default/40">
          {theses.length === 0 ? (
            <div className="p-4 text-center text-xs text-atlas-text-muted">
              No investment theses defined.
            </div>
          ) : (
            theses.map((th) => {
              const isSelected = th.thesis_id === selectedThesisId;
              const sMeta = getThesisStatusDisplay(th.status);
              return (
                <div
                  key={th.thesis_id}
                  onClick={() => onSelectThesis(th.thesis_id)}
                  className={`p-3 cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-atlas-accent/10 border-l-2 border-atlas-accent"
                      : "hover:bg-atlas-surface-1"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-atlas-text-primary truncate">
                      {th.title}
                    </span>
                    <Badge variant={sMeta.variant} className="text-[9px]">
                      {sMeta.label}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-atlas-text-muted mt-1 font-mono">
                    <span>{th.target_entity_id || "General"}</span>
                    <span>{Math.round((th.conviction_score || 0) * 100)}% Conviction</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Center Thesis Detail */}
      <div className="flex-1 flex flex-col overflow-hidden bg-atlas-surface-0">
        {currentThesis ? (
          <>
            {/* Header Details */}
            <div className="border-b border-atlas-border-default bg-atlas-surface-1 px-4 py-3 shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-sm font-bold text-atlas-text-primary">
                      {currentThesis.title}
                    </h2>
                    {statusMeta && (
                      <Badge variant={statusMeta.variant} className="text-[10px]">
                        {statusMeta.label}
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-atlas-text-muted mt-1 font-mono">
                    <span>Target: {currentThesis.target_entity_name || currentThesis.target_entity_id || "Market"}</span>
                    <span>•</span>
                    <span>Horizon: {currentThesis.horizon_months || 12} Months</span>
                    <span>•</span>
                    <span>Conviction: {Math.round((currentThesis.conviction_score || 0) * 100)}%</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button variant="secondary" size="xs" onClick={() => setIsAddingArg(true)}>
                    + Add Argument
                  </Button>
                  <Button
                    variant="ghost"
                    size="xs"
                    className="text-atlas-negative"
                    onClick={() => {
                      if (window.confirm(`Delete thesis "${currentThesis.title}"?`)) {
                        onDeleteThesis(currentThesis.thesis_id);
                      }
                    }}
                  >
                    Delete Thesis
                  </Button>
                </div>
              </div>

              {currentThesis.summary && (
                <p className="text-xs text-atlas-text-secondary mt-2 leading-relaxed bg-atlas-surface-0 p-2.5 rounded-xs border border-atlas-border-default">
                  {currentThesis.summary}
                </p>
              )}
            </div>

            {/* Add Argument Modal Form */}
            {isAddingArg && (
              <form onSubmit={handleAddArgSubmit} className="border-b border-atlas-border-default bg-atlas-surface-1 p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
                    Add Structured Thesis Argument
                  </span>
                  <button
                    type="button"
                    onClick={() => setIsAddingArg(false)}
                    className="text-atlas-text-muted hover:text-atlas-text-primary text-xs font-mono"
                  >
                    ✕
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <select
                    value={argType}
                    onChange={(e) => setArgType(e.target.value as ThesisArgumentType)}
                    className="rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-secondary"
                  >
                    <option value="BULL_CASE">Bull Case Pillar</option>
                    <option value="BEAR_CASE">Bear Case / Counterthesis</option>
                    <option value="CATALYST">Key Catalyst</option>
                    <option value="KEY_RISK">Core Risk Factor</option>
                    <option value="CORE_ASSUMPTION">Core Valuation Assumption</option>
                    <option value="BASE_CASE">Base Case Factor</option>
                  </select>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] text-atlas-text-muted">Strength: {argStrength}%</span>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={argStrength}
                      onChange={(e) => setArgStrength(Number(e.target.value))}
                      className="flex-1 h-1.5 bg-atlas-surface-2"
                    />
                  </div>
                </div>
                <textarea
                  value={argStatement}
                  onChange={(e) => setArgStatement(e.target.value)}
                  rows={2}
                  placeholder="State the core argument, empirical driver, or mechanism..."
                  className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-2 text-xs text-atlas-text-primary focus:outline-hidden"
                  required
                />
                <Input
                  value={argCitations}
                  onChange={(e) => setArgCitations(e.target.value)}
                  placeholder="Evidence Citations (comma-separated IDs, e.g. cit-10k-q4)"
                />
                <div className="flex items-center justify-end gap-2 pt-1">
                  <Button variant="ghost" size="xs" type="button" onClick={() => setIsAddingArg(false)}>
                    Cancel
                  </Button>
                  <Button variant="primary" size="xs" type="submit" disabled={isSubmittingArg}>
                    {isSubmittingArg ? "Adding..." : "Add to Thesis"}
                  </Button>
                </div>
              </form>
            )}

            {/* Arguments Sections Grid */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {/* Bull Case Column */}
                <div className="rounded-xs border border-atlas-positive/30 bg-atlas-surface-1/40 p-3 space-y-2">
                  <div className="flex items-center justify-between border-b border-atlas-positive/20 pb-1.5">
                    <span className="text-xs font-bold text-atlas-positive uppercase tracking-wider">
                      Bull Case Arguments ({bullArgs.length})
                    </span>
                  </div>
                  {bullArgs.length === 0 ? (
                    <p className="text-xs text-atlas-text-muted italic py-2">
                      No bull case pillars added.
                    </p>
                  ) : (
                    bullArgs.map((arg) => (
                      <div
                        key={arg.argument_id}
                        className="rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-2 text-xs space-y-1 relative group"
                      >
                        <p className="text-atlas-text-primary text-[11px] leading-relaxed">
                          {arg.statement}
                        </p>
                        <div className="flex items-center justify-between text-[10px] text-atlas-text-muted font-mono">
                          <span>Strength: {Math.round((arg.strength_score || 0) * 100)}%</span>
                          <button
                            onClick={() => onDeleteArgument(arg.argument_id)}
                            className="text-atlas-negative hover:underline opacity-0 group-hover:opacity-100"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Bear Case Column */}
                <div className="rounded-xs border border-atlas-negative/30 bg-atlas-surface-1/40 p-3 space-y-2">
                  <div className="flex items-center justify-between border-b border-atlas-negative/20 pb-1.5">
                    <span className="text-xs font-bold text-atlas-negative uppercase tracking-wider">
                      Bear Case & Counterthesis ({bearArgs.length})
                    </span>
                  </div>
                  {bearArgs.length === 0 ? (
                    <p className="text-xs text-atlas-text-muted italic py-2">
                      No bear case counter-arguments added.
                    </p>
                  ) : (
                    bearArgs.map((arg) => (
                      <div
                        key={arg.argument_id}
                        className="rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-2 text-xs space-y-1 relative group"
                      >
                        <p className="text-atlas-text-primary text-[11px] leading-relaxed">
                          {arg.statement}
                        </p>
                        <div className="flex items-center justify-between text-[10px] text-atlas-text-muted font-mono">
                          <span>Strength: {Math.round((arg.strength_score || 0) * 100)}%</span>
                          <button
                            onClick={() => onDeleteArgument(arg.argument_id)}
                            className="text-atlas-negative hover:underline opacity-0 group-hover:opacity-100"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Catalysts & Risks Row */}
              <div className="grid grid-cols-2 gap-4">
                {/* Key Catalysts */}
                <div className="rounded-xs border border-atlas-border-default bg-atlas-surface-1/40 p-3 space-y-2">
                  <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider block border-b border-atlas-border-default pb-1.5">
                    Identified Catalysts ({catalysts.length})
                  </span>
                  {catalysts.length === 0 ? (
                    <p className="text-xs text-atlas-text-muted italic py-2">
                      No catalysts defined.
                    </p>
                  ) : (
                    catalysts.map((arg) => (
                      <div
                        key={arg.argument_id}
                        className="rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-2 text-xs space-y-1 relative group"
                      >
                        <p className="text-atlas-text-primary text-[11px]">{arg.statement}</p>
                        <div className="flex items-center justify-between text-[10px] text-atlas-text-muted font-mono">
                          <span>Strength: {Math.round((arg.strength_score || 0) * 100)}%</span>
                          <button
                            onClick={() => onDeleteArgument(arg.argument_id)}
                            className="text-atlas-negative hover:underline opacity-0 group-hover:opacity-100"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Key Risks */}
                <div className="rounded-xs border border-atlas-border-default bg-atlas-surface-1/40 p-3 space-y-2">
                  <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider block border-b border-atlas-border-default pb-1.5">
                    Core Risk Factors & Assumptions ({risks.length + assumptions.length})
                  </span>
                  {[...risks, ...assumptions].length === 0 ? (
                    <p className="text-xs text-atlas-text-muted italic py-2">
                      No risks or assumptions defined.
                    </p>
                  ) : (
                    [...risks, ...assumptions].map((arg) => (
                      <div
                        key={arg.argument_id}
                        className="rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-2 text-xs space-y-1 relative group"
                      >
                        <p className="text-atlas-text-primary text-[11px]">{arg.statement}</p>
                        <div className="flex items-center justify-between text-[10px] text-atlas-text-muted font-mono">
                          <span>{arg.argument_type}</span>
                          <button
                            onClick={() => onDeleteArgument(arg.argument_id)}
                            className="text-atlas-negative hover:underline opacity-0 group-hover:opacity-100"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex h-full items-center justify-center text-xs text-atlas-text-muted">
            Select or create an investment thesis from the sidebar.
          </div>
        )}
      </div>
    </div>
  );
}
