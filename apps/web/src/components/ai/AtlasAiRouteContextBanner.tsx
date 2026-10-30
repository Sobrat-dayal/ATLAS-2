"use client";

import { usePathname } from "next/navigation";
import { Compass } from "lucide-react";
import { getRouteContext } from "@/lib/ai/routeRegistry";

export function AtlasAiRouteContextBanner() {
  const pathname = usePathname();
  const routeContext = getRouteContext(pathname);

  return (
    <div className="flex items-center justify-between border-b border-atlas-border-default/60 bg-atlas-surface-2/40 px-3 py-1.5 text-[11px] text-atlas-text-secondary">
      <div className="flex items-center gap-1.5 overflow-hidden">
        <Compass className="h-3 w-3 shrink-0 text-atlas-accent" />
        <span className="font-medium text-atlas-text-primary">
          {routeContext.module_name}
        </span>
        <span className="font-mono text-[10px] text-atlas-text-muted">
          ({routeContext.route})
        </span>
      </div>
      <span className="text-[10px] text-atlas-text-muted truncate max-w-[180px] hidden sm:inline" title={routeContext.summary}>
        {routeContext.summary}
      </span>
    </div>
  );
}

