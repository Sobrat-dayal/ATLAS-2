"use client";

import React, { useMemo, useState } from "react";
import {
  Building2,
  Cpu,
  Layers,
  ShieldCheck,
  Truck,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Info,
  ExternalLink,
} from "lucide-react";
import {
  SupplyChainEdgeDTO,
  SupplyChainNetworkResponseDTO,
  SupplyChainNodeDTO,
} from "@/lib/companies/supply-chain";

interface SupplyChainNetworkGraphProps {
  network: SupplyChainNetworkResponseDTO | null;
  onSelectNode?: (node: SupplyChainNodeDTO) => void;
  onInspectEdge?: (relationshipId: string) => void;
  depth: number;
  setDepth: (depth: number) => void;
  direction: string;
  setDirection: (dir: string) => void;
}

export function SupplyChainNetworkGraph({
  network,
  onSelectNode,
  onInspectEdge,
  depth,
  setDepth,
  direction,
  setDirection,
}: SupplyChainNetworkGraphProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [hoveredEdgeId, setHoveredEdgeId] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  // Group nodes by visual columns
  const layout = useMemo(() => {
    if (!network || !network.nodes.length) {
      return { nodesWithPos: [], edgesWithPos: [], width: 1100, height: 600 };
    }

    const tier2Nodes: SupplyChainNodeDTO[] = [];
    const tier1SupplierNodes: SupplyChainNodeDTO[] = [];
    let subjectNode: SupplyChainNodeDTO | null = null;
    const tier1CustomerNodes: SupplyChainNodeDTO[] = [];

    // Distinguish supplier vs customer from edge sources/targets
    const subjectId = network.subject_company_entity_id;
    const directSuppliers = new Set<string>();
    const directCustomers = new Set<string>();

    network.edges.forEach((edge) => {
      if (edge.target === subjectId) {
        directSuppliers.add(edge.source);
      } else if (edge.source === subjectId) {
        directCustomers.add(edge.target);
      }
    });

    network.nodes.forEach((node) => {
      if (node.is_subject || node.entity_id === subjectId) {
        subjectNode = node;
      } else if (node.tier === 2) {
        tier2Nodes.push(node);
      } else if (directSuppliers.has(node.entity_id)) {
        tier1SupplierNodes.push(node);
      } else if (directCustomers.has(node.entity_id)) {
        tier1CustomerNodes.push(node);
      } else {
        tier1SupplierNodes.push(node);
      }
    });

    const colX = {
      tier2: 120,
      tier1Sup: 400,
      subject: 700,
      tier1Cust: 980,
    };

    const nodePositions = new Map<string, { x: number; y: number }>();

    // Calculate Y spacing
    const maxRows = Math.max(
      tier2Nodes.length,
      tier1SupplierNodes.length,
      tier1CustomerNodes.length,
      1
    );
    const rowHeight = 72;
    const startY = 80;
    const totalHeight = Math.max(560, startY + maxRows * rowHeight + 40);

    // Position Subject
    if (subjectNode) {
      nodePositions.set((subjectNode as SupplyChainNodeDTO).entity_id, {
        x: colX.subject,
        y: totalHeight / 2,
      });
    }

    // Position Tier 1 Suppliers
    const t1SupSpacing = totalHeight / (tier1SupplierNodes.length + 1);
    tier1SupplierNodes.forEach((node, idx) => {
      nodePositions.set(node.entity_id, {
        x: colX.tier1Sup,
        y: (idx + 1) * t1SupSpacing,
      });
    });

    // Position Tier 2 Suppliers
    const t2Spacing = totalHeight / (tier2Nodes.length + 1);
    tier2Nodes.forEach((node, idx) => {
      nodePositions.set(node.entity_id, {
        x: colX.tier2,
        y: (idx + 1) * t2Spacing,
      });
    });

    // Position Tier 1 Customers
    const t1CustSpacing = totalHeight / (tier1CustomerNodes.length + 1);
    tier1CustomerNodes.forEach((node, idx) => {
      nodePositions.set(node.entity_id, {
        x: colX.tier1Cust,
        y: (idx + 1) * t1CustSpacing,
      });
    });

    const nodesWithPos = network.nodes.map((node) => {
      const pos = nodePositions.get(node.entity_id) || { x: colX.subject, y: totalHeight / 2 };
      return { ...node, ...pos };
    });

    const edgesWithPos = network.edges.map((edge) => {
      const srcPos = nodePositions.get(edge.source) || { x: 0, y: 0 };
      const tgtPos = nodePositions.get(edge.target) || { x: 0, y: 0 };
      return { ...edge, srcPos, tgtPos };
    });

    return { nodesWithPos, edgesWithPos, width: 1160, height: totalHeight };
  }, [network]);

  const activeNode = useMemo(() => {
    if (!selectedNodeId || !network) return null;
    return network.nodes.find((n) => n.entity_id === selectedNodeId) || null;
  }, [selectedNodeId, network]);

  if (!network) {
    return (
      <div className="p-8 text-center text-atlas-text-muted bg-atlas-surface border border-atlas-border-subtle rounded-md">
        No network graph data available.
      </div>
    );
  }

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded-md overflow-hidden flex flex-col">
      {/* Controls Bar */}
      <div className="p-3 border-b border-atlas-border-subtle flex flex-wrap items-center justify-between gap-3 bg-atlas-surface-subtle/40">
        <div className="flex items-center gap-4">
          {/* Depth Control */}
          <div className="flex items-center gap-1 text-xs">
            <span className="text-atlas-text-muted text-[11px] font-medium mr-1 flex items-center gap-1">
              <Layers className="w-3 h-3 text-atlas-accent" />
              Graph Depth:
            </span>
            <button
              onClick={() => setDepth(1)}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                depth === 1
                  ? "bg-blue-600 text-white"
                  : "bg-atlas-surface border border-atlas-border-subtle text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Tier 1 (Direct)
            </button>
            <button
              onClick={() => setDepth(2)}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                depth === 2
                  ? "bg-purple-600 text-white"
                  : "bg-atlas-surface border border-atlas-border-subtle text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Tier 2 (Multi-Tier)
            </button>
            <button
              onClick={() => setDepth(3)}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                depth === 3
                  ? "bg-indigo-600 text-white"
                  : "bg-atlas-surface border border-atlas-border-subtle text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Tier 3 (Deep)
            </button>
          </div>

          {/* Direction Control */}
          <div className="flex items-center gap-1 text-xs border-l border-atlas-border-subtle pl-3">
            <span className="text-atlas-text-muted text-[11px] font-medium mr-1">Direction:</span>
            <button
              onClick={() => setDirection("BOTH")}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                direction === "BOTH"
                  ? "bg-atlas-surface-subtle text-atlas-text-primary border border-atlas-border-subtle font-semibold"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              Full Chain
            </button>
            <button
              onClick={() => setDirection("UPSTREAM")}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                direction === "UPSTREAM"
                  ? "bg-atlas-surface-subtle text-atlas-text-primary border border-atlas-border-subtle font-semibold"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              Upstream Only
            </button>
            <button
              onClick={() => setDirection("DOWNSTREAM")}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                direction === "DOWNSTREAM"
                  ? "bg-atlas-surface-subtle text-atlas-text-primary border border-atlas-border-subtle font-semibold"
                  : "text-atlas-text-muted hover:text-atlas-text-primary"
              }`}
            >
              Downstream Only
            </button>
          </div>
        </div>

        {/* Zoom & Reset Controls */}
        <div className="flex items-center gap-1.5 text-xs">
          <button
            onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.1))}
            className="p-1 bg-atlas-surface border border-atlas-border-subtle rounded text-atlas-text-muted hover:text-atlas-text-primary"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="font-mono text-[11px] text-atlas-text-muted px-1">
            {Math.round(zoomLevel * 100)}%
          </span>
          <button
            onClick={() => setZoomLevel((z) => Math.min(1.4, z + 0.1))}
            className="p-1 bg-atlas-surface border border-atlas-border-subtle rounded text-atlas-text-muted hover:text-atlas-text-primary"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => {
              setZoomLevel(1);
              setSelectedNodeId(null);
            }}
            className="p-1 bg-atlas-surface border border-atlas-border-subtle rounded text-atlas-text-muted hover:text-atlas-text-primary ml-1"
            title="Reset View"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div className="relative overflow-auto bg-[#090d16] min-h-[560px] flex items-center justify-center p-4 select-none">
        {/* Network Column Labels */}
        <div className="absolute top-3 left-0 right-0 px-6 flex justify-between pointer-events-none text-[10px] font-mono uppercase tracking-wider text-atlas-text-muted/60">
          <div className="w-[200px] text-left">Tier-2 Precursors</div>
          <div className="w-[200px] text-center">Tier-1 Direct Suppliers</div>
          <div className="w-[180px] text-center font-bold text-blue-400/80">Subject Entity</div>
          <div className="w-[200px] text-right">Downstream Customers</div>
        </div>

        <svg
          width={layout.width * zoomLevel}
          height={layout.height * zoomLevel}
          viewBox={`0 0 ${layout.width} ${layout.height}`}
          className="transition-transform duration-150"
        >
          <defs>
            {/* Arrow Marker for supplier -> customer flow */}
            <marker
              id="arrow-default"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#3b82f6" fillOpacity="0.7" />
            </marker>
            <marker
              id="arrow-hover"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="7"
              markerHeight="7"
              orient="auto-start-reverse"
            >
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#60a5fa" />
            </marker>
            <marker
              id="arrow-downstream"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#10b981" fillOpacity="0.7" />
            </marker>
          </defs>

          {/* Render Directed Edges */}
          {layout.edgesWithPos.map((edge) => {
            const isHovered = hoveredEdgeId === edge.relationship_id;
            const isConnectedToSelected =
              selectedNodeId &&
              (edge.source === selectedNodeId || edge.target === selectedNodeId);
            const isDownstream = edge.source === network.subject_company_entity_id;

            // Generate cubic bezier curve
            const dx = edge.tgtPos.x - edge.srcPos.x;
            const curveFactor = 0.5;
            const pathD = `M ${edge.srcPos.x + 85} ${edge.srcPos.y} C ${
              edge.srcPos.x + 85 + dx * curveFactor
            } ${edge.srcPos.y}, ${edge.tgtPos.x - 85 - dx * curveFactor} ${
              edge.tgtPos.y
            }, ${edge.tgtPos.x - 85} ${edge.tgtPos.y}`;

            const strokeColor = isHovered
              ? "#60a5fa"
              : isConnectedToSelected
              ? "#93c5fd"
              : isDownstream
              ? "#10b98188"
              : "#3b82f666";

            const markerId = isHovered
              ? "url(#arrow-hover)"
              : isDownstream
              ? "url(#arrow-downstream)"
              : "url(#arrow-default)";

            return (
              <g
                key={edge.relationship_id}
                className="cursor-pointer group"
                onMouseEnter={() => setHoveredEdgeId(edge.relationship_id)}
                onMouseLeave={() => setHoveredEdgeId(null)}
                onClick={() => onInspectEdge && onInspectEdge(edge.relationship_id)}
              >
                {/* Invisible wide path for easy click/hover */}
                <path d={pathD} fill="none" stroke="transparent" strokeWidth="16" />
                {/* Visible curve */}
                <path
                  d={pathD}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={isHovered || isConnectedToSelected ? "2.5" : "1.5"}
                  markerEnd={markerId}
                  className="transition-all duration-150"
                />
              </g>
            );
          })}

          {/* Render Nodes */}
          {layout.nodesWithPos.map((node) => {
            const isSubject = node.is_subject;
            const isSelected = selectedNodeId === node.entity_id;
            const cardWidth = isSubject ? 180 : 160;
            const cardHeight = isSubject ? 56 : 48;

            return (
              <g
                key={node.entity_id}
                transform={`translate(${node.x - cardWidth / 2}, ${node.y - cardHeight / 2})`}
                className="cursor-pointer"
                onClick={() => {
                  setSelectedNodeId(node.entity_id);
                  if (onSelectNode) onSelectNode(node);
                }}
              >
                {/* Node Box */}
                <rect
                  width={cardWidth}
                  height={cardHeight}
                  rx="6"
                  ry="6"
                  fill={
                    isSubject
                      ? "#1e293b"
                      : isSelected
                      ? "#1e3a8a"
                      : "#0f172a"
                  }
                  stroke={
                    isSubject
                      ? "#3b82f6"
                      : isSelected
                      ? "#60a5fa"
                      : node.tier === 2
                      ? "#7c3aed66"
                      : "#334155"
                  }
                  strokeWidth={isSubject || isSelected ? "2" : "1"}
                  className="transition-colors duration-150 drop-shadow-md"
                />

                {/* Node Text & Badges */}
                <text
                  x="12"
                  y="20"
                  fill="#f8fafc"
                  fontSize={isSubject ? "12" : "11"}
                  fontWeight={isSubject ? "600" : "500"}
                  className="pointer-events-none"
                >
                  {node.name.length > 20 ? node.name.slice(0, 18) + "..." : node.name}
                </text>

                <text
                  x="12"
                  y="36"
                  fill="#94a3b8"
                  fontSize="9"
                  fontFamily="monospace"
                  className="pointer-events-none"
                >
                  {node.country} • {isSubject ? "CORE SUBJECT" : `Tier ${node.tier}`}
                </text>

                {/* Tier Badge on top-right */}
                {!isSubject && (
                  <circle
                    cx={cardWidth - 14}
                    cy="14"
                    r="4"
                    fill={node.tier === 1 ? "#3b82f6" : "#a855f7"}
                    className="pointer-events-none"
                  />
                )}
              </g>
            );
          })}
        </svg>

        {/* Selected Node Details Floating Overlay */}
        {activeNode && (
          <div className="absolute bottom-4 left-4 p-3 bg-atlas-surface/95 border border-atlas-border-subtle rounded-md shadow-xl backdrop-blur-md max-w-sm text-xs z-10">
            <div className="flex items-center justify-between mb-1.5">
              <span className="font-semibold text-atlas-text-primary flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5 text-blue-400" />
                {activeNode.name}
              </span>
              <button
                onClick={() => setSelectedNodeId(null)}
                className="text-atlas-text-muted hover:text-atlas-text-primary text-[10px]"
              >
                ✕
              </button>
            </div>
            <div className="text-[11px] text-atlas-text-secondary space-y-1">
              <div>
                <span className="text-atlas-text-muted">Entity Kind:</span> {activeNode.kind}
              </div>
              <div>
                <span className="text-atlas-text-muted">Jurisdiction:</span> {activeNode.country}
              </div>
              <div>
                <span className="text-atlas-text-muted">Sector / Industry:</span>{" "}
                {activeNode.industry || activeNode.sector}
              </div>
              <div>
                <span className="text-atlas-text-muted">Tier Position:</span> Tier {activeNode.tier}{" "}
                {activeNode.is_subject ? "(Subject)" : ""}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-2.5 border-t border-atlas-border-subtle bg-atlas-surface-subtle/50 text-[11px] text-atlas-text-muted flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-atlas-accent shrink-0" />
          <span>
            Material flow direction: <strong className="text-blue-400">SUPPLIER</strong> provides
            components/services to <strong className="text-emerald-400">CUSTOMER</strong>. Click any
            connecting edge to inspect verified regulatory evidence.
          </span>
        </div>
        <div className="font-mono text-[10px]">
          Nodes: {network.node_count} | Edges: {network.edge_count}
        </div>
      </div>
    </div>
  );
}
