"use client";

import React from "react";
import { PlusCircle, RefreshCw, MinusCircle, GitCompare } from "lucide-react";
import { NLQueryModificationDiff } from "@/lib/screeners/types";

interface TranslationDiffProps {
  diff: NLQueryModificationDiff;
}

export function TranslationDiff({ diff }: TranslationDiffProps) {
  const hasAdded = diff.added_conditions && diff.added_conditions.length > 0;
  const hasUpdated = diff.updated_conditions && diff.updated_conditions.length > 0;
  const hasRemoved = diff.removed_conditions && diff.removed_conditions.length > 0;

  if (!hasAdded && !hasUpdated && !hasRemoved) {
    return null;
  }

  return (
    <div className="flex flex-col gap-2.5 rounded-md border border-border/80 bg-muted/15 p-3.5">
      <div className="flex items-center gap-2 text-xs font-semibold text-foreground">
        <GitCompare className="h-4 w-4 text-primary" />
        <span>Proposed Screen Modifications</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs">
        {/* Added Conditions */}
        {hasAdded && (
          <div className="flex flex-col gap-1.5 rounded border border-emerald-500/30 bg-emerald-500/5 p-2.5">
            <span className="flex items-center gap-1.5 font-semibold text-emerald-500 text-[11px] uppercase tracking-wider">
              <PlusCircle className="h-3 w-3" />
              Added ({diff.added_conditions.length})
            </span>
            <div className="flex flex-col gap-1 font-mono text-xs text-foreground">
              {diff.added_conditions.map((f, i) => (
                <div key={i} className="flex items-center justify-between gap-1 rounded bg-background/60 px-2 py-1">
                  <span>{f.filter_id}</span>
                  <span className="text-emerald-500 font-semibold">{f.operator} {String(f.value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Updated Conditions */}
        {hasUpdated && (
          <div className="flex flex-col gap-1.5 rounded border border-blue-500/30 bg-blue-500/5 p-2.5">
            <span className="flex items-center gap-1.5 font-semibold text-blue-500 text-[11px] uppercase tracking-wider">
              <RefreshCw className="h-3 w-3" />
              Updated ({diff.updated_conditions.length})
            </span>
            <div className="flex flex-col gap-1 font-mono text-xs text-foreground">
              {diff.updated_conditions.map((f, i) => (
                <div key={i} className="flex items-center justify-between gap-1 rounded bg-background/60 px-2 py-1">
                  <span>{f.filter_id}</span>
                  <span className="text-blue-500 font-semibold">{f.operator} {String(f.value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Removed Conditions */}
        {hasRemoved && (
          <div className="flex flex-col gap-1.5 rounded border border-rose-500/30 bg-rose-500/5 p-2.5">
            <span className="flex items-center gap-1.5 font-semibold text-rose-500 text-[11px] uppercase tracking-wider">
              <MinusCircle className="h-3 w-3" />
              Removed ({diff.removed_conditions.length})
            </span>
            <div className="flex flex-col gap-1 font-mono text-xs text-foreground">
              {diff.removed_conditions.map((fid, i) => (
                <div key={i} className="flex items-center justify-between gap-1 rounded bg-background/60 px-2 py-1 line-through text-muted-foreground">
                  <span>{fid}</span>
                  <span className="text-rose-500 font-semibold">Excluded</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
