"use client";

import React from "react";
import Link from "next/link";
import {
  Building2,
  FileText,
  Globe,
  Box,
  TrendingUp,
  X,
  AlertCircle,
  Loader2,
  Search,
  ExternalLink,
  RotateCw,
} from "lucide-react";
import { useSelectedEntity } from "@/hooks/entity";
import { useCommandPalette } from "@/hooks/commands";
import { HomeWidgetSurface } from "./HomeWidgetSurface";

export function HomeCurrentContext() {
  const {
    selectedEntityId,
    selectedEntity,
    status,
    error,
    clearSelectedEntity,
    refreshSelectedEntity,
  } = useSelectedEntity();

  const { triggerSearchFocus } = useCommandPalette();

  const humanizeType = (type?: string) => {
    if (!type) return "Universal Entity";
    return type
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const getEntityIcon = (type?: string) => {
    switch (type?.toLowerCase()) {
      case "company":
        return <Building2 className="h-4 w-4" aria-hidden="true" />;
      case "security":
      case "equity":
      case "etf":
      case "index":
      case "crypto":
        return <TrendingUp className="h-4 w-4" aria-hidden="true" />;
      case "research_document":
      case "document":
        return <FileText className="h-4 w-4" aria-hidden="true" />;
      case "country":
      case "geographic_entity":
      case "region":
        return <Globe className="h-4 w-4" aria-hidden="true" />;
      default:
        return <Box className="h-4 w-4" aria-hidden="true" />;
    }
  };

  return (
    <HomeWidgetSurface
      id="current-context"
      title="Current Focus"
      subtitle="Universal Entity Context"
      actions={
        selectedEntityId && (
          <button
            type="button"
            onClick={clearSelectedEntity}
            className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-hover rounded transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
            aria-label="Clear selected entity"
          >
            <X className="h-3 w-3" aria-hidden="true" />
            <span>Clear selection</span>
          </button>
        )
      }
    >
      {/* 1. Loading State */}
      {status === "loading" && (
        <div className="flex items-center gap-3 py-6 px-4 bg-atlas-surface-2/40 rounded border border-atlas-border-subtle">
          <Loader2 className="h-5 w-5 animate-spin text-atlas-accent" aria-hidden="true" />
          <div>
            <p className="text-xs font-medium text-atlas-text-primary">
              Fetching entity metadata...
            </p>
            <p className="text-[11px] text-atlas-text-muted mt-0.5 font-mono">
              ID: {selectedEntityId}
            </p>
          </div>
        </div>
      )}

      {/* 2. Error State */}
      {status === "error" && (
        <div className="flex flex-col gap-2 p-4 bg-red-950/20 border border-red-500/30 rounded">
          <div className="flex items-center gap-2 text-red-400">
            <AlertCircle className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
            <p className="text-xs font-semibold">Failed to load entity context</p>
          </div>
          <p className="text-[11px] text-red-300/80">
            {error?.message || "An error occurred retrieving canonical entity metadata."}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <button
              type="button"
              onClick={() => refreshSelectedEntity()}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-red-500/20 hover:bg-red-500/30 text-red-200 border border-red-500/40 rounded transition-colors"
            >
              <RotateCw className="h-3 w-3" aria-hidden="true" />
              <span>Retry</span>
            </button>
            <button
              type="button"
              onClick={clearSelectedEntity}
              className="px-2 py-1 text-xs text-atlas-text-secondary hover:text-atlas-text-primary transition-colors"
            >
              Clear selection
            </button>
          </div>
        </div>
      )}

      {/* 3. Empty State (No Entity Selected) */}
      {!selectedEntityId && status !== "loading" && status !== "error" && (
        <div className="flex flex-col items-center justify-center text-center p-6 bg-atlas-surface-2/20 border border-dashed border-atlas-border-subtle rounded-sm">
          <div className="h-8 w-8 rounded-full bg-atlas-surface-3 border border-atlas-border-default flex items-center justify-center text-atlas-text-muted mb-3">
            <Box className="h-4 w-4" aria-hidden="true" />
          </div>
          <h3 className="text-xs font-semibold text-atlas-text-primary">
            No entity selected
          </h3>
          <p className="text-[11px] text-atlas-text-muted mt-1 max-w-xs">
            Search ATLAS to select a company, security, country, or another supported universal entity.
          </p>
          <button
            type="button"
            onClick={() => triggerSearchFocus()}
            className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-sm bg-atlas-surface-2 hover:bg-atlas-surface-hover border border-atlas-border-default hover:border-atlas-border-strong text-atlas-text-primary transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
          >
            <Search className="h-3.5 w-3.5 text-atlas-text-secondary" aria-hidden="true" />
            <span>Search Entities</span>
          </button>
        </div>
      )}

      {/* 4. Ready State (Entity Selected) */}
      {selectedEntityId && status === "ready" && selectedEntity && (
        <div className="flex flex-col gap-3">
          <div className="flex items-start justify-between gap-3 p-3 bg-atlas-surface-2/60 rounded border border-atlas-border-default">
            <div className="flex items-start gap-3 min-w-0">
              <div className="h-9 w-9 rounded bg-atlas-surface-3 border border-atlas-border-default flex items-center justify-center text-atlas-accent flex-shrink-0 mt-0.5">
                {getEntityIcon(selectedEntity.entity_type)}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-sm font-semibold text-atlas-text-primary truncate">
                    {selectedEntity.display_name || selectedEntity.canonical_name}
                  </h3>
                  <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider rounded bg-atlas-surface-3 text-atlas-text-secondary border border-atlas-border-subtle">
                    {humanizeType(selectedEntity.entity_type)}
                  </span>
                </div>
                {selectedEntity.canonical_name &&
                  selectedEntity.canonical_name !== selectedEntity.display_name && (
                    <p className="text-[11px] text-atlas-text-muted mt-0.5 truncate">
                      Canonical: {selectedEntity.canonical_name}
                    </p>
                  )}
                <p className="text-[10px] font-mono text-atlas-text-muted mt-1 truncate">
                  UUID: {selectedEntity.entity_id}
                </p>
              </div>
            </div>
          </div>

          {/* Quick Context Launch Links (Preserve Selected Entity) */}
          <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
            <span className="text-[11px] text-atlas-text-muted">Analyze in:</span>
            {selectedEntity.entity_type?.toLowerCase() === "company" && (
              <Link
                href="/companies"
                className="inline-flex items-center gap-1 px-2 py-1 text-[11px] font-medium bg-atlas-surface-2 hover:bg-atlas-surface-hover text-atlas-text-primary border border-atlas-border-default rounded transition-colors"
              >
                <span>Company Overview</span>
                <ExternalLink className="h-3 w-3 text-atlas-text-muted" aria-hidden="true" />
              </Link>
            )}
            {(selectedEntity.entity_type?.toLowerCase() === "security" ||
              selectedEntity.entity_type?.toLowerCase() === "equity") && (
              <Link
                href="/charts"
                className="inline-flex items-center gap-1 px-2 py-1 text-[11px] font-medium bg-atlas-surface-2 hover:bg-atlas-surface-hover text-atlas-text-primary border border-atlas-border-default rounded transition-colors"
              >
                <span>Chart Instrument</span>
                <ExternalLink className="h-3 w-3 text-atlas-text-muted" aria-hidden="true" />
              </Link>
            )}
            <Link
              href="/research"
              className="inline-flex items-center gap-1 px-2 py-1 text-[11px] font-medium bg-atlas-surface-2 hover:bg-atlas-surface-hover text-atlas-text-primary border border-atlas-border-default rounded transition-colors"
            >
              <span>Research</span>
              <ExternalLink className="h-3 w-3 text-atlas-text-muted" aria-hidden="true" />
            </Link>
            <Link
              href="/markets"
              className="inline-flex items-center gap-1 px-2 py-1 text-[11px] font-medium bg-atlas-surface-2 hover:bg-atlas-surface-hover text-atlas-text-primary border border-atlas-border-default rounded transition-colors"
            >
              <span>Markets</span>
              <ExternalLink className="h-3 w-3 text-atlas-text-muted" aria-hidden="true" />
            </Link>
          </div>
        </div>
      )}
    </HomeWidgetSurface>
  );
}
