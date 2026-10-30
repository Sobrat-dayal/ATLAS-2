"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createWorkspace,
  deleteWorkspace,
  duplicateWorkspace,
  listTemplates,
  listWorkspaces,
  restoreWorkspace,
  setDefaultWorkspace,
  updateWorkspace,
} from "@/lib/workspaces/api";
import { Workspace, WorkspaceSortOption, WorkspaceTemplate } from "@/lib/workspaces/types";

export function useWorkspaces() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [templates, setTemplates] = useState<WorkspaceTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<WorkspaceSortOption>("RECENTLY_OPENED");
  const [activeTab, setActiveTab] = useState<"ALL" | "FAVORITES" | "RECENT" | "TEMPLATES">("ALL");

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [wsList, tmplList] = await Promise.all([
        listWorkspaces(sortBy),
        listTemplates(),
      ]);
      setWorkspaces(wsList);
      setTemplates(tmplList);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load workspaces");
    } finally {
      setIsLoading(false);
    }
  }, [sortBy]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleCreate = async (name: string, description?: string, templateId?: string) => {
    try {
      const created = await createWorkspace({
        name,
        description,
        template_id: templateId,
      });
      await refresh();
      return created;
    } catch (err: unknown) {
      throw err;
    }
  };

  const handleDuplicate = async (workspaceId: string, newName?: string) => {
    try {
      const dup = await duplicateWorkspace(workspaceId, newName);
      await refresh();
      return dup;
    } catch (err: unknown) {
      throw err;
    }
  };

  const handleDelete = async (workspaceId: string) => {
    try {
      await deleteWorkspace(workspaceId);
      await refresh();
    } catch (err: unknown) {
      throw err;
    }
  };

  const handleToggleFavorite = async (ws: Workspace) => {
    try {
      await updateWorkspace(ws.workspace_id, { is_favorite: !ws.is_favorite });
      await refresh();
    } catch (err: unknown) {
      throw err;
    }
  };

  const handleSetDefault = async (workspaceId: string) => {
    try {
      await setDefaultWorkspace(workspaceId);
      await refresh();
    } catch (err: unknown) {
      throw err;
    }
  };

  // Filtered desks
  const filteredWorkspaces = workspaces.filter((ws) => {
    const matchesSearch =
      ws.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (ws.description && ws.description.toLowerCase().includes(searchQuery.toLowerCase()));

    if (!matchesSearch) return false;

    if (activeTab === "FAVORITES") {
      return ws.is_favorite;
    }
    if (activeTab === "RECENT") {
      return true; // already sorted
    }
    return true;
  });

  return {
    workspaces: filteredWorkspaces,
    allWorkspaces: workspaces,
    templates,
    isLoading,
    error,
    searchQuery,
    setSearchQuery,
    sortBy,
    setSortBy,
    activeTab,
    setActiveTab,
    refresh,
    handleCreate,
    handleDuplicate,
    handleDelete,
    handleToggleFavorite,
    handleSetDefault,
  };
}

