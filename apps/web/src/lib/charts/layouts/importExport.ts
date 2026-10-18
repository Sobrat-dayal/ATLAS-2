/**
 * Portable JSON Import & Export Utilities for ATLAS Chart Layouts (Stage 74).
 *
 * Implements:
 * - Versioned export format envelope (atlas_chart_layout v1)
 * - Strict stripping of sensitive tokens, user IDs, or proprietary runtime objects
 * - File-size boundary verification (max 512 KiB)
 * - Import preview aggregation (charts, indicators, drawings, sync groups)
 * - Safe file reading in browser environment
 */

import {
  LayoutExportEnvelope,
  SavedChartLayoutDocumentV1,
} from "./types";
import { validateLayoutDocument, LayoutValidationError, MAX_DOCUMENT_BYTES } from "./schema";

export interface ImportPreviewSummary {
  layoutName: string;
  layoutId: string;
  panelCount: number;
  indicatorCount: number;
  drawingCount: number;
  syncGroupCount: number;
  document: SavedChartLayoutDocumentV1;
}

/**
 * Creates a clean, portable export envelope JSON string.
 */
export function generateExportEnvelope(
  layoutName: string,
  document: SavedChartLayoutDocumentV1
): string {
  const validated = validateLayoutDocument(document);

  const envelope: LayoutExportEnvelope = {
    format: "atlas_chart_layout",
    export_version: 1,
    exported_at: new Date().toISOString(),
    layout_name: layoutName.trim() || "ATLAS Chart Layout",
    document_schema_version: 1,
    layout_document: validated,
  };

  return JSON.stringify(envelope, null, 2);
}

/**
 * Triggers a browser file download of the exported JSON layout.
 */
export function triggerLayoutDownload(layoutName: string, jsonString: string): void {
  if (typeof window === "undefined" || typeof document === "undefined") return;

  const blob = new Blob([jsonString], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  const safeFilename = layoutName
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, "_")
    .replace(/_+/g, "_");

  anchor.href = url;
  anchor.download = `atlas_layout_${safeFilename || "chart"}.json`;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

/**
 * Validates and parses raw imported JSON text into a verified preview summary.
 */
export function parseAndValidateImportJson(jsonText: string): ImportPreviewSummary {
  if (jsonText.length > MAX_DOCUMENT_BYTES) {
    throw new LayoutValidationError(
      `Import file size (${jsonText.length} bytes) exceeds maximum permitted limit of ${MAX_DOCUMENT_BYTES} bytes.`
    );
  }

  let parsed: any;
  try {
    parsed = JSON.parse(jsonText);
  } catch (err: any) {
    throw new LayoutValidationError(`Invalid JSON format: ${err.message}`);
  }

  if (!parsed || typeof parsed !== "object") {
    throw new LayoutValidationError("Imported file must contain a valid JSON object.");
  }

  // Verify envelope format
  if (parsed.format !== "atlas_chart_layout") {
    throw new LayoutValidationError(
      `Unrecognized layout format '${parsed.format}'. Expected 'atlas_chart_layout'.`
    );
  }

  if (parsed.export_version !== 1) {
    throw new LayoutValidationError(
      `Unsupported export_version '${parsed.export_version}'. Only version 1 is supported.`
    );
  }

  const rawDoc = parsed.layout_document;
  if (!rawDoc || typeof rawDoc !== "object") {
    throw new LayoutValidationError("Missing 'layout_document' in import file.");
  }

  // Validate the layout document
  const validatedDoc = validateLayoutDocument(rawDoc);

  let totalIndicators = 0;
  let totalDrawings = 0;
  for (const p of validatedDoc.panels) {
    totalIndicators += p.indicators?.length || 0;
    totalDrawings += p.drawings?.length || 0;
  }

  return {
    layoutName: parsed.layout_name || "Imported Layout",
    layoutId: validatedDoc.layout_id,
    panelCount: validatedDoc.panels.length,
    indicatorCount: totalIndicators,
    drawingCount: totalDrawings,
    syncGroupCount: validatedDoc.synchronization_groups?.length || 0,
    document: validatedDoc,
  };
}
