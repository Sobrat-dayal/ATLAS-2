"use client";

import React from "react";
import { ATLAS_MODULES } from "@/config/atlas-modules";
import { PageHeader, AtlasFullscreen } from "@/design-system";
import { IntelligenceShell } from "@/components/intelligence/v1";

export default function IntelligencePage() {
  return (
    <div className="flex h-full flex-col overflow-hidden bg-black text-zinc-100">
      <div className="px-4 py-2 shrink-0 border-b border-zinc-800 z-10 relative bg-zinc-950">
        <PageHeader
          title={ATLAS_MODULES.intelligence.label}
          description="Institutional Financial Intelligence Workspace: Universal Events, Knowledge Graph, Financial Exposure & Physical Observations"
          className="mb-0 pb-0 border-b-0"
          actions={<AtlasFullscreen />}
        />
      </div>

      <div className="flex-1 overflow-hidden relative">
        <IntelligenceShell />
      </div>
    </div>
  );
}
