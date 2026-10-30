"use client";

import React from "react";
import { X, BookOpen, Calendar, ShieldCheck, FileText } from "lucide-react";
import { formatPublicationDate } from "@/lib/ai/research/sourceFormatting";

interface AiResearchCitationViewerProps {
  citation: Record<string, any> | null;
  onClose: () => void;
}

export function AiResearchCitationViewer({ citation, onClose }: AiResearchCitationViewerProps) {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="w-full max-w-lg rounded-lg bg-atlas-surface-1 border border-atlas-border-default shadow-xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-atlas-accent" />
            <span className="text-xs font-semibold text-atlas-text-primary">
              Verified Source Excerpt
            </span>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950/60 border border-emerald-500/40 text-emerald-300 font-mono">
              VERIFIED
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-atlas-text-secondary hover:text-atlas-text-primary rounded hover:bg-atlas-surface-3 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4 text-xs overflow-y-auto max-h-[70vh]">
          {/* Document metadata */}
          <div className="space-y-1">
            <h4 className="font-medium text-atlas-text-primary text-sm">
              {citation.title || "Document Title"}
            </h4>
            <div className="flex flex-wrap items-center gap-3 text-atlas-text-secondary text-[11px]">
              {citation.symbol && (
                <span className="font-mono text-atlas-accent font-semibold">
                  {citation.symbol}
                </span>
              )}
              {citation.document_type && (
                <span className="px-1.5 py-0.2 rounded bg-atlas-surface-2 border border-atlas-border-default">
                  {citation.document_type}
                </span>
              )}
              {citation.publication_date && (
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3 opacity-70" />
                  {formatPublicationDate(citation.publication_date)}
                </span>
              )}
              {citation.page_number && (
                <span className="flex items-center gap-1 font-mono">
                  <FileText className="h-3 w-3 opacity-70" />
                  Page {citation.page_number}
                </span>
              )}
            </div>
          </div>

          {/* Section title */}
          {citation.section_title && (
            <div className="p-2 rounded bg-atlas-surface-2 border border-atlas-border-default/60">
              <span className="text-[10px] uppercase font-semibold text-atlas-text-muted tracking-wider block mb-0.5">
                Section
              </span>
              <span className="text-atlas-text-primary font-medium">
                {citation.section_title}
              </span>
            </div>
          )}

          {/* Exact quote span */}
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-semibold text-atlas-text-muted tracking-wider block">
              Grounded Evidence Span
            </span>
            <div className="p-3 rounded bg-atlas-surface-2/80 border border-atlas-border-default text-atlas-text-primary font-mono text-[11px] leading-relaxed whitespace-pre-wrap select-text">
              {citation.quote_span || citation.claim_text || "No quote text available."}
            </div>
          </div>

          {/* Governance Footer */}
          <div className="flex items-center justify-between pt-2 border-t border-atlas-border-default text-[10px] text-atlas-text-muted">
            <span className="flex items-center gap-1">
              <ShieldCheck className="h-3 w-3 text-emerald-400" />
              Source: {citation.publisher || "Regulatory Registry"}
            </span>
            <span className="font-mono">
              Citation: {citation.citation_id || "cite_verified"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
