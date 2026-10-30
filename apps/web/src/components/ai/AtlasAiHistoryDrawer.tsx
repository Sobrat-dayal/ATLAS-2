"use client";

import { MessageSquare, Pin, Plus, Search, Trash2, X } from "lucide-react";
import { useAiHistory } from "@/hooks/ai/useAiHistory";
import { useAiOverlayStore } from "@/hooks/ai/useAiOverlay";

export function AtlasAiHistoryDrawer() {
  const {
    conversations,
    isLoading,
    searchQuery,
    setSearchQuery,
    startNewChat,
    togglePin,
    deleteConversation,
  } = useAiHistory();

  const {
    activeConversationId,
    setActiveConversationId,
    setHistoryDrawerOpen,
  } = useAiOverlayStore();

  const pinned = conversations.filter((c) => c.is_pinned);
  const recent = conversations.filter((c) => !c.is_pinned);

  const handleSelect = (id: string) => {
    setActiveConversationId(id);
    setHistoryDrawerOpen(false);
  };

  return (
    <div className="absolute inset-0 z-20 flex flex-col bg-atlas-surface-1/95 backdrop-blur-sm border-r border-atlas-border-default">
      {/* Header */}
      <div className="flex h-12 items-center justify-between border-b border-atlas-border-default px-3 shrink-0">
        <span className="text-xs font-semibold text-atlas-text-primary">
          Conversations ({conversations.length})
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => startNewChat()}
            className="flex items-center gap-1 rounded bg-atlas-surface-2 hover:bg-atlas-surface-hover px-2 py-1 text-xs text-atlas-text-primary transition-colors border border-atlas-border-default"
          >
            <Plus className="h-3 w-3" />
            <span>New Chat</span>
          </button>
          <button
            onClick={() => setHistoryDrawerOpen(false)}
            className="rounded p-1 text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors ml-1"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="p-3 border-b border-atlas-border-default/60 shrink-0">
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-2 h-3.5 w-3.5 text-atlas-text-muted" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search conversations..."
            className="h-7 w-full rounded border border-atlas-border-default bg-atlas-surface-2 pl-8 pr-3 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-accent focus:outline-none"
          />
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-3">
        {isLoading && (
          <div className="py-6 text-center text-xs text-atlas-text-muted">
            Loading history...
          </div>
        )}

        {!isLoading && conversations.length === 0 && (
          <div className="py-6 text-center text-xs text-atlas-text-muted">
            No conversations found.
          </div>
        )}

        {/* Pinned Section */}
        {pinned.length > 0 && (
          <div>
            <div className="px-2 py-1 text-[10px] font-semibold tracking-wider text-atlas-text-muted uppercase">
              Pinned
            </div>
            <div className="space-y-1">
              {pinned.map((c) => (
                <div
                  key={c.conversation_id}
                  onClick={() => handleSelect(c.conversation_id)}
                  className={`group flex items-center justify-between rounded px-2.5 py-1.5 text-xs cursor-pointer transition-colors ${
                    activeConversationId === c.conversation_id
                      ? "bg-atlas-surface-selected text-atlas-accent font-medium border border-atlas-accent/30"
                      : "text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                  }`}
                >
                  <div className="flex items-center gap-2 truncate min-w-0">
                    <Pin className="h-3 w-3 shrink-0 text-atlas-accent fill-current" />
                    <span className="truncate">{c.title}</span>
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        togglePin(c.conversation_id, true);
                      }}
                      className="p-1 hover:text-atlas-accent"
                      title="Unpin"
                    >
                      <Pin className="h-3 w-3" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteConversation(c.conversation_id);
                      }}
                      className="p-1 hover:text-rose-400"
                      title="Delete"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Section */}
        {recent.length > 0 && (
          <div>
            <div className="px-2 py-1 text-[10px] font-semibold tracking-wider text-atlas-text-muted uppercase">
              Recent
            </div>
            <div className="space-y-1">
              {recent.map((c) => (
                <div
                  key={c.conversation_id}
                  onClick={() => handleSelect(c.conversation_id)}
                  className={`group flex items-center justify-between rounded px-2.5 py-1.5 text-xs cursor-pointer transition-colors ${
                    activeConversationId === c.conversation_id
                      ? "bg-atlas-surface-selected text-atlas-accent font-medium border border-atlas-accent/30"
                      : "text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                  }`}
                >
                  <div className="flex items-center gap-2 truncate min-w-0">
                    <MessageSquare className="h-3 w-3 shrink-0 text-atlas-text-muted" />
                    <span className="truncate">{c.title}</span>
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        togglePin(c.conversation_id, false);
                      }}
                      className="p-1 hover:text-atlas-accent"
                      title="Pin to top"
                    >
                      <Pin className="h-3 w-3" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteConversation(c.conversation_id);
                      }}
                      className="p-1 hover:text-rose-400"
                      title="Delete"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

