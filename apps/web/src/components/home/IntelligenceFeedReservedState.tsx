"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Lock, Radio } from "lucide-react";
import { ATLAS_MODULES } from "@/config/atlas-modules";
import { useAuthorization } from "@/hooks/authorization";

export function IntelligenceFeedReservedState() {
  const { canViewModule } = useAuthorization();
  const isPermitted = canViewModule("intelligence");
  const intelligenceRoute = ATLAS_MODULES.intelligence.route;

  return (
    <div className="flex flex-col items-center justify-center text-center py-6 px-4 rounded border border-dashed border-atlas-border-subtle bg-atlas-surface-2/20 select-none">
      {/* Neutral icon - Section 83, 85, 86: Static neutral icon, no spinning radar or pulse */}
      <div className="h-8 w-8 rounded-full bg-atlas-surface-3 border border-atlas-border-subtle flex items-center justify-center text-atlas-text-muted mb-2.5">
        <Radio className="h-4 w-4" aria-hidden="true" />
      </div>

      {/* Heading - Section 70 */}
      <h4 className="text-xs font-semibold text-atlas-text-primary">
        Intelligence feed not connected
      </h4>

      {/* Accurate truthful copy - Section 70, 71 */}
      <p className="text-[11px] text-atlas-text-muted mt-1 max-w-sm leading-relaxed">
        Verified intelligence updates will appear here when the ATLAS Intelligence service becomes available.
      </p>

      {/* Safe workspace navigation button - Section 16, 92 */}
      {isPermitted ? (
        <Link
          href={intelligenceRoute}
          className="mt-3.5 inline-flex items-center gap-1.5 px-3 py-1 rounded bg-atlas-surface-2 hover:bg-atlas-surface-3 border border-atlas-border-subtle hover:border-atlas-border-strong text-atlas-text-primary text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal"
          aria-label="Open Intelligence Workspace"
        >
          <span>Open Intelligence Workspace</span>
          <ArrowRight className="h-3 w-3 text-atlas-text-secondary" aria-hidden="true" />
        </Link>
      ) : (
        <div className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded bg-atlas-surface-2 text-atlas-text-muted border border-atlas-border-subtle text-xs font-medium opacity-60 cursor-not-allowed">
          <Lock className="h-3 w-3" aria-hidden="true" />
          <span>Access Restricted</span>
        </div>
      )}
    </div>
  );
}
