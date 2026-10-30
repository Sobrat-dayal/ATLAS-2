"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import {
  createChannel as apiCreateChannel,
  deleteChannel as apiDeleteChannel,
  listChannels as apiListChannels,
  updateChannel as apiUpdateChannel,
  updateChannelState as apiUpdateChannelState,
} from "@/lib/context/api";
import { globalEventBus } from "@/lib/context/eventBus";
import {
  ContextDimension,
  ContextScope,
  ContextSelectionEvent,
  LinkChannel,
  SubscriptionMode,
} from "@/lib/context/types";

export interface GlobalContextValue {
  channels: LinkChannel[];
  activeChannelId: string;
  activeChannel: LinkChannel | undefined;
  isLoading: boolean;
  error: string | null;
  isLinkManagerOpen: boolean;
  setIsLinkManagerOpen: (open: boolean) => void;
  setActiveChannelId: (id: string) => void;
  refreshChannels: (workspaceId?: string) => Promise<void>;
  createChannel: (
    name: string,
    color?: string,
    workspaceId?: string,
    scope?: ContextScope,
    initialContext?: Record<string, unknown>
  ) => Promise<LinkChannel>;
  updateChannel: (
    channelId: string,
    data: { name?: string; display_color_token?: string; scope?: ContextScope }
  ) => Promise<LinkChannel>;
  deleteChannel: (channelId: string) => Promise<void>;
  publishSelection: (params: {
    channelId: string;
    dimension: ContextDimension;
    canonicalTargetId: string;
    targetType?: string;
    originPanelInstanceId?: string;
    payload?: Record<string, unknown>;
  }) => void;
}

const GlobalContext = createContext<GlobalContextValue | null>(null);

// Built-in canonical fallback channels if API is starting up
const DEFAULT_FALLBACK_CHANNELS: LinkChannel[] = [
  {
    channel_id: "chan_default_a",
    owner_user_id: "usr_default_trader",
    name: "Channel A (Blue)",
    display_color_token: "#3B82F6",
    scope: "USER_APPLICATION",
    enabled: true,
    supported_dimensions: [
      "INSTRUMENT",
      "COMPANY",
      "PORTFOLIO",
      "DATE_RANGE",
      "TIMEFRAME",
      "REPORTING_CURRENCY",
    ],
    context_snapshot: { INSTRUMENT: "AAPL", TIMEFRAME: "1D", REPORTING_CURRENCY: "USD" },
    revision: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    channel_id: "chan_default_b",
    owner_user_id: "usr_default_trader",
    name: "Channel B (Green)",
    display_color_token: "#10B981",
    scope: "USER_APPLICATION",
    enabled: true,
    supported_dimensions: [
      "INSTRUMENT",
      "COMPANY",
      "ECONOMIC_SERIES",
      "DATE_RANGE",
      "TIMEFRAME",
    ],
    context_snapshot: { ECONOMIC_SERIES: "CPI", TIMEFRAME: "1M", REPORTING_CURRENCY: "USD" },
    revision: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    channel_id: "chan_default_c",
    owner_user_id: "usr_default_trader",
    name: "Channel C (Amber)",
    display_color_token: "#F59E0B",
    scope: "WORKSPACE",
    enabled: true,
    supported_dimensions: ["INSTRUMENT", "TIMEFRAME"],
    context_snapshot: { INSTRUMENT: "NVDA", TIMEFRAME: "15m" },
    revision: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

export function GlobalContextProvider({
  children,
  workspaceId,
}: {
  children: React.ReactNode;
  workspaceId?: string;
}) {
  const [channels, setChannels] = useState<LinkChannel[]>(DEFAULT_FALLBACK_CHANNELS);
  const [activeChannelId, setActiveChannelId] = useState<string>("chan_default_a");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isLinkManagerOpen, setIsLinkManagerOpen] = useState<boolean>(false);

  const refreshChannels = useCallback(
    async (wsId?: string) => {
      setIsLoading(true);
      setError(null);
      try {
        const fetched = await apiListChannels(wsId || workspaceId);
        if (fetched && fetched.length > 0) {
          setChannels(fetched);
          if (!fetched.some((c) => c.channel_id === activeChannelId)) {
            setActiveChannelId(fetched[0].channel_id);
          }
          // Seed channel revisions in event bus
          for (const c of fetched) {
            globalEventBus.setChannelRevision(c.channel_id, c.revision);
          }
        }
      } catch {
        // Keep fallback channels
      } finally {
        setIsLoading(false);
      }
    },
    [activeChannelId, workspaceId]
  );

  useEffect(() => {
    refreshChannels();
  }, [refreshChannels]);

  const activeChannel = channels.find((c) => c.channel_id === activeChannelId) || channels[0];

  const handleCreateChannel = async (
    name: string,
    color?: string,
    wsId?: string,
    scope?: ContextScope,
    initialContext?: Record<string, unknown>
  ): Promise<LinkChannel> => {
    try {
      const created = await apiCreateChannel({
        name,
        display_color_token: color || "#3B82F6",
        workspace_id: wsId || workspaceId,
        scope: scope || "WORKSPACE",
        initial_context: initialContext,
      });
      setChannels((prev) => [...prev, created]);
      setActiveChannelId(created.channel_id);
      globalEventBus.setChannelRevision(created.channel_id, created.revision);
      return created;
    } catch {
      // Local fallback creation
      const localChan: LinkChannel = {
        channel_id: `chan_${Math.random().toString(36).substring(2, 9)}`,
        owner_user_id: "usr_local",
        name,
        display_color_token: color || "#3B82F6",
        workspace_id: wsId || workspaceId,
        scope: scope || "WORKSPACE",
        enabled: true,
        supported_dimensions: [
          "INSTRUMENT",
          "COMPANY",
          "PORTFOLIO",
          "DATE_RANGE",
          "TIMEFRAME",
          "REPORTING_CURRENCY",
        ],
        context_snapshot: initialContext || {},
        revision: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setChannels((prev) => [...prev, localChan]);
      setActiveChannelId(localChan.channel_id);
      globalEventBus.setChannelRevision(localChan.channel_id, 1);
      return localChan;
    }
  };

  const handleUpdateChannel = async (
    channelId: string,
    data: { name?: string; display_color_token?: string; scope?: ContextScope }
  ): Promise<LinkChannel> => {
    try {
      const updated = await apiUpdateChannel(channelId, data);
      setChannels((prev) => prev.map((c) => (c.channel_id === channelId ? updated : c)));
      return updated;
    } catch {
      setChannels((prev) =>
        prev.map((c) => (c.channel_id === channelId ? { ...c, ...data } : c))
      );
      return channels.find((c) => c.channel_id === channelId)!;
    }
  };

  const handleDeleteChannel = async (channelId: string): Promise<void> => {
    try {
      await apiDeleteChannel(channelId);
    } catch {
      // ignore
    }
    setChannels((prev) => prev.filter((c) => c.channel_id !== channelId));
    if (activeChannelId === channelId) {
      const remaining = channels.filter((c) => c.channel_id !== channelId);
      if (remaining.length > 0) {
        setActiveChannelId(remaining[0].channel_id);
      }
    }
  };

  const publishSelection = useCallback(
    (params: {
      channelId: string;
      dimension: ContextDimension;
      canonicalTargetId: string;
      targetType?: string;
      originPanelInstanceId?: string;
      payload?: Record<string, unknown>;
    }) => {
      const targetChan = channels.find((c) => c.channel_id === params.channelId);
      const nextRev = (targetChan?.revision || globalEventBus.getChannelRevision(params.channelId)) + 1;

      const event: ContextSelectionEvent = {
        event_id: `evt_${Math.random().toString(36).substring(2, 11)}`,
        origin_panel_instance_id: params.originPanelInstanceId,
        channel_id: params.channelId,
        scope: targetChan?.scope || "WORKSPACE",
        dimension: params.dimension,
        canonical_target_id: params.canonicalTargetId,
        target_type: params.targetType || params.dimension,
        payload: params.payload || {},
        context_revision: nextRev,
        emitted_at: new Date().toISOString(),
        selection_reason: "USER_CLICK",
      };

      // 1. Dispatch locally and across tabs via eventBus
      globalEventBus.publish(event);

      // 2. Optimistically update local channel context state
      const updates: Record<string, unknown> = {
        [params.dimension]: params.canonicalTargetId,
        ...(params.payload || {}),
      };

      setChannels((prev) =>
        prev.map((c) =>
          c.channel_id === params.channelId
            ? {
                ...c,
                context_snapshot: { ...c.context_snapshot, ...updates },
                revision: nextRev,
                updated_at: new Date().toISOString(),
              }
            : c
        )
      );

      // 3. Persist to backend asynchronously
      apiUpdateChannelState(params.channelId, updates, targetChan?.revision).catch(() => {
        // Silent catch for ephemeral local navigation
      });
    },
    [channels]
  );

  return (
    <GlobalContext.Provider
      value={{
        channels,
        activeChannelId,
        activeChannel,
        isLoading,
        error,
        isLinkManagerOpen,
        setIsLinkManagerOpen,
        setActiveChannelId,
        refreshChannels,
        createChannel: handleCreateChannel,
        updateChannel: handleUpdateChannel,
        deleteChannel: handleDeleteChannel,
        publishSelection,
      }}
    >
      {children}
    </GlobalContext.Provider>
  );
}

export function useGlobalContext(): GlobalContextValue {
  const ctx = useContext(GlobalContext);
  if (!ctx) {
    throw new Error("useGlobalContext must be used within a GlobalContextProvider");
  }
  return ctx;
}
