"use client";

import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";
import {
  WatchlistSummary,
  WatchlistDetail,
  WatchlistItem,
} from "@/lib/watchlists/types";
import {
  listWatchlists,
  getWatchlist,
  createWatchlist,
  updateWatchlist,
  deleteWatchlist,
  addWatchlistItem,
  removeWatchlistItem,
  reorderWatchlistItems,
} from "@/lib/watchlists/api";
import {
  WatchlistColumnConfigV1,
} from "@/lib/watchlists/columns/types";
import {
  getDefaultColumnConfig,
} from "@/lib/watchlists/columns/registry";
import {
  getWatchlistColumnPreferences,
  updateWatchlistColumnPreferences,
  resetWatchlistColumnPreferences,
} from "@/lib/watchlists/columns/api";
import { WatchlistHeader } from "./WatchlistHeader";
import { WatchlistTable } from "./WatchlistTable";
import { WatchlistColumnManager } from "./WatchlistColumnManager";
import { WatchlistSelectedInspector } from "./WatchlistSelectedInspector";
import { WatchlistEmptyState } from "./WatchlistEmptyState";
import { WatchlistErrorState } from "./WatchlistErrorState";
import { CreateWatchlistDialog } from "./CreateWatchlistDialog";
import { RenameWatchlistDialog } from "./RenameWatchlistDialog";
import { DeleteWatchlistDialog } from "./DeleteWatchlistDialog";
import { AddInstrumentDialog } from "./AddInstrumentDialog";
import { useWatchlistLive, useWatchlistEnrichment } from "@/hooks/watchlists";
import { Loader2 } from "lucide-react";

export function WatchlistsWorkspace() {
  const [watchlists, setWatchlists] = useState<WatchlistSummary[]>([]);
  const [activeWatchlistId, setActiveWatchlistId] = useState<string | null>(null);
  const [activeWatchlist, setActiveWatchlist] = useState<WatchlistDetail | null>(null);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);

  // Live streaming state (Stage 78)
  const { liveQuotes, status: liveStatus, reconnect: reconnectLive } = useWatchlistLive(activeWatchlist);

  // Column preferences state (Stage 77)
  const [columnConfig, setColumnConfig] = useState<WatchlistColumnConfigV1>(getDefaultColumnConfig());
  const [columnRevision, setColumnRevision] = useState<number>(0);
  const [isColumnsManagerOpen, setIsColumnsManagerOpen] = useState<boolean>(false);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Enrichment state (Stage 79)
  const { enrichmentData } = useWatchlistEnrichment(activeWatchlist, columnConfig, liveQuotes);

  const [loading, setLoading] = useState<boolean>(true);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [mutationError, setMutationError] = useState<string | null>(null);

  // Modal dialog states
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isRenameOpen, setIsRenameOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [isAddOpen, setIsAddOpen] = useState(false);

  // 1. Initial load of user watchlists
  const fetchWatchlists = useCallback(async (selectId?: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await listWatchlists(1, 50);
      const items = res.items || [];
      setWatchlists(items);

      if (items.length > 0) {
        const nextId = selectId && items.some((w) => w.id === selectId)
          ? selectId
          : items[0].id;
        setActiveWatchlistId(nextId);
      } else {
        setActiveWatchlistId(null);
        setActiveWatchlist(null);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load watchlists.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- Asynchronous initial load of user watchlists
    fetchWatchlists();
  }, [fetchWatchlists]);

  // 2. Load active watchlist detail and column preferences when activeWatchlistId changes
  const fetchWatchlistDetail = useCallback(async (id: string, isRefresh: boolean = false) => {
    try {
      if (isRefresh) {
        setIsRefreshing(true);
      } else {
        setLoadingDetail(true);
      }
      setMutationError(null);

      // Concurrently fetch watchlist membership detail and column preferences
      const [detail, prefRes] = await Promise.allSettled([
        getWatchlist(id),
        getWatchlistColumnPreferences(id),
      ]);

      if (detail.status === "fulfilled") {
        setActiveWatchlist(detail.value);
        if (detail.value.items.length > 0) {
          setSelectedItemId((prev) =>
            detail.value.items.some((it) => it.id === prev) ? prev : detail.value.items[0].id
          );
        } else {
          setSelectedItemId(null);
        }
      } else {
        throw detail.reason;
      }

      if (prefRes.status === "fulfilled") {
        setColumnConfig(prefRes.value.configuration);
        setColumnRevision(prefRes.value.revision);
      } else {
        // Fall back to canonical default layout
        setColumnConfig(getDefaultColumnConfig());
        setColumnRevision(0);
      }
    } catch (err: unknown) {
      setMutationError(err instanceof Error ? err.message : "Failed to load watchlist details.");
    } finally {
      setLoadingDetail(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (activeWatchlistId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- Asynchronous watchlist detail fetch on active ID change
      fetchWatchlistDetail(activeWatchlistId);
    } else {
      setActiveWatchlist(null);
      setSelectedItemId(null);
      setColumnConfig(getDefaultColumnConfig());
    }
  }, [activeWatchlistId, fetchWatchlistDetail]);

  // Set of existing instrument entity IDs in active watchlist (for search deduplication)
  const existingInstrumentIds = useMemo(() => {
    if (!activeWatchlist) return new Set<string>();
    return new Set(activeWatchlist.items.map((i) => i.instrument_entity_id));
  }, [activeWatchlist]);

  // Selected item object for inspector enhanced with live streaming values
  const selectedItem = useMemo(() => {
    if (!activeWatchlist || !selectedItemId) return null;
    const base = activeWatchlist.items.find((i) => i.id === selectedItemId);
    if (!base) return null;
    const lq = liveQuotes.get(base.instrument_entity_id?.toLowerCase());
    if (!lq) return base;
    return {
      ...base,
      last_price: lq.last_price ?? base.last_price,
      bid_price: lq.bid_price ?? base.bid_price,
      ask_price: lq.ask_price ?? base.ask_price,
      absolute_change: lq.absolute_change ?? base.absolute_change,
      percentage_change: lq.percentage_change ?? base.percentage_change,
      change_direction: lq.change_direction ?? base.change_direction,
      freshness_status: lq.freshness_status ?? base.freshness_status,
      delivery_delay_status: lq.delivery_delay_status ?? base.delivery_delay_status,
      source_timestamp: lq.source_timestamp ?? base.source_timestamp,
      quote_measure: lq.quote_measure ?? base.quote_measure,
      provider: lq.provider ?? base.provider,
    };
  }, [activeWatchlist, selectedItemId, liveQuotes]);

  // Handler: Update Column Configuration with Debounced Persistence
  const handleUpdateColumnConfig = (newConfig: WatchlistColumnConfigV1) => {
    setColumnConfig(newConfig);

    if (!activeWatchlistId) return;

    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(async () => {
      try {
        const res = await updateWatchlistColumnPreferences(
          activeWatchlistId,
          newConfig,
          columnRevision > 0 ? columnRevision : undefined
        );
        setColumnRevision(res.revision);
      } catch (err: unknown) {
        const isConflict =
          err && typeof err === "object" && "status" in err && (err.status === 409 || err.status === 412);
        if (isConflict) {
          setMutationError(
            "Column preferences conflict: a newer configuration was saved on another session. Reloading latest preferences..."
          );
          try {
            const latest = await getWatchlistColumnPreferences(activeWatchlistId);
            setColumnConfig(latest.configuration);
            setColumnRevision(latest.revision);
          } catch {
            // keep current local state
          }
        }
      }
    }, 400); // 400ms debounce
  };

  // Handler: Reset Column Configuration to Defaults
  const handleResetColumnConfigDefaults = async () => {
    if (!activeWatchlistId) return;
    try {
      const res = await resetWatchlistColumnPreferences(activeWatchlistId);
      setColumnConfig(res.configuration);
      setColumnRevision(res.revision);
    } catch {
      setColumnConfig(getDefaultColumnConfig());
    }
  };

  // Handler: Create Watchlist
  const handleCreateWatchlist = async (data: { name: string; description?: string }) => {
    const created = await createWatchlist(data);
    await fetchWatchlists(created.id);
  };

  // Handler: Rename Watchlist
  const handleRenameWatchlist = async (data: { name: string; description?: string }) => {
    if (!activeWatchlistId || !activeWatchlist) return;
    const updated = await updateWatchlist(activeWatchlistId, data, activeWatchlist.revision);
    setWatchlists((prev) =>
      prev.map((w) => (w.id === updated.id ? { ...w, name: updated.name, description: updated.description } : w))
    );
    setActiveWatchlist((prev) =>
      prev ? { ...prev, name: updated.name, description: updated.description, revision: updated.revision } : prev
    );
  };

  // Handler: Delete Watchlist
  const handleDeleteWatchlist = async () => {
    if (!activeWatchlistId) return;
    await deleteWatchlist(activeWatchlistId);
    const remaining = watchlists.filter((w) => w.id !== activeWatchlistId);
    setWatchlists(remaining);
    if (remaining.length > 0) {
      setActiveWatchlistId(remaining[0].id);
    } else {
      setActiveWatchlistId(null);
      setActiveWatchlist(null);
    }
  };

  // Handler: Add Instrument
  const handleAddInstrument = async (data: { instrument_entity_id: string; market_series_id?: string }) => {
    if (!activeWatchlistId) return;
    const newItem = await addWatchlistItem(activeWatchlistId, data);
    setActiveWatchlist((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        items: [...prev.items, newItem],
        total_items: prev.total_items + 1,
        revision: prev.revision + 1,
      };
    });
    setWatchlists((prev) =>
      prev.map((w) => (w.id === activeWatchlistId ? { ...w, item_count: w.item_count + 1 } : w))
    );
    setSelectedItemId(newItem.id);
  };

  // Handler: Remove Instrument
  const handleRemoveInstrument = async (item: WatchlistItem) => {
    if (!activeWatchlistId) return;
    await removeWatchlistItem(activeWatchlistId, item.id);
    setActiveWatchlist((prev) => {
      if (!prev) return prev;
      const remaining = prev.items.filter((i) => i.id !== item.id).map((i, idx) => ({ ...i, position: idx }));
      return {
        ...prev,
        items: remaining,
        total_items: Math.max(0, prev.total_items - 1),
        revision: prev.revision + 1,
      };
    });
    setWatchlists((prev) =>
      prev.map((w) => (w.id === activeWatchlistId ? { ...w, item_count: Math.max(0, w.item_count - 1) } : w))
    );
    if (selectedItemId === item.id) {
      setSelectedItemId(null);
    }
  };

  // Handler: Reorder with Optimistic Update and Rollback
  const handleReorder = async (newOrderedItems: WatchlistItem[]) => {
    if (!activeWatchlistId || !activeWatchlist) return;

    const previousItems = activeWatchlist.items;
    const expectedRevision = activeWatchlist.revision;

    // 1. Optimistic local update
    const reindexed = newOrderedItems.map((item, idx) => ({ ...item, position: idx }));
    setActiveWatchlist((prev) => (prev ? { ...prev, items: reindexed } : prev));
    setMutationError(null);

    // 2. Persist to server
    try {
      const res = await reorderWatchlistItems(activeWatchlistId, {
        ordered_item_ids: reindexed.map((i) => i.id),
        expected_revision: expectedRevision,
      });

      // Update confirmed revision
      setActiveWatchlist((prev) => (prev ? { ...prev, revision: res.revision } : prev));
    } catch (err: unknown) {
      // 3. Rollback on failure
      setActiveWatchlist((prev) => (prev ? { ...prev, items: previousItems } : prev));
      setMutationError(
        err instanceof Error
          ? err.message
          : "Reorder failed due to a concurrent update. Reverting to latest server order."
      );
      // Fetch authoritative state
      fetchWatchlistDetail(activeWatchlistId, true);
    }
  };

  // Render loading state
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-zinc-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-zinc-300" />
        <span className="text-xs uppercase font-mono tracking-wider">Loading Watchlists...</span>
      </div>
    );
  }

  // Render error state
  if (error) {
    return <WatchlistErrorState message={error} onRetry={() => fetchWatchlists()} />;
  }

  // Render zero-watchlists state
  if (watchlists.length === 0) {
    return (
      <div className="p-4 sm:p-6 max-w-6xl mx-auto space-y-4">
        <WatchlistHeader
          watchlists={[]}
          activeWatchlist={null}
          activeWatchlistId={null}
          onSelectWatchlist={() => {}}
          onCreateNew={() => setIsCreateOpen(true)}
          onAddInstrument={() => {}}
          onRename={() => {}}
          onDelete={() => {}}
          onRefresh={() => {}}
        />
        <WatchlistEmptyState
          variant="no_watchlists"
          onCreateWatchlist={() => setIsCreateOpen(true)}
        />
        <CreateWatchlistDialog
          isOpen={isCreateOpen}
          onClose={() => setIsCreateOpen(false)}
          onSubmit={handleCreateWatchlist}
        />
      </div>
    );
  }

  return (
    <div className="p-3 sm:p-6 max-w-7xl mx-auto space-y-4">
      {/* Header bar */}
      <WatchlistHeader
        watchlists={watchlists}
        activeWatchlist={activeWatchlist}
        activeWatchlistId={activeWatchlistId}
        isRefreshing={isRefreshing}
        visibleColumnCount={columnConfig.visible_column_ids.length}
        activeSort={columnConfig.sort}
        connectionState={liveStatus.connection}
        dataQuality={liveStatus.dataQuality}
        activeSubscribedCount={liveStatus.activeSubscriptionsCount}
        onSelectWatchlist={(id) => setActiveWatchlistId(id)}
        onCreateNew={() => setIsCreateOpen(true)}
        onAddInstrument={() => setIsAddOpen(true)}
        onRename={() => setIsRenameOpen(true)}
        onDelete={() => setIsDeleteOpen(true)}
        onRefresh={() => {
          if (activeWatchlistId) fetchWatchlistDetail(activeWatchlistId, true);
        }}
        onReconnect={reconnectLive}
        onRefreshSort={() => {
          handleUpdateColumnConfig({ ...columnConfig });
        }}
        onOpenColumns={() => setIsColumnsManagerOpen(true)}
        onClearSort={() =>
          handleUpdateColumnConfig({
            ...columnConfig,
            sort: { column_id: null, direction: null },
          })
        }
      />

      {/* Mutation error banner */}
      {mutationError && (
        <div className="p-3 rounded bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-center justify-between">
          <span>{mutationError}</span>
          <button
            type="button"
            onClick={() => setMutationError(null)}
            className="text-red-400 hover:text-red-200 text-xs underline ml-2"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main content: Empty list or Table */}
      {loadingDetail ? (
        <div className="flex flex-col items-center justify-center min-h-[300px] text-zinc-400 gap-3">
          <Loader2 className="w-5 h-5 animate-spin text-zinc-300" />
          <span className="text-xs uppercase font-mono tracking-wider">
            Loading Watchlist Items...
          </span>
        </div>
      ) : activeWatchlist && activeWatchlist.items.length === 0 ? (
        <WatchlistEmptyState
          variant="empty_watchlist"
          watchlistName={activeWatchlist.name}
          onAddInstrument={() => setIsAddOpen(true)}
        />
      ) : activeWatchlist ? (
        <>
          <WatchlistTable
            items={activeWatchlist.items}
            liveQuotes={liveQuotes}
            enrichmentData={enrichmentData}
            config={columnConfig}
            onUpdateConfig={handleUpdateColumnConfig}
            selectedItemId={selectedItemId}
            onSelectItem={(item) => setSelectedItemId(item.id)}
            onRemoveItem={handleRemoveInstrument}
            onReorder={handleReorder}
          />

          {/* Selected Instrument Inspector */}
          <WatchlistSelectedInspector
            item={selectedItem}
            onClose={() => setSelectedItemId(null)}
          />
        </>
      ) : null}

      {/* Column Manager Dialog (Stage 77) */}
      <WatchlistColumnManager
        isOpen={isColumnsManagerOpen}
        config={columnConfig}
        onClose={() => setIsColumnsManagerOpen(false)}
        onUpdateConfig={handleUpdateColumnConfig}
        onResetDefaults={handleResetColumnConfigDefaults}
      />

      {/* Existing Dialogs */}
      <CreateWatchlistDialog
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSubmit={handleCreateWatchlist}
      />

      <RenameWatchlistDialog
        isOpen={isRenameOpen}
        currentName={activeWatchlist?.name || ""}
        currentDescription={activeWatchlist?.description || ""}
        onClose={() => setIsRenameOpen(false)}
        onSubmit={handleRenameWatchlist}
      />

      <DeleteWatchlistDialog
        isOpen={isDeleteOpen}
        watchlistName={activeWatchlist?.name || ""}
        itemCount={activeWatchlist?.total_items || 0}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={handleDeleteWatchlist}
      />

      <AddInstrumentDialog
        isOpen={isAddOpen}
        watchlistName={activeWatchlist?.name || ""}
        existingInstrumentIds={existingInstrumentIds}
        onClose={() => setIsAddOpen(false)}
        onAdd={handleAddInstrument}
      />
    </div>
  );
}
