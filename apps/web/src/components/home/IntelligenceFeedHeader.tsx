"use client";

import React from "react";
import Link from "next/link";
import { ExternalLink, Lock, Radio } from "lucide-react";
import { ATLAS_MODULES } from "@/config/atlas-modules";
import { useAuthorization } from "@/hooks/authorization";

interface IntelligenceFeedHeaderProps {
  statusLabel?: string;
}

export function IntelligenceFeedHeader({
  statusLabel = "Not Connected",
}: IntelligenceFeedHeaderProps) {
  const { canViewModule } = useAuthorization();
  const isPermitted = canViewModule("intelligence");
  const intelligenceRoute = ATLAS_MODULES.intelligence.route;

  return (
    <div className="flex items-center justify-between gap-2 pb-2.5 border-b border-atlas-border-subtle select-none">
      <div className="flex items-center gap-2 min-w-0">
        <div className="h-6 w-6 rounded bg-atlas-surface-3 flex items-center justify-center text-atlas-text-secondary shrink-0 border border-atlas-border-subtle">
          <Radio className="h-3.5 w-3.5 text-atlas-text-muted" aria-hidden="true" />
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-xs font-semibold text-atlas-text-primary tracking-wide">
              Intelligence Feed
            </h3>
            {/* Neutral Status Badge - Section 12, 151, 152: Never deceptive green or live pulse */}
            <span
              className="inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-mono font-medium bg-atlas-surface-3 text-atlas-text-muted border border-atlas-border-subtle"
              title="Intelligence services are not yet connected in this roadmap stage"
            >
              {statusLabel}
            </span>
          </div>
          <p className="text-[11px] text-atlas-text-muted truncate">
            Research signals, events and connected intelligence.
          </p>
        </div>
      </div>

      {/* Navigation action - Section 16, 92: Safe internal route /intelligence */}
      <div className="shrink-0">
        {isPermitted ? (
          <Link
            href={intelligenceRoute}
            className="inline-flex items-center gap-1 px-2 py-1 rounded bg-atlas-surface-2 hover:bg-atlas-surface-3 border border-atlas-border-subtle hover:border-atlas-border-strong text-atlas-text-secondary hover:text-atlas-text-primary text-[11px] font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal"
            aria-label="Open Intelligence workspace"
            title="Navigate to the full Intelligence workspace"
          >
            <span>Open Intelligence</span>
            <ExternalLink className="h-3 w-3" aria-hidden="true" />
          </Link>
        ) : (
          <span
            className="inline-flex items-center gap-1 px-2 py-1 rounded bg-atlas-surface-2 text-atlas-text-muted border border-atlas-border-subtle text-[11px] font-medium opacity-60 cursor-not-allowed"
            title="You do not have permission to view the Intelligence module"
          >
            <Lock className="h-3 w-3" aria-hidden="true" />
            <span>Restricted</span>
          </span>
        )}
      </div>
    </div>
  );
}
