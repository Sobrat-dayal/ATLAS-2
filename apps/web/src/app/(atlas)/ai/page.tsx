"use client";

import { useEffect, useState } from "react";
import { ATLAS_MODULES } from "@/config/atlas-modules";
import {
  AtlasInspector,
  AtlasPanel,
  AtlasResizeHandle,
  AtlasSplit,
  PageHeader,
} from "@/design-system";
import {
  AtlasAiComposer,
  AtlasAiMessageList,
} from "@/components/ai";
import { useAiConversation } from "@/hooks/ai/useAiConversation";
import { useAiHistory } from "@/hooks/ai/useAiHistory";
import { useAiOverlayStore } from "@/hooks/ai/useAiOverlay";
import { listModels } from "@/lib/ai/api";
import { getRouteContext } from "@/lib/ai/routeRegistry";
import { ModelCapability } from "@/lib/ai/types";
import {
  Bot,
  Cpu,
  Layers,
  MessageSquare,
  Pin,
  Plus,
  Search,
  ShieldAlert,
  Trash2,
} from "lucide-react";

export default function AIPage() {
  const { activeConversationId, setActiveConversationId } = useAiOverlayStore();
  const {
    conversations,
    searchQuery,
    setSearchQuery,
    startNewChat,
    togglePin,
    deleteConversation,
    refreshHistory,
  } = useAiHistory();

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
  } = useAiConversation(activeConversationId);

  const [models, setModels] = useState<ModelCapability[]>([]);
  const routeContext = getRouteContext("/ai");

  useEffect(() => {
    listModels().then((res) => setModels(res.models)).catch(() => {});
  }, []);

  const handleSelectConv = (id: string) => {
    setActiveConversationId(id);
  };

  const handleStartNew = async () => {
    const newConv = await startNewChat();
    if (newConv) {
      setActiveConversationId(newConv.conversation_id);
    }
  };

  const handleSend = (content: string) => {
    sendMessage(content, routeContext);
    refreshHistory();
  };

  const activeModel = models.find((m) => m.model_id === conversation?.model_id) || models[0];

  return (
    <div className="flex h-full flex-col bg-atlas-bg-0">
      {/* Page Header */}
      <div className="px-4 py-3 shrink-0 border-b border-atlas-border-default bg-atlas-surface-1">
        <PageHeader
          title={ATLAS_MODULES.ai.label}
          description={ATLAS_MODULES.ai.description}
          className="mb-0 pb-0 border-b-0"
        />
      </div>

      {/* Tri-Pane Split View */}
      <div className="flex-1 overflow-hidden">
        <AtlasSplit id="layout.ai" direction="horizontal" defaultLayout={[22, 54, 24]}>
          {/* Panel 1: Conversation History */}
          <AtlasPanel id="ai.history" minSize={16} defaultSize={22}>
            <div className="h-full bg-atlas-surface-1 border-r border-atlas-border-default flex flex-col">
              <div className="p-3 border-b border-atlas-border-default flex items-center justify-between">
                <span className="text-xs font-semibold text-atlas-text-primary">
                  Conversations ({conversations.length})
                </span>
                <button
                  onClick={handleStartNew}
                  className="flex items-center gap-1 rounded bg-atlas-surface-2 hover:bg-atlas-surface-hover px-2 py-1 text-xs text-atlas-text-primary border border-atlas-border-default transition-colors"
                  title="New Conversation"
                >
                  <Plus className="h-3 w-3 text-atlas-accent" />
                  <span>New</span>
                </button>
              </div>

              {/* Search */}
              <div className="p-2.5 border-b border-atlas-border-default/60">
                <div className="relative">
                  <Search className="pointer-events-none absolute left-2.5 top-2 h-3.5 w-3.5 text-atlas-text-muted" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search chats..."
                    className="h-7 w-full rounded border border-atlas-border-default bg-atlas-surface-2 pl-8 pr-2.5 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted focus:border-atlas-accent focus:outline-none"
                  />
                </div>
              </div>

              {/* Conversation items */}
              <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {conversations.length === 0 && (
                  <div className="py-8 text-center text-xs text-atlas-text-muted">
                    No conversations yet.
                  </div>
                )}

                {conversations.map((c) => (
                  <div
                    key={c.conversation_id}
                    onClick={() => handleSelectConv(c.conversation_id)}
                    className={`group flex items-center justify-between rounded px-2.5 py-2 text-xs cursor-pointer transition-colors ${
                      activeConversationId === c.conversation_id
                        ? "bg-atlas-surface-selected text-atlas-accent font-medium border border-atlas-accent/30"
                        : "text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate min-w-0">
                      {c.is_pinned ? (
                        <Pin className="h-3 w-3 shrink-0 text-atlas-accent fill-current" />
                      ) : (
                        <MessageSquare className="h-3 w-3 shrink-0 text-atlas-text-muted" />
                      )}
                      <span className="truncate">{c.title}</span>
                    </div>

                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          togglePin(c.conversation_id, c.is_pinned);
                        }}
                        className="p-1 hover:text-atlas-accent"
                        title={c.is_pinned ? "Unpin" : "Pin"}
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
          </AtlasPanel>

          <AtlasResizeHandle />

          {/* Panel 2: Main AI Conversation Canvas */}
          <AtlasPanel id="ai.workspace" minSize={40} defaultSize={54} className="flex flex-col bg-atlas-bg-0">
            {error && (
              <div className="bg-rose-500/10 border-b border-rose-500/30 px-4 py-2 text-xs text-rose-400">
                {error}
              </div>
            )}

            <AtlasAiMessageList
              messages={messages}
              isGenerating={isGenerating}
              streamingDelta={streamingDelta}
              onSelectPrompt={handleSend}
              onRegenerateMessage={(msgId) => regenerate(msgId)}
            />

            <AtlasAiComposer
              onSendMessage={handleSend}
              onStopGeneration={stopGeneration}
              isGenerating={isGenerating}
              disabled={isLoading}
            />
          </AtlasPanel>

          <AtlasResizeHandle />

          {/* Panel 3: AI Intelligence Inspector */}
          <AtlasInspector
            id="ai.context"
            title="Intelligence Inspector"
            minSize={18}
            maxSize={35}
            defaultSize={24}
          >
            <div className="p-3 space-y-4 text-xs">
              {/* Active Model Spec */}
              <div className="rounded border border-atlas-border-default bg-atlas-surface-2 p-3 space-y-2">
                <div className="flex items-center gap-1.5 font-semibold text-atlas-text-primary">
                  <Cpu className="h-3.5 w-3.5 text-atlas-accent" />
                  <span>Model Engine</span>
                </div>
                <div className="text-[11px] space-y-1 text-atlas-text-secondary">
                  <div className="flex justify-between">
                    <span className="text-atlas-text-muted">Model ID:</span>
                    <span className="font-mono">{activeModel?.model_id || "atlas-intelligence-v1"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-atlas-text-muted">Context Window:</span>
                    <span>{activeModel?.context_window?.toLocaleString() || "32,768"} tokens</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-atlas-text-muted">Streaming:</span>
                    <span className="text-emerald-400">Enabled (SSE)</span>
                  </div>
                </div>
              </div>

              {/* Session Metrics */}
              {conversation && (
                <div className="rounded border border-atlas-border-default bg-atlas-surface-2 p-3 space-y-2">
                  <div className="flex items-center gap-1.5 font-semibold text-atlas-text-primary">
                    <Layers className="h-3.5 w-3.5 text-atlas-accent" />
                    <span>Session Telemetry</span>
                  </div>
                  <div className="text-[11px] space-y-1 text-atlas-text-secondary">
                    <div className="flex justify-between">
                      <span className="text-atlas-text-muted">Messages:</span>
                      <span>{messages.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-atlas-text-muted">Total Tokens:</span>
                      <span>{conversation.total_tokens?.toLocaleString() || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-atlas-text-muted">Active Route:</span>
                      <span className="font-mono text-atlas-accent">/ai</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Governance & Boundary Notices */}
              <div className="rounded border border-amber-500/20 bg-amber-500/5 p-3 space-y-1.5">
                <div className="flex items-center gap-1.5 font-semibold text-amber-400">
                  <ShieldAlert className="h-3.5 w-3.5" />
                  <span>Stage 124 Governance</span>
                </div>
                <p className="text-[11px] text-atlas-text-secondary leading-relaxed">
                  The AI Assistant provides quantitative reasoning and navigation. Live order routing and autonomous terminal execution are restricted until subsequent roadmap stages.
                </p>
              </div>
            </div>
          </AtlasInspector>
        </AtlasSplit>
      </div>
    </div>
  );
}
