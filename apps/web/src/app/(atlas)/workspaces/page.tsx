"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { RefreshCw } from "lucide-react";
import { GlobalContextProvider } from "@/components/context/GlobalContextProvider";
import { WorkspaceDesktop } from "@/components/workspaces/WorkspaceDesktop";
import { WorkspaceHome } from "@/components/workspaces/WorkspaceHome";
import { useWorkspaces } from "@/hooks/workspaces/useWorkspaces";

function WorkspacesContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialId = searchParams.get("id");

  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(initialId);

  const {
    workspaces,
    allWorkspaces,
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
  } = useWorkspaces();

  // Sync state if URL search param changes
  useEffect(() => {
    const idFromUrl = searchParams.get("id");
    if (idFromUrl !== activeWorkspaceId) {
      setActiveWorkspaceId(idFromUrl);
    }
  }, [searchParams]);

  const handleOpenWorkspace = (workspaceId: string) => {
    setActiveWorkspaceId(workspaceId);
    router.push(`/workspaces?id=${workspaceId}`);
  };

  const handleBackToGallery = () => {
    setActiveWorkspaceId(null);
    router.push("/workspaces");
    refresh();
  };

  if (activeWorkspaceId) {
    return (
      <GlobalContextProvider workspaceId={activeWorkspaceId}>
        <WorkspaceDesktop
          workspaceId={activeWorkspaceId}
          allWorkspaces={allWorkspaces}
          onSwitchWorkspace={handleOpenWorkspace}
          onBackToGallery={handleBackToGallery}
        />
      </GlobalContextProvider>
    );
  }

  return (
    <WorkspaceHome
      workspaces={workspaces}
      allWorkspaces={allWorkspaces}
      templates={templates}
      isLoading={isLoading}
      error={error}
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
      sortBy={sortBy}
      setSortBy={setSortBy}
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      onOpenWorkspace={handleOpenWorkspace}
      onCreateWorkspace={handleCreate}
      onDuplicateWorkspace={handleDuplicate}
      onDeleteWorkspace={handleDelete}
      onToggleFavorite={handleToggleFavorite}
      onSetDefault={handleSetDefault}
      onRefresh={refresh}
    />
  );
}

export default function WorkspacesPage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center justify-center h-full bg-atlas-surface-0 font-mono text-xs text-atlas-text-muted">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-500 mb-2" />
          <span>Loading ATLAS Workspaces Engine...</span>
        </div>
      }
    >
      <WorkspacesContent />
    </Suspense>
  );
}
