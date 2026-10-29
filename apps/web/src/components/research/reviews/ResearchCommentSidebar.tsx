"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchCommentThreadResponse,
  CommentAnchorType,
  CreateCommentThreadRequest,
} from "@/lib/research/types";
import {
  getCommentThreadStatusDisplay,
  formatResearchDate,
} from "@/lib/research/formatting";

interface ResearchCommentSidebarProps {
  threads: ResearchCommentThreadResponse[];
  resourceType?: string;
  resourceId?: string;
  currentRevisionNumber: number;
  isLoading?: boolean;
  onAddThread: (data: CreateCommentThreadRequest) => Promise<unknown>;
  onAddReply: (threadId: string, body: string) => Promise<unknown>;
  onResolveThread: (threadId: string) => Promise<unknown>;
  onReopenThread: (threadId: string) => Promise<unknown>;
}

export function ResearchCommentSidebar({
  threads,
  resourceType,
  resourceId,
  currentRevisionNumber,
  isLoading = false,
  onAddThread,
  onAddReply,
  onResolveThread,
  onReopenThread,
}: ResearchCommentSidebarProps) {
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [anchorType, setAnchorType] = useState<CommentAnchorType>("REPORT_SECTION");
  const [anchorRef, setAnchorRef] = useState<string>("Executive Summary");
  const [anchorText, setAnchorText] = useState<string>("");
  const [newCommentBody, setNewCommentBody] = useState<string>("");
  const [replyBodies, setReplyBodies] = useState<Record<string, string>>({});
  const [expandedThreads, setExpandedThreads] = useState<Record<string, boolean>>({});

  const toggleExpand = (threadId: string) => {
    setExpandedThreads((prev) => ({
      ...prev,
      [threadId]: !(prev[threadId] ?? true),
    }));
  };

  const handleCreateThread = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCommentBody.trim() || !anchorRef.trim()) return;

    try {
      await onAddThread({
        anchor_type: anchorType,
        anchor_reference: anchorRef.trim(),
        anchor_text: anchorText.trim() || undefined,
        initial_comment: newCommentBody.trim(),
        target_revision_number: currentRevisionNumber,
      });
      setNewCommentBody("");
      setAnchorText("");
      setIsCreating(false);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendReply = async (threadId: string) => {
    const body = replyBodies[threadId];
    if (!body || !body.trim()) return;

    try {
      await onAddReply(threadId, body.trim());
      setReplyBodies((prev) => ({ ...prev, [threadId]: "" }));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-full flex-col border-l border-atlas-border-default bg-atlas-surface-0 w-80 shrink-0">
      {/* Sidebar Header */}
      <div className="flex items-center justify-between border-b border-atlas-border-default px-3 py-2.5">
        <div>
          <h4 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
            Discussion & Audit Threads
          </h4>
          <span className="text-[10px] text-atlas-text-muted">
            {threads.length} thread(s) anchored to research
          </span>
        </div>
        <Button
          variant={isCreating ? "secondary" : "primary"}
          size="xs"
          onClick={() => setIsCreating(!isCreating)}
        >
          {isCreating ? "Cancel" : "+ Comment"}
        </Button>
      </div>

      {/* New Anchored Comment Form */}
      {isCreating && (
        <form onSubmit={handleCreateThread} className="border-b border-atlas-border-default bg-atlas-surface-1 p-3 space-y-2">
          <div className="text-[11px] font-semibold text-atlas-text-primary">
            New Anchored Comment Thread
          </div>

          <div>
            <label className="block text-[10px] text-atlas-text-muted">Anchor Target:</label>
            <select
              value={anchorType}
              onChange={(e) => setAnchorType(e.target.value as CommentAnchorType)}
              className="mt-0.5 w-full rounded-xs border border-atlas-border-default bg-atlas-surface-2 p-1 text-[11px] text-atlas-text-primary"
            >
              <option value="REPORT_SECTION">Section Heading</option>
              <option value="CONTENT_BLOCK">Specific Block</option>
              <option value="CITATION">Source Citation</option>
              <option value="ANALYSIS_RUN">Analysis Run</option>
              <option value="FINDING">Analytical Finding</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-atlas-text-muted">Anchor Reference / Identifier:</label>
            <input
              type="text"
              value={anchorRef}
              onChange={(e) => setAnchorRef(e.target.value)}
              placeholder="e.g. Executive Summary or block-id"
              className="mt-0.5 w-full rounded-xs border border-atlas-border-default bg-atlas-surface-2 p-1 text-[11px] text-atlas-text-primary"
            />
          </div>

          <div>
            <label className="block text-[10px] text-atlas-text-muted">Quoted Text (Optional):</label>
            <input
              type="text"
              value={anchorText}
              onChange={(e) => setAnchorText(e.target.value)}
              placeholder="Selected report passage"
              className="mt-0.5 w-full rounded-xs border border-atlas-border-default bg-atlas-surface-2 p-1 text-[11px] text-atlas-text-primary"
            />
          </div>

          <div>
            <label className="block text-[10px] text-atlas-text-muted">Comment:</label>
            <textarea
              value={newCommentBody}
              onChange={(e) => setNewCommentBody(e.target.value)}
              placeholder="Enter review query or comment..."
              className="mt-0.5 w-full h-16 rounded-xs border border-atlas-border-default bg-atlas-surface-2 p-1.5 text-[11px] text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
            />
          </div>

          <div className="flex justify-end gap-1 pt-1">
            <Button type="submit" variant="primary" size="xs">
              Post Comment
            </Button>
          </div>
        </form>
      )}

      {/* Threads List */}
      <div className="flex-1 overflow-y-auto divide-y divide-atlas-border-default">
        {isLoading ? (
          <div className="p-4 text-center text-xs text-atlas-text-muted">
            Loading comments...
          </div>
        ) : threads.length === 0 ? (
          <div className="p-4 text-center text-xs text-atlas-text-muted">
            No anchored comments yet. Highlight report text or use &ldquo;+ Comment&rdquo; to anchor review notes.
          </div>
        ) : (
          threads.map((t) => {
            const statusMeta = getCommentThreadStatusDisplay(t.resolution_status);
            const isExpanded = expandedThreads[t.thread_id] ?? true;
            const replyText = replyBodies[t.thread_id] || "";

            return (
              <div key={t.thread_id} className="p-3 space-y-2 hover:bg-atlas-surface-1 transition-colors">
                {/* Thread Anchor Header */}
                <div className="flex items-start justify-between gap-1">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5">
                      <Badge variant="outline" className="text-[9px] font-mono">
                        {t.anchor_type.replace("_", " ")}
                      </Badge>
                      <Badge variant={statusMeta.variant} className="text-[9px]">
                        {statusMeta.label}
                      </Badge>
                      {t.is_stale && (
                        <Badge variant="warning" className="text-[9px]">
                          Stale Anchor
                        </Badge>
                      )}
                    </div>
                    <div className="mt-1 truncate font-semibold text-[11px] text-atlas-text-primary">
                      {t.anchor_reference}
                    </div>
                  </div>

                  <div className="flex items-center gap-1">
                    {t.resolution_status === "OPEN" ? (
                      <Button
                        variant="ghost"
                        size="xs"
                        className="text-[10px] text-emerald-400 hover:text-emerald-300"
                        onClick={() => onResolveThread(t.thread_id)}
                      >
                        ✓ Resolve
                      </Button>
                    ) : (
                      <Button
                        variant="ghost"
                        size="xs"
                        className="text-[10px] text-amber-400 hover:text-amber-300"
                        onClick={() => onReopenThread(t.thread_id)}
                      >
                        ↺ Reopen
                      </Button>
                    )}
                  </div>
                </div>

                {t.anchor_text && (
                  <div className="border-l-2 border-atlas-border-strong pl-2 text-[10px] italic text-atlas-text-muted line-clamp-2">
                    &ldquo;{t.anchor_text}&rdquo;
                  </div>
                )}

                {/* Comment Messages */}
                {isExpanded && (
                  <div className="space-y-1.5 pt-1">
                    {t.comments.map((c) => (
                      <div
                        key={c.comment_id}
                        className="rounded-xs bg-atlas-surface-2 p-2 text-[11px]"
                      >
                        <div className="flex items-center justify-between text-[10px] text-atlas-text-muted">
                          <span className="font-semibold text-atlas-text-primary">
                            {c.author_user_id}
                          </span>
                          <span>{formatResearchDate(c.created_at)}</span>
                        </div>
                        <p className="mt-1 text-atlas-text-secondary whitespace-pre-wrap">
                          {c.body}
                        </p>
                      </div>
                    ))}

                    {/* Reply Input */}
                    <div className="mt-2 flex items-center gap-1 pt-1">
                      <input
                        type="text"
                        value={replyText}
                        onChange={(e) =>
                          setReplyBodies((prev) => ({ ...prev, [t.thread_id]: e.target.value }))
                        }
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            handleSendReply(t.thread_id);
                          }
                        }}
                        placeholder="Reply..."
                        className="flex-1 rounded-xs border border-atlas-border-default bg-atlas-surface-2 px-2 py-1 text-[11px] text-atlas-text-primary placeholder:text-atlas-text-muted focus:outline-none"
                      />
                      <Button
                        variant="primary"
                        size="xs"
                        onClick={() => handleSendReply(t.thread_id)}
                      >
                        Send
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
