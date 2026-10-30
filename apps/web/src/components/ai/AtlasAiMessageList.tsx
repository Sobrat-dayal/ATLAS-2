"use client";

import { useEffect, useRef } from "react";
import { AiMessage } from "@/lib/ai/types";
import { AtlasAiAssistantMessage } from "./AtlasAiAssistantMessage";
import { AtlasAiEmptyState } from "./AtlasAiEmptyState";
import { AtlasAiUserMessage } from "./AtlasAiUserMessage";

interface AtlasAiMessageListProps {
  messages: AiMessage[];
  isGenerating: boolean;
  streamingDelta: string;
  onSelectPrompt: (prompt: string) => void;
  onRegenerateMessage?: (messageId: string) => void;
}

export function AtlasAiMessageList({
  messages,
  isGenerating,
  streamingDelta,
  onSelectPrompt,
  onRegenerateMessage,
}: AtlasAiMessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingDelta, isGenerating]);

  if (messages.length === 0 && !isGenerating) {
    return <AtlasAiEmptyState onSelectPrompt={onSelectPrompt} />;
  }

  return (
    <div className="flex-1 overflow-y-auto py-3 space-y-1">
      {messages.map((msg) => {
        if (msg.role === "user") {
          return <AtlasAiUserMessage key={msg.message_id} message={msg} />;
        }
        return (
          <AtlasAiAssistantMessage
            key={msg.message_id}
            message={msg}
            onRegenerate={() => onRegenerateMessage?.(msg.message_id)}
          />
        );
      })}

      {/* Real-time Streaming assistant message placeholder */}
      {isGenerating && (
        <AtlasAiAssistantMessage
          contentOverride={streamingDelta}
          isStreaming={true}
        />
      )}

      <div ref={bottomRef} className="h-1" />
    </div>
  );
}

