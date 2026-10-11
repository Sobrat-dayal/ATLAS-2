import { BottomPanelId } from "./types";

export const DEFAULT_BOTTOM_PANEL_HEIGHT = 280;
export const MIN_BOTTOM_PANEL_HEIGHT = 160;
export const MAX_BOTTOM_PANEL_HEIGHT_RATIO = 0.45;
export const MAX_ABSOLUTE_BOTTOM_PANEL_HEIGHT = 640;

/**
 * Clamp requested bottom panel height against viewport bounds.
 * Must respect minimum height (160px) and maximum ratio of usable viewport height (45%).
 */
export function clampBottomPanelHeight(
  requestedHeight: number,
  viewportHeight: number = typeof window !== "undefined" ? window.innerHeight : 900
): number {
  if (typeof requestedHeight !== "number" || isNaN(requestedHeight)) {
    return DEFAULT_BOTTOM_PANEL_HEIGHT;
  }
  const effectiveViewport = Math.max(viewportHeight, 400);
  const maxAllowedByRatio = Math.floor(effectiveViewport * MAX_BOTTOM_PANEL_HEIGHT_RATIO);
  const maxAllowed = Math.min(maxAllowedByRatio, MAX_ABSOLUTE_BOTTOM_PANEL_HEIGHT);
  const effectiveMax = Math.max(MIN_BOTTOM_PANEL_HEIGHT, maxAllowed);

  if (requestedHeight < MIN_BOTTOM_PANEL_HEIGHT) {
    return MIN_BOTTOM_PANEL_HEIGHT;
  }
  if (requestedHeight > effectiveMax) {
    return effectiveMax;
  }
  return Math.round(requestedHeight);
}

/**
 * Pure transition helper: clicking active item toggles/closes it; clicking different opens target.
 */
export function getNextBottomPanelState(
  currentActiveId: BottomPanelId | null,
  targetId: BottomPanelId
): BottomPanelId | null {
  return currentActiveId === targetId ? null : targetId;
}
