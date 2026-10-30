"use client";

import { useSavedTerminal } from "@/hooks/saved/useSavedTerminal";
import { SavedBulkToolbar } from "./SavedBulkToolbar";
import { SavedCollectionDialog } from "./SavedCollectionDialog";
import { SavedCollectionSidebar } from "./SavedCollectionSidebar";
import { SavedDeleteConfirmDialog } from "./SavedDeleteConfirmDialog";
import { SavedFilterBar } from "./SavedFilterBar";
import { SavedHeader } from "./SavedHeader";
import { SavedItemCardGrid } from "./SavedItemCardGrid";
import { SavedItemInspector } from "./SavedItemInspector";
import { SavedItemTable } from "./SavedItemTable";

export function SavedTerminalWorkspace() {
  const terminal = useSavedTerminal();

  return (
    <div className="flex h-full flex-col bg-atlas-surface-0 overflow-hidden">
      {/* Top Header */}
      <div className="px-4 pt-3 pb-1">
        <SavedHeader
          summary={terminal.summary}
          isLoading={terminal.isLoading}
          onRefresh={terminal.refresh}
          onCreateCollection={() => terminal.setIsCreateCollectionOpen(true)}
        />
      </div>

      {/* Main Terminal Body */}
      <div className="flex-1 flex overflow-hidden border-t border-atlas-border-default">
        {/* Left Sidebar: Collections, Tabs, Tags */}
        <div className="w-56 shrink-0 h-full border-r border-atlas-border-default">
          <SavedCollectionSidebar
            activeTab={terminal.activeTab}
            onSelectTab={terminal.setActiveTab}
            collections={terminal.collections}
            collectionTree={terminal.collectionTree}
            selectedCollectionId={terminal.selectedCollectionId}
            onSelectCollection={terminal.setSelectedCollectionId}
            tags={terminal.tags}
            selectedTag={terminal.selectedTag}
            onSelectTag={terminal.setSelectedTag}
            onCreateCollection={() => terminal.setIsCreateCollectionOpen(true)}
            onEditCollection={(col) => terminal.setEditingCollection(col)}
            onDeleteCollection={(cid) => terminal.onDeleteCollectionConfirm(cid)}
          />
        </div>

        {/* Center Workspace: Filter bar, Bulk toolbar, Items view */}
        <div className="flex-1 flex flex-col h-full min-w-0 overflow-hidden bg-atlas-surface-0">
          <SavedFilterBar
            searchQuery={terminal.searchQuery}
            onSearchChange={terminal.setSearchQuery}
            selectedTargetType={terminal.selectedTargetType}
            onSelectTargetType={terminal.setSelectedTargetType}
            selectedModule={terminal.selectedModule}
            onSelectModule={terminal.setSelectedModule}
            sortBy={terminal.sortBy}
            onSortChange={terminal.setSortBy}
            viewMode={terminal.viewMode}
            onViewModeChange={terminal.setViewMode}
            totalCount={terminal.totalCount}
          />

          <SavedBulkToolbar
            selectedCount={terminal.selectedItemIds.length}
            collections={terminal.collections}
            onBulkAction={terminal.onBulkAction}
            onClearSelection={terminal.clearSelection}
          />

          {terminal.error && (
            <div className="p-2 bg-rose-500/10 border-b border-rose-500/20 text-rose-400 text-xs px-4 shrink-0 flex items-center justify-between">
              <span>{terminal.error}</span>
              <button
                type="button"
                onClick={terminal.refresh}
                className="underline hover:text-rose-300 ml-2"
              >
                Retry
              </button>
            </div>
          )}

          {terminal.viewMode === "table" ? (
            <SavedItemTable
              items={terminal.items}
              selectedItemIds={terminal.selectedItemIds}
              inspectedItemId={terminal.inspectedItem?.saved_item_id}
              onSelectItem={terminal.toggleSelectItem}
              onSelectAll={terminal.selectAllItems}
              onInspectItem={(item) => terminal.setInspectedItem(item)}
              onToggleFavorite={terminal.onToggleFavorite}
              onTogglePin={terminal.onTogglePin}
              onDeleteItem={(item) => {
                terminal.setItemToDelete(item);
                terminal.setIsDeleteConfirmOpen(true);
              }}
            />
          ) : (
            <SavedItemCardGrid
              items={terminal.items}
              selectedItemIds={terminal.selectedItemIds}
              inspectedItemId={terminal.inspectedItem?.saved_item_id}
              onSelectItem={terminal.toggleSelectItem}
              onInspectItem={(item) => terminal.setInspectedItem(item)}
              onToggleFavorite={terminal.onToggleFavorite}
              onTogglePin={terminal.onTogglePin}
              onDeleteItem={(item) => {
                terminal.setItemToDelete(item);
                terminal.setIsDeleteConfirmOpen(true);
              }}
            />
          )}
        </div>

        {/* Right Inspector Drawer / Panel */}
        {terminal.inspectedItem && (
          <div className="w-80 shrink-0 h-full">
            <SavedItemInspector
              item={terminal.inspectedItem}
              collections={terminal.collections}
              onClose={() => terminal.setInspectedItem(null)}
              onToggleFavorite={terminal.onToggleFavorite}
              onTogglePin={terminal.onTogglePin}
              onUpdateNote={terminal.onUpdateNote}
              onAssignTag={terminal.onAssignTag}
              onRemoveTag={terminal.onRemoveTag}
              onAddItemToCollection={terminal.onAddItemToCollection}
              onRemoveItemFromCollection={terminal.onRemoveItemFromCollection}
              onDeleteItem={(item) => {
                terminal.setItemToDelete(item);
                terminal.setIsDeleteConfirmOpen(true);
              }}
            />
          </div>
        )}
      </div>

      {/* Modals */}
      <SavedCollectionDialog
        isOpen={terminal.isCreateCollectionOpen || !!terminal.editingCollection}
        collection={terminal.editingCollection}
        allCollections={terminal.collections}
        onClose={() => {
          terminal.setIsCreateCollectionOpen(false);
          terminal.setEditingCollection(null);
        }}
        onSubmit={async (data) => {
          if (terminal.editingCollection) {
            await terminal.onUpdateCollectionSubmit(terminal.editingCollection.collection_id, data);
          } else {
            await terminal.onCreateCollectionSubmit(data);
          }
        }}
      />

      <SavedDeleteConfirmDialog
        isOpen={terminal.isDeleteConfirmOpen}
        item={terminal.itemToDelete}
        bulkCount={terminal.selectedItemIds.length}
        onClose={() => {
          terminal.setIsDeleteConfirmOpen(false);
          terminal.setItemToDelete(null);
        }}
        onConfirm={terminal.onConfirmDeleteItem}
      />
    </div>
  );
}

