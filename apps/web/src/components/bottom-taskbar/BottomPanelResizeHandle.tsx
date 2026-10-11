"use client";

import React, { useCallback, useRef } from "react";
import {
  DEFAULT_BOTTOM_PANEL_HEIGHT,
  MIN_BOTTOM_PANEL_HEIGHT,
  clampBottomPanelHeight,
} from "@/lib/bottom-taskbar";

export interface BottomPanelResizeHandleProps {
  panelHeight: number;
  onHeightChange: (height: number) => void;
  onResetHeight?: () => void;
}

export function BottomPanelResizeHandle({
  panelHeight,
  onHeightChange,
  onResetHeight,
}: BottomPanelResizeHandleProps) {
  const isDraggingRef = useRef(false);
  const startYRef = useRef(0);
  const startHeightRef = useRef(panelHeight);

  const handlePointerDown = useCallback(
    (e: React.PointerEvent<HTMLDivElement>) => {
      // Only primary button
      if (e.button !== 0) return;
      isDraggingRef.current = true;
      startYRef.current = e.clientY;
      startHeightRef.current = panelHeight;

      const target = e.currentTarget;
      target.setPointerCapture(e.pointerId);

      const handlePointerMove = (moveEvent: PointerEvent) => {
        if (!isDraggingRef.current) return;
        // Dragging upward (negative deltaY) increases panel height
        const deltaY = moveEvent.clientY - startYRef.current;
        const newHeight = startHeightRef.current - deltaY;
        const clamped = clampBottomPanelHeight(newHeight, window.innerHeight);
        onHeightChange(clamped);
      };

      const handlePointerUp = (upEvent: PointerEvent) => {
        isDraggingRef.current = false;
        try {
          target.releasePointerCapture(upEvent.pointerId);
        } catch {
          // ignore if already released
        }
        window.removeEventListener("pointermove", handlePointerMove);
        window.removeEventListener("pointerup", handlePointerUp);
        window.removeEventListener("pointercancel", handlePointerUp);
      };

      window.addEventListener("pointermove", handlePointerMove);
      window.addEventListener("pointerup", handlePointerUp);
      window.addEventListener("pointercancel", handlePointerUp);
    },
    [panelHeight, onHeightChange]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      const step = 16;
      if (e.key === "ArrowUp") {
        e.preventDefault();
        onHeightChange(clampBottomPanelHeight(panelHeight + step, window.innerHeight));
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        onHeightChange(clampBottomPanelHeight(panelHeight - step, window.innerHeight));
      } else if (e.key === "Home") {
        e.preventDefault();
        onHeightChange(MIN_BOTTOM_PANEL_HEIGHT);
      } else if (e.key === "End") {
        e.preventDefault();
        onHeightChange(clampBottomPanelHeight(9999, window.innerHeight));
      } else if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        onHeightChange(DEFAULT_BOTTOM_PANEL_HEIGHT);
      }
    },
    [panelHeight, onHeightChange]
  );

  const handleDoubleClick = useCallback(() => {
    if (onResetHeight) {
      onResetHeight();
    } else {
      onHeightChange(DEFAULT_BOTTOM_PANEL_HEIGHT);
    }
  }, [onResetHeight, onHeightChange]);

  const maxAllowed = clampBottomPanelHeight(9999, typeof window !== "undefined" ? window.innerHeight : 900);

  return (
    <div
      role="separator"
      tabIndex={0}
      aria-orientation="horizontal"
      aria-label="Resize bottom workspace panel"
      aria-valuenow={panelHeight}
      aria-valuemin={MIN_BOTTOM_PANEL_HEIGHT}
      aria-valuemax={maxAllowed}
      onPointerDown={handlePointerDown}
      onKeyDown={handleKeyDown}
      onDoubleClick={handleDoubleClick}
      title="Drag to resize panel, double-click to reset, or use ArrowUp / ArrowDown"
      className="group absolute top-0 left-0 right-0 h-1.5 -translate-y-1/2 cursor-row-resize select-none z-20 flex items-center justify-center focus:outline-none focus:ring-1 focus:ring-atlas-accent"
    >
      {/* Visual divider line */}
      <div className="h-[2px] w-full bg-atlas-border-default group-hover:bg-atlas-accent transition-colors" />

      {/* Center grab pill affordance */}
      <div className="absolute h-1 w-8 rounded-full bg-atlas-border-strong group-hover:bg-atlas-accent transition-colors" />
    </div>
  );
}
