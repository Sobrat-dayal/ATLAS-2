"use client";

import React, { useRef, useState } from "react";
import { TerminalSession, TerminalUserPreferences } from "@/lib/terminal/types";
import { useExecution } from "@/hooks/terminal/useExecution";
import { usePythonEnvironments } from "@/hooks/terminal/usePythonEnvironments";
import { ExecutionStatusBadge } from "../execution/ExecutionStatusBadge";
import { PythonEnvironmentSelector } from "../python/PythonEnvironmentSelector";
import { Play, Square, Copy, Trash2, Check, AlertCircle } from "lucide-react";

interface PythonConsoleProps {
  session: TerminalSession;
  preferences: TerminalUserPreferences;
  onUpdateDraft: (newDraft: string) => void;
}

export function PythonConsole({
  session,
  preferences,
  onUpdateDraft,
}: PythonConsoleProps) {
  const [draft, setDraft] = useState<string>(session.draft_content || "print(2 + 2)\n");
  const [copied, setCopied] = useState<boolean>(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { environments, selectedEnvId, setSelectedEnvId } = usePythonEnvironments();
  const { isExecuting, currentExecution, outputChunks, error, execute, cancel, clear } =
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
      return;
    }

    // Tab key inserts 4 spaces
    if (e.key === "Tab") {
      e.preventDefault();
      const textarea = textareaRef.current;
      if (!textarea) return;

      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;

      const newVal = draft.substring(0, start) + "    " + draft.substring(end);
      setDraft(newVal);
      onUpdateDraft(newVal);

      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }, 0);
    }
  };

  const handleRun = async () => {
    if (isExecuting || !draft.trim()) return;
    try {
      await execute({
        input_code: draft,
        execution_type: "PYTHON",
        environment_id: selectedEnvId,
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
      {/* Console Subheader / Actions */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-atlas-surface-1 border-b border-atlas-border-subtle text-[11px] select-none text-atlas-text-muted">
        <div className="flex items-center gap-3">
          <span className="text-atlas-text-primary font-semibold">Python Quantitative Sandbox</span>
          <span className="text-zinc-600">&bull;</span>
          <PythonEnvironmentSelector
            environments={environments}
            selectedEnvId={selectedEnvId}
            onSelect={setSelectedEnvId}
            disabled={isExecuting}
          />
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
              title="Stop Execution"
            >
              <Square className="h-3 w-3 fill-rose-300" />
              <span>Stop</span>
            </button>
          ) : (
            <button
              type="button"
              onClick={handleRun}
              className="flex items-center gap-1 px-2.5 py-0.5 rounded bg-blue-600 hover:bg-blue-500 text-white font-semibold transition shadow-sm"
              title="Run Script (Ctrl+Enter)"
            >
              <Play className="h-3 w-3 fill-white" />
              <span>Run</span>
            </button>
          )}

          <div className="h-3 w-[1px] bg-neutral-800 mx-1" />

          <button
            type="button"
            onClick={handleCopy}
            title="Copy Python Code"
            className="flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
          >
            {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
            <span className="text-[10px]">{copied ? "Copied" : "Copy"}</span>
          </button>
          <button
            type="button"
            onClick={handleClear}
            title="Clear Draft & Output"
            className="flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
          >
            <Trash2 className="h-3 w-3" />
            <span className="text-[10px]">Clear</span>
          </button>
        </div>
      </div>

      {/* Split View: Editor and Output */}
      <div className="flex flex-col md:flex-row flex-1 overflow-hidden">
        {/* Editor Pane */}
        <div className="flex flex-1 overflow-hidden relative border-b md:border-b-0 md:border-r border-atlas-border-subtle/70">
          {/* Line Numbers */}
          <div className="w-10 bg-atlas-surface-1/40 border-r border-atlas-border-subtle/50 text-atlas-text-muted/40 text-right pr-2 select-none pt-2.5 overflow-hidden text-[11px]">
            {Array.from({ length: lineCount }).map((_, i) => (
              <div key={i}>{i + 1}</div>
            ))}
          </div>

          {/* Text Area */}
          <textarea
            ref={textareaRef}
            value={draft}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="# Write Python code here... Press Ctrl+Enter to run"
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

        {/* Output Pane */}
        <div className="flex flex-col flex-1 bg-neutral-950 overflow-hidden text-xs">
          <div className="flex items-center justify-between px-3 py-1 bg-neutral-900/60 border-b border-neutral-800 text-[11px] text-neutral-400 select-none">
            <span className="font-semibold text-neutral-300">Terminal Output</span>
            {currentExecution?.duration_ms != null && (
              <span className="text-[10px] text-neutral-500">
                Latency: {currentExecution.duration_ms.toFixed(1)}ms
              </span>
            )}
          </div>

          <div className="flex-1 p-3 overflow-auto custom-scrollbar font-mono text-[11px] space-y-2">
            {error && (
              <div className="flex items-start gap-2 p-2 rounded bg-rose-950/40 border border-rose-900/60 text-rose-300">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div className="whitespace-pre-wrap">{error}</div>
              </div>
            )}

            {outputChunks.length > 0 ? (
              <div className="space-y-1">
                {outputChunks.map((chunk) => (
                  <div
                    key={chunk.seq_num}
                    className={`whitespace-pre-wrap ${
                      chunk.stream_type === "stderr" || chunk.stream_type === "error"
                        ? "text-rose-400"
                        : "text-neutral-200"
                    }`}
                  >
                    {chunk.payload}
                  </div>
                ))}
              </div>
            ) : currentExecution?.stdout_summary ? (
              <div className="whitespace-pre-wrap text-neutral-200">
                {currentExecution.stdout_summary}
              </div>
            ) : !isExecuting ? (
              <div className="text-neutral-600 italic select-none">
                Ready to execute. Press Run or Ctrl+Enter to execute in sandboxed environment.
              </div>
            ) : (
              <div className="text-blue-400 animate-pulse">Running in isolated sandbox...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
