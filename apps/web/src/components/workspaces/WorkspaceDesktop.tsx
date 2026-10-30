"use client";

import React, { useState } from "react";
import { AlertTriangle, Plus, RefreshCw } from "lucide-react";
import { Button } from "@/design-system";
import { useWorkspaceDesktop } from "@/hooks/workspaces/useWorkspaceDesktop";
import { Workspace } from "@/lib/workspaces/types";
import { WorkspaceLayoutRenderer } from "./layout/WorkspaceLayoutRenderer";
import { WorkspaceAddPanelDialog } from "./WorkspaceAddPanelDialog";
import { WorkspaceHeader } from "./WorkspaceHeader";
import { WorkspaceLinkGroupsDialog } from "./WorkspaceLinkGroupsDialog";
import { WorkspaceSettingsDialog } from "./WorkspaceSettingsDialog";

interface WorkspaceDesktopProps {
  workspaceId: string;
  allWorkspaces: Workspace[];
  onSwitchWorkspace: (workspaceId: string) => void;
  onBackToGallery: () => void;
}

export function WorkspaceDesktop({
  workspaceId,
  allWorkspaces,
  onSwitchWorkspace,
  onBackToGallery,
}: WorkspaceDesktopProps) {
  const {
    workspace,
    layoutRoot,
    panelInstances,
    linkGroups,
    maximizedPanelId,
    isLoading,
    error,
    saveState,
    setMaximizedPanelId,
    toggleMaximizePanel,
    handleManualSave,
    handleResolveConflictReload,
    handleResolveConflictOverwrite,
    handleAddPanel,
    handleUpdatePanelConfig,
    handleRemovePanel,
    handleSplitPanel,
    handleDockIntoTab,
    handleSetActiveTab,
    handleUpdateSplitRatios,
    handleRecoverLayout,
    handleUpdateLinkContext,
    handleCreateLinkGroup,
    handleDeleteLinkGroup,
    reloadDesk,
  } = useWorkspaceDesktop(workspaceId);

  // Dialogs state
  const [isAddPanelOpen, setIsAddPanelOpen] = useState(false);
  const [isLinkGroupsOpen, setIsLinkGroupsOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Loading state
  if (isLoading && !workspace) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-atlas-surface-0 font-mono text-xs text-atlas-text-muted">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-500 mb-2" />
        <span>Restoring Workspace Layout & Analytical Panels...</span>
      </div>
    );
  }

  // Error state
  if (error && !workspace) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-atlas-surface-0 font-mono text-xs p-4 text-center">
        <AlertTriangle className="w-8 h-8 text-rose-500 mb-2" />
        <h3 className="text-sm font-bold text-atlas-text-primary mb-1">Failed to Load Workspace</h3>
        <p className="text-atlas-text-muted max-w-sm mb-4 font-sans">{error}</p>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="xs" onClick={onBackToGallery}>
            Back to Desks
          </Button>
          <Button variant="primary" size="xs" onClick={reloadDesk}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  if (!workspace || !layoutRoot) {
    return null;
  }

  return (
    <div className="flex flex-col w-full h-full bg-atlas-surface-0 overflow-hidden">
      {/* Header */}
      <WorkspaceHeader
        workspace={workspace}
        allWorkspaces={allWorkspaces}
        saveState={saveState}
        onSwitchWorkspace={onSwitchWorkspace}
        onManualSave={handleManualSave}
        onAddPanel={() => setIsAddPanelOpen(true)}
        onOpenLinkGroups={() => setIsLinkGroupsOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onBackToGallery={onBackToGallery}
        onResolveConflictReload={handleResolveConflictReload}
        onResolveConflictOverwrite={handleResolveConflictOverwrite}
      />

      {/* Main Multi-Panel Layout Area */}
      <div className="flex-1 w-full h-full overflow-hidden p-1 relative">
        <WorkspaceLayoutRenderer
          node={layoutRoot}
          panelInstances={panelInstances}
          linkGroups={linkGroups}
          maximizedPanelId={maximizedPanelId}
          onToggleMaximize={toggleMaximizePanel}
          onSplitRight={(targetPid) => {
            setIsAddPanelOpen(true);
          }}
          onSplitBottom={(targetPid) => {
            setIsAddPanelOpen(true);
          }}
          onClosePanel={handleRemovePanel}
          onSetActiveTab={handleSetActiveTab}
          onUpdateSplitRatios={handleUpdateSplitRatios}
          onUpdateContext={handleUpdateLinkContext}
          onUpdateConfig={handleUpdatePanelConfig}
          onOpenSettings={(pid) => setIsSettingsOpen(true)}
        />
      </div>

      {/* Add Panel Dialog */}
      <WorkspaceAddPanelDialog
        isOpen={isAddPanelOpen}
        onClose={() => setIsAddPanelOpen(false)}
        onAddPanel={async (panelTypeId, titleOverride, config, dockPosition) => {
          await handleAddPanel(panelTypeId, titleOverride, config, undefined, undefined, dockPosition);
        }}
      />

      {/* Link Groups Manager Modal */}
      <WorkspaceLinkGroupsDialog
        isOpen={isLinkGroupsOpen}
        linkGroups={linkGroups}
        panelInstances={panelInstances}
        onClose={() => setIsLinkGroupsOpen(false)}
        onUpdateContext={handleUpdateLinkContext}
        onCreateLinkGroup={handleCreateLinkGroup}
        onDeleteLinkGroup={handleDeleteLinkGroup}
        onUpdatePanelGroup={async (pid, gid) => {
          await handleUpdatePanelConfig(pid, {
            link_group_id: gid,
            independent_mode: gid === null,
          });
        }}
      />

      {/* Desk Settings Modal */}
      <WorkspaceSettingsDialog
        isOpen={isSettingsOpen}
        workspace={workspace}
        onClose={() => setIsSettingsOpen(false)}
        onUpdateMetadata={async (data) => {
          await reloadDesk();
        }}
      />
    </div>
  );
}

