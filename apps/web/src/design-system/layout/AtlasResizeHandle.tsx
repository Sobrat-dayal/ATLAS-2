"use client";

import * as React from "react";
import { Separator, SeparatorProps } from "react-resizable-panels";
import { cn } from "../utils/cn";

export interface AtlasResizeHandleProps extends SeparatorProps {
  className?: string;
  withHandleIcon?: boolean;
}

export function AtlasResizeHandle({ 
  className, 
  withHandleIcon = false,
  ...props 
}: AtlasResizeHandleProps) {
  return (
    <Separator
      className={cn(
        "relative flex w-1.5 shrink-0 items-center justify-center bg-transparent transition-colors hover:bg-atlas-blue/20 active:bg-atlas-blue/40 hover:cursor-col-resize active:cursor-col-resize z-10",
        // Horizontal support (when parent group is vertical, handle is horizontal)
        "data-[panel-group-direction=vertical]:h-1.5 data-[panel-group-direction=vertical]:w-full data-[panel-group-direction=vertical]:hover:cursor-row-resize data-[panel-group-direction=vertical]:active:cursor-row-resize",
        // Visual divider
        "after:absolute after:inset-y-0 after:left-1/2 after:w-px after:-translate-x-1/2 after:bg-atlas-border-default",
        "data-[panel-group-direction=vertical]:after:inset-x-0 data-[panel-group-direction=vertical]:after:top-1/2 data-[panel-group-direction=vertical]:after:h-px data-[panel-group-direction=vertical]:after:w-full data-[panel-group-direction=vertical]:after:-translate-y-1/2",
        className
      )}
      {...props}
    >
      {withHandleIcon && (
        <div className="z-10 flex h-4 w-3 items-center justify-center rounded-sm border border-atlas-border-strong bg-atlas-surface-2 data-[panel-group-direction=vertical]:h-3 data-[panel-group-direction=vertical]:w-4">
          <svg className="h-2.5 w-2.5 text-atlas-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
          </svg>
        </div>
      )}
    </Separator>
  );
}
