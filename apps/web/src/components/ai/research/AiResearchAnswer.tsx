"use client";

import React, { useState } from "react";
import { CheckCircle2, AlertTriangle, Clock, ShieldCheck, Sparkles } from "lucide-react";
import { ResearchAnswerResponse, ResearchCitationDTO } from "@/lib/ai/research/types";
import { parseAnswerCitations } from "@/lib/ai/research/citationValidation";
import { AiResearchCitation } from "./AiResearchCitation";
import { AiResearchCitationViewer } from "./AiResearchCitationViewer";
import { AiResearchEvidenceInspector } from "./AiResearchEvidenceInspector";

interface AiResearchAnswerProps {
  response: ResearchAnswerResponse;
}

export function AiResearchAnswer({ response }: AiResearchAnswerProps) {
  const [selectedCitation, setSelectedCitation] = useState<Record<string, any> | null>(null);

  const segments = parseAnswerCitations(response.answer_text, response.citations);
  const isInsufficient = response.status === "INSUFFICIENT_EVIDENCE";

  return (
    <div className="space-y-3.5">
      {/* Header Banner */}
      <div className="flex items-center justify-between text-xs pb-2 border-b border-atlas-border-default/60">
        <div className="flex items-center gap-2">
          {isInsufficient ? (
            <span className="flex items-center gap-1.5 text-amber-400 font-medium">
              <AlertTriangle className="h-3.5 w-3.5" />
              Insufficient Evidence
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
              <CheckCircle2 className="h-3.5 w-3.5" />
              Grounded Institutional Research
            </span>
          )}
          <span className="text-atlas-text-muted text-[11px] font-mono">
            ({response.strategy})
          </span>
        </div>

        <div className="flex items-center gap-3 text-[11px] text-atlas-text-muted">
          <span className="flex items-center gap-1">
            <ShieldCheck className="h-3 w-3 text-atlas-accent" />
            {response.source_count} source(s)
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {response.execution_time_ms.toFixed(1)}ms
          </span>
        </div>
      </div>

      {/* Answer Text with Inline Citations */}
      <div className="text-xs leading-relaxed text-atlas-text-primary select-text space-y-2">
        <p>
          {segments.map((seg, idx) => {
            if (seg.type === "citation" && seg.citation) {
              return (
                <AiResearchCitation
                  key={`cite_${idx}`}
                  citation={seg.citation}
                  onClick={(c) => setSelectedCitation(c)}
                />
              );
            }
            return <span key={`txt_${idx}`}>{seg.text}</span>;
          })}
        </p>
      </div>

      {/* Conflicting Sources Notice */}
      {response.evidence_manifest?.has_conflicting_sources && (
        <div className="p-2.5 rounded bg-amber-950/30 border border-amber-500/30 text-amber-200 text-[11px] flex items-start gap-2">
          <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5 text-amber-400" />
          <div className="space-y-0.5">
            <span className="font-semibold block">Conflicting Reporting Definitions Identified</span>
            <span>{response.evidence_manifest.conflict_notes}</span>
          </div>
        </div>
      )}

      {/* Evidence Inspector */}
      {response.citations && response.citations.length > 0 && (
        <AiResearchEvidenceInspector
          citations={response.citations}
          onSelectCitation={(c) => setSelectedCitation(c)}
        />
      )}

      {/* Limitations */}
      {response.limitations && response.limitations.length > 0 && (
        <div className="text-[10px] text-atlas-text-muted space-y-0.5 pt-1 border-t border-atlas-border-default/40">
          <span className="font-semibold uppercase tracking-wider block">Methodological Limitations:</span>
          <ul className="list-disc list-inside space-y-0.5 pl-1">
            {response.limitations.map((lim, i) => (
              <li key={i}>{lim}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Citation Modal */}
      <AiResearchCitationViewer
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
}
