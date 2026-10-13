"use client";

import React from "react";
import { IntelligenceFeedViewState, IntelligenceFeedViewItem } from "@/lib/intelligence-feed/types";
import { HomeWidgetSurface } from "./HomeWidgetSurface";
import { IntelligenceFeedHeader } from "./IntelligenceFeedHeader";
import { IntelligenceFeedReservedState } from "./IntelligenceFeedReservedState";
import { IntelligenceFeedItemCard } from "./IntelligenceFeedItemCard";

interface HomeIntelligenceFeedProps {
  /**
   * Current feed view state.
   * In Stage 55, production status is permanently "reserved" until Stage 138 connects.
   */
  state?: IntelligenceFeedViewState;
  /**
   * Future intelligence view items.
   * In Stage 55 production, this is empty (zero fake items).
   */
  items?: IntelligenceFeedViewItem[];
}

export function HomeIntelligenceFeed({
  state = "reserved",
  items = [],
}: HomeIntelligenceFeedProps) {
  return (
    <HomeWidgetSurface
      id="home-intelligence-feed"
      title="Intelligence Feed"
      subtitle="Signals, events and connected intelligence"
    >
      <div className="flex flex-col gap-3 min-w-0">
        <IntelligenceFeedHeader
          statusLabel={state === "reserved" ? "Not Connected" : state}
        />

        {/* State-driven view rendering */}
        {state === "reserved" && <IntelligenceFeedReservedState />}

        {state === "ready" && items.length > 0 && (
          <div className="space-y-2">
            {items.map((item) => (
              <IntelligenceFeedItemCard key={item.id} item={item} />
            ))}
          </div>
        )}

        {state === "empty" && (
          <div className="py-6 px-4 text-center rounded border border-dashed border-atlas-border-subtle bg-atlas-surface-2/20">
            <p className="text-xs font-medium text-atlas-text-primary">
              No intelligence items available.
            </p>
          </div>
        )}

        {state === "loading" && (
          <div className="space-y-2 py-2" aria-label="Loading intelligence signals">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-14 rounded border border-atlas-border-subtle bg-atlas-surface-2/40 animate-pulse"
              />
            ))}
          </div>
        )}

        {state === "error" && (
          <div className="p-3 rounded border border-atlas-error/30 bg-atlas-error/10 text-xs text-atlas-error">
            Failed to connect to Intelligence service.
          </div>
        )}
      </div>
    </HomeWidgetSurface>
  );
}
