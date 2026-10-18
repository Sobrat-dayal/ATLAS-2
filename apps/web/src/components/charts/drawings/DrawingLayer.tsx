"use client";

/**
 * Interactive SVG Drawing Layer Component for ATLAS Charts (Stage 71).
 *
 * Implements:
 * - High-DPI crisp SVG vector drawing layer directly aligned with chart canvas.
 * - Dynamic projection of financial { time, price } coordinates to screen { x, y }.
 * - Interactive drawing creation with real-time transient preview.
 * - Smart snapping to canonical qualified OHLC observations.
 * - Non-intrusive pass-through: chart pan & zoom works when not editing drawings.
 * - Precise hit-testing and anchor handle dragging.
 * - Whole-drawing translation.
 * - Full keyboard shortcuts (Escape, Del, Ctrl+Z, Ctrl+Shift+Z).
 * - Full rendering for all 9 canonical drawing tools.
 */

import React, { useEffect, useMemo, useRef, useState } from "react";
import { IChartApi, ISeriesApi } from "lightweight-charts";
import { ChartBarDTO } from "@/lib/charts/types";
import {
  DrawingAnchor,
  DrawingObject,
  DrawingType,
  RenderedAnchor,
  ScreenPoint,
  SnappingMode,
} from "@/lib/charts/drawings/types";
import { CoordinateMapper } from "@/lib/charts/drawings/coordinateMapper";
import { strokeStyleToDashArray } from "@/lib/charts/drawings/geometry";
import { resolveSnapping, SnapTargetResult } from "@/lib/charts/drawings/snapping";
import {
  calculateCombinedMeasurement,
  calculatePriceMeasurement,
  calculateTimeMeasurement,
} from "@/lib/charts/drawings/measurements";
import { calculateFibonacciLevels } from "@/lib/charts/drawings/fibonacci";
import { drawingStore } from "@/lib/charts/drawings/drawingStore";

export interface DrawingLayerProps {
  chart: IChartApi | null;
  series: ISeriesApi<any> | null;
  bars: ChartBarDTO[];
  width: number;
  height: number;
  activeTool: DrawingType | null;
  snappingMode: SnappingMode;
  selectedDrawingId: string | null;
  onSelectDrawing: (id: string | null) => void;
  onDrawingCreated?: (drawing: DrawingObject) => void;
}

export function DrawingLayer({
  chart,
  series,
  bars,
  width,
  height,
  activeTool,
  snappingMode,
  selectedDrawingId,
  onSelectDrawing,
  onDrawingCreated,
}: DrawingLayerProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [, setViewportTick] = useState(0);

  // Initialize coordinate mapper
  const coordinateMapper = useMemo(() => {
    if (!chart || !series) return null;
    return new CoordinateMapper({ chart, series, bars });
  }, [chart, series, bars]);

  // Subscribe to chart viewport changes (pan, zoom) to re-project anchors
  useEffect(() => {
    if (!chart) return;
    const timeScale = chart.timeScale();

    const handleRangeChange = () => {
      setViewportTick((t) => t + 1);
    };

    timeScale.subscribeVisibleLogicalRangeChange(handleRangeChange);
    return () => {
      timeScale.unsubscribeVisibleLogicalRangeChange(handleRangeChange);
    };
  }, [chart]);

  // Deselect on empty chart click
  useEffect(() => {
    if (!chart) return;
    const handleClick = () => {
      if (!activeTool) {
        onSelectDrawing(null);
      }
    };

    chart.subscribeClick(handleClick);
    return () => {
      chart.unsubscribeClick(handleClick);
    };
  }, [chart, activeTool, onSelectDrawing]);

  // Sync bars with coordinate mapper
  useEffect(() => {
    if (coordinateMapper) {
      coordinateMapper.updateBars(bars);
    }
  }, [coordinateMapper, bars]);

  // Current session drawings
  const drawings = drawingStore.getDrawings();

  // Creation State
  const [creationAnchors, setCreationAnchors] = useState<DrawingAnchor[]>([]);
  const [currentPointer, setCurrentPointer] = useState<ScreenPoint | null>(null);
  const [activeSnapTarget, setActiveSnapTarget] = useState<SnapTargetResult | null>(null);

  // Dragging State (for moving an existing drawing or dragging an anchor)
  const [draggingMode, setDraggingMode] = useState<"NONE" | "ANCHOR" | "WHOLE">("NONE");
  const [draggedDrawingId, setDraggedDrawingId] = useState<string | null>(null);
  const [draggedAnchorIndex, setDraggedAnchorIndex] = useState<number>(-1);
  const [dragStartPointer, setDragStartPointer] = useState<ScreenPoint | null>(null);
  const [dragStartAnchors, setDragStartAnchors] = useState<DrawingAnchor[]>([]);

  // Keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
        return;
      }

      // Escape: Cancel creation or deselect
      if (e.key === "Escape") {
        e.preventDefault();
        setCreationAnchors([]);
        drawingStore.setActiveTool(null);
        drawingStore.setSelectedDrawingId(null);
        setDraggingMode("NONE");
        return;
      }

      // Delete / Backspace: Delete selected drawing
      if (e.key === "Delete" || e.key === "Backspace") {
        if (selectedDrawingId) {
          e.preventDefault();
          drawingStore.deleteDrawing(selectedDrawingId);
        }
        return;
      }

      // Undo: Ctrl+Z / Cmd+Z
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && !e.shiftKey) {
        e.preventDefault();
        drawingStore.undo();
        return;
      }

      // Redo: Ctrl+Shift+Z or Ctrl+Y
      if (
        ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && e.shiftKey) ||
        ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y")
      ) {
        e.preventDefault();
        drawingStore.redo();
        return;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [selectedDrawingId]);

  // Convert pointer event to local SVG screen coordinates
  const getLocalPoint = (e: React.PointerEvent<any>): ScreenPoint => {
    if (!svgRef.current) return { x: e.clientX, y: e.clientY };
    const rect = svgRef.current.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  };

  // Resolve snapping for a screen point
  const resolvePoint = (
    screenPoint: ScreenPoint,
    isModifierActive: boolean = false
  ): SnapTargetResult => {
    if (!coordinateMapper) {
      return {
        anchor: { time: 0, price: 0 },
        screenPoint,
        snapped: false,
      };
    }

    return resolveSnapping(
      screenPoint,
      bars,
      {
        timeToScreen: (t) => coordinateMapper.financialToScreen({ time: t, price: 0 })?.x ?? null,
        priceToScreen: (p) => coordinateMapper.financialToScreen({ time: 0, price: p })?.y ?? null,
        screenToTime: (x) => coordinateMapper.screenToFinancial({ x, y: 0 })?.time ?? null,
        screenToPrice: (y) => coordinateMapper.screenToFinancial({ x: 0, y })?.price ?? null,
      },
      {
        mode: snappingMode,
        pixelTolerance: 15,
        isModifierActive,
      }
    );
  };

  // Convert drawing anchors to rendered screen anchors
  const projectAnchors = (anchors: DrawingAnchor[]): RenderedAnchor[] => {
    if (!coordinateMapper) return [];
    const result: RenderedAnchor[] = [];

    for (const a of anchors) {
      const pt = coordinateMapper.financialToScreen(a);
      if (pt) {
        result.push({
          time: a.time,
          price: a.price,
          x: pt.x,
          y: pt.y,
        });
      }
    }

    return result;
  };

  // --- SVG BACKGROUND POINTER DOWN (Tool Creation Mode) ---
  const handleSvgPointerDown = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!activeTool) return;

    const point = getLocalPoint(e);
    const snapResult = resolvePoint(point, e.shiftKey || e.altKey);

    // 1-anchor tools commit immediately
    if (
      activeTool === "horizontal_line" ||
      activeTool === "horizontal_ray" ||
      activeTool === "vertical_line"
    ) {
      const created = drawingStore.addDrawing(activeTool, [snapResult.anchor]);
      setCreationAnchors([]);
      if (created && onDrawingCreated) {
        onDrawingCreated(created);
      }
      return;
    }

    // 2-anchor tools
    if (creationAnchors.length === 0) {
      // First anchor
      setCreationAnchors([snapResult.anchor]);
      drawingStore.setInteractionState("PLACING_NEXT_ANCHOR");
    } else {
      // Second anchor commit
      const finalAnchors = [creationAnchors[0], snapResult.anchor];
      const created = drawingStore.addDrawing(activeTool, finalAnchors);
      setCreationAnchors([]);
      drawingStore.setInteractionState("IDLE");
      if (created && onDrawingCreated) {
        onDrawingCreated(created);
      }
    }
  };

  // --- DRAWING BODY POINTER DOWN (Whole Drawing Drag) ---
  const handleBodyPointerDown = (e: React.PointerEvent, drawingId: string) => {
    if (activeTool) return; // tool creation takes precedence
    e.stopPropagation();

    onSelectDrawing(drawingId);
    const target = drawings.find((d) => d.id === drawingId);
    if (!target || target.locked) return;

    const point = getLocalPoint(e);
    setDraggedDrawingId(drawingId);
    setDraggedAnchorIndex(-1);
    setDraggingMode("WHOLE");
    setDragStartPointer(point);
    setDragStartAnchors(JSON.parse(JSON.stringify(target.anchors)));

    (e.currentTarget as Element).setPointerCapture(e.pointerId);
  };

  // --- ANCHOR HANDLE POINTER DOWN (Anchor Drag) ---
  const handleHandlePointerDown = (
    e: React.PointerEvent,
    drawingId: string,
    anchorIdx: number
  ) => {
    if (activeTool) return;
    e.stopPropagation();

    onSelectDrawing(drawingId);
    const target = drawings.find((d) => d.id === drawingId);
    if (!target || target.locked) return;

    const point = getLocalPoint(e);
    setDraggedDrawingId(drawingId);
    setDraggedAnchorIndex(anchorIdx);
    setDraggingMode("ANCHOR");
    setDragStartPointer(point);
    setDragStartAnchors(JSON.parse(JSON.stringify(target.anchors)));

    (e.currentTarget as Element).setPointerCapture(e.pointerId);
  };

  // --- GENERAL POINTER MOVE ---
  const handlePointerMove = (e: React.PointerEvent<SVGSVGElement>) => {
    const point = getLocalPoint(e);
    setCurrentPointer(point);

    const snapResult = resolvePoint(point, e.shiftKey || e.altKey);
    setActiveSnapTarget(snapResult.snapped ? snapResult : null);

    // If dragging
    if (draggingMode !== "NONE" && draggedDrawingId && dragStartPointer && coordinateMapper) {
      const target = drawings.find((d) => d.id === draggedDrawingId);
      if (!target || target.locked) return;

      if (draggingMode === "ANCHOR" && draggedAnchorIndex >= 0) {
        const updatedAnchors = [...dragStartAnchors];
        updatedAnchors[draggedAnchorIndex] = snapResult.anchor;
        target.anchors = updatedAnchors;
        setViewportTick((t) => t + 1);
      } else if (draggingMode === "WHOLE") {
        const startFin = coordinateMapper.screenToFinancial(dragStartPointer);
        const currFin = coordinateMapper.screenToFinancial(point);

        if (startFin && currFin) {
          const deltaPrice = currFin.price - startFin.price;
          const deltaTime = currFin.time - startFin.time;

          const updatedAnchors = dragStartAnchors.map((a) => ({
            time: a.time + deltaTime,
            price: a.price + deltaPrice,
          }));

          target.anchors = updatedAnchors;
          setViewportTick((t) => t + 1);
        }
      }
    }
  };

  // --- POINTER UP / COMMIT ---
  const handlePointerUp = (e: React.PointerEvent) => {
    if (draggingMode !== "NONE" && draggedDrawingId) {
      const target = drawings.find((d) => d.id === draggedDrawingId);
      if (target) {
        drawingStore.commitDrawingAnchors(draggedDrawingId, target.anchors);
      }
      try {
        (e.currentTarget as Element).releasePointerCapture(e.pointerId);
      } catch {
        // ignore
      }
      setDraggingMode("NONE");
      setDraggedDrawingId(null);
      setDraggedAnchorIndex(-1);
      setDragStartPointer(null);
      setDragStartAnchors([]);
    }
  };

  const isCapturing = activeTool !== null || draggingMode !== "NONE";

  return (
    <svg
      ref={svgRef}
      className={`absolute inset-0 w-full h-full overflow-hidden select-none z-10 ${
        isCapturing
          ? "pointer-events-auto cursor-crosshair"
          : "pointer-events-none"
      }`}
      onPointerDown={handleSvgPointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      role="application"
      aria-label="Interactive Chart Drawings Layer"
    >
      <defs>
        <filter id="badge-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="1" stdDeviation="2" floodColor="#000000" floodOpacity="0.8" />
        </filter>
      </defs>

      {/* RENDER COMMITTED DRAWINGS */}
      {drawings.map((drawing) => {
        if (!drawing.visible) return null;
        const isSelected = drawing.id === selectedDrawingId;
        const pts = projectAnchors(drawing.anchors);
        if (pts.length === 0) return null;

        const strokeColor = drawing.style.color;
        const strokeWidth = drawing.style.lineWidth;
        const strokeDasharray = strokeStyleToDashArray(drawing.style.lineStyle, strokeWidth);
        const fillOpacity = drawing.style.fillOpacity;

        return (
          <g
            key={drawing.id}
            opacity={drawing.locked ? 0.75 : 1}
            className="pointer-events-auto"
          >
            {/* 1. TRENDLINE */}
            {drawing.type === "trendline" && pts.length >= 2 && (
              <g
                className="cursor-move"
                onPointerDown={(e) => handleBodyPointerDown(e, drawing.id)}
                onPointerUp={handlePointerUp}
              >
                {/* Fat invisible hit line */}
                <line
                  x1={pts[0].x}
                  y1={pts[0].y}
                  x2={pts[1].x}
                  y2={pts[1].y}
                  stroke="transparent"
                  strokeWidth={Math.max(14, strokeWidth + 10)}
                />
                {/* Visual Line */}
                <line
                  x1={pts[0].x}
                  y1={pts[0].y}
                  x2={pts[1].x}
                  y2={pts[1].y}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDasharray}
                  strokeLinecap="round"
                />
              </g>
            )}

            {/* 2. HORIZONTAL LINE */}
            {drawing.type === "horizontal_line" && pts.length >= 1 && (
              <g
                className="cursor-move"
                onPointerDown={(e) => handleBodyPointerDown(e, drawing.id)}
                onPointerUp={handlePointerUp}
              >
                <line
                  x1={0}
                  y1={pts[0].y}
                  x2={width}
                  y2={pts[0].y}
                  stroke="transparent"
                  strokeWidth={14}
                />
                <line
                  x1={0}
                  y1={pts[0].y}
                  x2={width}
                  y2={pts[0].y}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDasharray}
                />
                {drawing.style.showLabel && (
                  <g transform={`translate(${Math.max(10, width - 65)}, ${pts[0].y - 9})`}>
                    <rect
                      width={60}
                      height={18}
                      rx={3}
                      fill={strokeColor}
                      fillOpacity={0.9}
                      filter="url(#badge-shadow)"
                    />
                    <text
                      x={30}
                      y={12}
                      textAnchor="middle"
                      fill="#000000"
                      fontSize={10}
                      fontFamily="var(--font-geist-mono), monospace"
                      fontWeight="bold"
                    >
                      ${drawing.anchors[0].price.toFixed(2)}
                    </text>
                  </g>
                )}
              </g>
            )}

            {/* 3. HORIZONTAL RAY */}
            {drawing.type === "horizontal_ray" && pts.length >= 1 && (
              <g
                className="cursor-move"
                onPointerDown={(e) => handleBodyPointerDown(e, drawing.id)}
                onPointerUp={handlePointerUp}
              >
                <line
                  x1={pts[0].x}
                  y1={pts[0].y}
                  x2={width}
                  y2={pts[0].y}
                  stroke="transparent"
                  strokeWidth={14}
                />
                <line
                  x1={pts[0].x}
                  y1={pts[0].y}
                  x2={width}
                  y2={pts[0].y}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDasharray}
                />
                {drawing.style.showLabel && (
                  <g transform={`translate(${Math.max(10, width - 65)}, ${pts[0].y - 9})`}>
                    <rect
                      width={60}
                      height={18}
                      rx={3}
                      fill={strokeColor}
                      fillOpacity={0.9}
                      filter="url(#badge-shadow)"
                    />
                    <text
                      x={30}
                      y={12}
                      textAnchor="middle"
                      fill="#000000"
                      fontSize={10}
                      fontFamily="var(--font-geist-mono), monospace"
                      fontWeight="bold"
                    >
                      ${drawing.anchors[0].price.toFixed(2)}
                    </text>
                  </g>
                )}
              </g>
            )}

            {/* 4. VERTICAL LINE */}
            {drawing.type === "vertical_line" && pts.length >= 1 && (
              <g
                className="cursor-move"
                onPointerDown={(e) => handleBodyPointerDown(e, drawing.id)}
                onPointerUp={handlePointerUp}
              >
                <line
                  x1={pts[0].x}
                  y1={0}
                  x2={pts[0].x}
                  y2={height}
                  stroke="transparent"
                  strokeWidth={14}
                />
                <line
                  x1={pts[0].x}
                  y1={0}
                  x2={pts[0].x}
                  y2={height}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDasharray}
                />
                {drawing.style.showLabel && (
                  <g transform={`translate(${pts[0].x - 45}, ${height - 24})`}>
                    <rect
                      width={90}
                      height={18}
                      rx={3}
                      fill="#18181b"
                      stroke={strokeColor}
                      strokeWidth={1}
                      filter="url(#badge-shadow)"
                    />
                    <text
                      x={45}
                      y={12}
                      textAnchor="middle"
                      fill="#f4f4f5"
                      fontSize={9}
                      fontFamily="var(--font-geist-mono), monospace"
                    >
                      {new Date(drawing.anchors[0].time * 1000).toISOString().slice(5, 16)}
                    </text>
                  </g>
                )}
              </g>
            )}

            {/* 5. RECTANGLE */}
            {drawing.type === "rectangle" && pts.length >= 2 && (
              <g
                className="cursor-move"
                onPointerDown={(e) => handleBodyPointerDown(e, drawing.id)}
                onPointerUp={handlePointerUp}
              >
                <rect
                  x={Math.min(pts[0].x, pts[1].x)}
                  y={Math.min(pts[0].y, pts[1].y)}
                  width={Math.max(1, Math.abs(pts[1].x - pts[0].x))}
                  height={Math.max(1, Math.abs(pts[1].y - pts[0].y))}
                  fill={strokeColor}
                  fillOpacity={fillOpacity}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDasharray}
                />
              </g>
            )}

            {/* 6. PRICE RANGE */}
            {drawing.type === "price_range" && pts.length >= 2 && (() => {
              const pRes = calculatePriceMeasurement(
                drawing.anchors[0].price,
                drawing.anchors[1].price,
                drawing.context.quotation_unit
              );
              const minX = Math.min(pts[0].x, pts[1].x);
              const maxX = Math.max(pts[0].x, pts[1].x);
              const minY = Math.min(pts[0].y, pts[1].y);
              const maxY = Math.max(pts[0].y, pts[1].y);
              const midX = (minX + maxX) / 2;
              const midY = (minY + maxY) / 2;

              return (
                <g
                  className="cursor-move"
                  onPointerDown={(e) => handleBodyPointerDown(e, drawing.id)}
                  onPointerUp={handlePointerUp}
                >
                  <rect
                    x={minX}
                    y={minY}
                    width={Math.max(20, maxX - minX)}
                    height={Math.max(1, maxY - minY)}
                    fill={strokeColor}
                    fillOpacity={fillOpacity}
                    stroke={strokeColor}
                    strokeWidth={strokeWidth}
                    strokeDasharray={strokeDasharray}
                  />
                  <g transform={`translate(${midX - 55}, ${midY - 11})`}>
                    <rect
                      width={110}
                      height={22}
                      rx={4}
                      fill="#09090b"
                      stroke={strokeColor}
                      strokeWidth={1}
                      filter="url(#badge-shadow)"
                    />
                    <text
                      x={55}
                      y={15}
                      textAnchor="middle"
                      fill={pRes.isPositive ? "#34d399" : "#f87171"}
                      fontSize={10}
                      fontFamily="var(--font-geist-mono), monospace"
                      fontWeight="bold"
                    >
                      {pRes.deltaPriceFormatted} ({pRes.deltaPercentFormatted})
                    </text>
                  </g>
                </g>
              );
            })()}

            {/* 7. TIME RANGE */}
            {drawing.type === "time_range" && pts.length >= 2 && (() => {
              const tRes = calculateTimeMeasurement(
                drawing.anchors[0].time,
                drawing.anchors[1].time,
                bars
              );
              const minX = Math.min(pts[0].x, pts[1].x);
              const maxX = Math.max(pts[0].x, pts[1].x);
              const midX = (minX + maxX) / 2;
              const midY = (pts[0].y + pts[1].y) / 2;

              return (
                <g
                  className="cursor-move"
                  onPointerDown={(e) => handleBodyPointerDown(e, drawing.id)}
                  onPointerUp={handlePointerUp}
                >
                  <rect
                    x={minX}
                    y={Math.min(pts[0].y, pts[1].y)}
                    width={Math.max(1, maxX - minX)}
                    height={Math.abs(pts[1].y - pts[0].y) || 40}
                    fill={strokeColor}
                    fillOpacity={fillOpacity}
                    stroke={strokeColor}
                    strokeWidth={strokeWidth}
                    strokeDasharray={strokeDasharray}
                  />
                  <g transform={`translate(${midX - 60}, ${midY - 11})`}>
                    <rect
                      width={120}
                      height={22}
                      rx={4}
                      fill="#09090b"
                      stroke={strokeColor}
                      strokeWidth={1}
                      filter="url(#badge-shadow)"
                    />
                    <text
                      x={60}
                      y={15}
                      textAnchor="middle"
                      fill="#38bdf8"
                      fontSize={10}
                      fontFamily="var(--font-geist-mono), monospace"
                      fontWeight="bold"
                    >
                      {tRes.elapsedFormatted} · {tRes.barCountFormatted}
                    </text>
                  </g>
                </g>
              );
            })()}

            {/* 8. COMBINED PRICE & TIME MEASURE */}
            {drawing.type === "price_time_measure" && pts.length >= 2 && (() => {
              const comb = calculateCombinedMeasurement(
                drawing.anchors[0].price,
                drawing.anchors[1].price,
                drawing.anchors[0].time,
                drawing.anchors[1].time,
                bars,
                drawing.context.quotation_unit
              );
              const minX = Math.min(pts[0].x, pts[1].x);
              const maxX = Math.max(pts[0].x, pts[1].x);
              const minY = Math.min(pts[0].y, pts[1].y);
              const maxY = Math.max(pts[0].y, pts[1].y);
              const midX = (minX + maxX) / 2;
              const midY = (minY + maxY) / 2;

              return (
                <g
                  className="cursor-move"
                  onPointerDown={(e) => handleBodyPointerDown(e, drawing.id)}
                  onPointerUp={handlePointerUp}
                >
                  <rect
                    x={minX}
                    y={minY}
                    width={Math.max(1, maxX - minX)}
                    height={Math.max(1, maxY - minY)}
                    fill={strokeColor}
                    fillOpacity={fillOpacity}
                    stroke={strokeColor}
                    strokeWidth={1}
                    strokeDasharray="4 2"
                  />
                  <line
                    x1={pts[0].x}
                    y1={pts[0].y}
                    x2={pts[1].x}
                    y2={pts[1].y}
                    stroke={strokeColor}
                    strokeWidth={strokeWidth}
                  />
                  <g transform={`translate(${midX - 70}, ${midY - 18})`}>
                    <rect
                      width={140}
                      height={36}
                      rx={4}
                      fill="#09090b"
                      stroke={strokeColor}
                      strokeWidth={1}
                      filter="url(#badge-shadow)"
                    />
                    <text
                      x={70}
                      y={14}
                      textAnchor="middle"
                      fill={comb.price.isPositive ? "#34d399" : "#f87171"}
                      fontSize={10}
                      fontFamily="var(--font-geist-mono), monospace"
                      fontWeight="bold"
                    >
                      {comb.price.deltaPriceFormatted} ({comb.price.deltaPercentFormatted})
                    </text>
                    <text
                      x={70}
                      y={28}
                      textAnchor="middle"
                      fill="#a1a1aa"
                      fontSize={9}
                      fontFamily="var(--font-geist-mono), monospace"
                    >
                      {comb.time.elapsedFormatted} · {comb.time.barCountFormatted}
                    </text>
                  </g>
                </g>
              );
            })()}

            {/* 9. FIBONACCI RETRACEMENT */}
            {drawing.type === "fibonacci_retracement" && pts.length >= 2 && (() => {
              const fibLevels = calculateFibonacciLevels(
                drawing.anchors[0].price,
                drawing.anchors[1].price
              );
              const minX = Math.min(pts[0].x, pts[1].x);
              const maxX = Math.max(pts[0].x, pts[1].x);

              return (
                <g
                  className="cursor-move"
                  onPointerDown={(e) => handleBodyPointerDown(e, drawing.id)}
                  onPointerUp={handlePointerUp}
                >
                  <line
                    x1={pts[0].x}
                    y1={pts[0].y}
                    x2={pts[1].x}
                    y2={pts[1].y}
                    stroke="#71717a"
                    strokeWidth={1}
                    strokeDasharray="3 3"
                  />
                  {fibLevels.map((lvl) => {
                    const levelScreenY = coordinateMapper?.financialToScreen({
                      time: 0,
                      price: lvl.price,
                    })?.y;
                    if (levelScreenY === undefined || levelScreenY === null) return null;

                    return (
                      <g key={lvl.ratio}>
                        <line
                          x1={minX}
                          y1={levelScreenY}
                          x2={Math.max(maxX, width - 40)}
                          y2={levelScreenY}
                          stroke={lvl.color}
                          strokeWidth={strokeWidth}
                        />
                        <text
                          x={minX + 4}
                          y={levelScreenY - 3}
                          fill={lvl.color}
                          fontSize={9}
                          fontFamily="var(--font-geist-mono), monospace"
                          fontWeight="bold"
                        >
                          {lvl.percentageLabel} - ${lvl.priceFormatted}
                        </text>
                      </g>
                    );
                  })}
                </g>
              );
            })()}

            {/* SELECTION HANDLES */}
            {isSelected && !drawing.locked && (
              <g className="selection-handles">
                {pts.map((pt, idx) => (
                  <circle
                    key={idx}
                    cx={pt.x}
                    cy={pt.y}
                    r={5}
                    fill="#ffffff"
                    stroke="#0284c7"
                    strokeWidth={2}
                    className="cursor-pointer hover:scale-125 transition-transform"
                    filter="url(#badge-shadow)"
                    onPointerDown={(e) => handleHandlePointerDown(e, drawing.id, idx)}
                    onPointerUp={handlePointerUp}
                  />
                ))}
              </g>
            )}
          </g>
        );
      })}

      {/* TRANSIENT PREVIEW DURING DRAWING CREATION */}
      {activeTool && creationAnchors.length > 0 && currentPointer && coordinateMapper && (() => {
        const p1 = coordinateMapper.financialToScreen(creationAnchors[0]);
        const p2 = activeSnapTarget ? activeSnapTarget.screenPoint : currentPointer;
        if (!p1) return null;

        return (
          <g opacity={0.8} className="preview-drawing pointer-events-none">
            {activeTool === "trendline" && (
              <line
                x1={p1.x}
                y1={p1.y}
                x2={p2.x}
                y2={p2.y}
                stroke="#38bdf8"
                strokeWidth={2}
                strokeDasharray="4 4"
              />
            )}
            {activeTool === "rectangle" && (
              <rect
                x={Math.min(p1.x, p2.x)}
                y={Math.min(p1.y, p2.y)}
                width={Math.max(1, Math.abs(p2.x - p1.x))}
                height={Math.max(1, Math.abs(p2.y - p1.y))}
                fill="#06b6d4"
                fillOpacity={0.15}
                stroke="#06b6d4"
                strokeWidth={1.5}
                strokeDasharray="4 4"
              />
            )}
            {activeTool === "price_range" && (
              <rect
                x={Math.min(p1.x, p2.x)}
                y={Math.min(p1.y, p2.y)}
                width={Math.max(20, Math.abs(p2.x - p1.x))}
                height={Math.max(1, Math.abs(p2.y - p1.y))}
                fill="#38bdf8"
                fillOpacity={0.15}
                stroke="#38bdf8"
                strokeWidth={1.5}
                strokeDasharray="4 4"
              />
            )}
            {activeTool === "time_range" && (
              <rect
                x={Math.min(p1.x, p2.x)}
                y={Math.min(p1.y, p2.y)}
                width={Math.max(1, Math.abs(p2.x - p1.x))}
                height={Math.max(40, Math.abs(p2.y - p1.y))}
                fill="#a855f7"
                fillOpacity={0.15}
                stroke="#a855f7"
                strokeWidth={1.5}
                strokeDasharray="4 4"
              />
            )}
            {activeTool === "price_time_measure" && (
              <>
                <rect
                  x={Math.min(p1.x, p2.x)}
                  y={Math.min(p1.y, p2.y)}
                  width={Math.max(1, Math.abs(p2.x - p1.x))}
                  height={Math.max(1, Math.abs(p2.y - p1.y))}
                  fill="#f43f5e"
                  fillOpacity={0.15}
                  stroke="#f43f5e"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                />
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke="#f43f5e"
                  strokeWidth={1.5}
                />
              </>
            )}
            {activeTool === "fibonacci_retracement" && (
              <line
                x1={p1.x}
                y1={p1.y}
                x2={p2.x}
                y2={p2.y}
                stroke="#e4e4e7"
                strokeWidth={1.5}
                strokeDasharray="4 4"
              />
            )}
            <circle cx={p1.x} cy={p1.y} r={4} fill="#38bdf8" />
          </g>
        );
      })()}

      {/* SMART SNAPPING INDICATOR TARGET */}
      {activeSnapTarget && (
        <g
          transform={`translate(${activeSnapTarget.screenPoint.x}, ${activeSnapTarget.screenPoint.y})`}
          className="pointer-events-none"
        >
          <circle r={6} fill="none" stroke="#10b981" strokeWidth={1.5} />
          <circle r={2} fill="#10b981" />
          {activeSnapTarget.snapField && (
            <text
              x={9}
              y={-3}
              fill="#10b981"
              fontSize={9}
              fontFamily="var(--font-geist-mono), monospace"
              fontWeight="bold"
            >
              SNAP: {activeSnapTarget.snapField.toUpperCase()}
            </text>
          )}
        </g>
      )}
    </svg>
  );
}
