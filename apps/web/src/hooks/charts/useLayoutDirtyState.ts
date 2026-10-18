"use client";

/**
 * Hook for detecting unsaved configuration changes in the current chart workspace (Stage 74).
 *
 * Implements:
 * - Subscribes to workspaceStore state updates
 * - Subscribes to drawing and synchronization changes
 * - Evaluates deterministic canonical dirty-state comparison
 * - Excludes transient updates (quote updates, live ticks, hover states, crosshair moves)
 */

import { useEffect, useState } from "react";
import {
  isWorkspaceDirty,
  SavedChartLayoutDocumentV1,
  serializeChartWorkspace,
  workspaceStore,
  chartSyncStore,
} from "@/lib/charts";

export function useLayoutDirtyState(savedSnapshot: SavedChartLayoutDocumentV1 | null) {
  const [isDirty, setIsDirty] = useState<boolean>(false);

  useEffect(() => {
    if (!savedSnapshot) {
      setIsDirty(false);
      return;
    }

    const checkDirty = () => {
      try {
        const workingDoc = serializeChartWorkspace(workspaceStore.getState(), {
          syncStore: chartSyncStore,
        });
        const dirty = isWorkspaceDirty(savedSnapshot, workingDoc);
        setIsDirty(dirty);
      } catch (err) {
        console.warn("Failed to check workspace dirty state:", err);
      }
    };

    // Initial check
    checkDirty();

    // Subscribe to workspace store changes
    const unsubWorkspace = workspaceStore.subscribe(() => {
      checkDirty();
    });

    // Subscribe to sync store changes
    const unsubSync = chartSyncStore.subscribe(() => {
      checkDirty();
    });

    return () => {
      unsubWorkspace();
      unsubSync();
    };
  }, [savedSnapshot]);

  return { isDirty };
}
