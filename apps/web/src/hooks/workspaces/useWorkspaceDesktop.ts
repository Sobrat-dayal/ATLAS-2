"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { globalEventBus } from "@/lib/context/eventBus";
import {
  addPanel,
  createLinkGroup,
  deleteLinkGroup,
  getWorkspace,
  recoverLayout,
  removePanel as apiRemovePanel,
  updateLayout as apiUpdateLayout,
  updateLinkGroupContext,
  updatePanel as apiUpdatePanel,
  updateWorkspace,
} from "@/lib/workspaces/api";
import {
  dockIntoTabStack,
  removePanel,
  setActiveTab,
  splitPanel,
  updateSplitRatios,
} from "@/lib/workspaces/layoutOperations";
import {
  LayoutNode,
  PanelTypeId,
  SaveState,
  SplitOrientation,
  Workspace,
  WorkspaceLinkGroup,
  WorkspacePanelInstance,
} from "@/lib/workspaces/types";

export function useWorkspaceDesktop(workspaceId: string) {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [layoutRoot, setLayoutRoot] = useState<LayoutNode | null>(null);
  const [panelInstances, setPanelInstances] = useState<Record<string, WorkspacePanelInstance>>({});
  const [linkGroups, setLinkGroups] = useState<WorkspaceLinkGroup[]>([]);
  const [maximizedPanelId, setMaximizedPanelId] = useState<string | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<SaveState>("SAVED");
  const [revision, setRevision] = useState<number>(1);

  // Autosave timer ref
  const autosaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const pendingLayoutRef = useRef<{ root: LayoutNode; panels: Record<string, WorkspacePanelInstance> } | null>(null);

  // Load workspace data
  const loadDesk = useCallback(async () => {
    if (!workspaceId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await getWorkspace(workspaceId);
      setWorkspace(data);
      setRevision(data.layout_revision || 1);
      if (data.layout) {
        setLayoutRoot(data.layout.root_node);
        setPanelInstances(data.layout.panel_instances || {});
      }
      setLinkGroups(data.link_groups || []);
      setSaveState("SAVED");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load workspace");
    } finally {
      setIsLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    loadDesk();
  }, [loadDesk]);

  // Persist layout commit
  const commitLayout = useCallback(
    async (root: LayoutNode, panels: Record<string, WorkspacePanelInstance>, currentRev: number) => {
      setSaveState("SAVING");
      try {
        const res = await apiUpdateLayout(workspaceId, {
          expected_revision: currentRev,
          layout: {
            root_node: root,
            panel_instances: panels,
            schema_version: 1,
          },
        });
        setRevision((prev) => prev + 1);
        setSaveState("SAVED");
        pendingLayoutRef.current = null;
      } catch (err: any) {
        if (err?.status === 409 || err?.code === "WORKSPACE_LAYOUT_REVISION_CONFLICT") {
          setSaveState("CONFLICT");
        } else {
          setSaveState("ERROR");
        }
      }
    },
    [workspaceId]
  );

  // Schedule autosave with debounce
  const scheduleAutosave = useCallback(
    (newRoot: LayoutNode, newPanels: Record<string, WorkspacePanelInstance>) => {
      setSaveState("UNSAVED_CHANGES");
      pendingLayoutRef.current = { root: newRoot, panels: newPanels };

      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
      }

      autosaveTimerRef.current = setTimeout(() => {
        commitLayout(newRoot, newPanels, revision);
      }, 700);
    },
    [commitLayout, revision]
  );

  // Immediate manual save
  const handleManualSave = useCallback(() => {
    if (layoutRoot) {
      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
      }
      commitLayout(layoutRoot, panelInstances, revision);
    }
  }, [commitLayout, layoutRoot, panelInstances, revision]);

  // Resolve version conflict by reloading latest state
  const handleResolveConflictReload = useCallback(async () => {
    await loadDesk();
  }, [loadDesk]);

  // Force overwrite in conflict
  const handleResolveConflictOverwrite = useCallback(async () => {
    if (!layoutRoot || !workspace) return;
    try {
      // Fetch latest revision to align expected_revision
      const latest = await getWorkspace(workspaceId);
      await commitLayout(layoutRoot, panelInstances, latest.layout_revision);
    } catch {
      await loadDesk();
    }
  }, [commitLayout, layoutRoot, loadDesk, panelInstances, workspace, workspaceId]);

  // Panel operations
  const handleAddPanel = useCallback(
    async (
      panelTypeId: PanelTypeId,
      titleOverride?: string,
      configuration?: Record<string, unknown>,
      linkGroupId?: string,
      dockTargetPanelId?: string,
      dockPosition: "right" | "bottom" | "tab" = "right"
    ) => {
      try {
        const newPanel = await addPanel(workspaceId, {
          panel_type_id: panelTypeId,
          title_override: titleOverride,
          configuration,
          link_group_id: linkGroupId,
          dock_target_panel_id: dockTargetPanelId,
          dock_position: dockPosition,
        });

        // Refresh entire desk to acquire updated tree and revision
        await loadDesk();
        return newPanel;
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to add panel");
        throw err;
      }
    },
    [loadDesk, workspaceId]
  );

  const handleUpdatePanelConfig = useCallback(
    async (panelId: string, updates: Partial<WorkspacePanelInstance>) => {
      setPanelInstances((prev) => {
        const current = prev[panelId];
        if (!current) return prev;
        const updated = { ...current, ...updates, updated_at: new Date().toISOString() };
        const nextMap = { ...prev, [panelId]: updated };
        if (layoutRoot) {
          scheduleAutosave(layoutRoot, nextMap);
        }
        return nextMap;
      });

      try {
        await apiUpdatePanel(workspaceId, panelId, updates);
      } catch (err: unknown) {
        console.error("Failed to persist panel config update", err);
      }
    },
    [layoutRoot, scheduleAutosave, workspaceId]
  );

  const handleRemovePanel = useCallback(
    async (panelId: string) => {
      if (!layoutRoot) return;
      if (maximizedPanelId === panelId) {
        setMaximizedPanelId(null);
      }

      const nextRoot = removePanel(layoutRoot, panelId);
      const nextPanels = { ...panelInstances };
      delete nextPanels[panelId];

      if (nextRoot) {
        setLayoutRoot(nextRoot);
      }
      setPanelInstances(nextPanels);

      try {
        await apiRemovePanel(workspaceId, panelId);
        setRevision((prev) => prev + 1);
        setSaveState("SAVED");
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to remove panel");
      }
    },
    [layoutRoot, maximizedPanelId, panelInstances, workspaceId]
  );

  const handleSplitPanel = useCallback(
    (targetPanelId: string, orientation: SplitOrientation, newPanelId: string) => {
      if (!layoutRoot) return;
      const nextRoot = splitPanel(layoutRoot, targetPanelId, orientation, newPanelId);
      setLayoutRoot(nextRoot);
      scheduleAutosave(nextRoot, panelInstances);
    },
    [layoutRoot, panelInstances, scheduleAutosave]
  );

  const handleDockIntoTab = useCallback(
    (targetPanelId: string, newPanelId: string) => {
      if (!layoutRoot) return;
      const nextRoot = dockIntoTabStack(layoutRoot, targetPanelId, newPanelId);
      setLayoutRoot(nextRoot);
      scheduleAutosave(nextRoot, panelInstances);
    },
    [layoutRoot, panelInstances, scheduleAutosave]
  );

  const handleSetActiveTab = useCallback(
    (tabStackId: string, activePanelId: string) => {
      if (!layoutRoot) return;
      const nextRoot = setActiveTab(layoutRoot, tabStackId, activePanelId);
      setLayoutRoot(nextRoot);
      scheduleAutosave(nextRoot, panelInstances);
    },
    [layoutRoot, panelInstances, scheduleAutosave]
  );

  const handleUpdateSplitRatios = useCallback(
    (splitNodeId: string, newRatios: number[]) => {
      if (!layoutRoot) return;
      const nextRoot = updateSplitRatios(layoutRoot, splitNodeId, newRatios);
      setLayoutRoot(nextRoot);
      scheduleAutosave(nextRoot, panelInstances);
    },
    [layoutRoot, panelInstances, scheduleAutosave]
  );

  const handleRecoverLayout = useCallback(async () => {
    try {
      const recovered = await recoverLayout(workspaceId);
      setLayoutRoot(recovered.root_node);
      setPanelInstances(recovered.panel_instances || {});
      setRevision((prev) => prev + 1);
      setSaveState("SAVED");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to recover layout");
    }
  }, [workspaceId]);

  // Context & Link Groups
  const handleUpdateLinkContext = useCallback(
    async (linkGroupId: string, contextUpdates: Record<string, unknown>) => {
      let nextVersion = 1;
      setLinkGroups((prev) =>
        prev.map((g) => {
          if (g.link_group_id !== linkGroupId) return g;
          // Check for loop / identical value
          let isDifferent = false;
          for (const [k, v] of Object.entries(contextUpdates)) {
            if (g.context[k] !== v) {
              isDifferent = true;
              break;
            }
          }
          if (!isDifferent) return g;

          nextVersion = g.version + 1;
          return {
            ...g,
            context: { ...g.context, ...contextUpdates },
            version: nextVersion,
          };
        })
      );

      // Stage 121: Publish to cross-panel event bus
      if (contextUpdates.INSTRUMENT) {
        globalEventBus.publish({
          event_id: `evt_${Math.random().toString(36).substring(2, 11)}`,
          channel_id: linkGroupId,
          scope: "WORKSPACE",
          dimension: "INSTRUMENT",
          canonical_target_id: String(contextUpdates.INSTRUMENT),
          target_type: "INSTRUMENT",
          payload: contextUpdates,
          context_revision: nextVersion,
          emitted_at: new Date().toISOString(),
          selection_reason: "USER_CLICK",
        });
      }

      try {
        await updateLinkGroupContext(workspaceId, linkGroupId, contextUpdates);
      } catch (err: unknown) {
        console.error("Failed to broadcast link context", err);
      }
    },
    [workspaceId]
  );

  const handleCreateLinkGroup = useCallback(
    async (name: string, color: string, initialContext?: Record<string, unknown>) => {
      try {
        const created = await createLinkGroup(workspaceId, name, color, initialContext);
        setLinkGroups((prev) => [...prev, created]);
        return created;
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to create link group");
        throw err;
      }
    },
    [workspaceId]
  );

  const handleDeleteLinkGroup = useCallback(
    async (linkGroupId: string) => {
      try {
        await deleteLinkGroup(workspaceId, linkGroupId);
        setLinkGroups((prev) => prev.filter((g) => g.link_group_id !== linkGroupId));
        // Disconnect member panels
        setPanelInstances((prev) => {
          const next = { ...prev };
          for (const pid of Object.keys(next)) {
            if (next[pid].link_group_id === linkGroupId) {
              next[pid] = { ...next[pid], link_group_id: null, independent_mode: true };
            }
          }
          return next;
        });
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to delete link group");
      }
    },
    [workspaceId]
  );

  // Keyboard Shortcuts Handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Save: Cmd+S or Ctrl+S
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        handleManualSave();
      }
      // Escape restores maximized panel
      if (e.key === "Escape" && maximizedPanelId) {
        setMaximizedPanelId(null);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleManualSave, maximizedPanelId]);

  return {
    workspace,
    layoutRoot,
    panelInstances,
    linkGroups,
    maximizedPanelId,
    isLoading,
    error,
    saveState,
    revision,
    setMaximizedPanelId,
    toggleMaximizePanel: (panelId: string) =>
      setMaximizedPanelId((curr) => (curr === panelId ? null : panelId)),
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
    reloadDesk: loadDesk,
  };
}

