"use client";

import React from "react";
import { HomeHeader } from "./HomeHeader";
import { HomeDashboardGrid } from "./HomeDashboardGrid";

export function HomePage() {
  return (
    <div className="p-4 md:p-6 space-y-5 max-w-[1600px] mx-auto w-full min-w-0">
      <HomeHeader />
      <HomeDashboardGrid />
    </div>
  );
}
