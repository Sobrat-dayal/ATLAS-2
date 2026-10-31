"use client";

import React, { useState } from "react";
import { ATLAS_MODULES } from "@/config/atlas-modules";
import { PageHeader } from "@/design-system";
import { UniversalEventExplorer } from "@/components/events/UniversalEventExplorer";
import { Radio, Activity, Globe } from "lucide-react";

export default function IntelligencePage() {
  const [activeTab, setActiveTab] = useState<"universal_events" | "signals">("universal_events");

  return (
    <div className="flex h-full flex-col bg-black text-zinc-100">
      <div className="px-4 py-2.5 shrink-0 border-b border-zinc-800 bg-zinc-950 flex flex-wrap items-center justify-between gap-3">
        <div>
          <PageHeader
            title={ATLAS_MODULES.intelligence.label}
            description={ATLAS_MODULES.intelligence.description}
            className="mb-0 pb-0 border-b-0"
          />
        </div>

        {/* Intelligence View Switcher */}
        <div className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 rounded p-0.5 text-xs font-mono">
          <button
            onClick={() => setActiveTab("universal_events")}
            className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
              activeTab === "universal_events"
                ? "bg-blue-600 text-white font-semibold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Radio className="w-3.5 h-3.5 text-blue-300" />
            <span>Universal Event Model (Stage 135)</span>
          </button>

          <button
            onClick={() => setActiveTab("signals")}
            className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 ${
              activeTab === "signals"
                ? "bg-blue-600 text-white font-semibold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Globe className="w-3.5 h-3.5 text-emerald-400" />
            <span>Signal Map</span>
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        {activeTab === "universal_events" ? (
          <UniversalEventExplorer />
        ) : (
          <div className="flex h-full items-center justify-center p-8 text-center text-zinc-500 font-mono text-sm border m-4 border-dashed border-zinc-800 rounded-lg">
            <div className="space-y-2">
              <Globe className="w-8 h-8 text-zinc-600 mx-auto" />
              <p>Global Real-Time Signal Geospatial Grid</p>
              <p className="text-xs text-zinc-600">Integrated with Stage 129–134 Spatial Engine</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
