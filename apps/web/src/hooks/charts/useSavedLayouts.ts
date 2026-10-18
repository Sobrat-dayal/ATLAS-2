"use client";

/**
 * Saved Chart Layouts Management Hook (Stage 74).
 *
 * Implements:
 * - Querying, creating, updating, duplicating, renaming, and deleting saved layouts
 * - Concurrency conflict detection (412 / 409) and resolution workflows (Save As New, Reload)
 * - Atomic workspace serialization & hydration integration
 * - JSON import & export integration
 * - Server confirmation tracking and error state management
 */

import { useCallback, useEffect, useState } from "react";
import {
  createSavedLayout,
  deleteSavedLayout,
  duplicateSavedLayout,
  fetchSavedLayout,
  fetchSavedLayouts,
  hydrateChartWorkspace,
  LayoutConflictApiError,
  LayoutConflictState,
  parseAndValidateImportJson,
  patchSavedLayoutMetadata,
  RestorationReport,
  SavedChartLayoutDocumentV1,
  SavedLayoutDetail,
  SavedLayoutSummary,
  serializeChartWorkspace,
  triggerLayoutDownload,
  generateExportEnvelope,
  updateSavedLayout,
  workspaceStore,
  chartSyncStore,
  DrawingSessionStore,
} from "@/lib/charts";

export function useSavedLayouts() {
  const [layouts, setLayouts] = useState<SavedLayoutSummary[]>([]);
  const [currentLayout, setCurrentLayout] = useState<SavedLayoutDetail | null>(null);
  const [savedSnapshot, setSavedSnapshot] = useState<SavedChartLayoutDocumentV1 | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [conflictState, setConflictState] = useState<LayoutConflictState | null>(null);
  const [restorationReport, setRestorationReport] = useState<RestorationReport | null>(null);

  // Refresh layouts list
  const refreshLayouts = useCallback(async (search?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetchSavedLayouts(1, 100, search);
      setLayouts(res.items || []);
    } catch (err: any) {
      console.error("Failed to fetch saved chart layouts:", err);
      setError(err.message || "Failed to load saved layouts.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial load of layouts list
  useEffect(() => {
    refreshLayouts();
  }, [refreshLayouts]);

  // Load a layout by ID
  const loadLayout = useCallback(
    async (layoutId: string): Promise<boolean> => {
      setIsLoading(true);
      setError(null);
      try {
        const detail = await fetchSavedLayout(layoutId);
        // Hydrate workspace state, drawings, and sync groups
        const report = hydrateChartWorkspace(detail.document, {
          workspaceStoreInstance: workspaceStore,
          syncStoreInstance: chartSyncStore,
        });

        setCurrentLayout(detail);
        setSavedSnapshot(detail.document);
        setRestorationReport(report);
        setConflictState(null);
        return true;
      } catch (err: any) {
        console.error(`Failed to load layout '${layoutId}':`, err);
        setError(err.message || "Failed to load layout configuration.");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // Save current working configuration into the existing loaded layout
  const saveCurrentLayout = useCallback(async (): Promise<boolean> => {
    if (!currentLayout) {
      // Must use Save As if no current layout exists
      return false;
    }

    setIsSaving(true);
    setError(null);

    const workingDoc = serializeChartWorkspace(workspaceStore.getState(), {
      syncStore: chartSyncStore,
    });

    try {
      const updated = await updateSavedLayout(currentLayout.id, {
        document: workingDoc,
        expected_revision: currentLayout.revision,
      });

      setCurrentLayout(updated);
      setSavedSnapshot(updated.document);
      setConflictState(null);
      await refreshLayouts();
      return true;
    } catch (err: any) {
      if (err instanceof LayoutConflictApiError || err.status === 412 || err.status === 409) {
        // Concurrency conflict detected: another session saved a newer revision
        setConflictState({
          layoutId: currentLayout.id,
          layoutName: currentLayout.name,
          expectedRevision: currentLayout.revision,
          serverRevision: currentLayout.revision + 1,
          workingDocument: workingDoc,
        });
      } else {
        setError(err.message || "Failed to save chart layout.");
      }
      return false;
    } finally {
      setIsSaving(false);
    }
  }, [currentLayout, refreshLayouts]);

  // Save As a brand new layout
  const saveAsLayout = useCallback(
    async (name: string, description?: string, isDefault?: boolean): Promise<SavedLayoutDetail | null> => {
      setIsSaving(true);
      setError(null);

      const workingDoc = serializeChartWorkspace(workspaceStore.getState(), {
        syncStore: chartSyncStore,
      });

      try {
        const created = await createSavedLayout({
          name: name.trim(),
          description: description?.trim() || undefined,
          document: workingDoc,
          is_default: isDefault ?? false,
        });

        setCurrentLayout(created);
        setSavedSnapshot(created.document);
        setConflictState(null);
        await refreshLayouts();
        return created;
      } catch (err: any) {
        console.error("Failed to create new layout:", err);
        setError(err.message || "Failed to create layout.");
        return null;
      } finally {
        setIsSaving(false);
      }
    },
    [refreshLayouts]
  );

  // Rename a layout
  const renameLayout = useCallback(
    async (layoutId: string, newName: string): Promise<boolean> => {
      setError(null);
      try {
        const updated = await patchSavedLayoutMetadata(layoutId, {
          name: newName.trim(),
        });
        if (currentLayout?.id === layoutId) {
          setCurrentLayout(updated);
        }
        await refreshLayouts();
        return true;
      } catch (err: any) {
        console.error("Failed to rename layout:", err);
        setError(err.message || "Failed to rename layout.");
        return false;
      }
    },
    [currentLayout, refreshLayouts]
  );

  // Toggle default layout status
  const setDefaultLayout = useCallback(
    async (layoutId: string, isDefault: boolean): Promise<boolean> => {
      setError(null);
      try {
        const updated = await patchSavedLayoutMetadata(layoutId, {
          is_default: isDefault,
        });
        if (currentLayout?.id === layoutId) {
          setCurrentLayout(updated);
        }
        await refreshLayouts();
        return true;
      } catch (err: any) {
        console.error("Failed to set default layout:", err);
        setError(err.message || "Failed to update default layout.");
        return false;
      }
    },
    [currentLayout, refreshLayouts]
  );

  // Duplicate layout
  const duplicateLayout = useCallback(
    async (layoutId: string, customName?: string): Promise<SavedLayoutDetail | null> => {
      setError(null);
      try {
        const duplicated = await duplicateSavedLayout(layoutId, customName);
        await refreshLayouts();
        return duplicated;
      } catch (err: any) {
        console.error("Failed to duplicate layout:", err);
        setError(err.message || "Failed to duplicate layout.");
        return null;
      }
    },
    [refreshLayouts]
  );

  // Delete layout
  const deleteLayout = useCallback(
    async (layoutId: string): Promise<boolean> => {
      setError(null);
      try {
        await deleteSavedLayout(layoutId);
        if (currentLayout?.id === layoutId) {
          setCurrentLayout(null);
          setSavedSnapshot(null);
        }
        await refreshLayouts();
        return true;
      } catch (err: any) {
        console.error("Failed to delete layout:", err);
        setError(err.message || "Failed to delete layout.");
        return false;
      }
    },
    [currentLayout, refreshLayouts]
  );

  // Export current workspace or specified layout to JSON download
  const exportLayout = useCallback(
    async (layoutId?: string): Promise<void> => {
      setError(null);
      try {
        let name = "ATLAS Workspace";
        let doc: SavedChartLayoutDocumentV1;

        if (layoutId && currentLayout?.id !== layoutId) {
          const detail = await fetchSavedLayout(layoutId);
          name = detail.name;
          doc = detail.document;
        } else if (currentLayout) {
          name = currentLayout.name;
          doc = serializeChartWorkspace(workspaceStore.getState(), {
            syncStore: chartSyncStore,
          });
        } else {
          doc = serializeChartWorkspace(workspaceStore.getState(), {
            syncStore: chartSyncStore,
          });
        }

        const json = generateExportEnvelope(name, doc);
        triggerLayoutDownload(name, json);
      } catch (err: any) {
        console.error("Failed to export layout:", err);
        setError(err.message || "Failed to export layout.");
      }
    },
    [currentLayout]
  );

  // Import JSON layout file and save as a new layout
  const importLayout = useCallback(
    async (jsonContent: string, customName?: string): Promise<SavedLayoutDetail | null> => {
      setError(null);
      try {
        const preview = parseAndValidateImportJson(jsonContent);
        const nameToUse = customName || preview.layoutName || "Imported Layout";

        const created = await createSavedLayout({
          name: nameToUse,
          document: preview.document,
          is_default: false,
        });

        // Hydrate imported workspace immediately
        const report = hydrateChartWorkspace(created.document, {
          workspaceStoreInstance: workspaceStore,
          syncStoreInstance: chartSyncStore,
        });

        setCurrentLayout(created);
        setSavedSnapshot(created.document);
        setRestorationReport(report);
        await refreshLayouts();
        return created;
      } catch (err: any) {
        console.error("Failed to import layout:", err);
        setError(err.message || "Failed to import layout.");
        return null;
      }
    },
    [refreshLayouts]
  );

  // Dismiss conflict state
  const clearConflictState = useCallback(() => {
    setConflictState(null);
  }, []);

  return {
    layouts,
    currentLayout,
    savedSnapshot,
    isLoading,
    isSaving,
    error,
    conflictState,
    restorationReport,
    refreshLayouts,
    loadLayout,
    saveCurrentLayout,
    saveAsLayout,
    renameLayout,
    setDefaultLayout,
    duplicateLayout,
    deleteLayout,
    exportLayout,
    importLayout,
    clearConflictState,
  };
}
