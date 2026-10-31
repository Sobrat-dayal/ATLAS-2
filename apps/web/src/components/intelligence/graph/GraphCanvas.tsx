'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AtlasEventEntityRelationship,
  CanonicalGraphNodeRef,
  GraphNodeType,
  PredicateType,
} from '@/lib/intelligence/graph/types';
import { NODE_TYPE_CONFIGS } from '@/lib/intelligence/graph/nodeTypes';
import { PREDICATE_REGISTRY, VERIFICATION_STATUS_META } from '@/lib/intelligence/graph/predicates';

interface GraphCanvasProps {
  nodes: CanonicalGraphNodeRef[];
  relationships: AtlasEventEntityRelationship[];
  selectedNodeKey?: string | null;
  selectedRelationshipId?: string | null;
  onSelectNode: (node: CanonicalGraphNodeRef) => void;
  onSelectRelationship: (rel: AtlasEventEntityRelationship) => void;
}

interface NodeLayout {
  node: CanonicalGraphNodeRef;
  x: number;
  y: number;
  radius: number;
}

export function GraphCanvas({
  nodes,
  relationships,
  selectedNodeKey,
  selectedRelationshipId,
  onSelectNode,
  onSelectRelationship,
}: GraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const [isPanning, setIsPanning] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [nodePositions, setNodePositions] = useState<Record<string, { x: number; y: number }>>({});
  const [draggingNodeKey, setDraggingNodeKey] = useState<string | null>(null);

  // Resize observer
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        setDimensions({
          width: Math.max(400, entry.contentRect.width),
          height: Math.max(400, entry.contentRect.height),
        });
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  // Compute circular / force-directed initial layout around center
  useEffect(() => {
    if (!nodes.length) return;
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    const newPositions: Record<string, { x: number; y: number }> = {};

    // Center node is typically the first node or the EVENT node
    const eventIndex = nodes.findIndex((n) => n.node_type === 'EVENT');
    const centerIdx = eventIndex >= 0 ? eventIndex : 0;

    const peripheral = nodes.filter((_, idx) => idx !== centerIdx);
    const radius = Math.min(dimensions.width, dimensions.height) * 0.35;

    // Position center node
    const cNode = nodes[centerIdx];
    const cKey = `${cNode.node_type}:${cNode.entity_id}`;
    newPositions[cKey] = { x: centerX, y: centerY };

    // Position peripheral nodes evenly along concentric circles
    peripheral.forEach((node, idx) => {
      const key = `${node.node_type}:${node.entity_id}`;
      const angle = (2 * Math.PI * idx) / Math.max(1, peripheral.length);
      const dist = peripheral.length > 8 && idx % 2 === 1 ? radius * 1.25 : radius;
      newPositions[key] = {
        x: centerX + dist * Math.cos(angle),
        y: centerY + dist * Math.sin(angle),
      };
    });

    setNodePositions(newPositions);
  }, [nodes, dimensions.width, dimensions.height]);

  // Handle pan
  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('.graph-node')) return;
    setIsPanning(true);
    setDragStart({ x: e.clientX - transform.x, y: e.clientY - transform.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (draggingNodeKey) {
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      const mouseX = (e.clientX - rect.left - transform.x) / transform.scale;
      const mouseY = (e.clientY - rect.top - transform.y) / transform.scale;
      setNodePositions((prev) => ({
        ...prev,
        [draggingNodeKey]: { x: mouseX, y: mouseY },
      }));
      return;
    }

    if (!isPanning) return;
    setTransform((prev) => ({
      ...prev,
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    }));
  };

  const handleMouseUp = () => {
    setIsPanning(false);
    setDraggingNodeKey(null);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    const newScale = Math.min(Math.max(transform.scale * zoomFactor, 0.4), 2.5);
    setTransform((prev) => ({ ...prev, scale: newScale }));
  };

  const resetView = () => {
    setTransform({ x: 0, y: 0, scale: 1 });
  };

  // Node layout items
  const layoutNodes: NodeLayout[] = useMemo(() => {
    return nodes.map((node) => {
      const key = `${node.node_type}:${node.entity_id}`;
      const pos = nodePositions[key] || {
        x: dimensions.width / 2,
        y: dimensions.height / 2,
      };
      const radius = node.node_type === 'EVENT' ? 32 : 24;
      return { node, x: pos.x, y: pos.y, radius };
    });
  }, [nodes, nodePositions, dimensions]);

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full min-h-[500px] bg-slate-950/70 border border-slate-800/80 rounded-xl overflow-hidden select-none"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
      role="region"
      aria-label="Interactive Knowledge Graph Topology Canvas"
    >
      {/* Zoom / Reset Controls */}
      <div className="absolute top-3 right-3 z-20 flex items-center gap-1.5 bg-slate-900/90 border border-slate-800/80 p-1 rounded-lg backdrop-blur shadow-lg">
        <button
          onClick={() => setTransform((prev) => ({ ...prev, scale: Math.min(prev.scale * 1.2, 2.5) }))}
          className="w-7 h-7 flex items-center justify-center text-slate-300 hover:text-white hover:bg-slate-800 rounded transition"
          title="Zoom In"
          aria-label="Zoom In"
        >
          +
        </button>
        <button
          onClick={() => setTransform((prev) => ({ ...prev, scale: Math.max(prev.scale * 0.8, 0.4) }))}
          className="w-7 h-7 flex items-center justify-center text-slate-300 hover:text-white hover:bg-slate-800 rounded transition"
          title="Zoom Out"
          aria-label="Zoom Out"
        >
          −
        </button>
        <button
          onClick={resetView}
          className="px-2 h-7 flex items-center justify-center text-xs text-slate-400 hover:text-white hover:bg-slate-800 rounded transition"
          title="Reset View"
        >
          Reset
        </button>
      </div>

      {/* SVG Canvas */}
      <svg
        className="w-full h-full cursor-grab active:cursor-grabbing"
        width={dimensions.width}
        height={dimensions.height}
      >
        <defs>
          {/* Arrow marker for directed predicates */}
          <marker
            id="arrowhead"
            viewBox="0 0 10 10"
            refX="22"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
          <marker
            id="arrowhead-active"
            viewBox="0 0 10 10"
            refX="22"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
          </marker>
        </defs>

        <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.scale})`}>
          {/* Edges / Relationships */}
          {relationships.map((rel) => {
            const sKey = `${rel.source_node.node_type}:${rel.source_node.entity_id}`;
            const tKey = `${rel.target_node.node_type}:${rel.target_node.entity_id}`;
            const sPos = nodePositions[sKey];
            const tPos = nodePositions[tKey];
            if (!sPos || !tPos) return null;

            const isSelected = selectedRelationshipId === rel.relationship_id;
            const midX = (sPos.x + tPos.x) / 2;
            const midY = (sPos.y + tPos.y) / 2;

            const predMeta = PREDICATE_REGISTRY[rel.predicate];
            const isNear = rel.predicate === 'GEOGRAPHICALLY_NEAR';

            return (
              <g
                key={rel.relationship_id}
                className="cursor-pointer group"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectRelationship(rel);
                }}
              >
                {/* Hit area line */}
                <line
                  x1={sPos.x}
                  y1={sPos.y}
                  x2={tPos.x}
                  y2={tPos.y}
                  stroke="transparent"
                  strokeWidth="16"
                />
                {/* Visible line */}
                <line
                  x1={sPos.x}
                  y1={sPos.y}
                  x2={tPos.x}
                  y2={tPos.y}
                  stroke={isSelected ? '#38bdf8' : isNear ? '#f59e0b' : '#475569'}
                  strokeWidth={isSelected ? 3 : isNear ? 2 : 1.5}
                  strokeDasharray={isNear ? '4 3' : undefined}
                  markerEnd={isSelected ? 'url(#arrowhead-active)' : 'url(#arrowhead)'}
                  className="transition-colors duration-150 group-hover:stroke-sky-400"
                />
                {/* Edge Label Badge */}
                <g transform={`translate(${midX}, ${midY})`}>
                  <rect
                    x="-45"
                    y="-9"
                    width="90"
                    height="18"
                    rx="4"
                    fill="#0f172a"
                    stroke={isSelected ? '#38bdf8' : '#334155'}
                    strokeWidth="1"
                    className="group-hover:stroke-sky-400 transition"
                  />
                  <text
                    x="0"
                    y="3"
                    textAnchor="middle"
                    fill={isSelected ? '#38bdf8' : '#94a3b8'}
                    fontSize="9"
                    fontFamily="monospace"
                    className="font-medium group-hover:fill-sky-300 pointer-events-none"
                  >
                    {predMeta?.label || rel.predicate}
                  </text>
                </g>
              </g>
            );
          })}

          {/* Nodes */}
          {layoutNodes.map(({ node, x, y, radius }) => {
            const key = `${node.node_type}:${node.entity_id}`;
            const isSelected = selectedNodeKey === key;
            const config = NODE_TYPE_CONFIGS[node.node_type] || NODE_TYPE_CONFIGS.OTHER_SUPPORTED_CANONICAL_ENTITY;

            return (
              <g
                key={key}
                className="graph-node cursor-pointer transition-transform group"
                transform={`translate(${x}, ${y})`}
                onMouseDown={(e) => {
                  e.stopPropagation();
                  setDraggingNodeKey(key);
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectNode(node);
                }}
              >
                {/* Selection halo */}
                {isSelected && (
                  <circle
                    r={radius + 7}
                    fill="none"
                    stroke="#38bdf8"
                    strokeWidth="2.5"
                    strokeDasharray="4 2"
                    className="animate-spin-slow opacity-90"
                  />
                )}

                {/* Node circle background */}
                <circle
                  r={radius}
                  fill={config.bgColor}
                  stroke={isSelected ? '#38bdf8' : config.borderColor}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                  className="group-hover:stroke-sky-400 group-hover:brightness-125 transition"
                />

                {/* Node icon or abbreviation */}
                <text
                  textAnchor="middle"
                  dy="4"
                  fill={config.color}
                  fontSize={radius > 26 ? '12' : '10'}
                  fontWeight="bold"
                  fontFamily="sans-serif"
                  className="pointer-events-none"
                >
                  {node.node_type === 'EVENT'
                    ? 'EVT'
                    : node.node_type === 'COMPANY'
                    ? 'CO'
                    : node.node_type === 'FINANCIAL_INSTRUMENT'
                    ? 'SEC'
                    : node.node_type.slice(0, 3)}
                </text>

                {/* Label under node */}
                <text
                  y={radius + 14}
                  textAnchor="middle"
                  fill={isSelected ? '#f8fafc' : '#cbd5e1'}
                  fontSize="11"
                  fontWeight={isSelected ? '600' : '400'}
                  className="pointer-events-none drop-shadow-md select-none"
                >
                  {node.canonical_name.length > 20
                    ? `${node.canonical_name.slice(0, 18)}...`
                    : node.canonical_name}
                </text>
              </g>
            );
          })}
        </g>
      </svg>

      {/* Legend */}
      <div className="absolute bottom-3 left-3 z-10 flex flex-wrap items-center gap-2 max-w-[80%] bg-slate-900/80 border border-slate-800/80 p-2 rounded-lg backdrop-blur text-xs text-slate-300">
        <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider">Topology:</span>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-sky-400"></span>
          <span>Event</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
          <span>Company</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-purple-400"></span>
          <span>Legal Entity</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-400"></span>
          <span>Instrument</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-orange-400"></span>
          <span>Infrastructure</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
          <span>Country</span>
        </div>
      </div>
    </div>
  );
}
