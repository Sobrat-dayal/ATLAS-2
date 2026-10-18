/**
 * Session Drawing Store and State Manager for ATLAS Charts (Stage 71).
 *
 * Implements:
 * - Scoped in-memory drawing collections indexed by [instrument_id:price_basis].
 * - Return-to-instrument session preservation (no cross-instrument leakage).
 * - Bounded drawing capacity (max 250 drawings per context).
 * - Undo/Redo command integration for all mutations.
 * - Active tool selection, snapping mode, and interaction state tracking.
 */

import {
  DrawingAnchor,
  DrawingChartContext,
  DrawingObject,
  DrawingStyle,
  DrawingType,
  InteractionState,
  SnappingMode,
} from "./types";
import { UndoRedoHistory } from "./undoRedo";

export interface DrawingStoreListener {
  (): void;
}

export const DEFAULT_DRAWING_STYLES: Record<DrawingType, DrawingStyle> = {
  trendline: {
    color: "#38bdf8",
    lineWidth: 2,
    lineStyle: "solid",
    fillOpacity: 0.15,
    showLabel: false,
  },
  horizontal_line: {
    color: "#10b981",
    lineWidth: 1.5,
    lineStyle: "solid",
    fillOpacity: 0.15,
    showLabel: true,
  },
  horizontal_ray: {
    color: "#06b6d4",
    lineWidth: 1.5,
    lineStyle: "dashed",
    fillOpacity: 0.15,
    showLabel: true,
  },
  vertical_line: {
    color: "#f59e0b",
    lineWidth: 1.5,
    lineStyle: "dashed",
    fillOpacity: 0.15,
    showLabel: true,
  },
  rectangle: {
    color: "#06b6d4",
    lineWidth: 1.5,
    lineStyle: "solid",
    fillOpacity: 0.15,
    showLabel: false,
  },
  price_range: {
    color: "#38bdf8",
    lineWidth: 1.5,
    lineStyle: "solid",
    fillOpacity: 0.18,
    showLabel: true,
  },
  time_range: {
    color: "#a855f7",
    lineWidth: 1.5,
    lineStyle: "solid",
    fillOpacity: 0.18,
    showLabel: true,
  },
  price_time_measure: {
    color: "#f43f5e",
    lineWidth: 1.5,
    lineStyle: "solid",
    fillOpacity: 0.18,
    showLabel: true,
  },
  fibonacci_retracement: {
    color: "#e4e4e7",
    lineWidth: 1.5,
    lineStyle: "solid",
    fillOpacity: 0.1,
    showLabel: true,
  },
};

export class DrawingSessionStore {
  private static instance: DrawingSessionStore;
  private static panelInstances: Map<string, DrawingSessionStore> = new Map();

  // Map of contextKey -> DrawingObject[]
  private contextDrawingsMap: Map<string, DrawingObject[]> = new Map();
  // Map of contextKey -> UndoRedoHistory
  private contextHistoryMap: Map<string, UndoRedoHistory> = new Map();

  private currentContext: DrawingChartContext = {
    instrument_entity_id: "default",
    symbol: "SPY",
    price_basis: "raw",
  };

  private activeTool: DrawingType | null = null;
  private selectedDrawingId: string | null = null;
  private hoveredDrawingId: string | null = null;
  private snappingMode: SnappingMode = "NEAREST_BAR";
  private interactionState: InteractionState = "IDLE";
  private transientPreviewAnchors: DrawingAnchor[] = [];

  private listeners: Set<DrawingStoreListener> = new Set();
  private maxDrawingsPerContext = 250;

  public constructor() {}

  public static getInstance(): DrawingSessionStore {
    if (!DrawingSessionStore.instance) {
      DrawingSessionStore.instance = new DrawingSessionStore();
    }
    return DrawingSessionStore.instance;
  }

  public static getForPanel(panelId?: string): DrawingSessionStore {
    if (!panelId) {
      return DrawingSessionStore.getInstance();
    }
    let store = DrawingSessionStore.panelInstances.get(panelId);
    if (!store) {
      store = new DrawingSessionStore();
      DrawingSessionStore.panelInstances.set(panelId, store);
    }
    return store;
  }

  public static disposePanel(panelId: string): void {
    DrawingSessionStore.panelInstances.delete(panelId);
  }

  private getContextKey(context: DrawingChartContext = this.currentContext): string {
    return `${context.instrument_entity_id || context.symbol}:${context.price_basis}`;
  }

  public setContext(context: DrawingChartContext): void {
    const prevKey = this.getContextKey(this.currentContext);
    const newKey = this.getContextKey(context);

    if (prevKey !== newKey) {
      this.currentContext = { ...context };
      this.selectedDrawingId = null;
      this.hoveredDrawingId = null;
      this.transientPreviewAnchors = [];
      this.interactionState = "IDLE";
      this.notify();
    }
  }

  public getCurrentContext(): DrawingChartContext {
    return { ...this.currentContext };
  }

  private getHistory(): UndoRedoHistory {
    const key = this.getContextKey();
    let history = this.contextHistoryMap.get(key);
    if (!history) {
      history = new UndoRedoHistory(100);
      this.contextHistoryMap.set(key, history);
    }
    return history;
  }

  public getDrawings(): DrawingObject[] {
    const key = this.getContextKey();
    return this.contextDrawingsMap.get(key) || [];
  }

  private setDrawings(drawings: DrawingObject[]): void {
    const key = this.getContextKey();
    this.contextDrawingsMap.set(key, drawings);
    this.notify();
  }

  public getActiveTool(): DrawingType | null {
    return this.activeTool;
  }

  public setActiveTool(tool: DrawingType | null): void {
    this.activeTool = tool;
    this.transientPreviewAnchors = [];
    this.interactionState = tool ? "TOOL_ARMED" : "IDLE";
    if (tool) {
      this.selectedDrawingId = null;
    }
    this.notify();
  }

  public getSelectedDrawingId(): string | null {
    return this.selectedDrawingId;
  }

  public setSelectedDrawingId(id: string | null): void {
    if (this.selectedDrawingId !== id) {
      this.selectedDrawingId = id;
      this.interactionState = id ? "DRAWING_SELECTED" : "IDLE";
      this.notify();
    }
  }

  public getSelectedDrawing(): DrawingObject | null {
    if (!this.selectedDrawingId) return null;
    const drawings = this.getDrawings();
    return drawings.find((d) => d.id === this.selectedDrawingId) || null;
  }

  public getHoveredDrawingId(): string | null {
    return this.hoveredDrawingId;
  }

  public setHoveredDrawingId(id: string | null): void {
    if (this.hoveredDrawingId !== id) {
      this.hoveredDrawingId = id;
      this.notify();
    }
  }

  public getSnappingMode(): SnappingMode {
    return this.snappingMode;
  }

  public setSnappingMode(mode: SnappingMode): void {
    this.snappingMode = mode;
    this.notify();
  }

  public cycleSnappingMode(): void {
    const modes: SnappingMode[] = ["OFF", "NEAREST_BAR", "OHLC"];
    const nextIdx = (modes.indexOf(this.snappingMode) + 1) % modes.length;
    this.setSnappingMode(modes[nextIdx]);
  }

  public getInteractionState(): InteractionState {
    return this.interactionState;
  }

  public setInteractionState(state: InteractionState): void {
    this.interactionState = state;
    this.notify();
  }

  public getTransientPreviewAnchors(): DrawingAnchor[] {
    return this.transientPreviewAnchors;
  }

  public setTransientPreviewAnchors(anchors: DrawingAnchor[]): void {
    this.transientPreviewAnchors = anchors;
    this.notify();
  }

  // --- MUTATION COMMANDS (WITH UNDO/REDO) ---

  public addDrawing(
    type: DrawingType,
    anchors: DrawingAnchor[],
    customStyle?: Partial<DrawingStyle>
  ): DrawingObject | null {
    const currentDrawings = this.getDrawings();

    if (currentDrawings.length >= this.maxDrawingsPerContext) {
      return null;
    }

    const defaultStyle = DEFAULT_DRAWING_STYLES[type];
    const newDrawing: DrawingObject = {
      id: `draw_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      type,
      version: 1,
      context: { ...this.currentContext },
      anchors: [...anchors],
      style: { ...defaultStyle, ...customStyle },
      visible: true,
      locked: false,
      zIndex: currentDrawings.length + 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    const nextDrawings = [...currentDrawings, newDrawing];

    // Push undo command
    this.getHistory().push("CREATE", currentDrawings, nextDrawings, [newDrawing.id]);

    this.setDrawings(nextDrawings);
    this.setSelectedDrawingId(newDrawing.id);
    this.setActiveTool(null);

    return newDrawing;
  }

  public commitDrawingAnchors(drawingId: string, newAnchors: DrawingAnchor[]): void {
    const currentDrawings = this.getDrawings();
    const target = currentDrawings.find((d) => d.id === drawingId);
    if (!target || target.locked) return;

    const nextDrawings = currentDrawings.map((d) => {
      if (d.id === drawingId) {
        return {
          ...d,
          anchors: [...newAnchors],
          updatedAt: new Date().toISOString(),
        };
      }
      return d;
    });

    this.getHistory().push("EDIT_ANCHOR", currentDrawings, nextDrawings, [drawingId]);
    this.setDrawings(nextDrawings);
  }

  public updateDrawingStyle(drawingId: string, styleUpdates: Partial<DrawingStyle>): void {
    const currentDrawings = this.getDrawings();
    const target = currentDrawings.find((d) => d.id === drawingId);
    if (!target) return;

    const nextDrawings = currentDrawings.map((d) => {
      if (d.id === drawingId) {
        return {
          ...d,
          style: { ...d.style, ...styleUpdates },
          updatedAt: new Date().toISOString(),
        };
      }
      return d;
    });

    this.getHistory().push("CHANGE_STYLE", currentDrawings, nextDrawings, [drawingId]);
    this.setDrawings(nextDrawings);
  }

  public toggleLock(drawingId: string): void {
    const currentDrawings = this.getDrawings();
    const target = currentDrawings.find((d) => d.id === drawingId);
    if (!target) return;

    const nextDrawings = currentDrawings.map((d) => {
      if (d.id === drawingId) {
        return {
          ...d,
          locked: !d.locked,
          updatedAt: new Date().toISOString(),
        };
      }
      return d;
    });

    this.getHistory().push("LOCK", currentDrawings, nextDrawings, [drawingId]);
    this.setDrawings(nextDrawings);
  }

  public toggleVisibility(drawingId: string): void {
    const currentDrawings = this.getDrawings();
    const target = currentDrawings.find((d) => d.id === drawingId);
    if (!target) return;

    const nextDrawings = currentDrawings.map((d) => {
      if (d.id === drawingId) {
        return {
          ...d,
          visible: !d.visible,
          updatedAt: new Date().toISOString(),
        };
      }
      return d;
    });

    this.getHistory().push("VISIBILITY", currentDrawings, nextDrawings, [drawingId]);
    this.setDrawings(nextDrawings);
  }

  public deleteDrawing(drawingId: string): void {
    const currentDrawings = this.getDrawings();
    const target = currentDrawings.find((d) => d.id === drawingId);
    if (!target) return;

    const nextDrawings = currentDrawings.filter((d) => d.id !== drawingId);

    this.getHistory().push("DELETE", currentDrawings, nextDrawings, [drawingId]);

    if (this.selectedDrawingId === drawingId) {
      this.selectedDrawingId = null;
    }
    if (this.hoveredDrawingId === drawingId) {
      this.hoveredDrawingId = null;
    }

    this.setDrawings(nextDrawings);
  }

  public clearDrawings(): void {
    const currentDrawings = this.getDrawings();
    if (currentDrawings.length === 0) return;

    this.getHistory().push(
      "CLEAR",
      currentDrawings,
      [],
      currentDrawings.map((d) => d.id)
    );

    this.selectedDrawingId = null;
    this.hoveredDrawingId = null;
    this.setDrawings([]);
  }

  /**
   * Replaces drawing collection for the current context during layout restoration.
   */
  public replaceAllDrawings(drawings: DrawingObject[]): void {
    const key = this.getContextKey();
    this.contextDrawingsMap.set(key, [...drawings]);
    this.selectedDrawingId = null;
    this.hoveredDrawingId = null;
    this.transientPreviewAnchors = [];
    this.interactionState = "IDLE";
    this.notify();
  }

  public undo(): boolean {
    const history = this.getHistory();
    const restored = history.undo();
    if (restored !== null) {
      const key = this.getContextKey();
      this.contextDrawingsMap.set(key, restored);
      // Validate selection
      if (this.selectedDrawingId && !restored.some((d) => d.id === this.selectedDrawingId)) {
        this.selectedDrawingId = null;
      }
      this.notify();
      return true;
    }
    return false;
  }

  public redo(): boolean {
    const history = this.getHistory();
    const restored = history.redo();
    if (restored !== null) {
      const key = this.getContextKey();
      this.contextDrawingsMap.set(key, restored);
      this.notify();
      return true;
    }
    return false;
  }

  public canUndo(): boolean {
    return this.getHistory().canUndo();
  }

  public canRedo(): boolean {
    return this.getHistory().canRedo();
  }

  // --- SUBSCRIBER MANAGEMENT ---

  public subscribe(listener: DrawingStoreListener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify(): void {
    this.listeners.forEach((listener) => {
      try {
        listener();
      } catch (err) {
        console.error("DrawingSessionStore listener error:", err);
      }
    });
  }
}

export const drawingStore = DrawingSessionStore.getInstance();
