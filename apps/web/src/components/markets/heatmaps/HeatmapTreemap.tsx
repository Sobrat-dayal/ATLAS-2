"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  HeatmapGroupNode,
  HeatmapHierarchyMode,
  HeatmapLeafNode,
  computeHierarchicalTreemap,
  computeSquarifiedLayout,
  formatSignedPercent,
} from "@/lib/markets/heatmaps";
import { HeatmapTile } from "./HeatmapTile";
import { ChevronRight, ArrowLeft } from "lucide-react";

interface HeatmapTreemapProps {
  nodes: HeatmapLeafNode[];
  groups: HeatmapGroupNode[];
  hierarchyMode: HeatmapHierarchyMode;
  selectedNode: HeatmapLeafNode | null;
  onSelectNode: (node: HeatmapLeafNode) => void;
  drilldownSector: string | null;
  onDrilldownSector: (sector: string | null) => void;
  weightUnit?: string | null;
}

export function HeatmapTreemap({
  nodes,
  groups,
  hierarchyMode,
  selectedNode,
  onSelectNode,
  drilldownSector,
  onDrilldownSector,
  weightUnit = "USD",
}: HeatmapTreemapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Measure container dimensions dynamically
  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        if (width > 0 && height > 0) {
          setDimensions({
            width: Math.floor(width),
            height: Math.max(Math.floor(height), 480),
          });
        }
      }
    });

    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  // Compute hierarchical or flat treemap layout
  const hierarchicalLayout = useMemo(() => {
    if (hierarchyMode !== "sector" || groups.length === 0) return null;
    return computeHierarchicalTreemap(groups, dimensions.width, dimensions.height);
  }, [hierarchyMode, groups, dimensions.width, dimensions.height]);

  const flatLayout = useMemo(() => {
    if (hierarchyMode === "sector" && groups.length > 0) return null;

    const items = nodes.map((node) => {
      const w =
        typeof node.normalized_weight === "string"
          ? parseFloat(node.normalized_weight)
          : typeof node.normalized_weight === "number"
          ? node.normalized_weight
          : typeof node.weight_value === "string"
          ? parseFloat(node.weight_value)
          : typeof node.weight_value === "number"
          ? node.weight_value
          : 1;

      return {
        id: node.node_id,
        weight: Math.max(w, 0.0001),
        data: node,
      };
    });

    return computeSquarifiedLayout(items, 0, 0, dimensions.width, dimensions.height);
  }, [hierarchyMode, groups, nodes, dimensions.width, dimensions.height]);

  return (
    <div className="flex flex-col gap-2 w-full">
      {/* Breadcrumbs for Drilldown */}
      {drilldownSector && (
        <div className="flex items-center gap-2 px-2 py-1 text-xs text-[var(--atlas-text-secondary)] border-b border-[var(--atlas-border-subtle)]">
          <button
            type="button"
            onClick={() => onDrilldownSector(null)}
            className="flex items-center gap-1 hover:text-[var(--atlas-text-primary)] transition-colors text-[var(--atlas-accent-primary)] font-medium"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>All Sectors</span>
          </button>
          <ChevronRight className="w-3 h-3 text-[var(--atlas-text-tertiary)]" />
          <span className="font-semibold text-[var(--atlas-text-primary)]">
            {drilldownSector}
          </span>
        </div>
      )}

      {/* Main Treemap Canvas Container */}
      <div
        ref={containerRef}
        style={{ height: `${dimensions.height}px` }}
        className="relative w-full rounded-lg bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] overflow-hidden shadow-inner select-none min-h-[500px]"
      >
        {/* Hierarchical Sector Groups */}
        {hierarchicalLayout &&
          hierarchicalLayout.map((groupRect) => (
            <div
              key={groupRect.group.group_id}
              style={{
                position: "absolute",
                left: `${groupRect.x}px`,
                top: `${groupRect.y}px`,
                width: `${groupRect.width}px`,
                height: `${groupRect.height}px`,
              }}
              className="border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-base)]/50 rounded-sm overflow-hidden"
            >
              {/* Sector Header */}
              {groupRect.headerHeight > 0 && (
                <div
                  role="button"
                  tabIndex={0}
                  onClick={() => onDrilldownSector(groupRect.group.label)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      onDrilldownSector(groupRect.group.label);
                    }
                  }}
                  className="flex items-center justify-between px-2 h-[26px] bg-[var(--atlas-surface-elevated)]/90 border-b border-[var(--atlas-border-subtle)] text-[10px] cursor-pointer hover:bg-[var(--atlas-surface-elevated)] transition-colors"
                  title={`Drill down into ${groupRect.group.label}`}
                >
                  <div className="flex items-center gap-1.5 truncate">
                    <span className="font-semibold text-[var(--atlas-text-primary)] truncate">
                      {groupRect.group.label}
                    </span>
                    <span className="text-[var(--atlas-text-tertiary)] font-mono">
                      ({groupRect.group.constituent_count})
                    </span>
                  </div>

                  {groupRect.group.aggregate_return !== undefined && groupRect.group.aggregate_return !== null && (
                    <span
                      className={`font-mono font-semibold px-1 py-0.2 rounded text-[9px] ${
                        Number(groupRect.group.aggregate_return) >= 0
                          ? "text-emerald-400 bg-emerald-950/60"
                          : "text-red-400 bg-red-950/60"
                      }`}
                      title={`Aggregate return: ${formatSignedPercent(groupRect.group.aggregate_return)} (${groupRect.group.aggregate_method})`}
                    >
                      {formatSignedPercent(groupRect.group.aggregate_return)}
                    </span>
                  )}
                </div>
              )}

              {/* Nested Constituent Tiles */}
              <div className="relative w-full h-full">
                {groupRect.children.map((tileRect) => (
                  <HeatmapTile
                    key={tileRect.id}
                    rect={{
                      ...tileRect,
                      // Translate tile coordinates relative to the sector container
                      x: tileRect.x - groupRect.x,
                      y: tileRect.y - (groupRect.y + groupRect.headerHeight),
                    }}
                    isSelected={selectedNode?.node_id === tileRect.data.node_id}
                    onSelect={onSelectNode}
                    weightUnit={weightUnit}
                  />
                ))}
              </div>
            </div>
          ))}

        {/* Flat Ungrouped Treemap */}
        {flatLayout &&
          flatLayout.map((tileRect) => (
            <HeatmapTile
              key={tileRect.id}
              rect={tileRect}
              isSelected={selectedNode?.node_id === tileRect.data.node_id}
              onSelect={onSelectNode}
              weightUnit={weightUnit}
            />
          ))}
      </div>
    </div>
  );
}
