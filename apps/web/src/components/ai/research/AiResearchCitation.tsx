"use client";

import React from "react";
import { BookOpen, AlertCircle } from "lucide-react";
import { ResearchCitationDTO } from "@/lib/ai/research/types";

interface AiResearchCitationProps {
  citation: ResearchCitationDTO;
  onClick?: (citation: ResearchCitationDTO) => void;
}

export function AiResearchCitation({ citation, onClick }: AiResearchCitationProps) {
  const isVerified = citation.status === "VERIFIED";

  return (
    <button
      type="button"
      onClick={() => onClick?.(citation)}
      className={`inline-flex items-center gap-1 mx-1 px-1.5 py-0.5 rounded text-[10px] font-mono transition-colors border ${
        isVerified
          ? "bg-atlas-surface-2 hover:bg-atlas-surface-3 text-atlas-accent border-atlas-accent/30 shadow-xs"
          : "bg-red-950/40 hover:bg-red-950/60 text-red-300 border-red-500/40"
      }`}
      title={
        isVerified
          ? `${citation.title} (Page ${citation.page_number})`
          : `Citation rejected: ${citation.validation_reason || "Unsupported"}`
      }
    >
      {isVerified ? (
        <BookOpen className="h-2.5 w-2.5 shrink-0 opacity-70" />
      ) : (
        <AlertCircle className="h-2.5 w-2.5 shrink-0 text-red-400" />
      )}
      <span>
        [{citation.symbol || "Source"} p.{citation.page_number}]
      </span>
    </button>
  );
}
