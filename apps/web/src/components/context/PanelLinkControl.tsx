"use client";

import React, { useRef, useState } from "react";
import { Check, ChevronDown, Layers, Link2, Sliders, Unlink } from "lucide-react";
import { useGlobalContext } from "./GlobalContextProvider";
import { ContextDimension } from "@/lib/context/types";
import { getPanelCapability } from "@/lib/context/capabilityRegistry";

interface PanelLinkControlProps {
  panelInstanceId: string;
  panelTypeId: string;
  currentChannelId?: string | null;
  isIndependent?: boolean;
  dimensionOverrides?: Partial<Record<ContextDimension, "FOLLOW" | "INDEPENDENT">>;
  onSelectChannel: (channelId: string | null) => void;
  onToggleDimensionOverride?: (dimension: ContextDimension, mode: "FOLLOW" | "INDEPENDENT") => void;
  onOpenManager?: () => void;
}

export function PanelLinkControl({
  panelInstanceId,
  panelTypeId,
  currentChannelId,
  isIndependent = false,
  dimensionOverrides = {},
  onSelectChannel,
  onToggleDimensionOverride,
  onOpenManager,
}: PanelLinkControlProps) {
  const { channels } = useGlobalContext();
  const [isOpen, setIsOpen] = useState(false);

  const activeChannel = !isIndependent
    ? channels.find((c) => c.channel_id === currentChannelId)
    : undefined;

  const cap = getPanelCapability(panelTypeId);
  const subscribableDims = cap?.subscribable_dimensions || [];

  return (
    <div className="relative font-mono text-xs">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1 px-1.5 py-0.5 rounded-xs hover:bg-atlas-surface-3 transition-colors text-atlas-text-secondary hover:text-atlas-text-primary border border-transparent hover:border-atlas-border-subtle"
        title={
          isIndependent
            ? "Panel is Independent (Unlinked)"
            : `Linked to ${activeChannel?.name || "Channel"}`
        }
      >
        <span
          className="w-2.5 h-2.5 rounded-full shrink-0 shadow-xs"
          style={{
            backgroundColor: isIndependent ? "#64748B" : activeChannel?.display_color_token || "#3B82F6",
          }}
        />
        <span className="text-[10px] uppercase font-bold hidden sm:inline">
          {isIndependent ? "IND" : activeChannel ? activeChannel.name.split(" ")[0] : "LINK"}
        </span>
        <ChevronDown className="w-2.5 h-2.5 opacity-60" />
      </button>

      {isOpen && (
        <div
          className="absolute right-0 top-full mt-1 w-56 bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-2xl z-50 p-1.5 space-y-1"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="px-1.5 py-0.5 text-[9px] uppercase font-bold text-atlas-text-muted border-b border-atlas-border-subtle">
            Select Link Channel
          </div>

          {/* Independent Option */}
          <button
            type="button"
            onClick={() => {
              onSelectChannel(null);
              setIsOpen(false);
            }}
            className={`w-full flex items-center justify-between px-2 py-1 rounded-xs text-left text-xs transition-colors ${
              isIndependent
                ? "bg-atlas-surface-selected text-atlas-text-primary font-bold"
                : "hover:bg-atlas-surface-hover text-atlas-text-secondary"
            }`}
          >
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-slate-500 shrink-0" />
              <span>Independent (Unlinked)</span>
            </div>
            {isIndependent && <Check className="w-3 h-3 text-atlas-accent" />}
          </button>

          {/* Available Channels */}
          {channels.map((c) => {
            const isSelected = !isIndependent && c.channel_id === currentChannelId;
            return (
              <button
                key={c.channel_id}
                type="button"
                onClick={() => {
                  onSelectChannel(c.channel_id);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center justify-between px-2 py-1 rounded-xs text-left text-xs transition-colors ${
                  isSelected
                    ? "bg-atlas-surface-selected text-atlas-text-primary font-bold"
                    : "hover:bg-atlas-surface-hover text-atlas-text-secondary"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="w-2 h-2 rounded-full shrink-0 shadow-xs"
                    style={{ backgroundColor: c.display_color_token }}
                  />
                  <span className="truncate">{c.name}</span>
                </div>
                {isSelected && <Check className="w-3 h-3 text-atlas-accent" />}
              </button>
            );
          })}

          {/* Per-Dimension Link Overrides */}
          {!isIndependent && subscribableDims.length > 1 && onToggleDimensionOverride && (
            <div className="pt-1.5 border-t border-atlas-border-subtle space-y-1">
              <div className="px-1.5 text-[9px] uppercase font-bold text-atlas-text-muted flex items-center gap-1">
                <Sliders className="w-2.5 h-2.5" />
                <span>Follow Dimensions</span>
              </div>
              <div className="px-1 space-y-1">
                {subscribableDims.map((dim) => {
                  const isFollowing = dimensionOverrides[dim] !== "INDEPENDENT";
                  return (
                    <label
                      key={dim}
                      className="flex items-center justify-between text-[10px] text-atlas-text-secondary hover:text-atlas-text-primary cursor-pointer px-1 py-0.5 rounded-xs hover:bg-atlas-surface-hover"
                    >
                      <span>{dim}</span>
                      <input
                        type="checkbox"
                        checked={isFollowing}
                        onChange={(e) => {
                          onToggleDimensionOverride(
                            dim,
                            e.target.checked ? "FOLLOW" : "INDEPENDENT"
                          );
                        }}
                        className="rounded-xs border-atlas-border-default bg-atlas-surface-0 w-3 h-3 text-blue-500 focus:ring-0"
                      />
                    </label>
                  );
                })}
              </div>
            </div>
          )}

          {/* Link Manager Shortcut */}
          {onOpenManager && (
            <div className="pt-1 border-t border-atlas-border-subtle">
              <button
                type="button"
                onClick={() => {
                  setIsOpen(false);
                  onOpenManager();
                }}
                className="w-full flex items-center gap-1.5 px-2 py-1 text-[10px] text-blue-400 hover:bg-atlas-surface-hover rounded-xs text-left"
              >
                <Layers className="w-3 h-3" />
                <span>Manage Channels...</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
