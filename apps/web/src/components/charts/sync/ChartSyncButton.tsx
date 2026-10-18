"use client";

/**
 * Chart Synchronization Toolbar Button for ATLAS Workspace Header (Stage 73).
 *
 * Implements:
 * - Compact top toolbar button displaying current synchronization state
 * - Clear visual distinction between Independent mode and Active Sync Group
 * - Keyboard accessible popover toggle (Enter, Space, Escape)
 * - Integration with ChartSyncMenu popover
 */

import React, { useState, useRef, useEffect } from "react";
import { Link2, Unlink, ChevronDown } from "lucide-react";
import { useChartSync } from "@/hooks/charts";
import { MultiChartWorkspaceState } from "@/lib/charts/workspace";
import { ChartSyncMenu } from "./ChartSyncMenu";

export interface ChartSyncButtonProps {
  workspaceState: MultiChartWorkspaceState;
}

export function ChartSyncButton({ workspaceState }: ChartSyncButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const { groups } = useChartSync();

  // Find active group with member panels, or first group
  const activeLinkedGroup = groups.find(
    (g) => g.enabled && g.memberPanelIds.length > 0
  );

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setIsOpen(false);
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setIsOpen((prev) => !prev);
    }
  };

  const isLinked = !!activeLinkedGroup;
  const memberCount = activeLinkedGroup ? activeLinkedGroup.memberPanelIds.length : 0;

  return (
    <div className="relative inline-block" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        aria-haspopup="dialog"
        aria-expanded={isOpen}
        aria-label="Chart Synchronization Menu"
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono transition-all border shadow-sm ${
          isLinked
            ? "bg-cyan-950/60 border-cyan-500/80 text-cyan-200 hover:bg-cyan-950/80 hover:border-cyan-400"
            : "bg-zinc-900 border-zinc-800 text-zinc-300 hover:border-zinc-700 hover:text-zinc-100"
        }`}
        title={
          isLinked
            ? `Synchronized in ${activeLinkedGroup.name} (${memberCount} panels)`
            : "Chart Synchronization: Independent Mode"
        }
      >
        {isLinked ? (
          <Link2 className="w-3.5 h-3.5 text-cyan-400" />
        ) : (
          <Unlink className="w-3.5 h-3.5 text-zinc-500" />
        )}

        <span className="text-zinc-400">Sync:</span>

        {isLinked ? (
          <span className="font-semibold text-cyan-300 flex items-center gap-1">
            <span
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: activeLinkedGroup.color }}
            />
            {activeLinkedGroup.name} ({memberCount})
          </span>
        ) : (
          <span className="font-normal text-zinc-400">Independent</span>
        )}

        <ChevronDown
          className={`w-3 h-3 text-zinc-400 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      <ChartSyncMenu
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        workspaceState={workspaceState}
      />
    </div>
  );
}
