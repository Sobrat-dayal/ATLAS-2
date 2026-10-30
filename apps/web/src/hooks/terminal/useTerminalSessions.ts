"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  closeTerminalSession,
  createTerminalSession,
  fetchTerminalSessions,
  reorderTerminalSessions,
  updateTerminalSession,
} from "@/lib/terminal/api";
import { TerminalSession, TerminalType } from "@/lib/terminal/types";

export function useTerminalSessions(workspaceId?: string | null) {
  const [sessions, setSessions] = useState<TerminalSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const debounceTimersRef = useRef<Record<string, NodeJS.Timeout>>({});

  // Fetch sessions on mount or workspace change
  const loadSessions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchTerminalSessions(workspaceId || undefined);
      setSessions(data);
      if (data.length > 0) {
        setActiveSessionId((prev) => {
          if (prev && data.some((s) => s.session_id === prev)) {
            return prev;
          }
          return data[0].session_id;
        });
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load terminal sessions";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const activeSession = sessions.find((s) => s.session_id === activeSessionId) || sessions[0] || null;

  // Create session
  const handleCreateSession = useCallback(
    async (type: TerminalType, displayName?: string, initialDraft: string = "") => {
      try {
        const created = await createTerminalSession({
          terminal_type: type,
          display_name: displayName,
          workspace_id: workspaceId || null,
          initial_draft: initialDraft,
        });
        setSessions((prev) => [...prev, created]);
        setActiveSessionId(created.session_id);
        return created;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to create session";
        setError(msg);
        throw err;
      }
    },
    [workspaceId]
  );

  // Close session
  const handleCloseSession = useCallback(
    async (sessionId: string) => {
      try {
        await closeTerminalSession(sessionId);
        setSessions((prev) => {
          const nextSessions = prev.filter((s) => s.session_id !== sessionId);
          if (activeSessionId === sessionId) {
            setActiveSessionId(nextSessions[0]?.session_id || null);
          }
          return nextSessions;
        });
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to close session";
        setError(msg);
      }
    },
    [activeSessionId]
  );

  // Rename session
  const handleRenameSession = useCallback(async (sessionId: string, newName: string) => {
    if (!newName.trim()) return;
    setSessions((prev) =>
      prev.map((s) => (s.session_id === sessionId ? { ...s, display_name: newName.trim() } : s))
    );
    try {
      await updateTerminalSession(sessionId, { display_name: newName.trim() });
    } catch (err: unknown) {
      console.warn("Failed to persist renamed title:", err);
    }
  }, []);

  // Update draft (independent per session, with optimistic update & debounce API save)
  const handleUpdateDraft = useCallback((sessionId: string, newDraft: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.session_id === sessionId ? { ...s, draft_content: newDraft } : s))
    );

    // Clear existing timer
    if (debounceTimersRef.current[sessionId]) {
      clearTimeout(debounceTimersRef.current[sessionId]);
    }

    // Debounce backend update by 600ms
    debounceTimersRef.current[sessionId] = setTimeout(async () => {
      try {
        await updateTerminalSession(sessionId, { draft_content: newDraft });
      } catch (err: unknown) {
        console.warn("Failed to persist draft content:", err);
      }
    }, 600);
  }, []);

  // Clear draft
  const handleClearDraft = useCallback((sessionId: string) => {
    handleUpdateDraft(sessionId, "");
  }, [handleUpdateDraft]);

  // Reorder sessions
  const handleReorderSessions = useCallback(async (reorderedSessionIds: string[]) => {
    setSessions((prev) => {
      const sessionMap = new Map(prev.map((s) => [s.session_id, s]));
      const ordered: TerminalSession[] = [];
      reorderedSessionIds.forEach((id, idx) => {
        const item = sessionMap.get(id);
        if (item) {
          ordered.push({ ...item, session_order: idx });
        }
      });
      return ordered;
    });

    try {
      await reorderTerminalSessions(reorderedSessionIds);
    } catch (err: unknown) {
      console.warn("Failed to persist session ordering:", err);
    }
  }, []);

  return {
    sessions,
    activeSession,
    activeSessionId,
    setActiveSessionId,
    loading,
    error,
    createSession: handleCreateSession,
    closeSession: handleCloseSession,
    renameSession: handleRenameSession,
    updateDraft: handleUpdateDraft,
    clearDraft: handleClearDraft,
    reorderSessions: handleReorderSessions,
    refresh: loadSessions,
  };
}

