"use client";

import React, { ReactNode } from "react";
import { useAtlasApplicationContext } from "../application-context";

export type SelectedEntityStatus = "idle" | "loading" | "ready" | "error";

export interface EntitySummary {
  entity_id: string;
  entity_type: string;
  canonical_name: string;
  display_name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  [key: string]: any;
}

export interface SelectedEntityContextValue {
  selectedEntityId: string | null;
  selectedEntity: EntitySummary | null;
  status: SelectedEntityStatus;
  error: Error | null;

  selectEntity: (entityId: string) => void;
  clearSelectedEntity: () => void;
  refreshSelectedEntity: () => Promise<void>;
}

// Kept for backward compatibility if any module still mounts it, though layout.tsx will swap it out.
export function SelectedEntityProvider({ children }: { children: ReactNode }) {
  return <>{children}</>;
}

export function useSelectedEntity(): SelectedEntityContextValue {
  const ctx = useAtlasApplicationContext();
  
  return {
    selectedEntityId: ctx.selectedEntityId,
    selectedEntity: ctx.selectedEntity,
    status: ctx.selectedEntityStatus,
    error: ctx.selectedEntityError,
    selectEntity: ctx.selectEntity,
    clearSelectedEntity: ctx.clearSelectedEntity,
    refreshSelectedEntity: ctx.refreshSelectedEntity,
  };
}
