"use client";

import * as React from "react";
import { Panel, PanelProps, PanelImperativeHandle } from "react-resizable-panels";
import { cn } from "../utils/cn";

export interface AtlasPanelProps extends PanelProps {
  id: string; // Enforce id in v4 layout
  children: React.ReactNode;
  className?: string;
  scrollable?: boolean;
}

export const AtlasPanel = React.forwardRef<PanelImperativeHandle, AtlasPanelProps>(
  ({ id, children, className, scrollable = false, ...props }, ref) => {
    return (
      <Panel panelRef={ref} id={id} {...props}>
        <div 
          className={cn(
            "h-full w-full",
            scrollable ? "overflow-auto custom-scrollbar" : "overflow-hidden",
            className
          )}
        >
          {children}
        </div>
      </Panel>
    );
  }
);

AtlasPanel.displayName = "AtlasPanel";
