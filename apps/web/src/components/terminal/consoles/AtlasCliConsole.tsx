"use client";

import React, { useEffect, useRef, useState } from "react";
import { TerminalSession, TerminalUserPreferences } from "@/lib/terminal/types";
import { useExecution } from "@/hooks/terminal/useExecution";
import { useAtlasCliCommands } from "@/hooks/terminal/useAtlasCliCommands";
import { AtlasCliResultViewer } from "../cli/AtlasCliResultViewer";
import type { TerminalExecutionDetail } from "@/lib/terminal/executionTypes";
import { Copy, Trash2, HelpCircle, Terminal as TermIcon, Loader2 } from "lucide-react";

interface AtlasCliConsoleProps {
  session: TerminalSession;
  preferences: TerminalUserPreferences;
  onUpdateDraft: (newDraft: string) => void;
}

interface CliHistoryItem {
  id: string;
  command: string;
  timestamp: string;
  execution?: TerminalExecutionDetail;
  systemMessage?: string;
  isError?: boolean;
}

export function AtlasCliConsole({
  session,
  preferences,
  onUpdateDraft,
}: AtlasCliConsoleProps) {
  const [historyItems, setHistoryItems] = useState<CliHistoryItem[]>([
    {
      id: "init",
      command: "",
      timestamp: new Date().toLocaleTimeString(),
      systemMessage:
        "ATLAS Financial Intelligence and Quantitative Research OS (v2.4.0) — Stage 123 Active\n" +
        "Sandboxed Execution Operational. Type 'atlas help' to view registered commands.",
    },
  ]);
  const [inputVal, setInputVal] = useState<string>(session.draft_content || "");
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIdx, setHistoryIdx] = useState<number>(-1);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { commands, getSuggestions } = useAtlasCliCommands();
  const { isExecuting, execute } = useExecution(session.session_id);

  const suggestions = getSuggestions(inputVal);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [historyItems, isExecuting]);

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const trimmed = inputVal.trim();
      if (!trimmed || isExecuting) return;

      const newHistory = [...commandHistory, trimmed];
      setCommandHistory(newHistory);
      setHistoryIdx(-1);

      const time = new Date().toLocaleTimeString();

      if (trimmed.toLowerCase() === "clear" || trimmed.toLowerCase() === "atlas clear") {
        setHistoryItems([]);
        setInputVal("");
        onUpdateDraft("");
        return;
      }

      // Add placeholder history item
      const itemId = `cli_${Date.now()}`;
      setInputVal("");
      onUpdateDraft("");

      try {
        const result = await execute({
          input_code: trimmed,
          execution_type: "ATLAS_CLI",
        });

        setHistoryItems((prev) => [
          ...prev,
          {
            id: itemId,
            command: trimmed,
            timestamp: time,
            execution: result,
          },
        ]);
      } catch (err: any) {
        setHistoryItems((prev) => [
          ...prev,
          {
            id: itemId,
            command: trimmed,
            timestamp: time,
            isError: true,
            systemMessage: err?.message || "Execution failed.",
          },
        ]);
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (commandHistory.length === 0) return;
      const nextIdx = historyIdx === -1 ? commandHistory.length - 1 : Math.max(0, historyIdx - 1);
      setHistoryIdx(nextIdx);
      setInputVal(commandHistory[nextIdx]);
      onUpdateDraft(commandHistory[nextIdx]);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIdx === -1) return;
      const nextIdx = historyIdx + 1;
      if (nextIdx >= commandHistory.length) {
        setHistoryIdx(-1);
        setInputVal("");
        onUpdateDraft("");
      } else {
        setHistoryIdx(nextIdx);
        setInputVal(commandHistory[nextIdx]);
        onUpdateDraft(commandHistory[nextIdx]);
      }
    } else if (e.key === "Tab" && suggestions.length > 0) {
      e.preventDefault();
      const first = suggestions[0].name;
      const completed = inputVal.startsWith("atlas ") ? `atlas ${first}` : first;
      setInputVal(completed);
      onUpdateDraft(completed);
    }
  };

  const handleClear = () => {
    setHistoryItems([]);
    setInputVal("");
    onUpdateDraft("");
  };

  const handleCopyAll = () => {
    const text = historyItems
      .map((item) => {
        if (item.systemMessage) return item.systemMessage;
        let out = `atlas> ${item.command}\n`;
        if (item.execution?.stdout_summary) out += `${item.execution.stdout_summary}\n`;
        if (item.execution?.error_message) out += `ERROR: ${item.execution.error_message}\n`;
        return out;
      })
      .join("\n");
    navigator.clipboard.writeText(text);
  };

  return (
    <div
      className="flex flex-col flex-1 h-full bg-atlas-surface-0 overflow-hidden font-mono"
      style={{
        fontSize: `${preferences.font_size}px`,
        fontFamily: preferences.font_family,
        lineHeight: preferences.line_height,
      }}
      onClick={() => inputRef.current?.focus()}
    >
      {/* Console Subheader */}
      <div className="flex items-center justify-between px-3 py-1 bg-atlas-surface-1 border-b border-atlas-border-subtle text-[11px] select-none text-atlas-text-muted">
        <div className="flex items-center gap-2">
          <TermIcon className="h-3.5 w-3.5 text-blue-400" />
          <span className="text-atlas-text-primary font-semibold">ATLAS CLI Command Router</span>
          <span className="text-zinc-500">&bull;</span>
          <span className="text-zinc-400">Environment: Host Sandbox (Strict Read-Only)</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopyAll}
            title="Copy scrollback history"
            className="flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors text-[10px]"
          >
            <Copy className="h-3 w-3" />
            <span>Copy</span>
          </button>
          <button
            type="button"
            onClick={handleClear}
            title="Clear scrollback history"
            className="flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors text-[10px]"
          >
            <Trash2 className="h-3 w-3" />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Scrollback History Area */}
      <div
        ref={scrollRef}
        className="flex-1 p-3 overflow-y-auto custom-scrollbar space-y-3 bg-neutral-950 font-mono text-xs"
      >
        {historyItems.map((item) => (
          <div key={item.id} className="space-y-1">
            {item.command && (
              <div className="flex items-center gap-2 text-neutral-400 font-semibold select-none">
                <span className="text-blue-400">atlas&gt;</span>
                <span className="text-neutral-100">{item.command}</span>
                {preferences.timestamp_display && (
                  <span className="text-[10px] text-neutral-600 font-normal ml-auto">
                    {item.timestamp}
                  </span>
                )}
              </div>
            )}

            {item.systemMessage && (
              <pre
                className={`p-2 rounded font-mono text-[11px] whitespace-pre-wrap leading-relaxed ${
                  item.isError
                    ? "bg-rose-950/40 border border-rose-900/60 text-rose-300"
                    : "bg-neutral-900/40 text-neutral-400 border border-neutral-900"
                }`}
              >
                {item.systemMessage}
              </pre>
            )}

            {item.execution && <AtlasCliResultViewer execution={item.execution} />}
          </div>
        ))}

        {isExecuting && (
          <div className="flex items-center gap-2 text-blue-400 text-xs py-1 animate-pulse">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>Executing command...</span>
          </div>
        )}
      </div>

      {/* Auto-suggestions Pill Bar */}
      {suggestions.length > 0 && inputVal.trim() && (
        <div className="px-3 py-1 bg-neutral-900/90 border-t border-neutral-800 flex items-center gap-2 text-[11px] overflow-x-auto select-none">
          <span className="text-neutral-500 font-semibold text-[10px] uppercase">Suggest:</span>
          {suggestions.slice(0, 5).map((s) => (
            <button
              key={s.command_id}
              onClick={() => {
                const completed = inputVal.startsWith("atlas ") ? `atlas ${s.name}` : s.name;
                setInputVal(completed);
                onUpdateDraft(completed);
                inputRef.current?.focus();
              }}
              className="px-2 py-0.5 rounded bg-neutral-800 hover:bg-neutral-700 text-neutral-300 border border-neutral-700 font-mono transition"
            >
              atlas {s.name}
            </button>
          ))}
          <span className="text-neutral-600 text-[10px] ml-auto">Tab to complete</span>
        </div>
      )}

      {/* Command Prompt Line */}
      <div className="flex items-center gap-2 px-3 py-2 bg-neutral-900 border-t border-neutral-800">
        <span className="text-blue-400 font-bold select-none text-xs">atlas&gt;</span>
        <input
          ref={inputRef}
          type="text"
          value={inputVal}
          onChange={(e) => {
            setInputVal(e.target.value);
            onUpdateDraft(e.target.value);
          }}
          onKeyDown={handleKeyDown}
          disabled={isExecuting}
          placeholder={isExecuting ? "Executing..." : "Enter command (e.g. 'atlas help', 'atlas workspace list', 'atlas version')..."}
          spellCheck={false}
          autoFocus
          className="flex-1 bg-transparent border-none outline-none text-neutral-100 placeholder:text-neutral-600 font-mono text-xs focus:ring-0 disabled:opacity-50"
          style={{
            fontFamily: preferences.font_family,
            fontSize: `${preferences.font_size}px`,
          }}
        />
      </div>
    </div>
  );
}
