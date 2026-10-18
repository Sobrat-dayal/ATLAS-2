"use client";

/**
 * React Hook for ATLAS Chart Drawing Tools (Stage 71).
 *
 * Connects the Chart Workspace with the DrawingSessionStore, providing reactive
 * state updates, instrument context binding, and command dispatchers.
 */

import { useEffect, useState } from "react";
import { ChartInstrumentMetadata } from "@/lib/charts/types";
import {
  DrawingAnchor,
  DrawingChartContext,
  DrawingObject,
  DrawingStyle,
  DrawingType,
  SnappingMode,
} from "@/lib/charts/drawings/types";
import { drawingStore } from "@/lib/charts/drawings/drawingStore";

export interface UseDrawingToolsProps {
  instrument: ChartInstrumentMetadata | null;
  priceBasis?: "raw" | "adjusted";
}

export function useDrawingTools({ instrument, priceBasis = "raw" }: UseDrawingToolsProps) {
  // Sync instrument context
  useEffect(() => {
    if (instrument) {
      const context: DrawingChartContext = {
        instrument_entity_id: instrument.entity_id || instrument.display_symbol,
        symbol: instrument.display_symbol,
        price_basis: priceBasis,
        quotation_unit: instrument.quotation_unit || instrument.price_currency || "USD",
      };
      drawingStore.setContext(context);
    }
  }, [instrument, priceBasis]);

  const [drawings, setDrawings] = useState<DrawingObject[]>(() => drawingStore.getDrawings());
  const [activeTool, setActiveToolState] = useState<DrawingType | null>(() => drawingStore.getActiveTool());
  const [selectedDrawingId, setSelectedDrawingIdState] = useState<string | null>(() =>
    drawingStore.getSelectedDrawingId()
  );
  const [hoveredDrawingId, setHoveredDrawingIdState] = useState<string | null>(() =>
    drawingStore.getHoveredDrawingId()
  );
  const [snappingMode, setSnappingModeState] = useState<SnappingMode>(() => drawingStore.getSnappingMode());
  const [canUndo, setCanUndoState] = useState<boolean>(() => drawingStore.canUndo());
  const [canRedo, setCanRedoState] = useState<boolean>(() => drawingStore.canRedo());

  // Subscribe to drawing store notifications
  useEffect(() => {
    const updateState = () => {
      setDrawings([...drawingStore.getDrawings()]);
      setActiveToolState(drawingStore.getActiveTool());
      setSelectedDrawingIdState(drawingStore.getSelectedDrawingId());
      setHoveredDrawingIdState(drawingStore.getHoveredDrawingId());
      setSnappingModeState(drawingStore.getSnappingMode());
      setCanUndoState(drawingStore.canUndo());
      setCanRedoState(drawingStore.canRedo());
    };

    const unsubscribe = drawingStore.subscribe(updateState);
    return () => {
      unsubscribe();
    };
  }, []);

  const selectedDrawing = drawings.find((d) => d.id === selectedDrawingId) || null;

  return {
    drawings,
    activeTool,
    selectedDrawing,
    selectedDrawingId,
    hoveredDrawingId,
    snappingMode,
    canUndo,
    canRedo,
    setActiveTool: (tool: DrawingType | null) => drawingStore.setActiveTool(tool),
    setSnappingMode: (mode: SnappingMode) => drawingStore.setSnappingMode(mode),
    cycleSnappingMode: () => drawingStore.cycleSnappingMode(),
    selectDrawing: (id: string | null) => drawingStore.setSelectedDrawingId(id),
    setHoveredDrawing: (id: string | null) => drawingStore.setHoveredDrawingId(id),
    addDrawing: (type: DrawingType, anchors: DrawingAnchor[], style?: Partial<DrawingStyle>) =>
      drawingStore.addDrawing(type, anchors, style),
    commitDrawingAnchors: (id: string, anchors: DrawingAnchor[]) =>
      drawingStore.commitDrawingAnchors(id, anchors),
    updateDrawingStyle: (id: string, style: Partial<DrawingStyle>) =>
      drawingStore.updateDrawingStyle(id, style),
    toggleLock: (id: string) => drawingStore.toggleLock(id),
    toggleVisibility: (id: string) => drawingStore.toggleVisibility(id),
    deleteDrawing: (id: string) => drawingStore.deleteDrawing(id),
    clearDrawings: () => drawingStore.clearDrawings(),
    undo: () => drawingStore.undo(),
    redo: () => drawingStore.redo(),
  };
}
