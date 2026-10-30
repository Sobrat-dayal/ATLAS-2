"use client";

import React, { useState } from "react";
import { useTerminalSessions } from "@/hooks/terminal/useTerminalSessions";
import { useTerminalPreferences } from "@/hooks/terminal/useTerminalPreferences";
import { TerminalHeader } from "./TerminalHeader";
import { TerminalTabBar } from "./TerminalTabBar";
import { TerminalStatusBar } from "./TerminalStatusBar";
import { TerminalSettingsModal } from "./TerminalSettingsModal";
import { AtlasCliConsole } from "./consoles/AtlasCliConsole";
import { PythonConsole } from "./consoles/PythonConsole";
import { SqlConsole } from "./consoles/SqlConsole";
import { LogsConsole } from "./consoles/LogsConsole";
import { AgentsConsole } from "./consoles/AgentsConsole";
import { McpConsole } from "./consoles/McpConsole";

interface TerminalDrawerProps {
  workspaceId?: string | null;
  workspaceName?: string;
  onClose?: () => void;
}

export function TerminalDrawer({
  workspaceId,
  workspaceName,
  onClose,
}: TerminalDrawerProps) {
  const {
    sessions,
    activeSession,
    activeSessionId,
    setActiveSessionId,
    loading,
    error,
    createSession,
    closeSession,
    renameSession,
    updateDraft,
  } = useTerminalSessions(workspaceId);

  const { preferences, updatePreferences } = useTerminalPreferences();

  const [isMaximized, setIsMaximized] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleToggleMaximize = () => {
    setIsMaximized(!isMaximized);
    if (isMinimized) setIsMinimized(false);
  };

  const handleMinimize = () => {
    setIsMinimized(!isMinimized);
    if (isMaximized) setIsMaximized(false);
  };

  const renderActiveConsole = () => {
    if (!activeSession) {
      return (
        <div className="flex flex-col items-center justify-center flex-1 h-full text-atlas-text-muted text-xs">
          <span>No terminal session selected.</span>
        </div>
      );
    }

    switch (activeSession.terminal_type) {
      case "ATLAS_CLI":
        return (
          <AtlasCliConsole
            key={activeSession.session_id}
            session={activeSession}
            preferences={preferences}
            onUpdateDraft={(draft) => updateDraft(activeSession.session_id, draft)}
          />
        );
      case "PYTHON":
        return (
          <PythonConsole
            key={activeSession.session_id}
            session={activeSession}
            preferences={preferences}
            onUpdateDraft={(draft) => updateDraft(activeSession.session_id, draft)}
          />
        );
      case "SQL":
        return (
          <SqlConsole
            key={activeSession.session_id}
            session={activeSession}
            preferences={preferences}
            onUpdateDraft={(draft) => updateDraft(activeSession.session_id, draft)}
          />
        );
      case "LOGS":
        return (
          <LogsConsole
            key={activeSession.session_id}
            session={activeSession}
            preferences={preferences}
          />
        );
      case "AGENTS":
        return (
          <AgentsConsole
            key={activeSession.session_id}
            session={activeSession}
            preferences={preferences}
          />
        );
      case "MCP":
        return (
          <McpConsole
            key={activeSession.session_id}
            session={activeSession}
            preferences={preferences}
          />
        );
      default:
        return (
          <div className="flex flex-col items-center justify-center flex-1 h-full text-atlas-text-muted text-xs">
            <span>Unsupported console type: {activeSession.terminal_type}</span>
          </div>
        );
    }
  };

  const containerClasses = isMaximized
    ? "fixed inset-0 z-50 flex flex-col bg-atlas-surface-0 shadow-2xl"
    : isMinimized
    ? "h-8 flex flex-col bg-atlas-surface-0 overflow-hidden"
    : "flex flex-col flex-1 h-full bg-atlas-surface-0 overflow-hidden";

  return (
    <div className={containerClasses} id="atlas-terminal-shell">
      {/* 1. Terminal Window Header */}
      <TerminalHeader
        workspaceName={workspaceName}
        isMaximized={isMaximized}
        onToggleMaximize={handleToggleMaximize}
        onMinimize={handleMinimize}
        onClose={onClose || (() => {})}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* When not minimized, render TabBar, Active Console, and StatusBar */}
      {!isMinimized && (
        <>
          {/* 2. Tab Bar */}
          <TerminalTabBar
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={setActiveSessionId}
            onCloseSession={closeSession}
            onRenameSession={renameSession}
            onCreateSession={(type) => createSession(type)}
          />

          {/* 3. Main Console Viewport */}
          <div className="flex-1 flex flex-col overflow-hidden relative">
            {loading && sessions.length === 0 ? (
              <div className="flex items-center justify-center flex-1 text-xs text-atlas-text-muted">
                Initializing ATLAS Terminal sessions...
              </div>
            ) : error && sessions.length === 0 ? (
              <div className="flex items-center justify-center flex-1 text-xs text-rose-400 p-4">
                {error}
              </div>
            ) : (
              renderActiveConsole()
            )}
          </div>

          {/* 4. Terminal Status Bar */}
          <TerminalStatusBar
            activeSession={activeSession}
            preferences={preferences}
          />
        </>
      )}

      {/* 5. Terminal Preferences Settings Modal */}
      <TerminalSettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        preferences={preferences}
        onSavePreferences={updatePreferences}
      />
    </div>
  );
}

