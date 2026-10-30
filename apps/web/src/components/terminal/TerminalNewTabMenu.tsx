"use client";

import React, { useEffect, useRef, useState } from "react";
import { Plus, Terminal, Code2, Database, ScrollText, Bot, Network } from "lucide-react";
import { TerminalType } from "@/lib/terminal/types";
import { TERMINAL_CAPABILITIES_CATALOG } from "@/lib/terminal/capabilities";

interface TerminalNewTabMenuProps {
  onSelectType: (type: TerminalType) => void;
}

export function TerminalNewTabMenu({ onSelectType }: TerminalNewTabMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  const items: { type: TerminalType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { type: "ATLAS_CLI", label: "ATLAS CLI", icon: Terminal },
    { type: "PYTHON", label: "Python Scratchpad", icon: Code2 },
    { type: "SQL", label: "SQL Query", icon: Database },
    { type: "LOGS", label: "Operational Logs", icon: ScrollText },
    { type: "AGENTS", label: "Agents Inspector", icon: Bot },
    { type: "MCP", label: "MCP Connections", icon: Network },
  ];

  return (
    <div className="relative inline-block" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        title="New Terminal Tab"
        aria-label="New Terminal Tab"
        className="flex items-center justify-center w-6 h-6 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface-hover transition-colors focus:outline-none"
      >
        <Plus className="h-3.5 w-3.5" />
      </button>

      {isOpen && (
        <div className="absolute left-0 bottom-full mb-1 w-64 rounded-md border border-atlas-border-default bg-atlas-surface-2 shadow-xl z-50 p-1">
          <div className="px-2 py-1 text-[10px] font-semibold text-atlas-text-muted uppercase tracking-wider border-b border-atlas-border-subtle mb-1">
            New Terminal Session
          </div>
          <div className="space-y-0.5">
            {items.map((item) => {
              const Icon = item.icon;
              const cap = TERMINAL_CAPABILITIES_CATALOG[item.type];
              return (
                <button
                  key={item.type}
                  type="button"
                  onClick={() => {
                    onSelectType(item.type);
                    setIsOpen(false);
                  }}
                  className="w-full flex items-start gap-2.5 px-2 py-1.5 text-left rounded hover:bg-atlas-surface-hover transition-colors group"
                >
                  <Icon className="h-3.5 w-3.5 text-atlas-accent shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <div className="text-xs font-medium text-atlas-text-primary group-hover:text-atlas-accent">
                      {item.label}
                    </div>
                    <div className="text-[10px] text-atlas-text-muted truncate">
                      {cap.description}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

