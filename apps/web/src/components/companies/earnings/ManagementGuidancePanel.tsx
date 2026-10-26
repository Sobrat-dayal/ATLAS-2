"use client";

import React from "react";
import {
  ManagementGuidanceItem,
  GuidanceStatus,
} from "@/lib/companies/earnings/types";
import {
  Target,
  Calendar,
  CheckCircle2,
  XCircle,
  FileText,
  Clock,
  ShieldAlert,
} from "lucide-react";

interface ManagementGuidancePanelProps {
  guidance: ManagementGuidanceItem[];
  currency?: string;
}

export const ManagementGuidancePanel: React.FC<ManagementGuidancePanelProps> = ({
  guidance,
  currency = "USD",
}) => {
  const getStatusBadge = (status: GuidanceStatus) => {
    switch (status) {
      case GuidanceStatus.ACTIVE:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-emerald-500 border border-emerald-500/20">
            <CheckCircle2 className="h-3 w-3" />
            ACTIVE
          </span>
        );
      case GuidanceStatus.REVISED:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-sky-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-sky-500 border border-sky-500/20">
            <Clock className="h-3 w-3" />
            REVISED
          </span>
        );
      case GuidanceStatus.WITHDRAWN:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-rose-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-rose-500 border border-rose-500/20">
            <XCircle className="h-3 w-3" />
            WITHDRAWN
          </span>
        );
      case GuidanceStatus.SUPERSEDED:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-amber-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-amber-500 border border-amber-500/20">
            <Clock className="h-3 w-3" />
            SUPERSEDED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-muted/40 px-1.5 py-0.5 text-[11px] font-medium text-muted-foreground border border-border/40">
            {status}
          </span>
        );
    }
  };

  const formatGuidanceValue = (item: ManagementGuidanceItem) => {
    if (item.formatted_range && item.formatted_range !== "—") {
      return item.formatted_range;
    }
    if (item.low_value !== null && item.low_value !== undefined && item.high_value !== null && item.high_value !== undefined) {
      return `${item.low_value} – ${item.high_value} ${item.currency || currency}`;
    }
    if (item.point_value !== null && item.point_value !== undefined) {
      return `${item.point_value} ${item.currency || currency}`;
    }
    return "Qualitative Guidance";
  };

  if (!guidance || guidance.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center border border-border/50 rounded-lg bg-card/40">
        <Target className="h-8 w-8 text-muted-foreground/40 mb-2" />
        <p className="text-sm font-medium text-foreground">No Management Guidance Records</p>
        <p className="text-xs text-muted-foreground mt-1 max-w-sm">
          No active or historical forward-looking guidance releases from executive management have been registered.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-foreground flex items-center gap-1.5">
            <Target className="h-4 w-4 text-primary" />
            Corporate Management Guidance
          </h3>
          <p className="text-xs text-muted-foreground">
            Official company-issued forward projections and financial guidance ranges released in earnings releases
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground bg-muted/20 px-2 py-1 rounded border border-border/40">
          <ShieldAlert className="h-3.5 w-3.5 text-amber-500" />
          <span>Management Guidance ≠ Analyst Consensus</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {guidance.map((item) => (
          <div
            key={item.guidance_id}
            className="flex flex-col justify-between rounded-lg border border-border/60 bg-card/50 p-3.5 space-y-3 hover:border-border transition-colors"
          >
            <div className="space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-xs font-semibold text-foreground tracking-tight">
                    {item.metric.replace(/_/g, " ")}
                  </span>
                  <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground mt-0.5">
                    <Calendar className="h-3 w-3" />
                    <span>Target Period: {item.fiscal_period}</span>
                  </div>
                </div>
                {getStatusBadge(item.status)}
              </div>

              {/* Guidance Range or Point Value Display */}
              <div className="rounded border border-border/40 bg-muted/20 p-2.5">
                <span className="text-[11px] uppercase tracking-wider text-muted-foreground font-medium block">
                  Management Projection
                </span>
                <span className="text-base font-bold text-foreground font-mono mt-0.5 block">
                  {formatGuidanceValue(item)}
                </span>
                <div className="flex items-center gap-2 mt-1 text-[11px] text-muted-foreground">
                  <span>Basis: {item.accounting_basis}</span>
                  <span>•</span>
                  <span>Currency: {item.currency}</span>
                </div>
              </div>

              {/* Notes / Context */}
              {item.notes && (
                <p className="text-xs text-muted-foreground italic line-clamp-2">
                  &ldquo;{item.notes}&rdquo;
                </p>
              )}
            </div>

            {/* Footer Metadata */}
            <div className="flex items-center justify-between pt-2 border-t border-border/40 text-[11px] text-muted-foreground font-mono">
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Issued: {item.issued_at}
              </span>
              {item.source_document && (
                <span className="flex items-center gap-1 text-primary hover:underline cursor-pointer" title={item.source_document}>
                  <FileText className="h-3 w-3" />
                  Doc Ref
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
