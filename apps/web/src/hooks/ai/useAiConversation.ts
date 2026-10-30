"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  cancelGeneration,
  createConversation,
  getConversation,
  listMessages,
  regenerateMessage,
  sendMessage as sendApiMessage,
  streamAiGeneration,
} from "@/lib/ai/api";
import { AiConversation, AiMessage, RouteContext } from "@/lib/ai/types";
import { useAiOverlayStore } from "./useAiOverlay";

export function useAiConversation(initialConversationId?: string | null) {
  const { activeConversationId, setActiveConversationId } = useAiOverlayStore();
  const conversationId = initialConversationId !== undefined ? initialConversationId : activeConversationId;

  const [conversation, setConversation] = useState<AiConversation | null>(null);
  const [messages, setMessages] = useState<AiMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamingDelta, setStreamingDelta] = useState("");
  const [activeGenerationId, setActiveGenerationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  // Load conversation & messages
  const loadConversationData = useCallback(async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const [conv, msgsResp] = await Promise.all([
        getConversation(id),
        listMessages(id),
      ]);
      setConversation(conv);
      setMessages(msgsResp.items);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (conversationId) {
      loadConversationData(conversationId);
    } else {
      setConversation(null);
      setMessages([]);
    }
  }, [conversationId, loadConversationData]);

  // Clean up abort controller on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Send Message
  const sendMessage = useCallback(
    async (content: string, routeContext?: RouteContext | null) => {
      if (!content.trim() || isGenerating) return;

      setError(null);
      let targetConvId = conversationId;

      try {
        // If no active conversation, create one automatically
        let finalConvId = targetConvId;
        if (!finalConvId) {
          const newConv = await createConversation();
          finalConvId = newConv.conversation_id;
          setConversation(newConv);
          setActiveConversationId(newConv.conversation_id);
        }
        const activeId: string = finalConvId;

        const { message: userMsg, generation_id } = await sendApiMessage(
          activeId,
          content,
          routeContext
        );

        setMessages((prev) => [...prev, userMsg]);
        setIsGenerating(true);
        setActiveGenerationId(generation_id);
        setStreamingDelta("");

        // Start SSE stream
        abortControllerRef.current = streamAiGeneration(generation_id, {
          onDelta: (delta) => {
            setStreamingDelta((prev) => prev + delta);
          },
          onRunCompleted: () => {
            setIsGenerating(false);
            setActiveGenerationId(null);
            // Refresh messages from server to get clean assistant message
            listMessages(activeId).then((res) => {
              setMessages(res.items);
              setStreamingDelta("");
            });
            getConversation(activeId).then(setConversation);
          },
          onRunCancelled: () => {
            setIsGenerating(false);
            setActiveGenerationId(null);
            listMessages(activeId).then((res) => {
              setMessages(res.items);
              setStreamingDelta("");
            });
          },
          onError: (err) => {
            setIsGenerating(false);
            setActiveGenerationId(null);
            setError(err.message || "Error during AI generation");
            setStreamingDelta("");
          },
        });
      } catch (err: unknown) {
        setIsGenerating(false);
        setActiveGenerationId(null);
        setError(err instanceof Error ? err.message : String(err));
      }
    },
    [conversationId, isGenerating, setActiveConversationId]
  );

  // Stop / Cancel Generation
  const stopGeneration = useCallback(async () => {
    if (!activeGenerationId) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    try {
      await cancelGeneration(activeGenerationId);
    } catch {
      // Ignore cancel error
    } finally {
      setIsGenerating(false);
      setActiveGenerationId(null);
      if (conversationId) {
        listMessages(conversationId).then((res) => setMessages(res.items));
      }
    }
  }, [activeGenerationId, conversationId]);

  // Regenerate Response
  const regenerate = useCallback(
    async (targetMessageId?: string) => {
      if (!conversationId || isGenerating) return;

      setError(null);
      setIsGenerating(true);
      setStreamingDelta("");

      try {
        const { generation_id } = await regenerateMessage(conversationId, targetMessageId);
        setActiveGenerationId(generation_id);

        abortControllerRef.current = streamAiGeneration(generation_id, {
          onDelta: (delta) => {
            setStreamingDelta((prev) => prev + delta);
          },
          onRunCompleted: () => {
            setIsGenerating(false);
            setActiveGenerationId(null);
            listMessages(conversationId).then((res) => {
              setMessages(res.items);
              setStreamingDelta("");
            });
          },
          onRunCancelled: () => {
            setIsGenerating(false);
            setActiveGenerationId(null);
            listMessages(conversationId).then((res) => {
              setMessages(res.items);
              setStreamingDelta("");
            });
          },
          onError: (err) => {
            setIsGenerating(false);
            setActiveGenerationId(null);
            setError(err.message || "Error during AI regeneration");
            setStreamingDelta("");
          },
        });
      } catch (err: unknown) {
        setIsGenerating(false);
        setActiveGenerationId(null);
        setError(err instanceof Error ? err.message : String(err));
      }
    },
    [conversationId, isGenerating]
  );

  return {
    conversation,
    messages,
    isLoading,
    isGenerating,
    streamingDelta,
    error,
    sendMessage,
    stopGeneration,
    regenerate,
    refreshConversation: () => conversationId && loadConversationData(conversationId),
  };
}
