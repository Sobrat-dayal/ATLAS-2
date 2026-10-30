"use client";

import { User } from "lucide-react";
import { AiMessage } from "@/lib/ai/types";

interface AtlasAiUserMessageProps {
  message: AiMessage;
}

export function AtlasAiUserMessage({ message }: AtlasAiUserMessageProps) {
  const timeStr = message.created_at
    ? new Date(message.created_at).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  return (
    <div className="flex justify-end gap-2 px-3 py-2">
      <div className="max-w-[85%] rounded-lg bg-atlas-surface-selected border border-atlas-accent/20 px-3.5 py-2.5 text-xs text-atlas-text-primary shadow-sm">
        {message.route_context && (
          <div className="mb-1 text-[10px] text-atlas-accent font-mono">
            {message.route_context.module_name} ({message.route_context.route})
          </div>
        )}
        <div className="whitespace-pre-wrap leading-relaxed select-text font-normal">
          {message.content}
        </div>
        <div className="mt-1 text-right text-[10px] text-atlas-text-muted">
          {timeStr}
        </div>
      </div>
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-atlas-surface-2 border border-atlas-border-default text-atlas-text-secondary">
        <User className="h-3.5 w-3.5" />
      </div>
    </div>
  );
}

