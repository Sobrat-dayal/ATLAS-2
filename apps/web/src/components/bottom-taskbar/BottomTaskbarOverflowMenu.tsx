"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { MoreHorizontal } from "lucide-react";
import { BottomPanelDefinition, BottomPanelId } from "@/lib/bottom-taskbar";

export interface BottomTaskbarOverflowMenuProps {
  panels: readonly BottomPanelDefinition[];
  activePanelId: BottomPanelId | null;
  onToggle: (id: BottomPanelId) => void;
}

export function BottomTaskbarOverflowMenu({
  panels,
  activePanelId,
  onToggle,
}: BottomTaskbarOverflowMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  // Outside click & Escape listener
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        handleClose();
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        handleClose();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, handleClose]);

  if (panels.length === 0) return null;

  const hasActiveItem = panels.some((p) => p.id === activePanelId);

  return (
    <div ref={menuRef} className="relative h-full flex items-center">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-label="More taskbar panels"
        title="More taskbar panels"
        className={`flex h-full items-center px-2.5 text-[11px] font-medium uppercase tracking-wider transition-colors select-none focus:outline-none focus:ring-1 focus:ring-atlas-accent ${
          hasActiveItem
            ? "text-atlas-accent bg-atlas-surface-selected"
            : "text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
        }`}
      >
        <MoreHorizontal className="h-3.5 w-3.5 mr-1 shrink-0" />
        <span className="hidden sm:inline">More</span>
      </button>

      {isOpen && (
        <div
          role="menu"
          aria-label="Additional taskbar panels"
          className="absolute bottom-full left-0 mb-1 w-48 rounded border border-atlas-border-default bg-atlas-surface-2 p-1 shadow-lg z-30 flex flex-col gap-0.5"
        >
          {panels.map((panel) => {
            const Icon = panel.icon;
            const isActive = panel.id === activePanelId;

            return (
              <button
                key={panel.id}
                type="button"
                role="menuitem"
                onClick={() => {
                  onToggle(panel.id);
                  handleClose();
                }}
                className={`flex w-full items-center px-2.5 py-1.5 text-xs rounded transition-colors text-left ${
                  isActive
                    ? "bg-atlas-surface-selected text-atlas-accent font-medium"
                    : "text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary"
                }`}
              >
                <Icon className="h-3.5 w-3.5 mr-2 shrink-0" />
                <span className="truncate">{panel.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
