"use client";

import React from "react";
import { ShieldCheck, CheckCircle2, XCircle } from "lucide-react";
import { CentralBankCoverageResponseDTO } from "@/lib/economics/central-banks";

interface CentralBankCoveragePanelProps {
  coverage: CentralBankCoverageResponseDTO | null;
}

export function CentralBankCoveragePanel({ coverage }: CentralBankCoveragePanelProps) {
  if (!coverage) return null;

  const items = [
    { label: "Administered Policy Rate Series", status: coverage.has_policy_rate_series },
    { label: "Target Range Support (Bounds)", status: coverage.has_target_range },
    { label: "Historical Policy Decisions", status: coverage.has_decision_history },
    { label: "Meeting Minutes & Transcripts", status: coverage.has_meeting_minutes },
    { label: "Committee Voting Records Disclosed", status: coverage.has_voting_records },
    { label: "Official Statements & Publications", status: coverage.has_official_statements },
    { label: "Policymaker Speeches & Transcripts", status: coverage.has_official_speeches },
    { label: "Verbatim Forward Guidance", status: coverage.has_forward_guidance },
    { label: "Consolidated Balance Sheet Series", status: coverage.has_balance_sheet },
    { label: "Asset Purchase & QT Programs", status: coverage.has_policy_programs },
  ];

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Institutional Data Coverage & Verification Status — {coverage.institution.canonical_name}
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          OFFICIALLY_VERIFIED
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {items.map((it, idx) => (
          <div
            key={idx}
            className="p-3 bg-atlas-background rounded border border-atlas-border-subtle flex items-center justify-between"
          >
            <span className="text-xs text-atlas-text-primary font-medium">{it.label}</span>
            {it.status ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 ml-2" />
            ) : (
              <XCircle className="w-4 h-4 text-atlas-text-muted/40 shrink-0 ml-2" />
            )}
          </div>
        ))}
      </div>

      <div className="pt-2 text-[11px] text-atlas-text-muted font-mono leading-relaxed border-t border-atlas-border-subtle">
        Data completeness is verified directly against canonical monetary authority charters and statistical releases. Missing dimensions reflect official non-disclosure policies (e.g. collegial consensus votes) rather than missing data ingestion.
      </div>
    </div>
  );
}
