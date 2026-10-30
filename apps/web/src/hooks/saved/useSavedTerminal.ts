"use client";

import { useCallback, useEffect, useState } from "react";
import {
  addItemsToCollection,
  assignTagToItem,
  createCollection,
  deleteCollection,
  deleteSavedItem,
  executeBulkAction,
  getCollectionTree,
  getLibrarySummary,
  listCollections,
  listSavedItems,
  listTags,
  removeItemFromCollection,
  removeTagFromItem,
  restoreSavedItem,
  saveItem,
  toggleFavorite,
  togglePin,
  updateCollection,
  updateSavedItem,
} from "@/lib/saved/api";
import {
  CreateSavedCollectionRequest,
  CreateSavedItemRequest,
  SavedBulkActionType,
  SavedCollection,
  SavedCollectionTree,
  SavedItem,
  SavedLibrarySummary,
  SavedSortOption,
  SavedTag,
  SavedTargetType,
} from "@/lib/saved/types";

export type SavedWorkspaceTab = "all" | "favorites" | "recent" | "collections" | "tags";

export function useSavedTerminal() {
  const [items, setItems] = useState<SavedItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [summary, setSummary] = useState<SavedLibrarySummary | null>(null);
  const [collections, setCollections] = useState<SavedCollection[]>([]);
  const [collectionTree, setCollectionTree] = useState<SavedCollectionTree[]>([]);
  const [tags, setTags] = useState<SavedTag[]>([]);

  // Navigation & filters
  const [activeTab, setActiveTab] = useState<SavedWorkspaceTab>("all");
  const [selectedCollectionId, setSelectedCollectionId] = useState<string | null>(null);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [selectedTargetType, setSelectedTargetType] = useState<SavedTargetType | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<SavedSortOption>("RECENTLY_SAVED");
  const [viewMode, setViewMode] = useState<"table" | "cards">("table");

  // Selection & Details
  const [selectedItemIds, setSelectedItemIds] = useState<string[]>([]);
  const [inspectedItem, setInspectedItem] = useState<SavedItem | null>(null);

  // Modals
  const [isCreateCollectionOpen, setIsCreateCollectionOpen] = useState(false);
  const [editingCollection, setEditingCollection] = useState<SavedCollection | null>(null);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<SavedItem | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load auxiliary metadata (Summary, Collections, Tags)
  const refreshAuxiliary = useCallback(async () => {
    try {
      const [sumData, colsData, treeData, tagsData] = await Promise.all([
        getLibrarySummary().catch(() => null),
        listCollections().catch(() => []),
        getCollectionTree().catch(() => []),
        listTags().catch(() => []),
      ]);
      if (sumData) setSummary(sumData);
      setCollections(colsData);
      setCollectionTree(treeData);
      setTags(tagsData);
    } catch (err: unknown) {
      console.error("Failed loading saved metadata", err);
    }
  }, []);

  // Fetch Items
  const fetchItems = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      let favoriteParam: boolean | undefined = undefined;
      if (activeTab === "favorites") {
        favoriteParam = true;
      }

      const sortParam = activeTab === "recent" ? "RECENTLY_SAVED" : sortBy;

      const res = await listSavedItems({
        search: searchQuery.trim() || undefined,
        target_type: selectedTargetType || undefined,
        target_module: selectedModule || undefined,
        collection_id: selectedCollectionId || undefined,
        tag: selectedTag || undefined,
        favorite: favoriteParam,
        sort_by: sortParam,
        page: 1,
        page_size: 100,
      });

      setItems(res.items);
      setTotalCount(res.total_count);

      // Keep inspected item in sync
      if (inspectedItem) {
        const found = res.items.find((i) => i.saved_item_id === inspectedItem.saved_item_id);
        if (found) setInspectedItem(found);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed loading saved items.");
    } finally {
      setIsLoading(false);
    }
  }, [
    activeTab,
    sortBy,
    searchQuery,
    selectedTargetType,
    selectedModule,
    selectedCollectionId,
    selectedTag,
    inspectedItem,
  ]);

  useEffect(() => {
    refreshAuxiliary();
  }, [refreshAuxiliary]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  // Bulk Selection
  const toggleSelectItem = (id: string) => {
    setSelectedItemIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const selectAllItems = () => {
    if (selectedItemIds.length === items.length) {
      setSelectedItemIds([]);
    } else {
      setSelectedItemIds(items.map((i) => i.saved_item_id));
    }
  };

  const clearSelection = () => {
    setSelectedItemIds([]);
  };

  // Actions on Items
  const onToggleFavorite = async (item: SavedItem) => {
    try {
      const nextFav = !item.favorite;
      // Optimistic update
      setItems((prev) =>
        prev.map((i) => (i.saved_item_id === item.saved_item_id ? { ...i, favorite: nextFav } : i))
      );
      if (inspectedItem?.saved_item_id === item.saved_item_id) {
        setInspectedItem((prev) => (prev ? { ...prev, favorite: nextFav } : null));
      }
      await toggleFavorite(item.saved_item_id, nextFav);
      refreshAuxiliary();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Favorite toggle failed.");
      fetchItems();
    }
  };

  const onTogglePin = async (item: SavedItem) => {
    try {
      const nextPin = !item.pinned;
      // Optimistic update
      setItems((prev) =>
        prev.map((i) => (i.saved_item_id === item.saved_item_id ? { ...i, pinned: nextPin } : i))
      );
      if (inspectedItem?.saved_item_id === item.saved_item_id) {
        setInspectedItem((prev) => (prev ? { ...prev, pinned: nextPin } : null));
      }
      await togglePin(item.saved_item_id, nextPin);
      fetchItems();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Pin toggle failed.");
      fetchItems();
    }
  };

  const onSaveNewItem = async (req: CreateSavedItemRequest) => {
    try {
      const created = await saveItem(req);
      await Promise.all([fetchItems(), refreshAuxiliary()]);
      setInspectedItem(created);
      return created;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save item.";
      setError(msg);
      throw err;
    }
  };

  const onUpdateNote = async (saved_item_id: string, note: string) => {
    try {
      const updated = await updateSavedItem(saved_item_id, { user_note: note });
      setItems((prev) =>
        prev.map((i) => (i.saved_item_id === saved_item_id ? updated : i))
      );
      if (inspectedItem?.saved_item_id === saved_item_id) {
        setInspectedItem(updated);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to update note.");
    }
  };

  const onAssignTag = async (saved_item_id: string, tagName: string) => {
    try {
      await assignTagToItem(saved_item_id, tagName);
      await Promise.all([fetchItems(), refreshAuxiliary()]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to assign tag.");
    }
  };

  const onRemoveTag = async (saved_item_id: string, tagId: string) => {
    try {
      await removeTagFromItem(saved_item_id, tagId);
      await Promise.all([fetchItems(), refreshAuxiliary()]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to remove tag.");
    }
  };

  const onConfirmDeleteItem = async () => {
    if (!itemToDelete && selectedItemIds.length === 0) return;
    try {
      if (itemToDelete) {
        await deleteSavedItem(itemToDelete.saved_item_id);
      } else {
        await executeBulkAction({
          action: "DELETE",
          saved_item_ids: selectedItemIds,
        });
        clearSelection();
      }
      setItemToDelete(null);
      setIsDeleteConfirmOpen(false);
      await Promise.all([fetchItems(), refreshAuxiliary()]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed deleting item.");
    }
  };

  const onRestore = async (saved_item_id: string) => {
    try {
      await restoreSavedItem(saved_item_id);
      await Promise.all([fetchItems(), refreshAuxiliary()]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed restoring item.");
    }
  };

  // Collection Actions
  const onCreateCollectionSubmit = async (req: CreateSavedCollectionRequest) => {
    try {
      const col = await createCollection(req);
      setIsCreateCollectionOpen(false);
      await refreshAuxiliary();
      return col;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed creating collection.");
      throw err;
    }
  };

  const onUpdateCollectionSubmit = async (
    collection_id: string,
    req: { name?: string; description?: string; parent_collection_id?: string | null }
  ) => {
    try {
      await updateCollection(collection_id, req);
      setEditingCollection(null);
      await refreshAuxiliary();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed updating collection.");
      throw err;
    }
  };

  const onDeleteCollectionConfirm = async (collection_id: string) => {
    try {
      await deleteCollection(collection_id);
      if (selectedCollectionId === collection_id) {
        setSelectedCollectionId(null);
      }
      await Promise.all([fetchItems(), refreshAuxiliary()]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed deleting collection.");
    }
  };

  const onAddItemToCollection = async (collection_id: string, saved_item_id: string) => {
    try {
      await addItemsToCollection(collection_id, [saved_item_id]);
      await Promise.all([fetchItems(), refreshAuxiliary()]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed adding item to collection.");
    }
  };

  const onRemoveItemFromCollection = async (collection_id: string, saved_item_id: string) => {
    try {
      await removeItemFromCollection(collection_id, saved_item_id);
      await Promise.all([fetchItems(), refreshAuxiliary()]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed removing item from collection.");
    }
  };

  // Bulk Actions
  const onBulkAction = async (
    action: SavedBulkActionType,
    collection_id?: string,
    tag_name?: string
  ) => {
    if (selectedItemIds.length === 0) return;
    try {
      await executeBulkAction({
        action,
        saved_item_ids: selectedItemIds,
        collection_id,
        tag_name,
      });
      clearSelection();
      await Promise.all([fetchItems(), refreshAuxiliary()]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Bulk action failed.");
    }
  };

  return {
    items,
    totalCount,
    summary,
    collections,
    collectionTree,
    tags,
    activeTab,
    selectedCollectionId,
    selectedTag,
    selectedModule,
    selectedTargetType,
    searchQuery,
    sortBy,
    viewMode,
    selectedItemIds,
    inspectedItem,
    isCreateCollectionOpen,
    editingCollection,
    isDeleteConfirmOpen,
    itemToDelete,
    isLoading,
    error,
    // Setters
    setActiveTab,
    setSelectedCollectionId,
    setSelectedTag,
    setSelectedModule,
    setSelectedTargetType,
    setSearchQuery,
    setSortBy,
    setViewMode,
    setInspectedItem,
    setIsCreateCollectionOpen,
    setEditingCollection,
    setIsDeleteConfirmOpen,
    setItemToDelete,
    // Operations
    toggleSelectItem,
    selectAllItems,
    clearSelection,
    onToggleFavorite,
    onTogglePin,
    onSaveNewItem,
    onUpdateNote,
    onAssignTag,
    onRemoveTag,
    onConfirmDeleteItem,
    onRestore,
    onCreateCollectionSubmit,
    onUpdateCollectionSubmit,
    onDeleteCollectionConfirm,
    onAddItemToCollection,
    onRemoveItemFromCollection,
    onBulkAction,
    refresh: fetchItems,
  };
}

