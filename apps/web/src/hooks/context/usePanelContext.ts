"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useGlobalContext } from "./useGlobalContext";
import { getPanelCapability } from "@/lib/context/capabilityRegistry";
import { globalEventBus } from "@/lib/context/eventBus";
import { transformEntityLocal } from "@/lib/context/transformations";
import {
  ContextDimension,
  ContextSelectionEvent,
  LinkChannel,
  LinkingStatus,
  TransformationType,
} from "@/lib/context/types";

export interface UsePanelContextProps {
  panelInstanceId: string;
  panelTypeId: string;
  linkGroupId?: string | null;
  independentMode?: boolean;
  initialLocalContext?: Record<string, unknown>;
}

export function usePanelContext({
  panelInstanceId,
  panelTypeId,
  linkGroupId,
  independentMode = false,
  initialLocalContext = {},
}: UsePanelContextProps) {
  const { channels, publishSelection } = useGlobalContext();

  const isIndependent = independentMode || !linkGroupId;
  const channel: LinkChannel | undefined = useMemo(() => {
    if (isIndependent) return undefined;
    return channels.find((c) => c.channel_id === linkGroupId);
  }, [channels, isIndependent, linkGroupId]);

  // Dimension overrides (per-dimension link control)
  // e.g. { TIMEFRAME: "INDEPENDENT" } allows chart to stay 1D while following INSTRUMENT
  const [dimensionOverrides, setDimensionOverrides] = useState<
    Partial<Record<ContextDimension, "FOLLOW" | "INDEPENDENT">>
  >({});

  // Local state for panel context
  const [panelContext, setPanelContext] = useState<Record<string, unknown>>(() => {
    if (channel) {
      return { ...channel.context_snapshot, ...initialLocalContext };
    }
    return initialLocalContext;
  });

  const [status, setStatus] = useState<LinkingStatus>(
    isIndependent ? "INDEPENDENT" : "LINKED"
  );
  const currentRevisionRef = useRef<number>(channel?.revision || 1);

  // Sync state if channel context snapshot updates
  useEffect(() => {
    if (!channel || isIndependent) {
      setStatus("INDEPENDENT");
      return;
    }

    setStatus("LINKED");
    setPanelContext((prev) => {
      const next = { ...prev };
      for (const [k, v] of Object.entries(channel.context_snapshot)) {
        const dim = k as ContextDimension;
        if (dimensionOverrides[dim] === "INDEPENDENT") {
          continue; // preserve independent local dimension
        }
        next[k] = v;
      }
      return next;
    });
  }, [channel, isIndependent, dimensionOverrides]);

  // Subscribe to inbound events from the Event Bus
  useEffect(() => {
    if (isIndependent || !linkGroupId) return;

    const cap = getPanelCapability(panelTypeId);
    const inboundDims: ContextDimension[] = cap
      ? cap.subscribable_dimensions
      : ["INSTRUMENT", "COMPANY"];

    const unsubscribe = globalEventBus.subscribe(
      linkGroupId,
      panelInstanceId,
      inboundDims,
      (event: ContextSelectionEvent) => {
        // 1. Revision ordering check
        if (event.context_revision < currentRevisionRef.current) {
          return; // Drop stale out-of-order event
        }
        currentRevisionRef.current = event.context_revision;

        // 2. Check per-dimension override
        if (dimensionOverrides[event.dimension] === "INDEPENDENT") {
          return; // Dimension is configured to remain local
        }

        setStatus("UPDATING");

        // 3. Transformation check
        let resolvedValue: unknown = event.canonical_target_id;
        const requiredTrans = cap?.required_transformations?.[event.dimension];

        if (requiredTrans) {
          const transResult = transformEntityLocal(
            event.canonical_target_id,
            `${event.dimension}_TO_${requiredTrans}` as TransformationType
          );
          if (transResult) {
            resolvedValue = transResult.canonical_name || transResult.symbol || transResult.entity_id;
          }
        }

        // 4. Apply updates locally
        setPanelContext((prev) => ({
          ...prev,
          [event.dimension]: resolvedValue,
          ...(event.payload || {}),
        }));

        setTimeout(() => {
          setStatus("UPDATED");
        }, 150);
      }
    );

    return () => {
      unsubscribe();
    };
  }, [dimensionOverrides, isIndependent, linkGroupId, panelInstanceId, panelTypeId]);

  // Publish user selection from this panel
  const selectEntity = useCallback(
    (dimension: ContextDimension, targetId: string, payload?: Record<string, unknown>) => {
      // Always update local state immediately
      setPanelContext((prev) => ({
        ...prev,
        [dimension]: targetId,
        ...(payload || {}),
      }));

      // If linked, publish to the channel
      if (!isIndependent && linkGroupId) {
        publishSelection({
          channelId: linkGroupId,
          dimension,
          canonicalTargetId: targetId,
          originPanelInstanceId: panelInstanceId,
          payload,
        });
      }
    },
    [isIndependent, linkGroupId, panelInstanceId, publishSelection]
  );

  const setDimensionMode = useCallback(
    (dimension: ContextDimension, mode: "FOLLOW" | "INDEPENDENT") => {
      setDimensionOverrides((prev) => ({ ...prev, [dimension]: mode }));
    },
    []
  );

  return {
    channel,
    channelColor: channel?.display_color_token || "#64748B",
    status,
    context: panelContext,
    isIndependent,
    dimensionOverrides,
    selectEntity,
    setDimensionMode,
  };
}
