"use client";

import React from "react";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Filter,
  Globe,
  HelpCircle,
  Info,
  Layers,
  Play,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import {
  FilterCriterion,
  NLTranslationProposal,
  SortCriterion,
  UniverseSelection,
} from "@/lib/screeners/types";

interface TranslationReviewPanelProps {
  proposal: NLTranslationProposal;
  isClarifying: boolean;
  onClarify: (ambiguityId: string, optionId: string) => void;
  onTransferToBuilder: (filters: FilterCriterion[], universe: UniverseSelection) => void;
  onApplyAndRun: (
    filters: FilterCriterion[],
    universe: UniverseSelection,
    sort: SortCriterion[]
  ) => void;
  onReset: () => void;
}

export function TranslationReviewPanel({
  proposal,
  isClarifying,
  onClarify,
  onTransferToBuilder,
  onApplyAndRun,
  onReset,
}: TranslationReviewPanelProps) {
  const isValid = proposal.status === "valid";
  const needsClarification = proposal.status === "needs_clarification";
  const isUnsupported = proposal.status === "unsupported";

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-border/80 bg-card p-5 shadow-sm text-card-foreground">
      {/* Header with Status and Requirement Coverage */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/50 pb-3.5">
        <div className="flex items-center gap-2.5">
          {isValid ? (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-500 border border-emerald-500/20">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Validated Translation
            </span>
          ) : needsClarification ? (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-2.5 py-0.5 text-xs font-semibold text-amber-500 border border-amber-500/20">
              <HelpCircle className="h-3.5 w-3.5" />
              Clarification Required
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/10 px-2.5 py-0.5 text-xs font-semibold text-rose-500 border border-rose-500/20">
              <AlertTriangle className="h-3.5 w-3.5" />
              Unsupported Elements
            </span>
          )}

          <span className="font-mono text-xs text-muted-foreground border-l border-border/60 pl-2.5">
            {proposal.coverage_count}
          </span>
        </div>

        <div className="flex items-center gap-2 text-[11px] font-mono text-muted-foreground">
          <span>Engine: {proposal.translator_version}</span>
          <span>·</span>
          <span>Revision: {proposal.registry_revision}</span>
        </div>
      </div>

      {/* Ambiguity Clarification Questions (if any) */}
      {proposal.ambiguities && proposal.ambiguities.length > 0 && (
        <div className="flex flex-col gap-3 rounded-md border border-amber-500/30 bg-amber-500/5 p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-amber-500">
            <HelpCircle className="h-4 w-4" />
            <span>Interactive Ambiguity Resolution</span>
          </div>
          <p className="text-xs text-muted-foreground">
            The screening request contains terminology with multiple valid market definitions. Select an approved interpretation to complete translation:
          </p>

          <div className="flex flex-col gap-3 pt-1">
            {proposal.ambiguities.map((amb) => (
              <div
                key={amb.ambiguity_id}
                className="flex flex-col gap-2 rounded border border-amber-500/20 bg-background/50 p-3"
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium text-xs text-foreground">
                    {amb.question}
                  </span>
                  <span className="rounded bg-amber-500/10 px-1.5 py-0.2 text-[10px] font-mono text-amber-500">
                    Source: &quot;{amb.source_phrase}&quot;
                  </span>
                </div>

                <div className="flex flex-wrap gap-2 pt-1">
                  {amb.options.map((opt) => (
                    <button
                      key={opt.id}
                      type="button"
                      disabled={isClarifying}
                      onClick={() => onClarify(amb.ambiguity_id, opt.id)}
                      className="flex items-center gap-1.5 rounded-md border border-border bg-card px-3 py-1.5 text-xs font-medium text-foreground transition-all hover:border-primary hover:bg-primary/10 hover:text-primary active:scale-[0.98] disabled:opacity-50"
                    >
                      <Sparkles className="h-3 w-3 text-primary" />
                      <span>{opt.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Unsupported Clauses Alert (if any) */}
      {proposal.unsupported && proposal.unsupported.length > 0 && (
        <div className="flex flex-col gap-2 rounded-md border border-rose-500/30 bg-rose-500/5 p-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-rose-500">
            <AlertTriangle className="h-4 w-4" />
            <span>Unsupported Screening Clauses</span>
          </div>
          <p className="text-xs text-muted-foreground">
            The following requirements cannot be executed by the deterministic Screener Engine and have not been silently replaced:
          </p>
          <ul className="list-inside list-disc flex flex-col gap-1 text-xs text-rose-400 font-mono">
            {proposal.unsupported.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Interpreted Universe Scope */}
      <div className="flex flex-wrap items-center gap-3 rounded-md border border-border/50 bg-muted/20 px-3.5 py-2.5 text-xs">
        <span className="flex items-center gap-1.5 font-medium text-muted-foreground">
          <Globe className="h-3.5 w-3.5 text-primary" />
          Universe Scope:
        </span>
        <span className="font-mono text-foreground">
          {proposal.universe.universe_id}
        </span>
        {proposal.universe.listing_country_codes && proposal.universe.listing_country_codes.length > 0 && (
          <span className="rounded bg-muted px-2 py-0.5 font-mono text-[11px] text-foreground border border-border/50">
            Countries: {proposal.universe.listing_country_codes.join(", ")}
          </span>
        )}
        {proposal.universe.exchange_mics && proposal.universe.exchange_mics.length > 0 && (
          <span className="rounded bg-muted px-2 py-0.5 font-mono text-[11px] text-foreground border border-border/50">
            Venues: {proposal.universe.exchange_mics.join(", ")}
          </span>
        )}
        {proposal.universe.sectors && proposal.universe.sectors.length > 0 && (
          <span className="rounded bg-muted px-2 py-0.5 font-mono text-[11px] text-foreground border border-border/50">
            Sectors: {proposal.universe.sectors.join(", ")}
          </span>
        )}
        {proposal.universe.industries && proposal.universe.industries.length > 0 && (
          <span className="rounded bg-muted px-2 py-0.5 font-mono text-[11px] text-foreground border border-border/50">
            Industries: {proposal.universe.industries.join(", ")}
          </span>
        )}
      </div>

      {/* Interpreted Proposed Filters List */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
            <Filter className="h-3.5 w-3.5 text-primary" />
            Interpreted Screening Conditions ({proposal.filters.length})
          </span>
        </div>

        {proposal.filters.length === 0 ? (
          <div className="rounded-md border border-border/60 bg-muted/10 p-4 text-center text-xs text-muted-foreground">
            No active quantitative filters extracted.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {proposal.filters.map((f, idx) => {
              // Find matching requirement explanation if available
              const req = proposal.requirements?.find(
                (r) => r.resolved_filter_id === f.filter_id
              );
              return (
                <div
                  key={f.condition_id || idx}
                  className="flex flex-col justify-between gap-1.5 rounded-md border border-border/60 bg-muted/20 p-3 hover:border-primary/40 transition-colors"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-semibold text-xs text-foreground">
                      {f.filter_id}
                    </span>
                    <span className="rounded bg-primary/10 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-primary uppercase">
                      {f.operator}
                    </span>
                  </div>

                  <div className="flex items-baseline gap-2 font-mono text-sm font-semibold text-foreground">
                    <span>
                      {f.operator === "between"
                        ? `${f.value} – ${f.secondary_value}`
                        : String(f.value)}
                    </span>
                    {f.currency && (
                      <span className="text-xs font-normal text-muted-foreground">
                        {f.currency}
                      </span>
                    )}
                    {f.unit && f.unit !== "monetary" && (
                      <span className="text-xs font-normal text-muted-foreground">
                        ({f.unit})
                      </span>
                    )}
                  </div>

                  {req && (
                    <div className="flex items-center gap-1 text-[11px] text-muted-foreground border-t border-border/40 pt-1.5">
                      <span className="text-primary/70">From:</span>
                      <span className="italic truncate max-w-[280px]">
                        &quot;{req.source_text}&quot;
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Assumptions & Defaults (if any) */}
      {proposal.assumptions && proposal.assumptions.length > 0 && (
        <div className="flex flex-col gap-1.5 rounded-md border border-border/40 bg-muted/10 px-3.5 py-2 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5 font-semibold text-[11px] text-foreground">
            <Info className="h-3 w-3 text-muted-foreground" />
            Inferred Conventions & Assumptions:
          </span>
          <ul className="list-inside list-disc flex flex-col gap-0.5 text-[11px]">
            {proposal.assumptions.map((assump, idx) => (
              <li key={idx}>{assump}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Primary Action Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border/50 pt-3">
        <button
          type="button"
          onClick={onReset}
          className="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted/60 hover:text-foreground transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>Clear Proposal</span>
        </button>

        <div className="flex flex-wrap items-center gap-2">
          {/* Transfer to Visual Filter Builder */}
          <button
            type="button"
            onClick={() => onTransferToBuilder(proposal.filters, proposal.universe)}
            className="flex items-center gap-1.5 rounded-md border border-border bg-background px-3.5 py-1.5 text-xs font-medium text-foreground hover:bg-muted/60 hover:border-primary/40 transition-colors"
            title="Load translated conditions into Visual Filter Builder for fine-tuning"
          >
            <Layers className="h-3.5 w-3.5 text-primary" />
            <span>Transfer to Visual Builder</span>
            <ArrowRight className="h-3 w-3 text-muted-foreground" />
          </button>

          {/* Apply & Run Screen Immediately */}
          <button
            type="button"
            disabled={!proposal.ready_for_review}
            onClick={() =>
              onApplyAndRun(
                proposal.filters,
                proposal.universe,
                proposal.sort || []
              )
            }
            className={`flex items-center gap-1.5 rounded-md px-4 py-1.5 text-xs font-semibold shadow-sm transition-all ${
              proposal.ready_for_review
                ? "bg-primary text-primary-foreground hover:bg-primary/90 active:scale-[0.98]"
                : "bg-muted text-muted-foreground cursor-not-allowed opacity-60"
            }`}
            title="Apply translated query and execute live financial screening"
          >
            <Play className="h-3.5 w-3.5 fill-current" />
            <span>Apply & Run Screen</span>
          </button>
        </div>
      </div>
    </div>
  );
}
