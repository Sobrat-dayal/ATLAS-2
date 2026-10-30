"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createConversation,
  deleteConversation as deleteApiConversation,
  listConversations,
  updateConversation,
} from "@/lib/ai/api";
import { AiConversation } from "@/lib/ai/types";
import { useAiOverlayStore } from "./useAiOverlay";

export function useAiHistory() {
  const [conversations, setConversations] = useState<AiConversation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { setActiveConversationId, setHistoryDrawerOpen } = useAiOverlayStore();

  const loadHistory = useCallback(async (search?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await listConversations(search, false, 50, 0);
      setConversations(resp.items);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHistory(searchQuery);
  }, [loadHistory, searchQuery]);

  const startNewChat = useCallback(
    async (modelId?: string) => {
      try {
        const newConv = await createConversation("New Conversation", modelId);
        setConversations((prev) => [newConv, ...prev]);
        setActiveConversationId(newConv.conversation_id);
        setHistoryDrawerOpen(false);
        return newConv;
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : String(err));
        return null;
      }
    },
    [setActiveConversationId, setHistoryDrawerOpen]
  );

  const renameConversation = useCallback(
    async (id: string, newTitle: string) => {
      try {
        const updated = await updateConversation(id, { title: newTitle });
        setConversations((prev) =>
          prev.map((c) => (c.conversation_id === id ? updated : c))
        );
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : String(err));
      }
    },
    []
  );

  const togglePin = useCallback(async (id: string, currentPinned: boolean) => {
    try {
      const updated = await updateConversation(id, { is_pinned: !currentPinned });
      setConversations((prev) =>
        prev.map((c) => (c.conversation_id === id ? updated : c))
      );
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, []);

  const deleteConversation = useCallback(
    async (id: string) => {
      try {
        await deleteApiConversation(id);
        setConversations((prev) => prev.filter((c) => c.conversation_id !== id));
        const { activeConversationId } = useAiOverlayStore.getState();
        if (activeConversationId === id) {
          setActiveConversationId(null);
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : String(err));
      }
    },
    [setActiveConversationId]
  );

  return {
    conversations,
    isLoading,
    searchQuery,
    setSearchQuery,
    error,
    refreshHistory: () => loadHistory(searchQuery),
    startNewChat,
    renameConversation,
    togglePin,
    deleteConversation,
  };
}

