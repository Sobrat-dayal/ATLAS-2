"use client";

import React, { useState } from "react";
import { Terminal, Code2, Database, ScrollText, Bot, Network, X } from "lucide-react";
import { TerminalSession, TerminalType } from "@/lib/terminal/types";
import { TerminalNewTabMenu } from "./TerminalNewTabMenu";

interface TerminalTabBarProps {
  sessions: TerminalSession[];
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onCloseSession: (sessionId: string) => void;
  onRenameSession: (sessionId: string, newTitle: string) => void;
  onCreateSession: (type: TerminalType) => void;
}

export function TerminalTabBar({
  sessions,
  activeSessionId,
  onSelectSession,
  onCloseSession,
  onRenameSession,
  onCreateSession,
}: TerminalTabBarProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState<string>("");

  const getIcon = (type: TerminalType) => {
    switch (type) {
      case "ATLAS_CLI":
        return Terminal;
      case "PYTHON":
        return Code2;
      case "SQL":
        return Database;
      case "LOGS":
        return ScrollText;
      case "AGENTS":
        return Bot;
      case "MCP":
        return Network;
      default:
        return Terminal;
    }
  };

  const handleStartRename = (session: TerminalSession) => {
    setEditingId(session.session_id);
    setEditTitle(session.display_name);
  };

  const handleSaveRename = (sessionId: string) => {
    if (editTitle.trim()) {
      onRenameSession(sessionId, editTitle.trim());
    }
    setEditingId(null);
  };

  return (
    <div className="flex items-center h-7 bg-atlas-surface-1 border-b border-atlas-border-subtle px-1 select-none overflow-x-auto custom-scrollbar shrink-0">
      <div className="flex items-center gap-0.5">
        {sessions.map((session) => {
          const isActive = session.session_id === activeSessionId;
          const Icon = getIcon(session.terminal_type);
          const isEditing = editingId === session.session_id;

          return (
            <div
              key={session.session_id}
              role="tab"
              aria-selected={isActive}
              onClick={() => onSelectSession(session.session_id)}
              onDoubleClick={() => handleStartRename(session)}
              className={`group flex items-center gap-1.5 h-6 px-2.5 rounded-t text-xs cursor-pointer border-t-2 border-transparent transition-colors ${
                isActive
                  ? "bg-atlas-surface-2 text-atlas-text-primary border-t-atlas-accent font-medium shadow-sm"
                  : "text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover"
              }`}
            >
              <Icon className={`h-3 w-3 shrink-0 ${isActive ? "text-atlas-accent" : "text-atlas-text-muted"}`} />

              {isEditing ? (
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={() => handleSaveRename(session.session_id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSaveRename(session.session_id);
                    if (e.key === "Escape") setEditingId(null);
                  }}
                  autoFocus
                  className="bg-atlas-surface-0 border border-atlas-accent rounded px-1 py-0 text-xs text-atlas-text-primary outline-none w-24"
                />
              ) : (
                <span className="truncate max-w-[120px]">{session.display_name}</span>
              )}

              {/* Close Button */}
              {sessions.length > 1 && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onCloseSession(session.session_id);
                  }}
                  title="Close Tab"
                  aria-label={`Close ${session.display_name} tab`}
                  className="rounded p-0.5 text-atlas-text-muted opacity-0 group-hover:opacity-100 hover:text-atlas-negative hover:bg-atlas-surface-3 transition-opacity ml-1"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex items-center ml-1 border-l border-atlas-border-subtle pl-1">
        <TerminalNewTabMenu onSelectType={onCreateSession} />
      </div>
    </div>
  );
}

