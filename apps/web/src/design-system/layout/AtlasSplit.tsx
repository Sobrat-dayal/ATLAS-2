"use client";

import * as React from "react";
import { Group, GroupProps, Layout } from "react-resizable-panels";
import { cn } from "../utils/cn";
import { getLayoutState, setLayoutState } from "./AtlasLayoutStorage";

// Since Group layout in v4 is a dictionary/map by Panel ID, we use Layout
export interface AtlasSplitProps extends Omit<GroupProps, "direction" | "orientation" | "defaultLayout" | "onLayoutChange"> {
  id: string; // Required for persistence
  direction: "horizontal" | "vertical";
  className?: string;
  defaultLayout?: number[] | Layout; // Support array for backward compat if needed
}

export function AtlasSplit({
  id,
  direction,
  className,
  defaultLayout,
  children,
  ...props
}: AtlasSplitProps) {
  const [isClient, setIsClient] = React.useState(false);
  const layoutCache = React.useRef<Layout | undefined>(undefined);

  React.useEffect(() => {
    setIsClient(true);
    const saved = getLayoutState(id);
    if (saved && !Array.isArray(saved)) {
      // we assume it's saved as an object map in layout state if it's v4
      layoutCache.current = saved;
    } else if (defaultLayout && !Array.isArray(defaultLayout)) {
      layoutCache.current = defaultLayout;
    }
  }, [id, defaultLayout]);

  const handleLayoutChange = React.useCallback(
    (layout: Layout) => {
      setLayoutState(id, layout);
    },
    [id]
  );

  return (
    <Group
      id={id}
      orientation={direction}
      className={cn("w-full h-full", className)}
      onLayoutChanged={(layout) => handleLayoutChange(layout)}
      {...(isClient && layoutCache.current ? { defaultLayout: layoutCache.current } : {})}
      {...props}
    >
      {children}
    </Group>
  );
}
