"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { ExternalLink, Layers } from "lucide-react";
import { IntelligenceFeedViewItem } from "@/lib/intelligence-feed/types";
import { ATLAS_MODULES, AtlasModuleId } from "@/config/atlas-modules";
import { useSelectedEntity } from "@/hooks/entity";
import { useAuthorization } from "@/hooks/authorization";

interface IntelligenceFeedItemCardProps {
  item: IntelligenceFeedViewItem;
}

export function IntelligenceFeedItemCard({ item }: IntelligenceFeedItemCardProps) {
  const router = useRouter();
  const { selectEntity } = useSelectedEntity();
  const { canViewModule } = useAuthorization();

  const handleNavigate = () => {
    if (item.internalTarget?.entityId) {
      selectEntity(item.internalTarget.entityId);
    }
    if (item.internalTarget?.moduleId) {
      const targetModule = item.internalTarget.moduleId as AtlasModuleId;
      if (canViewModule(targetModule)) {
        router.push(ATLAS_MODULES[targetModule]?.route || `/${item.internalTarget.moduleId}`);
      }
    }
  };

  const formatTimestamp = (isoString?: string | null) => {
    if (!isoString) return null;
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoString;
    }
  };

  const formattedDate = formatTimestamp(item.observedAt);

  return (
    <div className="flex flex-col gap-1.5 p-2.5 rounded border border-atlas-border-subtle bg-atlas-surface-card hover:border-atlas-border-strong hover:bg-atlas-surface-hover transition-colors">
      {/* Top Badges / Metadata */}
      <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono">
        {item.sourceLabel && (
          <span className="px-1.5 py-0.5 rounded bg-atlas-surface-3 text-atlas-text-secondary border border-atlas-border-subtle">
            {item.sourceLabel}
            {item.sourceCount != null && item.sourceCount > 1 && ` (${item.sourceCount} sources)`}
          </span>
        )}

        {formattedDate && (
          <span className="text-atlas-text-muted">
            {formattedDate}
          </span>
        )}
      </div>

      {/* Title - Plain text only (Section 124, 125) */}
      <h4 className="text-xs font-medium text-atlas-text-primary leading-snug">
        {item.title}
      </h4>

      {/* Summary - Plain text only (Section 124, 125) */}
      {item.summary && (
        <p className="text-[11px] text-atlas-text-secondary line-clamp-2 leading-relaxed">
          {item.summary}
        </p>
      )}

      {/* Associated Canonical Entity Badges & Action */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-atlas-border-subtle/50 mt-0.5 text-[10px]">
        <div className="flex flex-wrap items-center gap-1">
          {item.entityIds && item.entityIds.length > 0 && (
            <div className="flex items-center gap-1 font-mono text-atlas-text-muted">
              <Layers className="h-2.5 w-2.5" aria-hidden="true" />
              <span>{item.entityIds.length} related entity</span>
            </div>
          )}
        </div>

        {item.internalTarget && (
          <button
            type="button"
            onClick={handleNavigate}
            className="inline-flex items-center gap-1 text-atlas-teal hover:underline focus-visible:outline-none"
            title="Navigate to related internal ATLAS module"
          >
            <span>Open Target</span>
            <ExternalLink className="h-2.5 w-2.5" aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  );
}
