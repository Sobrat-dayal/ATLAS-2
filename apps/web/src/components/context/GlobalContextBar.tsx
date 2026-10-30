"use client";

import React, { useState } from "react";
import { ChevronDown, Globe, Layers, Link2, Settings, ShieldCheck, Sparkles } from "lucide-react";
import { useGlobalContext } from "./GlobalContextProvider";
import { LinkChannelManagerModal } from "./LinkChannelManagerModal";

export function GlobalContextBar() {
  const { channels, activeChannelId, activeChannel, setActiveChannelId } = useGlobalContext();
  const [isManagerOpen, setIsManagerOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const context = activeChannel?.context_snapshot || {};
  const activeInstrument = (context.INSTRUMENT as string) || (context.SYMBOL as string) || "—";
  const activeCurrency = (context.REPORTING_CURRENCY as string) || "USD";
  const activeTimeframe = (context.TIMEFRAME as string) || "1D";

  return (
    <>
      <div className="flex items-center gap-2 px-2.5 py-1 bg-atlas-surface-2 border border-atlas-border-default rounded-sm font-mono text-[11px] text-atlas-text-primary shrink-0 select-none">
        {/* Channel Switcher */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center gap-1.5 px-2 py-0.5 rounded-xs hover:bg-atlas-surface-3 transition-colors text-atlas-text-primary font-bold"
            title="Switch Global Link Channel"
          >
            <span
              className="w-2.5 h-2.5 rounded-full shrink-0 shadow-xs"
              style={{ backgroundColor: activeChannel?.display_color_token || "#3B82F6" }}
            />
            <span>{activeChannel?.name || "Global Link"}</span>
            <ChevronDown className="w-3 h-3 text-atlas-text-muted" />
          </button>

          {isDropdownOpen && (
            <div className="absolute left-0 top-full mt-1 w-52 bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-xl z-50 p-1 space-y-0.5">
              <div className="px-2 py-1 text-[10px] uppercase font-bold text-atlas-text-muted border-b border-atlas-border-subtle">
                Active Link Channels
              </div>
              {channels.map((c) => (
                <button
                  key={c.channel_id}
                  type="button"
                  onClick={() => {
                    setActiveChannelId(c.channel_id);
                    setIsDropdownOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-2 py-1.5 rounded-xs text-left transition-colors text-xs ${
                    c.channel_id === activeChannelId
                      ? "bg-atlas-surface-selected text-atlas-text-primary font-bold"
                      : "hover:bg-atlas-surface-hover text-atlas-text-secondary"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span
                      className="w-2 h-2 rounded-full shrink-0"
                      style={{ backgroundColor: c.display_color_token }}
                    />
                    <span className="truncate">{c.name}</span>
                  </div>
                  <span className="text-[9px] uppercase font-mono text-atlas-text-muted">
                    {c.scope === "USER_APPLICATION" ? "APP" : "WS"}
                  </span>
                </button>
              ))}
              <div className="pt-1 border-t border-atlas-border-subtle">
                <button
                  type="button"
                  onClick={() => {
                    setIsDropdownOpen(false);
                    setIsManagerOpen(true);
                  }}
                  className="w-full flex items-center gap-1.5 px-2 py-1 rounded-xs text-[10px] text-blue-400 hover:bg-atlas-surface-hover text-left"
                >
                  <Settings className="w-3 h-3" />
                  <span>Configure Link Channels...</span>
                </button>
              </div>
            </div>
          )}
        </div>

        <span className="text-atlas-border-default">|</span>

        {/* Selected Context Snapshot Pills */}
        <div className="flex items-center gap-1.5">
          <span className="text-atlas-text-muted text-[10px]">SYM:</span>
          <span className="px-1.5 py-0.2 bg-atlas-surface-3 rounded-xs font-bold text-blue-400">
            {activeInstrument}
          </span>

          <span className="text-atlas-text-muted text-[10px] ml-1">CCY:</span>
          <span className="px-1.5 py-0.2 bg-atlas-surface-3 rounded-xs text-emerald-400">
            {activeCurrency}
          </span>

          <span className="text-atlas-text-muted text-[10px] ml-1">TF:</span>
          <span className="px-1.5 py-0.2 bg-atlas-surface-3 rounded-xs text-purple-400">
            {activeTimeframe}
          </span>
        </div>

        <span className="text-atlas-border-default">|</span>

        {/* Manage Links trigger */}
        <button
          type="button"
          onClick={() => setIsManagerOpen(true)}
          className="flex items-center gap-1 text-[10px] text-atlas-text-muted hover:text-atlas-text-primary px-1.5 py-0.5 rounded-xs hover:bg-atlas-surface-3 transition-colors"
          title="Open Global Link Channel Manager"
        >
          <Layers className="w-3 h-3 text-atlas-accent" />
          <span className="hidden sm:inline">Manage Links</span>
        </button>
      </div>

      {/* Modal Dialog */}
      <LinkChannelManagerModal
        isOpen={isManagerOpen}
        onClose={() => setIsManagerOpen(false)}
      />
    </>
  );
}

