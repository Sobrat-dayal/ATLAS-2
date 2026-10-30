"use client";

import { useCallback, useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { fetchContextPreview } from "@/lib/ai/context/api";
import {
  AiContextEnvelope,
  AiContextPreviewRequest,
  ContextItem,
  ContextMode,
} from "@/lib/ai/context/types";
import { useAiContextPreferences } from "./useAiContextPreferences";

export interface ContextReferenceItem {
  type: string;
  target_id: string;
  is_pinned?: boolean;
  parameters?: Record<string, unknown>;
}

export function useAiContext() {
  const pathname = usePathname() || "/home";
  const { preferences, setContextMode, refreshPreferences } = useAiContextPreferences();

  const [previewEnvelope, setPreviewEnvelope] = useState<AiContextEnvelope | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);

  // Dynamic references requested by current active view or "Ask AI About This"
  const [requestedReferences, setRequestedReferences] = useState<ContextReferenceItem[]>([]);
  const [manualExcludedIds, setManualExcludedIds] = useState<string[]>([]);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);
  const [focusedPanelId, setFocusedPanelId] = useState<string | null>(null);
  const [globalLinkChannelId, setGlobalLinkChannelId] = useState<string | null>(null);

  // Infer module name from pathname
  const activeModule = pathname.split("/")[1] || "home";

  // Refresh context preview
  const refreshPreview = useCallback(async () => {
    setLoadingPreview(true);
    setPreviewError(null);
    try {
      const payload: AiContextPreviewRequest = {
        current_route: pathname,
        active_module: activeModule,
        workspace_id: activeWorkspaceId || undefined,
        focused_panel_id: focusedPanelId || undefined,
        global_link_channel_id: globalLinkChannelId || undefined,
        context_mode_override: preferences?.context_mode,
        requested_references: requestedReferences,
      };

      const envelope = await fetchContextPreview(payload);
      setPreviewEnvelope(envelope);
    } catch (err: unknown) {
      setPreviewError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoadingPreview(false);
    }
  }, [
    pathname,
    activeModule,
    activeWorkspaceId,
    focusedPanelId,
    globalLinkChannelId,
    preferences?.context_mode,
    requestedReferences,
  ]);

  // Trigger preview update on changes
  useEffect(() => {
    refreshPreview();
  }, [refreshPreview]);

  // Listen to global "Ask AI About This" event
  useEffect(() => {
    const handleAskAi = (e: Event) => {
      const customEvent = e as CustomEvent<{
        type: string;
        targetId: string;
        parameters?: Record<string, unknown>;
      }>;
      if (customEvent.detail && customEvent.detail.type && customEvent.detail.targetId) {
        setRequestedReferences((prev) => {
          const exists = prev.some(
            (r) =>
              r.type === customEvent.detail.type && r.target_id === customEvent.detail.targetId
          );
          if (exists) return prev;
          return [
            ...prev,
            {
              type: customEvent.detail.type,
              target_id: customEvent.detail.targetId,
              is_pinned: true,
              parameters: customEvent.detail.parameters,
            },
          ];
        });
      }
    };

    window.addEventListener("atlas:ask-ai-context", handleAskAi);
    return () => {
      window.removeEventListener("atlas:ask-ai-context", handleAskAi);
    };
  }, []);

  // Pin a reference
  const pinReference = useCallback(
    (type: string, targetId: string) => {
      setRequestedReferences((prev) => {
        const exists = prev.some((r) => r.type === type && r.target_id === targetId);
        if (exists) {
          return prev.map((r) =>
            r.type === type && r.target_id === targetId ? { ...r, is_pinned: true } : r
          );
        }
        return [...prev, { type, target_id: targetId, is_pinned: true }];
      });
    },
    []
  );

  // Unpin a reference
  const unpinReference = useCallback((type: string, targetId: string) => {
    setRequestedReferences((prev) =>
      prev.filter((r) => !(r.type === type && r.target_id === targetId && r.is_pinned))
    );
  }, []);

  // Exclude a target ID
  const excludeTargetId = useCallback((targetId: string) => {
    setManualExcludedIds((prev) => (prev.includes(targetId) ? prev : [...prev, targetId]));
    setRequestedReferences((prev) => prev.filter((r) => r.target_id !== targetId));
  }, []);

  // Re-include target ID
  const includeTargetId = useCallback((targetId: string) => {
    setManualExcludedIds((prev) => prev.filter((id) => id !== targetId));
  }, []);

  // Set explicit workspace/panel context
  const setWorkspaceScope = useCallback((wsId: string | null, panelId: string | null) => {
    setActiveWorkspaceId(wsId);
    setFocusedPanelId(panelId);
  }, []);

  const setLinkChannelScope = useCallback((channelId: string | null) => {
    setGlobalLinkChannelId(channelId);
  }, []);

  // Build the enriched context object to pass into sendMessage
  const getContextPayload = useCallback(() => {
    return {
      current_route: pathname,
      active_module: activeModule,
      workspace_id: activeWorkspaceId,
      focused_panel_id: focusedPanelId,
      global_link_channel_id: globalLinkChannelId,
      context_mode: preferences?.context_mode || "FOCUSED",
      requested_references: requestedReferences,
    };
  }, [
    pathname,
    activeModule,
    activeWorkspaceId,
    focusedPanelId,
    globalLinkChannelId,
    preferences?.context_mode,
    requestedReferences,
  ]);

  return {
    pathname,
    activeModule,
    preferences,
    contextMode: preferences?.context_mode || ("FOCUSED" as ContextMode),
    setContextMode,
    previewEnvelope,
    loadingPreview,
    previewError,
    refreshPreview,
    refreshPreferences,
    isInspectorOpen,
    setIsInspectorOpen,
    toggleInspector: () => setIsInspectorOpen((prev) => !prev),
    requestedReferences,
    setRequestedReferences,
    manualExcludedIds,
    pinReference,
    unpinReference,
    excludeTargetId,
    includeTargetId,
    setWorkspaceScope,
    setLinkChannelScope,
    getContextPayload,
  };
}
