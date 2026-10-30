"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp, Square } from "lucide-react";

interface AtlasAiComposerProps {
  onSendMessage: (content: string) => void;
  onStopGeneration: () => void;
  isGenerating: boolean;
  disabled?: boolean;
}

export function AtlasAiComposer({
  onSendMessage,
  onStopGeneration,
  isGenerating,
  disabled = false,
}: AtlasAiComposerProps) {
  const [content, setContent] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const maxChars = 16000;
  const isOverLimit = content.length > maxChars;

  // Auto-grow textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        160,
        Math.max(40, textareaRef.current.scrollHeight)
      )}px`;
    }
  }, [content]);

  const handleSend = () => {
    if (!content.trim() || isGenerating || isOverLimit || disabled) return;
    onSendMessage(content.trim());
    setContent("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "40px";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-atlas-border-default bg-atlas-surface-1 p-3 shrink-0">
      <div className="relative rounded-lg border border-atlas-border-default bg-atlas-surface-2 focus-within:border-atlas-accent focus-within:ring-1 focus-within:ring-atlas-accent/30 transition-all">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask ATLAS AI about markets, formulas, risk, or platform navigation..."
          disabled={disabled}
          rows={1}
          className="w-full resize-none bg-transparent px-3 py-2.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
        />

        <div className="flex items-center justify-between px-2.5 pb-2 pt-1 border-t border-atlas-border-default/20">
          <div className="flex items-center gap-2 text-[10px] text-atlas-text-muted">
            <span className={isOverLimit ? "text-rose-400 font-semibold" : ""}>
              {content.length > 500 ? `${content.length.toLocaleString()} / ${maxChars.toLocaleString()}` : ""}
            </span>
            <span className="hidden sm:inline">Enter ↵ to send • Shift+Enter for newline</span>
          </div>

          <div>
            {isGenerating ? (
              <button
                onClick={onStopGeneration}
                className="flex items-center gap-1 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40 px-2 py-1 text-xs font-medium hover:bg-rose-500/30 transition-colors"
                title="Stop Generation"
              >
                <Square className="h-3 w-3 fill-current" />
                <span className="text-[11px]">Stop</span>
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!content.trim() || isOverLimit || disabled}
                className="flex h-7 w-7 items-center justify-center rounded bg-atlas-accent text-white shadow-sm disabled:opacity-40 disabled:cursor-not-allowed hover:bg-atlas-accent/90 transition-all"
                title="Send Message"
              >
                <ArrowUp className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="mt-1.5 text-center text-[10px] text-atlas-text-muted select-none">
        ATLAS AI V1 provides institutional financial intelligence. Live trading & autonomous execution deferred to future stages.
      </div>
    </div>
  );
}

