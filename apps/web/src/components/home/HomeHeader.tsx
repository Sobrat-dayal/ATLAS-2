"use client";

import React from "react";
import { HomeQuickActions } from "./HomeQuickActions";

export interface HomeHeaderProps {
  title?: string;
  subtitle?: string;
}

export function HomeHeader({
  title = "ATLAS Overview",
  subtitle = "Your financial intelligence workspace.",
}: HomeHeaderProps) {
  return (
    <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-atlas-border-default">
      <div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-atlas-accent animate-pulse" aria-hidden="true" />
          <h1 className="text-lg md:text-xl font-semibold text-atlas-text-primary tracking-tight">
            {title}
          </h1>
        </div>
        <p className="text-xs md:text-sm text-atlas-text-secondary mt-0.5">
          {subtitle}
        </p>
      </div>

      <HomeQuickActions />
    </header>
  );
}
