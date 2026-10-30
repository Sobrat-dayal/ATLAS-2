"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp, Layers, BookOpen, Calendar, FileText } from "lucide-react";
import { ResearchCitationDTO } from "@/lib/ai/research/types";
import { formatPublicationDate } from "@/lib/ai/research/sourceFormatting";

interface AiResearchEvidenceInspectorProps {
  citations: ResearchCitationDTO[];
  onSelectCitation?: (citation: ResearchCitationDTO) => void;
}

export function AiResearchEvidenceInspector({
  citations,
  onSelectCitation,
}: AiResearchEvidenceInspectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="border border-atlas-border-default rounded-lg bg-atlas-surface-1 overflow-hidden">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3 py-2 text-xs text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-2 transition-colors font-medium"
      >
        <span className="flex items-center gap-2">
          <Layers className="h-3.5 w-3.5 text-atlas-accent" />
          <span>Evidence Sources & Grounded Citations ({citations.length})</span>
        </span>
        {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {isOpen && (
        <div className="p-3 border-t border-atlas-border-default space-y-2.5 max-h-72 overflow-y-auto">
          {citations.map((cite) => (
            <div
              key={cite.citation_id}
              onClick={() => onSelectCitation?.(cite)}
              className="p-2.5 rounded border border-atlas-border-default bg-atlas-surface-2 hover:border-atlas-accent/40 cursor-pointer transition-all space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-xs text-atlas-text-primary truncate max-w-[280px]">
                  {cite.title}
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-atlas-surface-3 border border-atlas-border-default text-atlas-accent">
                  Page {cite.page_number}
                </span>
              </div>

              <div className="flex items-center gap-2 text-[10px] text-atlas-text-muted">
                {cite.symbol && (
                  <span className="font-mono text-atlas-text-secondary">{cite.symbol}</span>
                )}
                <span>•</span>
                <span>{cite.section_title}</span>
                <span>•</span>
                <span className="flex items-center gap-0.5">
                  <Calendar className="h-2.5 w-2.5" />
                  {formatPublicationDate(cite.publication_date)}
                </span>
              </div>

              <div className="text-[11px] text-atlas-text-secondary line-clamp-2 font-mono bg-atlas-surface-1/60 p-1.5 rounded">
                "{cite.quote_span}"
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
