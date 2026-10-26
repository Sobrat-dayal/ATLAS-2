"use client";

import React from "react";
import {
  EarningsCallItem,
  TranscriptStatus,
} from "@/lib/companies/earnings/types";
import {
  PhoneCall,
  Calendar,
  Clock,
  ExternalLink,
  FileText,
  Lock,
  Headphones,
  CheckCircle2,
  Tag,
  ShieldCheck,
} from "lucide-react";

interface EarningsCallsPanelProps {
  calls: EarningsCallItem[];
}

export const EarningsCallsPanel: React.FC<EarningsCallsPanelProps> = ({ calls }) => {
  const getTranscriptBadge = (status: TranscriptStatus) => {
    switch (status) {
      case TranscriptStatus.AVAILABLE:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-emerald-500 border border-emerald-500/20">
            <CheckCircle2 className="h-3 w-3" />
            Transcript Available
          </span>
        );
      case TranscriptStatus.LICENSED_ONLY:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-amber-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-amber-500 border border-amber-500/20">
            <Lock className="h-3 w-3" />
            Licensed Access Only
          </span>
        );
      case TranscriptStatus.RESTRICTED:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-amber-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-amber-500 border border-amber-500/20">
            <Lock className="h-3 w-3" />
            Restricted
          </span>
        );
      case TranscriptStatus.PENDING:
      case TranscriptStatus.PROCESSING:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-sky-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-sky-500 border border-sky-500/20">
            <Clock className="h-3 w-3" />
            Processing
          </span>
        );
      case TranscriptStatus.SCHEDULED:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-primary/10 px-1.5 py-0.5 text-[11px] font-semibold text-primary border border-primary/20">
            <Calendar className="h-3 w-3" />
            Scheduled
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-muted/30 px-1.5 py-0.5 text-[11px] font-medium text-muted-foreground border border-border/40">
            Unavailable
          </span>
        );
    }
  };

  if (!calls || calls.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center border border-border/50 rounded-lg bg-card/40">
        <PhoneCall className="h-8 w-8 text-muted-foreground/40 mb-2" />
        <p className="text-sm font-medium text-foreground">No Earnings Call Records</p>
        <p className="text-xs text-muted-foreground mt-1 max-w-sm">
          No conference call, audio webcast, or verified earnings transcript document references are available.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-foreground flex items-center gap-1.5">
            <PhoneCall className="h-4 w-4 text-primary" />
            Earnings Calls, Webcasts & Transcripts
          </h3>
          <p className="text-xs text-muted-foreground">
            Verified corporate conference call events, official investor-relations audio webcasts and licensed transcripts
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground bg-muted/20 px-2 py-1 rounded border border-border/40">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
          <span>Strict Content Rights & Licensing Enforced</span>
        </div>
      </div>

      <div className="space-y-3">
        {calls.map((call) => (
          <div
            key={call.call_id}
            className="rounded-lg border border-border/60 bg-card/50 p-4 space-y-3 hover:border-border transition-colors"
          >
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/40 pb-2.5">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-foreground">
                  {call.fiscal_period} Earnings Conference Call
                </span>
                {getTranscriptBadge(call.transcript_status)}
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {call.call_datetime || "Date TBD"}
                </span>
                {call.timezone && (
                  <span className="text-[11px] text-muted-foreground">
                    ({call.timezone})
                  </span>
                )}
              </div>
            </div>

            {/* Key topics */}
            {call.key_topics && call.key_topics.length > 0 && (
              <div className="space-y-1 text-xs">
                <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                  <Tag className="h-3 w-3" />
                  Executive Discussion Topics
                </span>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {call.key_topics.map((topic: string, idx: number) => (
                    <span
                      key={idx}
                      className="rounded bg-primary/10 px-2 py-0.5 text-xs text-primary font-medium border border-primary/20"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Links and Document Access */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-border/40 text-xs">
              <div className="flex items-center gap-3">
                {call.webcast_url && (
                  <a
                    href={call.webcast_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-primary hover:underline font-medium"
                  >
                    <Headphones className="h-3.5 w-3.5" />
                    Official Audio Webcast
                    <ExternalLink className="h-3 w-3 ml-0.5" />
                  </a>
                )}
                {call.presentation_url && (
                  <a
                    href={call.presentation_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground font-medium"
                  >
                    <FileText className="h-3.5 w-3.5" />
                    Investor Presentation
                    <ExternalLink className="h-3 w-3 ml-0.5" />
                  </a>
                )}
              </div>

              {/* Transcript Reference */}
              {call.transcript_document_id && (
                <div className="flex items-center gap-1 text-muted-foreground text-[11px] font-mono">
                  <span>Doc ID:</span>
                  <span className="text-foreground">{call.transcript_document_id}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
