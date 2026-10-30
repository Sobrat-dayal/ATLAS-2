"use client";

import React, { useRef, useState } from "react";
import { TerminalSession, TerminalUserPreferences } from "@/lib/terminal/types";
import { useExecution } from "@/hooks/terminal/useExecution";
import { useSqlSources } from "@/hooks/terminal/useSqlSources";
import { SqlResultGrid } from "../sql/SqlResultGrid";
import { ExecutionStatusBadge } from "../execution/ExecutionStatusBadge";
import { Play, Square, Copy, Trash2, Check, Database, AlertCircle } from "lucide-react";

interface SqlConsoleProps {
  session: TerminalSession;
  preferences: TerminalUserPreferences;
  onUpdateDraft: (newDraft: string) => void;
}

export function SqlConsole({
  session,
  preferences,
  onUpdateDraft,
}: SqlConsoleProps) {
  const [draft, setDraft] = useState<string>(
    session.draft_content || "SELECT instrument, price FROM test_prices ORDER BY instrument;\n"
  );
  const [copied, setCopied] = useState<boolean>(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { sources, selectedSourceId, setSelectedSourceId } = useSqlSources();
  const { isExecuting, currentExecution, error, execute, cancel, clear } =
    useExecution(session.session_id);

  const lines = draft.split("\n");
  const lineCount = lines.length;

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setDraft(val);
    onUpdateDraft(val);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+Enter or Cmd+Enter to run
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      handleRun();
    }
  };

  const handleRun = async () => {
    if (isExecuting || !draft.trim()) return;
    try {
      await execute({
        input_code: draft,
        execution_type: "SQL",
        source_id: selectedSourceId,
      });
    } catch {
      // Handled in hook
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(draft);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleClear = () => {
    setDraft("");
    onUpdateDraft("");
    clear();
  };

  return (
    <div
      className="flex flex-col flex-1 h-full bg-atlas-surface-0 overflow-hidden font-mono"
      style={{
        fontSize: `${preferences.font_size}px`,
        fontFamily: preferences.font_family,
        lineHeight: preferences.line_height,
      }}
    >
      {/* Subheader & Connection Profile */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-atlas-surface-1 border-b border-atlas-border-subtle text-[11px] select-none text-atlas-text-muted">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 font-semibold text-atlas-text-primary">
            <Database className="h-3.5 w-3.5 text-blue-400" />
            <span>SQL Analytics Console</span>
          </div>
          <span className="text-zinc-600">&bull;</span>
          <div className="flex items-center gap-1">
            <span className="text-neutral-500 text-[10px]">Source:</span>
            <select
              value={selectedSourceId}
              onChange={(e) => setSelectedSourceId(e.target.value)}
              disabled={isExecuting}
              className="bg-neutral-900 text-neutral-300 border border-neutral-800 rounded px-2 py-0.5 text-xs font-mono focus:outline-none focus:border-blue-500 cursor-pointer disabled:opacity-50"
            >
              {sources.map((src) => (
                <option key={src.source_id} value={src.source_id}>
                  {src.display_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {currentExecution && (
            <ExecutionStatusBadge
              status={currentExecution.status}
              durationMs={currentExecution.duration_ms}
            />
          )}

          {isExecuting ? (
            <button
              type="button"
              onClick={cancel}
              className="flex items-center gap-1 px-2 py-0.5 rounded bg-rose-900/80 hover:bg-rose-800 text-rose-200 border border-rose-700 font-semibold transition"
              title="Cancel Query"
            >
              <Square className="h-3 w-3 fill-rose-300" />
              <span>Cancel</span>
            </button>
          ) : (
            <button
              type="button"
              onClick={handleRun}
              className="flex items-center gap-1 px-2.5 py-0.5 rounded bg-blue-600 hover:bg-blue-500 text-white font-semibold transition shadow-sm"
              title="Run Query (Ctrl+Enter)"
            >
              <Play className="h-3 w-3 fill-white" />
              <span>Run</span>
            </button>
          )}

          <div className="h-3 w-[1px] bg-neutral-800 mx-1" />

          <button
            type="button"
            onClick={handleCopy}
            title="Copy SQL Query"
            className="flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
          >
            {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
            <span className="text-[10px]">{copied ? "Copied" : "Copy"}</span>
          </button>
          <button
            type="button"
            onClick={handleClear}
            title="Clear Draft & Results"
            className="flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
          >
            <Trash2 className="h-3 w-3" />
            <span className="text-[10px]">Clear</span>
          </button>
        </div>
      </div>

      {/* Split: Editor and Result Grid */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Editor Area (compact top half) */}
        <div className="h-36 min-h-24 max-h-56 flex overflow-hidden relative border-b border-atlas-border-subtle/70 bg-atlas-surface-0">
          <div className="w-10 bg-atlas-surface-1/40 border-r border-atlas-border-subtle/50 text-atlas-text-muted/40 text-right pr-2 select-none pt-2.5 overflow-hidden text-[11px]">
            {Array.from({ length: lineCount }).map((_, i) => (
              <div key={i}>{i + 1}</div>
            ))}
          </div>

          <textarea
            ref={textareaRef}
            value={draft}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="-- Write read-only SQL query (SELECT, WITH ... SELECT). Press Ctrl+Enter to run"
            wrap={preferences.word_wrap ? "on" : "off"}
            spellCheck={false}
            className="flex-1 bg-transparent border-none outline-none resize-none p-2.5 text-atlas-text-primary custom-scrollbar font-mono focus:ring-0 selection:bg-atlas-accent/30"
            style={{
              fontFamily: preferences.font_family,
              fontSize: `${preferences.font_size}px`,
              lineHeight: preferences.line_height,
            }}
          />
        </div>

        {/* Results Area */}
        <div className="flex-1 flex flex-col bg-neutral-950 overflow-hidden">
          {error && (
            <div className="m-3 flex items-start gap-2 p-2.5 rounded bg-rose-950/40 border border-rose-900/60 text-rose-300 text-xs font-mono">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div className="whitespace-pre-wrap">{error}</div>
            </div>
          )}

          {currentExecution?.tabular_result ? (
            <div className="flex-1 p-2 overflow-hidden">
              <SqlResultGrid
                result={currentExecution.tabular_result}
                durationMs={currentExecution.duration_ms}
              />
            </div>
          ) : currentExecution?.stdout_summary ? (
            <div className="p-3 font-mono text-xs text-neutral-300">
              {currentExecution.stdout_summary}
            </div>
          ) : !isExecuting ? (
            <div className="flex-1 flex items-center justify-center text-xs font-mono text-neutral-600 select-none">
              Execute query to view tabular analytical results.
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-xs font-mono text-blue-400 animate-pulse">
              Executing query against analytical source...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
