"use client";

import { HomeCurrentContext } from "./HomeCurrentContext";
import { HomeQuickLaunch } from "./HomeQuickLaunch";
import { HomeMarketSummary } from "./HomeMarketSummary";
import { HomePersonalizedActivity } from "./HomePersonalizedActivity";
import { HomeWidgetSurface } from "./HomeWidgetSurface";
import { HomeReservedState } from "./HomeReservedState";

export function HomeDashboardGrid() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 min-w-0">
      {/* Left / Primary Column (7 cols on lg) */}
      <div className="lg:col-span-7 flex flex-col gap-5 min-w-0">
        {/* 1. Universal Entity Focus Context */}
        <HomeCurrentContext />

        {/* 2. Stage 52 Real Home Market Summary Widget */}
        <HomeMarketSummary />

        {/* 3. Stage 53 Real Home Personalized Activity Widget */}
        <HomePersonalizedActivity />
      </div>

      {/* Right / Secondary Column (5 cols on lg) */}
      <div className="lg:col-span-5 flex flex-col gap-5 min-w-0">
        {/* 4. Quick Launch Canonical Modules */}
        <HomeQuickLaunch />

        {/* 5. Future Operations & Intelligence Framework Slot (Stages 54 - 55) */}
        <HomeWidgetSurface
          id="home-operations-framework"
          title="Operations & Intelligence"
          subtitle="Stages 54–55 Framework Slot"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <HomeReservedState
              stage={54}
              featureName="Tasks & Approvals"
              description="Pending workflow tasks and action queues."
            />
            <HomeReservedState
              stage={55}
              featureName="Intelligence Feed"
              description="Prioritized signals, anomalies, and narrative alerts."
            />
          </div>
        </HomeWidgetSurface>
      </div>
    </div>
  );
}
