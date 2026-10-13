"use client";

import { HomeCurrentContext } from "./HomeCurrentContext";
import { HomeQuickLaunch } from "./HomeQuickLaunch";
import { HomeMarketSummary } from "./HomeMarketSummary";
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
      </div>

      {/* Right / Secondary Column (5 cols on lg) */}
      <div className="lg:col-span-5 flex flex-col gap-5 min-w-0">
        {/* 3. Quick Launch Canonical Modules */}
        <HomeQuickLaunch />

        {/* 4. Future Operations & Intelligence Framework Slot (Stages 53 - 55) */}
        <HomeWidgetSurface
          id="home-operations-framework"
          title="Operations & Intelligence"
          subtitle="Stages 53–55 Framework Slot"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <HomeReservedState
              stage={53}
              featureName="Personalized Activity"
              description="Recent entities, queries, and module history."
            />
            <HomeReservedState
              stage={54}
              featureName="Tasks & Approvals"
              description="Pending workflow tasks and action queues."
            />
          </div>
        </HomeWidgetSurface>
      </div>
    </div>
  );
}
