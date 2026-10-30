"use client";

import React, { useState } from "react";
import {
  Globe,
  Layers,
  Link2,
  Plus,
  RefreshCw,
  ShieldCheck,
  Trash2,
  X,
} from "lucide-react";
import { Badge, Button } from "@/design-system";
import { useGlobalContext } from "./GlobalContextProvider";
import { ContextScope } from "@/lib/context/types";

interface LinkChannelManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PRESET_COLORS = [
  "#3B82F6", // Blue
  "#10B981", // Emerald
  "#F59E0B", // Amber
  "#F43F5E", // Rose
  "#8B5CF6", // Purple
  "#06B6D4", // Cyan
  "#EC4899", // Pink
];

export function LinkChannelManagerModal({ isOpen, onClose }: LinkChannelManagerModalProps) {
  const {
    channels,
    activeChannelId,
    setActiveChannelId,
    createChannel,
    deleteChannel,
    publishSelection,
  } = useGlobalContext();

  const [selectedChannelId, setSelectedChannelId] = useState<string>(activeChannelId);
  const [isCreating, setIsCreating] = useState(false);
  const [newName, setNewName] = useState("");
  const [newColor, setNewColor] = useState(PRESET_COLORS[0]);
  const [newScope, setNewScope] = useState<ContextScope>("WORKSPACE");

  // Edit value
  const [editSymbol, setEditSymbol] = useState("");

  if (!isOpen) return null;

  const currentChannel = channels.find((c) => c.channel_id === selectedChannelId) || channels[0];

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      const created = await createChannel(newName.trim(), newColor, undefined, newScope);
      setSelectedChannelId(created.channel_id);
      setIsCreating(false);
      setNewName("");
    } catch (err) {
      console.error(err);
    }
  };

  const handleApplySymbol = () => {
    if (!editSymbol.trim() || !currentChannel) return;
    publishSelection({
      channelId: currentChannel.channel_id,
      dimension: "INSTRUMENT",
      canonicalTargetId: editSymbol.trim().toUpperCase(),
      payload: { symbol: editSymbol.trim().toUpperCase() },
    });
    setEditSymbol("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="flex flex-col w-full max-w-2xl bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-2xl overflow-hidden font-mono text-xs">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Global Link Channels & Context Synchronization
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-atlas-text-muted hover:text-atlas-text-primary p-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body Split */}
        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-atlas-border-default min-h-[360px]">
          {/* Left: Channels List */}
          <div className="p-3 bg-atlas-surface-0 flex flex-col justify-between">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] uppercase font-bold text-atlas-text-muted">
                  Link Channels ({channels.length})
                </span>
                <button
                  type="button"
                  onClick={() => setIsCreating(true)}
                  className="text-blue-400 hover:text-blue-300 text-[10px] flex items-center gap-1"
                >
                  <Plus className="w-3 h-3" />
                  New Channel
                </button>
              </div>

              {channels.map((c) => {
                const isSelected = c.channel_id === currentChannel?.channel_id;
                return (
                  <div
                    key={c.channel_id}
                    onClick={() => setSelectedChannelId(c.channel_id)}
                    className={`flex items-center justify-between p-2 rounded-xs border cursor-pointer transition-colors ${
                      isSelected
                        ? "border-blue-500 bg-blue-500/10 text-atlas-text-primary font-bold"
                        : "border-atlas-border-subtle bg-atlas-surface-1 hover:bg-atlas-surface-hover text-atlas-text-secondary"
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <span
                        className="w-2.5 h-2.5 rounded-full shrink-0 shadow-xs"
                        style={{ backgroundColor: c.display_color_token }}
                      />
                      <span className="truncate text-xs">{c.name}</span>
                    </div>
                    <Badge variant="outline" className="text-[9px] px-1 py-0 uppercase">
                      {c.scope === "USER_APPLICATION" ? "APP" : "WS"}
                    </Badge>
                  </div>
                );
              })}
            </div>

            <div className="pt-2 border-t border-atlas-border-subtle text-[10px] text-atlas-text-muted">
              Select a channel to inspect active dimensions, connected panels, and context values.
            </div>
          </div>

          {/* Right: Channel Detail & Inspector */}
          <div className="col-span-2 p-4 bg-atlas-surface-1 flex flex-col justify-between space-y-4">
            {isCreating ? (
              <form onSubmit={handleCreate} className="space-y-3">
                <div className="text-xs font-bold text-atlas-text-primary mb-2">
                  Create New Context Link Channel
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-[10px] uppercase font-bold text-atlas-text-muted">
                    Channel Name
                  </label>
                  <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="e.g. Group E (Volatility Spread)"
                    required
                    className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1.5 text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-border-focus"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-[10px] uppercase font-bold text-atlas-text-muted">
                    Scope
                  </label>
                  <select
                    value={newScope}
                    onChange={(e) => setNewScope(e.target.value as ContextScope)}
                    className="bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2 py-1.5 text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-border-focus"
                  >
                    <option value="WORKSPACE">WORKSPACE (Isolated to this desk)</option>
                    <option value="USER_APPLICATION">
                      USER_APPLICATION (Cross-Workspace & AppShell)
                    </option>
                  </select>
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] uppercase font-bold text-atlas-text-muted">
                    Display Color
                  </label>
                  <div className="flex items-center gap-2">
                    {PRESET_COLORS.map((col) => (
                      <button
                        key={col}
                        type="button"
                        onClick={() => setNewColor(col)}
                        className={`w-5 h-5 rounded-full border-2 transition-transform ${
                          newColor === col ? "scale-115 border-white" : "border-transparent"
                        }`}
                        style={{ backgroundColor: col }}
                      />
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-3 border-t border-atlas-border-subtle">
                  <Button variant="ghost" size="xs" type="button" onClick={() => setIsCreating(false)}>
                    Cancel
                  </Button>
                  <Button variant="primary" size="xs" type="submit" disabled={!newName.trim()}>
                    Save Channel
                  </Button>
                </div>
              </form>
            ) : currentChannel ? (
              <div className="space-y-4">
                {/* Channel Header */}
                <div className="flex items-center justify-between pb-2 border-b border-atlas-border-subtle">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-3.5 h-3.5 rounded-full shadow-xs"
                      style={{ backgroundColor: currentChannel.display_color_token }}
                    />
                    <div>
                      <h4 className="text-sm font-bold text-atlas-text-primary">
                        {currentChannel.name}
                      </h4>
                      <span className="text-[10px] text-atlas-text-muted uppercase">
                        ID: {currentChannel.channel_id} • Scope: {currentChannel.scope} • Rev:{" "}
                        {currentChannel.revision}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant={
                        currentChannel.channel_id === activeChannelId ? "primary" : "secondary"
                      }
                      size="xs"
                      onClick={() => setActiveChannelId(currentChannel.channel_id)}
                    >
                      {currentChannel.channel_id === activeChannelId ? "Active Channel" : "Set Active"}
                    </Button>
                    <button
                      type="button"
                      onClick={() => deleteChannel(currentChannel.channel_id)}
                      className="p-1 rounded-xs text-atlas-text-muted hover:text-rose-400 hover:bg-atlas-surface-2 transition-colors"
                      title="Delete Channel"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Active Snapshot Variables */}
                <div>
                  <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-1.5">
                    Synchronized Context Snapshot
                  </label>
                  <div className="bg-atlas-surface-0 border border-atlas-border-subtle rounded-sm p-2.5 space-y-1.5">
                    {Object.keys(currentChannel.context_snapshot).length === 0 ? (
                      <span className="text-atlas-text-muted text-[10px]">
                        No active context keys broadcasted yet.
                      </span>
                    ) : (
                      Object.entries(currentChannel.context_snapshot).map(([key, val]) => (
                        <div
                          key={key}
                          className="flex items-center justify-between text-xs py-0.5 border-b border-atlas-border-subtle/50 last:border-0"
                        >
                          <span className="font-bold text-atlas-text-secondary">{key}:</span>
                          <span className="font-mono text-blue-400 font-bold">{String(val)}</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Direct Instrument Override */}
                <div className="pt-2 border-t border-atlas-border-subtle">
                  <label className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-1">
                    Broadcast Financial Instrument Selection
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="e.g. NVDA, MSFT, SPY"
                      value={editSymbol}
                      onChange={(e) => setEditSymbol(e.target.value)}
                      className="flex-1 bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1 text-xs text-atlas-text-primary focus:outline-none focus:border-atlas-border-focus uppercase"
                    />
                    <Button
                      variant="primary"
                      size="xs"
                      onClick={handleApplySymbol}
                      disabled={!editSymbol.trim()}
                    >
                      Broadcast Selection
                    </Button>
                  </div>
                </div>
              </div>
            ) : null}

            {/* Footer */}
            <div className="flex items-center justify-end pt-3 border-t border-atlas-border-default">
              <Button variant="secondary" size="xs" onClick={onClose}>
                Done
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
