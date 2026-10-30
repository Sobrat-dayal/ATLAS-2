"use client";

import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { useAiConversation } from "@/hooks/ai/useAiConversation";
import { useAiOverlayStore } from "@/hooks/ai/useAiOverlay";
import { getRouteContext } from "@/lib/ai/routeRegistry";
import { AtlasAiComposer } from "./AtlasAiComposer";
import { AtlasAiHeader } from "./AtlasAiHeader";
import { AtlasAiHistoryDrawer } from "./AtlasAiHistoryDrawer";
import { AtlasAiMessageList } from "./AtlasAiMessageList";
import { AtlasAiRouteContextBanner } from "./AtlasAiRouteContextBanner";

export function AtlasAiOverlay() {
  const {
    isOpen,
    overlayWidth,
    setOverlayWidth,
    isHistoryDrawerOpen,
    setActiveConversationId,
  } = useAiOverlayStore();

  const pathname = usePathname();
  const routeContext = getRouteContext(pathname);

  const {
    conversation,
    messages,
    isLoading,
    isGenerating,
    streamingDelta,
    error,
    sendMessage,
    stopGeneration,
    regenerate,
    refreshConversation,
  } = useAiConversation();

  const [isResizing, setIsResizing] = useState(false);
  const resizeStartXRef = useRef(0);
  const resizeStartWidthRef = useRef(overlayWidth);

  // Drag handle resizing
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      // Moving left increases width, moving right decreases width (since panel is on right)
      const deltaX = resizeStartXRef.current - e.clientX;
      setOverlayWidth(resizeStartWidthRef.current + deltaX);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    }
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing, setOverlayWidth]);

  const handleStartResize = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    resizeStartXRef.current = e.clientX;
    resizeStartWidthRef.current = overlayWidth;
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
  };

  const handleSend = (text: string) => {
    sendMessage(text, routeContext);
  };

  if (!isOpen) return null;

  return (
    <div
      style={{ width: `${overlayWidth}px` }}
      className="fixed bottom-0 right-0 top-11 z-40 flex flex-col border-l border-atlas-border-default bg-atlas-bg-0 shadow-2xl transition-[width] duration-75 max-w-full"
    >
      {/* Resizable Left Edge Handle */}
      <div
        onMouseDown={handleStartResize}
        className="absolute -left-1 top-0 bottom-0 w-2 cursor-ew-resize hover:bg-atlas-accent/40 active:bg-atlas-accent transition-colors z-50 select-none"
        title="Drag to resize overlay"
      />

      {/* Header */}
      <AtlasAiHeader
        conversation={conversation}
        onNewChat={handleNewChat}
        onRefresh={refreshConversation}
      />

      {/* Route Context Awareness Banner */}
      <AtlasAiRouteContextBanner />

      {/* Body Area */}
      <div className="relative flex flex-1 flex-col overflow-hidden bg-atlas-bg-0">
        {/* History Drawer overlay */}
        {isHistoryDrawerOpen && <AtlasAiHistoryDrawer />}

        {/* Error Banner if any */}
        {error && (
          <div className="bg-rose-500/10 border-b border-rose-500/30 px-3 py-1.5 text-xs text-rose-400">
            {error}
          </div>
        )}

        {/* Message list */}
        <AtlasAiMessageList
          messages={messages}
          isGenerating={isGenerating}
          streamingDelta={streamingDelta}
          onSelectPrompt={handleSend}
          onRegenerateMessage={(msgId) => regenerate(msgId)}
        />
      </div>

      {/* Input Composer */}
      <AtlasAiComposer
        onSendMessage={handleSend}
        onStopGeneration={stopGeneration}
        isGenerating={isGenerating}
        disabled={isLoading}
      />
    </div>
  );
}

