"use client";

import React, { useEffect, useRef, useState } from "react";
import { TerminalSession, TerminalUserPreferences } from "@/lib/terminal/types";
import { REGISTERED_CLI_COMMANDS } from "@/lib/terminal/capabilities";
import { parseAnsiToSpans } from "@/lib/terminal/sanitization";
import { Copy, Trash2, Search, HelpCircle, ShieldAlert } from "lucide-react";

interface AtlasCliConsoleProps {
  session: TerminalSession;
  preferences: TerminalUserPreferences;
  onUpdateDraft: (newDraft: string) => void;
}

interface CliOutputLine {
  id: string;
  type: "input" | "system" | "error" | "help";
  text: string;
  timestamp: string;
}

export function AtlasCliConsole({
  session,
  preferences,
  onUpdateDraft,
}: AtlasCliConsoleProps) {
  const [output, setOutput] = useState<CliOutputLine[]>([
    {
      id: "line_init",
      type: "system",
      text: "ATLAS Terminal Shell (v2.4.0) — Stage 122 Active\nType 'help' to inspect documented financial commands and syntax.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [inputVal, setInputVal] = useState<string>(session.draft_content || "");
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number>(-1);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [showSearch, setShowSearch] = useState<boolean>(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll on new output
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [output]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const trimmed = inputVal.trim();
      if (!trimmed) return;

      const newHistory = [...history, trimmed];
      setHistory(newHistory);
      setHistoryIndex(-1);

      const time = new Date().toLocaleTimeString();
      const inputEntry: CliOutputLine = {
        id: `in_${Date.now()}`,
        type: "input",
        text: `atlas> ${trimmed}`,
        timestamp: time,
      };

      if (trimmed.toLowerCase() === "clear") {
        setOutput([]);
        setInputVal("");
        onUpdateDraft("");
        return;
      }

      let responseEntry: CliOutputLine;
      if (trimmed.toLowerCase() === "help") {
        const helpSummary = REGISTERED_CLI_COMMANDS.map(
          (c) => `  ${c.command.padEnd(14)} ${c.summary}`
        ).join("\n");
        responseEntry = {
          id: `help_${Date.now()}`,
          type: "help",
          text: `Documented ATLAS Commands:\n${helpSummary}\n\nNote: Command execution belongs to Stage 123.`,
          timestamp: time,
        };
      } else {
        responseEntry = {
          id: `notice_${Date.now()}`,
          type: "error",
          text: `atlas: Command '${trimmed}' received. Command execution is disabled in Stage 122.\nApproved sandboxed execution for Python, SQL, and ATLAS commands is provided in Stage 123.`,
          timestamp: time,
        };
      }

      setOutput((prev) => [...prev, inputEntry, responseEntry]);
      setInputVal("");
      onUpdateDraft("");
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (history.length === 0) return;
      const nextIdx = historyIndex === -1 ? history.length - 1 : Math.max(0, historyIndex - 1);
      setHistoryIndex(nextIdx);
      setInputVal(history[nextIdx] || "");
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIndex === -1) return;
      const nextIdx = historyIndex + 1;
      if (nextIdx >= history.length) {
        setHistoryIndex(-1);
        setInputVal("");
      } else {
        setHistoryIndex(nextIdx);
        setInputVal(history[nextIdx] || "");
      }
    }
  };

  const filteredOutput = searchQuery
    ? output.filter((line) => line.text.toLowerCase().includes(searchQuery.toLowerCase()))
    : output;

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
      {/* Mini-toolbar */}
      <div className="flex items-center justify-between px-3 py-1 bg-atlas-surface-1 border-b border-atlas-border-subtle text-[11px] select-none text-atlas-text-muted">
        <div className="flex items-center gap-2">
          <span className="text-atlas-text-primary font-semibold">ATLAS CLI Console</span>
          <span className="text-[10px] text-amber-400 bg-amber-400/10 px-1 rounded">Execution: Disabled</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowSearch(!showSearch)}
            title="Search Output"
            className="p-1 hover:text-atlas-text-primary rounded hover:bg-atlas-surface-hover transition-colors"
          >
            <Search className="h-3 w-3" />
          </button>
          <button
            type="button"
            onClick={() => setOutput([])}
            title="Clear Output Buffer"
            className="p-1 hover:text-atlas-text-primary rounded hover:bg-atlas-surface-hover transition-colors"
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* Search Bar */}
      {showSearch && (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-atlas-surface-2 border-b border-atlas-border-subtle">
          <Search className="h-3 w-3 text-atlas-text-muted" />
          <input
            type="text"
            placeholder="Find in output..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 bg-transparent text-xs text-atlas-text-primary outline-none"
            autoFocus
          />
          <button
            type="button"
            onClick={() => {
              setSearchQuery("");
              setShowSearch(false);
            }}
            className="text-[10px] text-atlas-text-muted hover:text-atlas-text-primary"
          >
            Esc
          </button>
        </div>
      )}

      {/* Output Scrollback */}
      <div
        ref={scrollRef}
        className="flex-1 p-3 overflow-y-auto space-y-1.5 custom-scrollbar text-atlas-text-primary selection:bg-atlas-accent/30"
      >
        {filteredOutput.map((line) => {
          const spans = parseAnsiToSpans(line.text);
          return (
            <div key={line.id} className="leading-relaxed">
              {preferences.timestamp_display && (
                <span className="text-[10px] text-atlas-text-muted mr-2 select-none opacity-60">
                  [{line.timestamp}]
                </span>
              )}
              {line.type === "input" && (
                <span className="text-atlas-accent font-semibold">{line.text}</span>
              )}
              {line.type === "help" && (
                <pre className="text-emerald-400 whitespace-pre-wrap">{line.text}</pre>
              )}
              {line.type === "error" && (
                <div className="text-amber-300 bg-amber-950/20 p-2 rounded border border-amber-800/30 whitespace-pre-wrap flex items-start gap-1.5 my-1">
                  <ShieldAlert className="h-3.5 w-3.5 shrink-0 mt-0.5 text-amber-400" />
                  <span>{line.text}</span>
                </div>
              )}
              {line.type === "system" && (
                <div className="text-atlas-text-muted whitespace-pre-wrap">{line.text}</div>
              )}
            </div>
          );
        })}

        {/* Input line */}
        <div className="flex items-center gap-2 pt-1 text-atlas-text-primary">
          <span className="text-atlas-accent font-bold select-none">atlas&gt;</span>
          <input
            ref={inputRef}
            type="text"
            value={inputVal}
            onChange={(e) => {
              setInputVal(e.target.value);
              onUpdateDraft(e.target.value);
            }}
            onKeyDown={handleKeyDown}
            autoFocus
            className="flex-1 bg-transparent border-none outline-none text-atlas-text-primary font-mono placeholder:text-atlas-text-muted/40"
            placeholder="Type command ('help' for syntax)..."
          />
        </div>
      </div>
    </div>
  );
}

