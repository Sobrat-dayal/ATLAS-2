"use client";

import React from "react";
import { BookOpen, Calendar, FileText, Sparkles } from "lucide-react";
import { ResearchPassageDTO } from "@/lib/ai/research/types";
import { formatPublicationDate, formatReliabilityTier } from "@/lib/ai/research/sourceFormatting";

interface AiResearchResultCardProps {
  passage: ResearchPassageDTO;
  onSelect?: (passage: ResearchPassageDTO) => void;
}

export function AiResearchResultCard({ passage, onSelect }: AiResearchResultCardProps) {
  return (
    <div
      onClick={() => onSelect?.(passage)}
      className="p-3 rounded-lg bg-atlas-surface-1 border border-atlas-border-default hover:border-atlas-accent/50 cursor-pointer transition-all space-y-2 group shadow-xs"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="h-3.5 w-3.5 text-atlas-accent" />
          <span className="font-semibold text-xs text-atlas-text-primary group-hover:text-atlas-accent transition-colors">
            {passage.title}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-atlas-surface-2 border border-atlas-border-default text-atlas-text-secondary">
            Score: {(passage.relevance_score * 100).toFixed(0)}%
          </span>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-atlas-surface-3 border border-atlas-border-default text-atlas-accent">
            Page {passage.page_number}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 text-[10px] text-atlas-text-muted">
        {passage.symbol && (
          <span className="font-mono text-atlas-text-secondary font-medium">
            {passage.symbol}
          </span>
        )}
        <span>•</span>
        <span>{passage.section_title}</span>
        <span>•</span>
        <span className="flex items-center gap-1">
          <Calendar className="h-2.5 w-2.5" />
          {formatPublicationDate(passage.publication_date)}
        </span>
      </div>

      <p className="text-[11px] leading-relaxed text-atlas-text-secondary font-mono bg-atlas-surface-2/60 p-2 rounded select-text">
        "{passage.snippet}"
      </p>
    </div>
  );
}

export function AiResearchResultList({
  passages,
  onSelectPassage,
}: {
  passages: ResearchPassageDTO[];
  onSelectPassage?: (p: ResearchPassageDTO) => void;
}) {
  if (!passages || passages.length === 0) {
    return (
      <div className="text-center py-6 text-xs text-atlas-text-muted">
        No passages found matching your search criteria.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {passages.map((p) => (
        <AiResearchResultCard key={p.chunk_id} passage={p} onSelect={onSelectPassage} />
      ))}
    </div>
  );
}
