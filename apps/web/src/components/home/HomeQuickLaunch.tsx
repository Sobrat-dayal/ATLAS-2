"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ChevronDown, ChevronUp, ArrowRight, Lock } from "lucide-react";
import { useAuthorization } from "@/hooks/authorization";
import { useActivityRecorder } from "@/hooks/home/useActivityRecorder";
import { getCuratedQuickLaunchItems, getAllQuickLaunchItems } from "@/lib/home/quick-launch";
import { HomeWidgetSurface } from "./HomeWidgetSurface";

export function HomeQuickLaunch() {
  const [showAllModules, setShowAllModules] = useState(false);
  const { canViewModule } = useAuthorization();
  const { recordModuleOpened } = useActivityRecorder();

  const curatedItems = getCuratedQuickLaunchItems();
  const allItems = getAllQuickLaunchItems();
  const displayItems = showAllModules ? allItems : curatedItems;

  return (
    <HomeWidgetSurface
      id="quick-launch"
      title="Quick Launch"
      subtitle={showAllModules ? "All Canonical Workspaces (20)" : "Core Workspaces (10)"}
      actions={
        <button
          type="button"
          onClick={() => setShowAllModules((prev) => !prev)}
          className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-hover rounded transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
          aria-expanded={showAllModules}
          aria-label={showAllModules ? "Show curated workspaces only" : "View all 20 workspaces"}
        >
          <span>{showAllModules ? "Show Curated" : "View All (20)"}</span>
          {showAllModules ? (
            <ChevronUp className="h-3 w-3" aria-hidden="true" />
          ) : (
            <ChevronDown className="h-3 w-3" aria-hidden="true" />
          )}
        </button>
      }
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {displayItems.map((item) => {
          const isPermitted = canViewModule(item.id);
          const Icon = item.icon;

          if (!isPermitted) {
            return (
              <div
                key={item.id}
                className="flex items-start gap-2.5 p-2.5 rounded border border-atlas-border-subtle bg-atlas-surface-2/20 opacity-50 cursor-not-allowed"
                aria-disabled="true"
                title="Access restricted by role permissions"
              >
                <div className="h-7 w-7 rounded bg-atlas-surface-3 flex items-center justify-center text-atlas-text-muted flex-shrink-0">
                  <Lock className="h-3.5 w-3.5" aria-hidden="true" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-semibold text-atlas-text-muted truncate">
                    {item.label}
                  </div>
                  <div className="text-[10px] text-atlas-text-muted/70 line-clamp-1 mt-0.5">
                    Restricted
                  </div>
                </div>
              </div>
            );
          }

          return (
            <Link
              key={item.id}
              href={item.route}
              onClick={() => recordModuleOpened(item.id)}
              className="group flex items-start gap-2.5 p-2.5 rounded border border-atlas-border-default bg-atlas-surface-2/40 hover:bg-atlas-surface-2 hover:border-atlas-border-strong transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
              aria-label={`Open ${item.label} workspace`}
            >
              <div className="h-7 w-7 rounded bg-atlas-surface-3 border border-atlas-border-subtle group-hover:border-atlas-accent/40 flex items-center justify-center text-atlas-text-secondary group-hover:text-atlas-accent flex-shrink-0 transition-colors">
                <Icon className="h-3.5 w-3.5" aria-hidden="true" />
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-1">
                  <span className="text-xs font-semibold text-atlas-text-primary group-hover:text-atlas-accent transition-colors truncate">
                    {item.label}
                  </span>
                  <ArrowRight className="h-3 w-3 text-atlas-text-muted group-hover:text-atlas-accent group-hover:translate-x-0.5 transition-all opacity-0 group-hover:opacity-100 flex-shrink-0" aria-hidden="true" />
                </div>
                <p className="text-[10px] text-atlas-text-muted line-clamp-1 mt-0.5">
                  {item.description}
                </p>
              </div>
            </Link>
          );
        })}
      </div>
    </HomeWidgetSurface>
  );
}
