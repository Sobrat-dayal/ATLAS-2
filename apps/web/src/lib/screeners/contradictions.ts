/**
 * Contradictory condition detection engine (Stage 95).
 * Detects provable impossible constraints on identical metrics and single-valued classifications.
 */

import { ConditionValidationIssue, ScreenerFilterDefinition, VisualFilterCondition } from "./types";

interface NumericBound {
  minVal: number | null;
  minStrict: boolean;
  minConditionId: string | null;
  maxVal: number | null;
  maxStrict: boolean;
  maxConditionId: string | null;
  eqVal: number | null;
  eqConditionId: string | null;
}

export function detectContradictions(
  conditions: VisualFilterCondition[],
  filtersRegistry: ScreenerFilterDefinition[]
): ConditionValidationIssue[] {
  const issues: ConditionValidationIssue[] = [];
  const filterMap = new Map<string, ScreenerFilterDefinition>(
    filtersRegistry.map((f) => [f.filter_id, f])
  );

  // 1. Numeric Boundary Contradictions
  const boundsByFilter = new Map<string, NumericBound>();

  for (const cond of conditions) {
    if (!cond.value || cond.value.trim() === "") continue;
    const def = filterMap.get(cond.filterId);
    if (!def) continue;

    const isNumeric = ["numeric", "currency", "percentage", "integer"].includes(def.value_type);
    if (!isNumeric || cond.operator === "in") continue;

    if (!boundsByFilter.has(cond.filterId)) {
      boundsByFilter.set(cond.filterId, {
        minVal: null,
        minStrict: false,
        minConditionId: null,
        maxVal: null,
        maxStrict: false,
        maxConditionId: null,
        eqVal: null,
        eqConditionId: null,
      });
    }
    const b = boundsByFilter.get(cond.filterId)!;

    const parsedVal = Number(cond.value);
    if (!Number.isFinite(parsedVal)) continue;

    if (cond.operator === "gt" || cond.operator === "gte") {
      const isStrict = cond.operator === "gt";
      if (b.minVal === null || parsedVal > b.minVal || (parsedVal === b.minVal && isStrict)) {
        b.minVal = parsedVal;
        b.minStrict = isStrict;
        b.minConditionId = cond.conditionId;
      }
    } else if (cond.operator === "lt" || cond.operator === "lte") {
      const isStrict = cond.operator === "lt";
      if (b.maxVal === null || parsedVal < b.maxVal || (parsedVal === b.maxVal && isStrict)) {
        b.maxVal = parsedVal;
        b.maxStrict = isStrict;
        b.maxConditionId = cond.conditionId;
      }
    } else if (cond.operator === "eq") {
      if (b.eqVal !== null && b.eqVal !== parsedVal) {
        issues.push({
          condition_id: cond.conditionId,
          filter_id: cond.filterId,
          code: "SCREENER_CONTRADICTORY_CONDITIONS",
          severity: "error",
          message: `Contradictory equality conditions: '${def.display_name}' cannot equal both ${b.eqVal} and ${parsedVal}.`,
        });
      }
      b.eqVal = parsedVal;
      b.eqConditionId = cond.conditionId;
    } else if (cond.operator === "between" && cond.secondaryValue) {
      const parsedUpper = Number(cond.secondaryValue);
      if (Number.isFinite(parsedUpper)) {
        if (b.minVal === null || parsedVal > b.minVal) {
          b.minVal = parsedVal;
          b.minStrict = false;
          b.minConditionId = cond.conditionId;
        }
        if (b.maxVal === null || parsedUpper < b.maxVal) {
          b.maxVal = parsedUpper;
          b.maxStrict = false;
          b.maxConditionId = cond.conditionId;
        }
      }
    }
  }

  // Evaluate accumulated numeric boundaries
  for (const [filterId, b] of boundsByFilter.entries()) {
    const def = filterMap.get(filterId);
    const label = def?.display_name ?? filterId;

    if (b.minVal !== null && b.maxVal !== null) {
      if (b.minVal > b.maxVal) {
        issues.push({
          condition_id: b.maxConditionId ?? b.minConditionId,
          filter_id: filterId,
          code: "SCREENER_CONTRADICTORY_CONDITIONS",
          severity: "error",
          message: `Contradictory conditions on ${label}: lower bound (${b.minVal}) strictly exceeds upper bound (${b.maxVal}).`,
        });
      } else if (b.minVal === b.maxVal && (b.minStrict || b.maxStrict)) {
        issues.push({
          condition_id: b.maxConditionId ?? b.minConditionId,
          filter_id: filterId,
          code: "SCREENER_CONTRADICTORY_CONDITIONS",
          severity: "error",
          message: `Contradictory conditions on ${label}: strict inequality boundary at ${b.minVal} cannot be satisfied.`,
        });
      }
    }
  }

  // 2. Single-valued Enum Contradictions
  const singleValuedFields = new Set([
    "sector",
    "industry",
    "exchange_mic",
    "listing_country_code",
    "issuer_country_code",
  ]);

  const eqSeen = new Map<string, { value: string; conditionId: string }>();

  for (const cond of conditions) {
    if (singleValuedFields.has(cond.filterId) && cond.operator === "eq") {
      const cleanVal = cond.value.trim().toLowerCase();
      if (!cleanVal) continue;

      if (eqSeen.has(cond.filterId)) {
        const prev = eqSeen.get(cond.filterId)!;
        if (prev.value !== cleanVal) {
          const def = filterMap.get(cond.filterId);
          const label = def?.display_name ?? cond.filterId;
          issues.push({
            condition_id: cond.conditionId,
            filter_id: cond.filterId,
            code: "SCREENER_CONTRADICTORY_CONDITIONS",
            severity: "error",
            message: `Contradictory conditions on ${label}: cannot equal both '${prev.value}' and '${cleanVal}' simultaneously.`,
          });
        }
      } else {
        eqSeen.set(cond.filterId, { value: cleanVal, conditionId: cond.conditionId });
      }
    }
  }

  return issues;
}
