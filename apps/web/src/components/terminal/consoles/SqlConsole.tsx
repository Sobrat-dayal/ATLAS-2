"use client";

import React, { useRef, useState } from "react";
import { TerminalSession, TerminalUserPreferences } from "@/lib/terminal/types";
import { Copy, Trash2, ShieldAlert, Check, Database } from "lucide-react";

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
  const [draft, setDraft] = useState<string>(session.draft_content || "");
  const [copied, setCopied] = useState<boolean>(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const lines = draft.split("\n");
  const lineCount = lines.length;

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setDraft(val);
    onUpdateDraft(val);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(draft);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleClear = () => {
    setDraft("");
    onUpdateDraft("");
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
      <div className="flex items-center justify-between px-3 py-1 bg-atlas-surface-1 border-b border-atlas-border-subtle text-[11px] select-none text-atlas-text-muted">
        <div className="flex items-center gap-2">
          <Database className="h-3 w-3 text-atlas-accent" />
          <span className="text-atlas-text-primary font-semibold">SQL Query Console</span>
          <span className="text-zinc-500">&bull;</span>
          <span className="text-zinc-400">Target: Primary Analytics Read-Only (Stage 123 Required)</span>
        </div>

        <div className="flex items-center gap-2">
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
            title="Clear Draft"
            className="flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
          >
            <Trash2 className="h-3 w-3" />
            <span className="text-[10px]">Clear</span>
          </button>
        </div>
      </div>

      {/* Execution Boundary Notice */}
      <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-950/20 border-b border-amber-900/30 text-amber-300 text-[11px] select-none">
        <ShieldAlert className="h-3.5 w-3.5 text-amber-400 shrink-0" />
        <span>
          Stage 122 provides SQL composition only. Direct database query execution is disabled. Stage 123 provides sandboxed query policies.
        </span>
      </div>

      {/* Multiline Editor Body */}
      <div className="flex flex-1 overflow-hidden relative">
        <div className="w-10 bg-atlas-surface-1/40 border-r border-atlas-border-subtle/50 text-atlas-text-muted/40 text-right pr-2 select-none pt-2.5 overflow-hidden">
          {Array.from({ length: lineCount }).map((_, i) => (
            <div key={i}>{i + 1}</div>
          ))}
        </div>

        <textarea
          ref={textareaRef}
          value={draft}
          onChange={handleChange}
          placeholder="-- Compose SQL query here... (Stage 122 Draft)"
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
    </div>
  );
}

