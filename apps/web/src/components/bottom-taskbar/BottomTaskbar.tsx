"use client";

import React from "react";
import { useBottomPanel } from "@/hooks/bottom-taskbar";
import {
  getPrimaryPanelDefinitions,
  getTrailingPanelDefinitions,
} from "@/lib/bottom-taskbar";
import { BottomTaskbarItem } from "./BottomTaskbarItem";
import { BottomTaskbarOverflowMenu } from "./BottomTaskbarOverflowMenu";

export function BottomTaskbar() {
  const { activePanelId, togglePanel } = useBottomPanel();
  const primaryPanels = getPrimaryPanelDefinitions();
  const trailingPanels = getTrailingPanelDefinitions();

  // Responsive division: first 3 panels always visible, others visible on sm+/md+ or overflow menu on very small screens
  const alwaysVisiblePrimary = primaryPanels.slice(0, 3);
  const secondaryPrimary = primaryPanels.slice(3);

  return (
    <footer
      role="toolbar"
      aria-label="Application Taskbar"
      className="flex h-8 w-full shrink-0 items-center justify-between border-t border-atlas-border-default bg-atlas-surface-1 px-1.5 sm:px-2 text-[11px] font-medium tracking-wider select-none z-10"
    >
      {/* Primary items (Left aligned) */}
      <div className="flex h-full items-center overflow-x-hidden">
        {/* Always visible on all screens */}
        {alwaysVisiblePrimary.map((panel) => (
          <BottomTaskbarItem
            key={panel.id}
            panel={panel}
            isActive={activePanelId === panel.id}
            onToggle={togglePanel}
          />
        ))}

        {/* Visible on sm+ screens */}
        <div className="hidden md:flex h-full items-center">
          {secondaryPrimary.map((panel) => (
            <BottomTaskbarItem
              key={panel.id}
              panel={panel}
              isActive={activePanelId === panel.id}
              onToggle={togglePanel}
            />
          ))}
        </div>

        {/* Overflow Menu on mobile / narrow viewports */}
        <div className="flex md:hidden h-full items-center">
          <BottomTaskbarOverflowMenu
            panels={secondaryPrimary}
            activePanelId={activePanelId}
            onToggle={togglePanel}
          />
        </div>
      </div>

      {/* Trailing items (Right aligned) — Terminal */}
      <div className="flex h-full items-center">
        {trailingPanels.map((panel) => (
          <BottomTaskbarItem
            key={panel.id}
            panel={panel}
            isActive={activePanelId === panel.id}
            onToggle={togglePanel}
            className="border-l border-atlas-border-subtle pl-3"
          />
        ))}
      </div>
    </footer>
  );
}
