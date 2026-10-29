"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchDependencyLineageResponse,
} from "@/lib/research/types";

interface ResearchDependencyLineageViewerProps {
  lineage: ResearchDependencyLineageResponse | null;
  isLoading: boolean;
  onRefresh?: () => void;
  onSelectNode?: (nodeId: string, nodeType: string) => void;
}

export function ResearchDependencyLineageViewer({
  lineage,
  isLoading,
  onRefresh,
  onSelectNode,
}: ResearchDependencyLineageViewerProps) {
  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
        Computing multi-hop dependency lineage graph...
      </div>
    );
  }

  if (!lineage) {
    return (
      <div className="flex h-64 flex-col items-center justify-center p-6 text-center text-xs text-atlas-text-muted border border-atlas-border-default rounded-sm bg-atlas-surface-1">
        <p className="font-medium text-atlas-text-primary">No Dependency Lineage Active</p>
        <p className="mt-1 text-atlas-text-muted">Select an artifact to inspect its upstream source dependencies and downstream deliverables.</p>
      </div>
    );
  }

  const { root_resource_type, root_resource_id, nodes, edges, has_cycle, max_depth_reached } = lineage;

  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 border border-atlas-border-default rounded-sm overflow-hidden">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-atlas-border-default px-4 py-3 bg-atlas-surface-1">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Dependency Lineage Graph
            </span>
            <Badge variant="outline" className="font-mono text-[10px]">
              Root: {root_resource_type}/{root_resource_id}
            </Badge>
          </div>
          {has_cycle && (
            <Badge variant="negative" className="text-[10px] font-bold">
              Cycle Detected
            </Badge>
          )}
          {max_depth_reached && (
            <Badge variant="warning" className="text-[10px]">
              Max Depth Reached
            </Badge>
          )}
        </div>
        {onRefresh && (
          <Button variant="ghost" size="xs" onClick={onRefresh}>
            ↻ Refresh Graph
          </Button>
        )}
      </div>

      {/* Main Graph Layout */}
      <div className="flex-1 overflow-auto p-4 space-y-6">
        {/* Discovered Nodes List */}
        <div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-atlas-text-muted mb-2">
            Lineage Nodes ({nodes.length})
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {nodes.map((node) => {
              const isRoot = node.id === root_resource_id;
              return (
                <div
                  key={node.id}
                  onClick={() => onSelectNode?.(node.id, node.type)}
                  className={`p-2.5 rounded-sm border cursor-pointer transition-all ${
                    isRoot
                      ? "border-atlas-accent bg-atlas-accent/10 shadow-xs"
                      : "border-atlas-border-default bg-atlas-surface-1 hover:border-atlas-border-hover hover:bg-atlas-surface-hover"
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <Badge
                      variant={isRoot ? "primary" : "outline"}
                      className="font-mono text-[9px] uppercase"
                    >
                      {node.type}
                    </Badge>
                    {isRoot && (
                      <span className="text-[9px] font-bold text-atlas-accent uppercase tracking-wider">
                        Target Root
                      </span>
                    )}
                  </div>
                  <div className="font-mono text-xs font-semibold text-atlas-text-primary truncate" title={node.id}>
                    {node.id}
                  </div>
                  {node.label && (
                    <div className="text-[11px] text-atlas-text-secondary truncate mt-0.5" title={node.label}>
                      {node.label}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Directed Lineage Edges */}
        <div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-atlas-text-muted mb-2">
            Directed Provenance Edges ({edges.length})
          </div>
          {edges.length === 0 ? (
            <div className="p-4 text-center text-xs text-atlas-text-muted bg-atlas-surface-1 rounded-sm border border-atlas-border-default">
              No dependency edges recorded for this artifact.
            </div>
          ) : (
            <div className="space-y-2">
              {edges.map((edge) => (
                <div
                  key={edge.edge_id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-sm border border-atlas-border-default bg-atlas-surface-1 text-xs gap-2"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <div className="font-mono bg-atlas-surface-0 px-2 py-0.5 rounded-xs border border-atlas-border-default text-[11px] text-atlas-text-secondary">
                      <span className="text-atlas-text-muted">[{edge.upstream_resource_type}]</span>{" "}
                      {edge.upstream_resource_id}
                    </div>
                    <span className="text-atlas-accent font-bold">➔</span>
                    <Badge variant="outline" className="font-mono text-[9px]">
                      {edge.dependency_type.replace(/_/g, " ")}
                    </Badge>
                    <span className="text-atlas-accent font-bold">➔</span>
                    <div className="font-mono bg-atlas-surface-0 px-2 py-0.5 rounded-xs border border-atlas-border-default text-[11px] text-atlas-text-primary font-medium">
                      <span className="text-atlas-text-muted">[{edge.downstream_resource_type}]</span>{" "}
                      {edge.downstream_resource_id}
                    </div>
                  </div>

                  {edge.source_reference && (
                    <div className="text-[10px] text-atlas-text-muted truncate max-w-xs font-sans">
                      Ref: {edge.source_reference}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
