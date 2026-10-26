"use client";

import React from "react";
import { HelpCircle, Sparkles } from "lucide-react";
import { NLAmbiguityQuestion } from "@/lib/screeners/types";

interface TranslationAmbiguityPanelProps {
  ambiguities: NLAmbiguityQuestion[];
  isClarifying: boolean;
  onClarify: (ambiguityId: string, optionId: string) => void;
}

export function TranslationAmbiguityPanel({
  ambiguities,
  isClarifying,
  onClarify,
}: TranslationAmbiguityPanelProps) {
  if (!ambiguities || ambiguities.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-3 rounded-md border border-amber-500/30 bg-amber-500/5 p-4">
      <div className="flex items-center gap-2 text-xs font-semibold text-amber-500">
        <HelpCircle className="h-4 w-4" />
        <span>Interactive Ambiguity Resolution</span>
      </div>
      <p className="text-xs text-muted-foreground">
        The screening request contains terminology with multiple valid market definitions. Select an approved interpretation to complete translation:
      </p>

      <div className="flex flex-col gap-3 pt-1">
        {ambiguities.map((amb) => (
          <div
            key={amb.ambiguity_id}
            className="flex flex-col gap-2 rounded border border-amber-500/20 bg-background/50 p-3"
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-medium text-xs text-foreground">
                {amb.question}
              </span>
              <span className="rounded bg-amber-500/10 px-1.5 py-0.5 text-[10px] font-mono text-amber-500">
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
  );
}
