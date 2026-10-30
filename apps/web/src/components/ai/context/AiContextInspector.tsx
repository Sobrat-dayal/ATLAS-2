"use client";

import React, { useState } from "react";
import {
  AiContextEnvelope,
  AiContextPreferences,
  ContextItem,
  ContextMode,
} from "@/lib/ai/context/types";
import { AiContextModeSelector } from "./AiContextModeSelector";
import { AiContextQualityBadge } from "./AiContextQualityBadge";

interface AiContextInspectorProps {
  envelope: AiContextEnvelope | null;
  preferences: AiContextPreferences | null;
  loading?: boolean;
  onModeChange: (mode: ContextMode) => void;
  onToggleWorkspace: () => void;
  onToggleHoldings: () => void;
  onToggleDrafts: () => void;
  onToggleProviderDisclosure: () => void;
  onPinItem?: (type: string, targetId: string) => void;
  onExcludeItem?: (targetId: string) => void;
  onIncludeItem?: (targetId: string) => void;
  onClose?: () => void;
}

export function AiContextInspector({
  envelope,
  preferences,
  loading,
  onModeChange,
  onToggleWorkspace,
  onToggleHoldings,
  onToggleDrafts,
  onToggleProviderDisclosure,
  onPinItem,
  onExcludeItem,
  onIncludeItem,
  onClose,
}: AiContextInspectorProps) {
  const [activeTab, setActiveTab] = useState<"sources" | "excluded" | "privacy">("sources");

  const mode = preferences?.context_mode || envelope?.context_mode || "FOCUSED";
  const totalTokens = envelope?.total_estimated_tokens || 0;
  const tokenBudget = envelope?.token_budget || 8000;
  const budgetPct = Math.min(100, Math.round((totalTokens / tokenBudget) * 100));

  return (
    <div className="flex flex-col border-b border-atlas-border-default bg-atlas-bg-1 p-3 text-xs shadow-md">
      {/* Top Bar: Title, Mode Selector, Close button */}
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-atlas-border-subtle">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-atlas-text-primary">Context Intelligence</span>
          {envelope && <AiContextQualityBadge status={envelope.quality_summary} />}
        </div>
        <div className="flex items-center gap-2">
          <AiContextModeSelector mode={mode} onChange={onModeChange} disabled={loading} />
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="text-atlas-text-tertiary hover:text-atlas-text-primary p-1 cursor-pointer"
              title="Close Context Inspector"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Warnings Banner if any */}
      {envelope?.warnings && envelope.warnings.length > 0 && (
        <div className="mb-2 p-2 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px]">
          {envelope.warnings.map((w, idx) => (
            <div key={idx} className="flex items-center gap-1">
              <span>⚠</span>
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}

      {/* Token Budget Gauge */}
      <div className="mb-2.5">
        <div className="flex justify-between text-[10px] text-atlas-text-secondary mb-1">
          <span>Context Window Allocation</span>
          <span>
            {totalTokens.toLocaleString()} / {tokenBudget.toLocaleString()} tokens ({budgetPct}%)
          </span>
        </div>
        <div className="h-1.5 w-full bg-atlas-bg-2 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              budgetPct > 90 ? "bg-rose-500" : budgetPct > 75 ? "bg-amber-500" : "bg-atlas-accent"
            }`}
            style={{ width: `${budgetPct}%` }}
          />
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex gap-2 border-b border-atlas-border-subtle pb-1 mb-2 text-[11px]">
        <button
          type="button"
          onClick={() => setActiveTab("sources")}
          className={`pb-1 font-medium transition-colors cursor-pointer ${
            activeTab === "sources"
              ? "text-atlas-accent border-b-2 border-atlas-accent font-semibold"
              : "text-atlas-text-secondary hover:text-atlas-text-primary"
          }`}
        >
          Included Sources ({envelope?.resolved_context_items.length || 0})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("excluded")}
          className={`pb-1 font-medium transition-colors cursor-pointer ${
            activeTab === "excluded"
              ? "text-atlas-accent border-b-2 border-atlas-accent font-semibold"
              : "text-atlas-text-secondary hover:text-atlas-text-primary"
          }`}
        >
          Excluded ({envelope?.excluded_items.length || 0})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("privacy")}
          className={`pb-1 font-medium transition-colors cursor-pointer ${
            activeTab === "privacy"
              ? "text-atlas-accent border-b-2 border-atlas-accent font-semibold"
              : "text-atlas-text-secondary hover:text-atlas-text-primary"
          }`}
        >
          Privacy & Disclosure
        </button>
      </div>

      {/* Tab 1: Included Sources */}
      {activeTab === "sources" && (
        <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
          {envelope?.resolved_context_items.length === 0 ? (
            <div className="text-center py-3 text-atlas-text-tertiary text-[11px]">
              No active context sources included (Context Mode is {mode}).
            </div>
          ) : (
            envelope?.resolved_context_items.map((item: ContextItem) => (
              <div
                key={item.context_item_id}
                className="flex flex-col p-1.5 rounded bg-atlas-bg-2 border border-atlas-border-subtle"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium text-atlas-text-primary truncate max-w-[140px]">
                      {item.canonical_target_id}
                    </span>
                    <span className="text-[10px] text-atlas-text-tertiary">
                      ({item.context_type.replace("_CONTEXT", "")})
                    </span>
                    <AiContextQualityBadge status={item.data_quality_status} />
                  </div>
                  <div className="flex items-center gap-1 text-[10px] text-atlas-text-secondary">
                    <span>{item.estimated_tokens} toks</span>
                    {onPinItem && (
                      <button
                        type="button"
                        onClick={() => onPinItem(item.context_type, item.canonical_target_id)}
                        className={`p-0.5 cursor-pointer ${
                          item.is_pinned ? "text-amber-400 font-bold" : "text-atlas-text-tertiary hover:text-amber-400"
                        }`}
                        title={item.is_pinned ? "Pinned in context" : "Pin this item in context"}
                      >
                        ★
                      </button>
                    )}
                    {onExcludeItem && (
                      <button
                        type="button"
                        onClick={() => onExcludeItem(item.canonical_target_id)}
                        className="text-atlas-text-tertiary hover:text-rose-400 cursor-pointer p-0.5"
                        title="Exclude from prompt"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </div>
                <div className="text-[11px] text-atlas-text-secondary line-clamp-2 mt-0.5">
                  {item.content_summary}
                </div>
                <div className="text-[9px] text-atlas-text-tertiary mt-1 flex justify-between">
                  <span>Ref: {item.source_reference}</span>
                  {item.as_of && <span>As of: {item.as_of}</span>}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 2: Excluded Sources */}
      {activeTab === "excluded" && (
        <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
          {envelope?.excluded_items.length === 0 ? (
            <div className="text-center py-3 text-atlas-text-tertiary text-[11px]">
              No sources were excluded.
            </div>
          ) : (
            envelope?.excluded_items.map((ex, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-1.5 rounded bg-atlas-bg-2/50 border border-atlas-border-subtle text-[11px]"
              >
                <div>
                  <span className="font-medium text-atlas-text-secondary mr-1">
                    {ex.target_id || ex.type}
                  </span>
                  <span className="text-[9px] uppercase px-1 py-0.5 rounded bg-atlas-bg-0 text-atlas-text-tertiary border border-atlas-border-subtle">
                    {ex.reason}
                  </span>
                  {ex.detail && (
                    <div className="text-[10px] text-atlas-text-tertiary mt-0.5">{ex.detail}</div>
                  )}
                </div>
                {onIncludeItem && ex.target_id && (
                  <button
                    type="button"
                    onClick={() => onIncludeItem(ex.target_id)}
                    className="text-atlas-accent hover:underline text-[10px] cursor-pointer ml-2"
                  >
                    Include
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 3: Privacy & Disclosure Toggles */}
      {activeTab === "privacy" && (
        <div className="space-y-2 py-1 text-[11px]">
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <div className="font-medium text-atlas-text-primary">Workspace Awareness</div>
              <div className="text-[10px] text-atlas-text-tertiary">
                Allow AI to inspect multi-panel workspace inventory and active channels.
              </div>
            </div>
            <input
              type="checkbox"
              checked={preferences?.allow_workspace_context ?? true}
              onChange={onToggleWorkspace}
              className="accent-atlas-accent h-4 w-4 rounded"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <div className="font-medium text-atlas-text-primary">Portfolio Holdings Sharing</div>
              <div className="text-[10px] text-atlas-text-tertiary">
                Disclose granular positions and lot weights (redacted by default for privacy).
              </div>
            </div>
            <input
              type="checkbox"
              checked={preferences?.allow_portfolio_holdings_context ?? false}
              onChange={onToggleHoldings}
              className="accent-atlas-accent h-4 w-4 rounded"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <div className="font-medium text-atlas-text-primary">Research Drafts Sharing</div>
              <div className="text-[10px] text-atlas-text-tertiary">
                Include unpublished analyst notes and draft reports in AI context.
              </div>
            </div>
            <input
              type="checkbox"
              checked={preferences?.allow_research_drafts_context ?? false}
              onChange={onToggleDrafts}
              className="accent-atlas-accent h-4 w-4 rounded"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <div className="font-medium text-atlas-text-primary">Provider Disclosure Notice</div>
              <div className="text-[10px] text-atlas-text-tertiary">
                Enforce vendor licensing restrictions for external model disclosure.
              </div>
            </div>
            <input
              type="checkbox"
              checked={preferences?.provider_disclosure_enabled ?? true}
              onChange={onToggleProviderDisclosure}
              className="accent-atlas-accent h-4 w-4 rounded"
            />
          </label>
        </div>
      )}
    </div>
  );
}

