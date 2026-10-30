"use client";

import React from "react";
import {
  AlertCircle,
  ArrowLeft,
  Check,
  ChevronDown,
  Layers,
  Link2,
  Plus,
  RefreshCw,
  Save,
  Settings,
} from "lucide-react";
import { Button } from "@/design-system";
import { SaveState, Workspace } from "@/lib/workspaces/types";

interface WorkspaceHeaderProps {
  workspace: Workspace;
  allWorkspaces: Workspace[];
  saveState: SaveState;
  onSwitchWorkspace: (workspaceId: string) => void;
  onManualSave: () => void;
  onAddPanel: () => void;
  onOpenLinkGroups: () => void;
  onOpenSettings: () => void;
  onBackToGallery: () => void;
  onResolveConflictReload?: () => void;
  onResolveConflictOverwrite?: () => void;
}

export function WorkspaceHeader({
  workspace,
  allWorkspaces,
  saveState,
  onSwitchWorkspace,
  onManualSave,
  onAddPanel,
  onOpenLinkGroups,
  onOpenSettings,
  onBackToGallery,
  onResolveConflictReload,
  onResolveConflictOverwrite,
}: WorkspaceHeaderProps) {
  const [isSwitcherOpen, setIsSwitcherOpen] = React.useState(false);

  const renderSaveBadge = () => {
    switch (saveState) {
      case "SAVED":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <Check className="w-2.5 h-2.5" />
            <span>Saved</span>
          </span>
        );
      case "SAVING":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-blue-500/10 text-blue-400 border border-blue-500/30">
            <RefreshCw className="w-2.5 h-2.5 animate-spin" />
            <span>Saving...</span>
          </span>
        );
      case "UNSAVED_CHANGES":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            <span>Unsaved Changes</span>
          </span>
        );
      case "CONFLICT":
        return (
          <div className="flex items-center gap-1.5">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/30">
              <AlertCircle className="w-2.5 h-2.5" />
              <span>Version Conflict</span>
            </span>
            {onResolveConflictReload && (
              <button
                type="button"
                onClick={onResolveConflictReload}
                className="text-[10px] text-blue-400 hover:underline"
              >
                Reload
              </button>
            )}
            {onResolveConflictOverwrite && (
              <button
                type="button"
                onClick={onResolveConflictOverwrite}
                className="text-[10px] text-amber-400 hover:underline"
              >
                Overwrite
              </button>
            )}
          </div>
        );
      case "ERROR":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/30">
            <AlertCircle className="w-2.5 h-2.5" />
            <span>Save Failed</span>
          </span>
        );
    }
  };

  return (
    <div className="flex items-center justify-between px-3 py-1.5 border-b border-atlas-border-default bg-atlas-surface-1 shrink-0">
      {/* Left: Back + Switcher */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onBackToGallery}
          className="p-1 text-atlas-text-muted hover:text-atlas-text-primary rounded-sm hover:bg-atlas-surface-hover"
          title="Back to Workspace Library"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>

        <div className="relative">
          <button
            type="button"
            onClick={() => setIsSwitcherOpen((prev) => !prev)}
            className="flex items-center gap-1.5 px-2 py-1 rounded-sm bg-atlas-surface-2 border border-atlas-border-default hover:border-atlas-border-focus text-xs font-semibold text-atlas-text-primary"
          >
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>{workspace.name}</span>
            <ChevronDown className="w-3 h-3 text-atlas-text-muted" />
          </button>

          {isSwitcherOpen && (
            <div className="absolute left-0 top-full mt-1 w-64 bg-atlas-surface-1 border border-atlas-border-default rounded-sm shadow-xl z-50 py-1 font-mono text-xs">
              <div className="px-2.5 py-1 text-[10px] uppercase font-bold text-atlas-text-muted border-b border-atlas-border-subtle">
                Switch Desk
              </div>
              <div className="max-h-60 overflow-auto custom-scrollbar">
                {allWorkspaces.map((ws) => (
                  <button
                    key={ws.workspace_id}
                    type="button"
                    onClick={() => {
                      onSwitchWorkspace(ws.workspace_id);
                      setIsSwitcherOpen(false);
                    }}
                    className={`w-full text-left px-2.5 py-1.5 flex items-center justify-between hover:bg-atlas-surface-hover ${
                      ws.workspace_id === workspace.workspace_id
                        ? "bg-blue-500/10 text-blue-400 font-semibold"
                        : "text-atlas-text-primary"
                    }`}
                  >
                    <span className="truncate">{ws.name}</span>
                    <span className="text-[10px] text-atlas-text-muted">
                      {ws.panel_count || 0} panels
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Save Status */}
        {renderSaveBadge()}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-1.5">
        <Button
          variant="secondary"
          size="xs"
          onClick={onManualSave}
          className="flex items-center gap-1 text-xs"
          title="Manual Save (Ctrl+S)"
        >
          <Save className="w-3 h-3" />
          <span>Save</span>
        </Button>

        <Button
          variant="primary"
          size="xs"
          onClick={onAddPanel}
          className="flex items-center gap-1 text-xs"
          title="Add Panel to Workspace (Alt+N)"
        >
          <Plus className="w-3 h-3" />
          <span>Add Panel</span>
        </Button>

        <Button
          variant="secondary"
          size="xs"
          onClick={onOpenLinkGroups}
          className="flex items-center gap-1 text-xs"
          title="Context Link Groups"
        >
          <Link2 className="w-3 h-3" />
          <span>Link Groups</span>
        </Button>

        <button
          type="button"
          onClick={onOpenSettings}
          className="p-1.5 text-atlas-text-muted hover:text-atlas-text-primary rounded-sm hover:bg-atlas-surface-hover border border-atlas-border-default"
          title="Workspace Settings"
        >
          <Settings className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

