"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ExternalLink,
  Lock,
  Layers,
  ArrowRight,
} from "lucide-react";
import { UserActivityItem } from "@/lib/activity/activity-types";
import { formatAbsoluteTime, formatRelativeTime } from "@/lib/activity/activity-format";
import { ATLAS_MODULES, AtlasModuleId } from "@/config/atlas-modules";
import { useSelectedEntity } from "@/hooks/entity";
import { useAuthorization } from "@/hooks/authorization";

interface HomeActivityRowProps {
  item: UserActivityItem;
}

export function HomeActivityRow({ item }: HomeActivityRowProps) {
  const router = useRouter();
  const { selectEntity } = useSelectedEntity();
  const { canViewModule } = useAuthorization();

  const isModuleEvent = item.event_type === "MODULE_OPENED";
  const moduleId = item.module_id as AtlasModuleId | undefined;
  const moduleConfig = moduleId ? ATLAS_MODULES[moduleId] : undefined;

  const isPermitted = isModuleEvent && moduleId ? canViewModule(moduleId) : item.is_accessible;

  const IconComponent = moduleConfig?.icon || Layers;
  const relativeTime = formatRelativeTime(item.occurred_at);
  const absoluteTime = formatAbsoluteTime(item.occurred_at);

  const handleEntityResume = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!item.entity_id || !item.is_accessible) return;
    selectEntity(item.entity_id);
    if (item.resume_target && item.resume_target.startsWith("/")) {
      router.push(item.resume_target);
    }
  };

  if (!isPermitted) {
    return (
      <div
        className="flex items-center justify-between p-2 rounded border border-atlas-border-subtle bg-atlas-surface-2/20 opacity-60 text-xs"
        aria-disabled="true"
      >
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="h-6 w-6 rounded bg-atlas-surface-3 flex items-center justify-center text-atlas-text-muted shrink-0">
            <Lock className="h-3 w-3" aria-hidden="true" />
          </div>
          <div className="min-w-0">
            <div className="font-medium text-atlas-text-muted truncate">
              {item.module_label || item.entity_display_name || "Restricted Item"}
            </div>
            <div className="text-[10px] text-atlas-text-muted/70">
              Access restricted
            </div>
          </div>
        </div>
        <time
          dateTime={item.occurred_at}
          title={absoluteTime}
          className="text-[10px] text-atlas-text-muted shrink-0 ml-2"
        >
          {relativeTime}
        </time>
      </div>
    );
  }

  return (
    <div className="group flex items-center justify-between p-2 rounded border border-atlas-border-subtle bg-atlas-surface-2/40 hover:bg-atlas-surface-2 hover:border-atlas-border-default transition-all text-xs">
      {/* Icon & Details */}
      <div className="flex items-center gap-2.5 min-w-0">
        <div className="h-7 w-7 rounded bg-atlas-surface-3 border border-atlas-border-subtle flex items-center justify-center text-atlas-text-secondary group-hover:text-atlas-accent group-hover:border-atlas-accent/40 transition-colors shrink-0">
          <IconComponent className="h-3.5 w-3.5" aria-hidden="true" />
        </div>
        <div className="min-w-0">
          <div className="font-medium text-atlas-text-primary group-hover:text-atlas-accent transition-colors truncate">
            {isModuleEvent
              ? (item.module_label || moduleConfig?.label || item.module_id)
              : (item.entity_display_name || "Universal Entity")}
          </div>
          <div className="text-[10px] text-atlas-text-muted truncate">
            {isModuleEvent ? "Opened workspace" : `Selected ${item.entity_type || "entity"}`}
          </div>
        </div>
      </div>

      {/* Timestamp & Resume Action */}
      <div className="flex items-center gap-2 shrink-0 ml-2">
        <time
          dateTime={item.occurred_at}
          title={absoluteTime}
          className="text-[11px] text-atlas-text-muted tabular-nums"
        >
          {relativeTime}
        </time>

        {isModuleEvent ? (
          <Link
            href={item.resume_target || moduleConfig?.route || "/"}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-hover border border-atlas-border-subtle hover:border-atlas-border-strong transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
            aria-label={`Reopen ${item.module_label || item.module_id} workspace`}
          >
            <span>Resume</span>
            <ArrowRight className="h-3 w-3 opacity-70 group-hover:opacity-100" aria-hidden="true" />
          </Link>
        ) : (
          <button
            type="button"
            onClick={handleEntityResume}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-hover border border-atlas-border-subtle hover:border-atlas-border-strong transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
            aria-label={`Select entity ${item.entity_display_name}`}
          >
            <span>Select</span>
            <ExternalLink className="h-3 w-3 opacity-70 group-hover:opacity-100" aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  );
}
