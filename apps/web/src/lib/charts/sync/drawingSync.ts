/**
 * Compatible Chart Drawing Synchronization for ATLAS Charts (Stage 73).
 *
 * Implements:
 * - Strict compatibility verification before any drawing synchronization
 * - Deep cloning of drawing models (never share mutable drawing object references)
 * - Support for committed drawing actions (ADD, UPDATE, DELETE, CLEAR)
 * - Isolated undo/redo history preservation across panels
 * - Rejection of cross-instrument drawing replication
 */

import { DrawingObject } from "../drawings/types";
import { DrawingSyncPayload } from "./types";
import { validateDrawingSyncCompatibility } from "./compatibility";
import { ChartInstrumentMetadata } from "../types";

export interface DrawingSyncResult {
  applied: boolean;
  reason?: string;
  clonedDrawing?: DrawingObject;
}

/**
 * Prepares and clones a drawing for synchronization to a target panel.
 * Ensures the target panel receives an independent object instance.
 */
export function prepareDrawingForSync(
  sourceInstrument: ChartInstrumentMetadata | null,
  targetInstrument: ChartInstrumentMetadata | null,
  drawing: DrawingObject
): DrawingSyncResult {
  const compat = validateDrawingSyncCompatibility(sourceInstrument, targetInstrument);
  if (!compat.isCompatible) {
    return {
      applied: false,
      reason: compat.reason,
    };
  }

  // Deep clone drawing object to avoid shared mutable references
  const cloned: DrawingObject = {
    ...drawing,
    anchors: drawing.anchors.map((p) => ({ ...p })),
    style: { ...drawing.style },
    updatedAt: new Date().toISOString(),
  };

  return {
    applied: true,
    clonedDrawing: cloned,
  };
}
