"use client";

import { HomeCurrentContext } from "./HomeCurrentContext";
import { HomeQuickLaunch } from "./HomeQuickLaunch";
import { HomeMarketSummary } from "./HomeMarketSummary";
import { HomePersonalizedActivity } from "./HomePersonalizedActivity";
import { HomeTasksApprovals } from "./HomeTasksApprovals";
import { HomeIntelligenceFeed } from "./HomeIntelligenceFeed";

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

        {/* 5. Stage 54 Real Home Tasks & Approvals Widget */}
        <HomeTasksApprovals />

        {/* 6. Stage 55 Home Intelligence Feed Placeholder Widget */}
        <HomeIntelligenceFeed />
      </div>
    </div>
  );
}
