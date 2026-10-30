"use client";

import { useEffect, useState } from "react";
import {
  ChevronDown,
  History,
  Minus,
  Plus,
  Sparkles,
  Wrench,
  X,
} from "lucide-react";
import { listModels, updateConversation } from "@/lib/ai/api";
import { AiConversation, ModelCapability } from "@/lib/ai/types";
import { useAiOverlayStore } from "@/hooks/ai/useAiOverlay";

interface AtlasAiHeaderProps {
  conversation: AiConversation | null;
  onNewChat: () => void;
  onRefresh?: () => void;
  onToggleToolSettings?: () => void;
}

export function AtlasAiHeader({
  conversation,
  onNewChat,
  onRefresh,
  onToggleToolSettings,
}: AtlasAiHeaderProps) {
  const { closeOverlay, isHistoryDrawerOpen, toggleHistoryDrawer } = useAiOverlayStore();

  const [models, setModels] = useState<ModelCapability[]>([]);
  const [selectedModelId, setSelectedModelId] = useState(
    conversation?.model_id || "atlas-intelligence-v1"
  );
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [titleInput, setTitleInput] = useState(conversation?.title || "New Chat");

  useEffect(() => {
    listModels().then((resp) => setModels(resp.models)).catch(() => {});
  }, []);

  useEffect(() => {
    if (conversation) {
      setTitleInput(conversation.title);
      setSelectedModelId(conversation.model_id);
    } else {
      setTitleInput("New Chat");
    }
  }, [conversation]);

  const handleSaveTitle = async () => {
    setIsEditingTitle(false);
    if (!conversation || !titleInput.trim() || titleInput === conversation.title) return;
    try {
      await updateConversation(conversation.conversation_id, { title: titleInput.trim() });
      onRefresh?.();
    } catch {
      // Revert title on error
      setTitleInput(conversation.title);
    }
  };

  const handleSelectModel = async (modelId: string) => {
    setSelectedModelId(modelId);
    if (conversation && modelId !== conversation.model_id) {
      try {
        await updateConversation(conversation.conversation_id, { model_id: modelId });
        onRefresh?.();
      } catch {
        // Handle error
      }
    }
  };

  return (
    <div className="flex h-12 shrink-0 items-center justify-between border-b border-atlas-border-default bg-atlas-surface-1 px-3">
      {/* Left controls: History toggle & Title */}
      <div className="flex items-center gap-2 overflow-hidden mr-2">
        <button
          onClick={toggleHistoryDrawer}
          className={`rounded p-1 text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors ${
            isHistoryDrawerOpen ? "bg-atlas-surface-selected text-atlas-accent" : ""
          }`}
          title="Toggle Chat History"
        >
          <History className="h-4 w-4" />
        </button>

        <button
          onClick={onNewChat}
          className="rounded p-1 text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
          title="Start New Conversation"
        >
          <Plus className="h-4 w-4" />
        </button>

        {isEditingTitle ? (
          <input
            type="text"
            value={titleInput}
            onChange={(e) => setTitleInput(e.target.value)}
            onBlur={handleSaveTitle}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSaveTitle();
              if (e.key === "Escape") {
                setIsEditingTitle(false);
                setTitleInput(conversation?.title || "New Chat");
              }
            }}
            autoFocus
            className="h-6 w-36 rounded bg-atlas-surface-2 px-1.5 text-xs text-atlas-text-primary border border-atlas-accent focus:outline-none"
          />
        ) : (
          <span
            onClick={() => conversation && setIsEditingTitle(true)}
            className="truncate text-xs font-semibold text-atlas-text-primary hover:text-atlas-accent cursor-pointer max-w-[140px] sm:max-w-[180px]"
            title={conversation?.title || "Click to rename"}
          >
            {conversation?.title || "New Chat"}
          </span>
        )}
      </div>

      {/* Right controls: Model selector & Close */}
      <div className="flex items-center gap-1.5">
        <div className="relative">
          <select
            value={selectedModelId}
            onChange={(e) => handleSelectModel(e.target.value)}
            className="h-7 cursor-pointer appearance-none rounded border border-atlas-border-default bg-atlas-surface-2 pl-2 pr-6 text-[11px] font-medium text-atlas-text-primary hover:bg-atlas-surface-hover focus:outline-none focus:border-atlas-accent"
          >
            {models.length > 0 ? (
              models.map((m) => (
                <option key={m.model_id} value={m.model_id}>
                  {m.name}
                </option>
              ))
            ) : (
              <option value="atlas-intelligence-v1">ATLAS Intelligence v1</option>
            )}
          </select>
          <ChevronDown className="pointer-events-none absolute right-1.5 top-2 h-3 w-3 text-atlas-text-muted" />
        </div>

        {onToggleToolSettings && (
          <button
            onClick={onToggleToolSettings}
            className="rounded p-1 text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
            title="Configure AI Tools & Permissions (Stage 126)"
          >
            <Wrench className="h-3.5 w-3.5" />
          </button>
        )}

        <button
          onClick={closeOverlay}
          className="rounded p-1 text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors ml-1"
          title="Close AI Assistant (Ctrl+Alt+A)"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

