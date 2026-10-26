/**
 * Query Transparency & Review Logic Formatter (Stage 95).
 * Deterministically projects typed screener conditions into unambiguous institutional financial language.
 */

import {
  QueryPreviewSummary,
  ScreenerFilterDefinition,
  ScreenerUniverseDefinition,
  VisualFilterCondition,
} from "./types";


const OPERATOR_LABELS: Record<string, string> = {
  gt: ">",
  gte: ">=",
  lt: "<",
  lte: "<=",
  eq: "=",
  ne: "!=",
  between: "BETWEEN",
  in: "IN",
};

export function formatConditionPlainEnglish(
  cond: VisualFilterCondition,
  filtersRegistry: ScreenerFilterDefinition[]
): string {
  const def = filtersRegistry.find((f) => f.filter_id === cond.filterId);
  const metricLabel = def?.display_name ?? cond.filterId;
  const opLabel = OPERATOR_LABELS[cond.operator] ?? cond.operator.toUpperCase();

  if (!cond.value || cond.value.trim() === "") {
    return `${metricLabel} ${opLabel} [Incomplete Draft]`;
  }

  // Range condition
  if (cond.operator === "between") {
    const lower = cond.value;
    const upper = cond.secondaryValue || "[Missing Upper Bound]";
    const unitSuffix = def?.unit_kind === "percent" ? "%" : def?.unit_kind === "multiple" ? "x" : "";
    const curSuffix = cond.currency ? ` ${cond.currency}` : "";
    return `${metricLabel} BETWEEN ${lower}${unitSuffix} AND ${upper}${unitSuffix}${curSuffix}`;
  }

  // Multi-select / Enum IN
  if (cond.operator === "in") {
    return `${metricLabel} IN [${cond.value}]`;
  }

  // Monetary / Numeric
  if (def?.value_type === "currency" || def?.unit_kind === "monetary") {
    const cur = cond.currency || "USD";
    const mag = cond.magnitude && cond.magnitude !== "UNITS" ? ` ${cond.magnitude}` : "";
    return `${metricLabel} ${opLabel} ${cond.value}${mag} (${cur})`;
  }

  // Percentage
  if (def?.value_type === "percentage" || def?.unit_kind === "percent") {
    return `${metricLabel} ${opLabel} ${cond.value}%`;
  }

  // Multiple (e.g. P/E, P/B)
  if (def?.unit_kind === "multiple") {
    return `${metricLabel} ${opLabel} ${cond.value}x`;
  }

  // Shares / Integer
  if (def?.unit_kind === "shares" || def?.value_type === "integer") {
    return `${metricLabel} ${opLabel} ${Number(cond.value).toLocaleString()} shares`;
  }

  return `${metricLabel} ${opLabel} ${cond.value}`;
}

export function generateQueryPreview(
  conditions: VisualFilterCondition[],
  filtersRegistry: ScreenerFilterDefinition[],
  selectedUniverseId: string,
  universes: ScreenerUniverseDefinition[],
  isValid: boolean,
  contradictionsDetected: boolean,
  warnings: string[]
): QueryPreviewSummary {
  const uDef = universes.find((u) => u.universe_id === selectedUniverseId);
  const universeName = uDef?.name ?? selectedUniverseId;

  const plainEnglishPredicates = conditions.map((c) =>
    formatConditionPlainEnglish(c, filtersRegistry)
  );

  return {
    universeId: selectedUniverseId,
    universeName,
    conditionsCount: conditions.length,
    plainEnglishPredicates,
    periodPolicy: "Latest Verified Annual / TTM Fiscal Reporting Period",
    currencyPolicy: "USD Canonical Base with Source Reporting Currency Qualification",
    isValid,
    contradictionsDetected,
    warnings,
  };
}
