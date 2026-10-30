"use client";

import React, { useState } from "react";
import { Link2, Plus, Trash2, X } from "lucide-react";
import { Button } from "@/design-system";
import { WorkspaceLinkGroup, WorkspacePanelInstance } from "@/lib/workspaces/types";

interface WorkspaceLinkGroupsDialogProps {
  isOpen: boolean;
  linkGroups: WorkspaceLinkGroup[];
  panelInstances: Record<string, WorkspacePanelInstance>;
  onClose: () => void;
  onUpdateContext: (linkGroupId: string, updates: Record<string, unknown>) => Promise<void>;
  onCreateLinkGroup: (name: string, color: string, initialContext?: Record<string, unknown>) => Promise<any>;
  onDeleteLinkGroup: (linkGroupId: string) => Promise<void>;
  onUpdatePanelGroup: (panelId: string, linkGroupId: string | null) => Promise<void>;
}

export function WorkspaceLinkGroupsDialog({
  isOpen,
  linkGroups,
  panelInstances,
  onClose,
  onUpdateContext,
  onCreateLinkGroup,
  onDeleteLinkGroup,
  onUpdatePanelGroup,
}: WorkspaceLinkGroupsDialogProps) {
  const [newGroupName, setNewGroupName] = useState("");
  const [newGroupColor, setNewGroupColor] = useState("#10b981");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGroupName.trim()) return;
    setIsSubmitting(true);
    try {
      await onCreateLinkGroup(newGroupName.trim(), newGroupColor, { INSTRUMENT: "AAPL" });
      setNewGroupName("");
    } catch (err: unknown) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
      <div className="flex flex-col w-full max-w-xl bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-2xl overflow-hidden font-mono text-xs">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-atlas-border-default bg-atlas-surface-2">
          <div className="flex items-center gap-2">
            <Link2 className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Cross-Panel Context Link Groups
            </h3>
          </div>
          <button type="button" onClick={onClose} className="text-atlas-text-muted hover:text-atlas-text-primary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4 max-h-[75vh] overflow-auto custom-scrollbar">
          <p className="text-[11px] text-atlas-text-muted font-sans">
            Panels assigned to the same Link Group synchronize their financial context in real-time. Changing an instrument in one panel will immediately broadcast to all linked charts, news, and fundamentals.
          </p>

          {/* Link Groups List */}
          <div className="space-y-3">
            {linkGroups.map((group) => {
              const currentSymbol = (group.context.INSTRUMENT as string) || "AAPL";
              const assignedPanels = Object.values(panelInstances).filter(
                (p) => p.link_group_id === group.link_group_id
              );

              return (
                <div
                  key={group.link_group_id}
                  className="p-3 rounded-sm border border-atlas-border-default bg-atlas-surface-0 flex flex-col gap-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: group.color }} />
                      <span className="font-bold text-xs text-atlas-text-primary">{group.name}</span>
                    </div>

                    <div className="flex items-center gap-1">
                      {linkGroups.length > 1 && (
                        <button
                          type="button"
                          onClick={() => onDeleteLinkGroup(group.link_group_id)}
                          className="p-1 text-atlas-text-muted hover:text-rose-400"
                          title="Delete Link Group"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Active Ticker Selection for this group */}
                  <div className="flex items-center gap-2 pt-1 border-t border-atlas-border-subtle">
                    <span className="text-[10px] text-atlas-text-muted uppercase">Broadcast Ticker:</span>
                    <div className="flex items-center gap-1">
                      {["AAPL", "MSFT", "NVDA", "GOOGL", "SPY"].map((sym) => (
                        <button
                          key={sym}
                          type="button"
                          onClick={() =>
                            onUpdateContext(group.link_group_id, { INSTRUMENT: sym, COMPANY: sym })
                          }
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            currentSymbol === sym
                              ? "bg-blue-600 text-white"
                              : "bg-atlas-surface-2 text-atlas-text-muted hover:text-atlas-text-primary border border-atlas-border-subtle"
                          }`}
                        >
                          {sym}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Assigned Panels Tags */}
                  <div className="text-[10px] text-atlas-text-muted">
                    <span>Assigned Panels: </span>
                    {assignedPanels.length === 0 ? (
                      <span className="italic">None</span>
                    ) : (
                      assignedPanels.map((p) => p.title_override || p.panel_type_id).join(", ")
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Add Group Form */}
          <form onSubmit={handleCreate} className="p-3 bg-atlas-surface-2 border border-atlas-border-default rounded-sm flex items-center gap-2">
            <input
              type="text"
              value={newGroupName}
              onChange={(e) => setNewGroupName(e.target.value)}
              placeholder="New link group name (e.g. Group C)..."
              className="flex-1 bg-atlas-surface-0 border border-atlas-border-default rounded-sm px-2.5 py-1 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
            />
            <input
              type="color"
              value={newGroupColor}
              onChange={(e) => setNewGroupColor(e.target.value)}
              className="w-7 h-7 p-0.5 rounded bg-transparent border border-atlas-border-default cursor-pointer"
              title="Select Group Color"
            />
            <Button variant="secondary" size="xs" type="submit" disabled={!newGroupName.trim() || isSubmitting}>
              <Plus className="w-3 h-3 mr-1" />
              Add Group
            </Button>
          </form>

          {/* Panel Assignment Selectors */}
          <div className="pt-2 border-t border-atlas-border-default">
            <span className="text-[10px] uppercase font-bold text-atlas-text-muted block mb-2">
              Assign Panels to Groups
            </span>
            <div className="space-y-1.5">
              {Object.values(panelInstances).map((panel) => (
                <div
                  key={panel.panel_instance_id}
                  className="flex items-center justify-between p-2 rounded-sm bg-atlas-surface-0 border border-atlas-border-subtle"
                >
                  <span className="text-xs text-atlas-text-primary truncate">
                    {panel.title_override || panel.panel_type_id}
                  </span>
                  <select
                    value={panel.link_group_id || "none"}
                    onChange={(e) =>
                      onUpdatePanelGroup(
                        panel.panel_instance_id,
                        e.target.value === "none" ? null : e.target.value
                      )
                    }
                    className="bg-atlas-surface-1 border border-atlas-border-default text-xs text-atlas-text-primary px-2 py-1 rounded-sm focus:outline-none"
                  >
                    <option value="none">Independent (No Link)</option>
                    {linkGroups.map((g) => (
                      <option key={g.link_group_id} value={g.link_group_id}>
                        {g.name}
                      </option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end px-4 py-2 border-t border-atlas-border-default bg-atlas-surface-2">
          <Button variant="primary" size="xs" onClick={onClose}>
            Done
          </Button>
        </div>
      </div>
    </div>
  );
}

