"use client";

import React from "react";
import { ContextItem } from "@/lib/ai/context/types";

interface AiContextChipsProps {
  items: ContextItem[];
  onRemoveItem?: (targetId: string) => void;
  onToggleInspector?: () => void;
  isInspectorOpen?: boolean;
}

export function AiContextChips({
  items,
  onRemoveItem,
  onToggleInspector,
  isInspectorOpen,
}: AiContextChipsProps) {
  if (!items || items.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5 px-3 py-1.5 bg-atlas-bg-1/70 border-t border-atlas-border-subtle text-xs">
      <span className="text-[10px] uppercase font-semibold text-atlas-text-tertiary select-none mr-1">
        Context:
      </span>
      {items.map((item) => {
        const typeLabel = item.context_type
          .replace("_CONTEXT", "")
          .replace("PAGE", "Page")
          .replace("INSTRUMENT", "Entity")
          .replace("COMPANY", "Company")
          .replace("CHART", "Chart")
          .replace("PORTFOLIO", "Portfolio")
          .replace("RISK", "Risk")
          .replace("OPTIONS", "Options")
          .replace("WORKSPACE", "Workspace")
          .replace("LINKED", "Link");

        return (
          <span
            key={item.context_item_id}
            className="inline-flex items-center gap-1 rounded bg-atlas-bg-2 border border-atlas-border-subtle px-1.5 py-0.5 text-[11px] text-atlas-text-primary shadow-2xs group"
            title={`${item.context_type}: ${item.canonical_target_id} (${item.estimated_tokens} tokens)`}
          >
            <span className="font-medium text-atlas-accent">{typeLabel}:</span>
            <span className="truncate max-w-[120px]">{item.canonical_target_id}</span>
            {item.is_pinned && (
              <span className="text-amber-400 text-[10px]" title="Pinned item">
                ★
              </span>
            )}
            {onRemoveItem && (
              <button
                type="button"
                onClick={() => onRemoveItem(item.canonical_target_id)}
                className="text-atlas-text-tertiary hover:text-rose-400 cursor-pointer ml-0.5 text-[10px] leading-none"
                title="Exclude this item from prompt context"
              >
                ✕
              </button>
            )}
          </span>
        );
      })}

      {onToggleInspector && (
        <button
          type="button"
          onClick={onToggleInspector}
          className="ml-auto inline-flex items-center gap-1 text-[10px] text-atlas-accent hover:underline cursor-pointer select-none"
          title="Inspect verified context envelope"
        >
          {isInspectorOpen ? "Hide Inspector ▲" : "Context Inspector ▼"}
        </button>
      )}
    </div>
  );
}

