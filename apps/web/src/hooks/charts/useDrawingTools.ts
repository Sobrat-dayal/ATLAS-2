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
import { DrawingSessionStore, drawingStore } from "@/lib/charts/drawings/drawingStore";

export interface UseDrawingToolsProps {
  instrument: ChartInstrumentMetadata | null;
  priceBasis?: "raw" | "adjusted";
  panelId?: string;
}

export function useDrawingTools({ instrument, priceBasis = "raw", panelId }: UseDrawingToolsProps) {
  const store = DrawingSessionStore.getForPanel(panelId);

  // Sync instrument context
  useEffect(() => {
    if (instrument) {
      const context: DrawingChartContext = {
        instrument_entity_id: instrument.entity_id || instrument.display_symbol,
        symbol: instrument.display_symbol,
        price_basis: priceBasis,
        quotation_unit: instrument.quotation_unit || instrument.price_currency || "USD",
      };
      store.setContext(context);
    }
  }, [instrument, priceBasis, store]);

  const [drawings, setDrawings] = useState<DrawingObject[]>(() => store.getDrawings());
  const [activeTool, setActiveToolState] = useState<DrawingType | null>(() => store.getActiveTool());
  const [selectedDrawingId, setSelectedDrawingIdState] = useState<string | null>(() =>
    store.getSelectedDrawingId()
  );
  const [hoveredDrawingId, setHoveredDrawingIdState] = useState<string | null>(() =>
    store.getHoveredDrawingId()
  );
  const [snappingMode, setSnappingModeState] = useState<SnappingMode>(() => store.getSnappingMode());
  const [canUndo, setCanUndoState] = useState<boolean>(() => store.canUndo());
  const [canRedo, setCanRedoState] = useState<boolean>(() => store.canRedo());

  // Subscribe to drawing store notifications
  useEffect(() => {
    const updateState = () => {
      setDrawings([...store.getDrawings()]);
      setActiveToolState(store.getActiveTool());
      setSelectedDrawingIdState(store.getSelectedDrawingId());
      setHoveredDrawingIdState(store.getHoveredDrawingId());
      setSnappingModeState(store.getSnappingMode());
      setCanUndoState(store.canUndo());
      setCanRedoState(store.canRedo());
    };

    const unsubscribe = store.subscribe(updateState);
    return () => {
      unsubscribe();
    };
  }, [store]);

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
    setActiveTool: (tool: DrawingType | null) => store.setActiveTool(tool),
    setSnappingMode: (mode: SnappingMode) => store.setSnappingMode(mode),
    cycleSnappingMode: () => store.cycleSnappingMode(),
    selectDrawing: (id: string | null) => store.setSelectedDrawingId(id),
    setHoveredDrawing: (id: string | null) => store.setHoveredDrawingId(id),
    addDrawing: (type: DrawingType, anchors: DrawingAnchor[], style?: Partial<DrawingStyle>) =>
      store.addDrawing(type, anchors, style),
    commitDrawingAnchors: (id: string, anchors: DrawingAnchor[]) =>
      store.commitDrawingAnchors(id, anchors),
    updateDrawingStyle: (id: string, style: Partial<DrawingStyle>) =>
      store.updateDrawingStyle(id, style),
    toggleLock: (id: string) => store.toggleLock(id),
    toggleVisibility: (id: string) => store.toggleVisibility(id),
    deleteDrawing: (id: string) => store.deleteDrawing(id),
    clearDrawings: () => store.clearDrawings(),
    undo: () => store.undo(),
    redo: () => store.redo(),
  };
}
