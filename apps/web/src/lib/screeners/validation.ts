/**
 * Client-Side Interactive Filter Validation & Dependency Engine (Stage 95).
 */

import {
  ConditionValidationIssue,
  ScreenerFilterDefinition,
  ScreenerUniverseDefinition,
  VisualFilterCondition,
} from "./types";
import { detectContradictions } from "./contradictions";

export const MAX_ACTIVE_CONDITIONS = 20;

export interface ClientValidationResult {
  updatedConditions: VisualFilterCondition[];
  isValid: boolean;
  issues: ConditionValidationIssue[];
  warnings: string[];
}

export function validateVisualConditions(
  conditions: VisualFilterCondition[],
  filtersRegistry: ScreenerFilterDefinition[],
  selectedUniverseId: string,
  universes: ScreenerUniverseDefinition[]
): ClientValidationResult {
  const issues: ConditionValidationIssue[] = [];
  const warnings: string[] = [];

  const filterMap = new Map<string, ScreenerFilterDefinition>(
    filtersRegistry.map((f) => [f.filter_id, f])
  );
  const uDef = universes.find((u) => u.universe_id === selectedUniverseId);

  // 1. Condition Limit Check
  if (conditions.length > MAX_ACTIVE_CONDITIONS) {
    issues.push({
      code: "SCREENER_CONDITION_LIMIT_EXCEEDED",
      severity: "error",
      message: `Maximum active filter limit of ${MAX_ACTIVE_CONDITIONS} exceeded (current: ${conditions.length}).`,
    });
  }

  // 2. Per-condition inspection
  const updatedConditions: VisualFilterCondition[] = conditions.map((cond) => {
    const fieldErrors: Record<string, string> = {};
    let status: VisualFilterCondition["status"] = "valid";
    let validationMessage: string | null = null;

    const def = filterMap.get(cond.filterId);
    if (!def) {
      status = "invalid";
      fieldErrors.filterId = `Filter '${cond.filterId}' is not recognized.`;
      validationMessage = fieldErrors.filterId;
      issues.push({
        condition_id: cond.conditionId,
        filter_id: cond.filterId,
        field_path: "filterId",
        code: "SCREENER_FILTER_NOT_FOUND",
        severity: "error",
        message: validationMessage,
      });
      return { ...cond, status, fieldErrors, validationMessage };
    }

    // Check operator validity
    if (!def.allowed_operators.includes(cond.operator)) {
      status = "invalid";
      fieldErrors.operator = `Operator '${cond.operator}' is not supported for ${def.display_name}.`;
      validationMessage = fieldErrors.operator;
      issues.push({
        condition_id: cond.conditionId,
        filter_id: cond.filterId,
        field_path: "operator",
        code: "SCREENER_OPERATOR_NOT_SUPPORTED",
        severity: "error",
        message: validationMessage,
      });
    }

    // Check universe eligibility dependency
    if (def.eligible_security_types && def.eligible_security_types.length > 0 && uDef) {
      const overlap = def.eligible_security_types.some((st) =>
        uDef.eligible_security_types.includes(st)
      );
      if (!overlap) {
        const warn = `Metric '${def.display_name}' applies to ${def.eligible_security_types.join(", ")}, which are excluded in '${uDef.name}'.`;
        warnings.push(warn);
        issues.push({
          condition_id: cond.conditionId,
          filter_id: cond.filterId,
          code: "SCREENER_UNIVERSE_INCOMPATIBILITY",
          severity: "warning",
          message: warn,
        });
      }
    }

    // Check empty value (incomplete draft)
    const valStr = cond.value?.trim() ?? "";
    if (valStr === "") {
      status = "incomplete";
      fieldErrors.value = "Enter a threshold value.";
      validationMessage = "Threshold required";
      return { ...cond, status, fieldErrors, validationMessage };
    }

    // Intermediate typing states (e.g. '-' or '12.') are incomplete, not hard fatal errors
    if (valStr === "-" || valStr === "." || valStr === "-.") {
      status = "incomplete";
      fieldErrors.value = "Complete entering the numeric value.";
      validationMessage = "Incomplete numeric value";
      return { ...cond, status, fieldErrors, validationMessage };
    }

    // Check numeric constraints
    const isNumericType = ["numeric", "currency", "percentage", "integer"].includes(def.value_type);
    if (isNumericType && cond.operator !== "in") {
      const num = Number(valStr);
      if (Number.isNaN(num) || !Number.isFinite(num)) {
        status = "invalid";
        fieldErrors.value = "Value must be a valid finite number.";
        validationMessage = fieldErrors.value;
        issues.push({
          condition_id: cond.conditionId,
          filter_id: cond.filterId,
          field_path: "value",
          code: "SCREENER_VALUE_TYPE_INVALID",
          severity: "error",
          message: validationMessage,
        });
      } else {
        // Bound checks if defined
        if (def.min_value !== undefined && def.min_value !== null && num < def.min_value) {
          status = "invalid";
          fieldErrors.value = `Value cannot be less than minimum (${def.min_value}).`;
          validationMessage = fieldErrors.value;
          issues.push({
            condition_id: cond.conditionId,
            filter_id: cond.filterId,
            field_path: "value",
            code: "SCREENER_RANGE_INVALID",
            severity: "error",
            message: validationMessage,
          });
        }
        if (def.max_value !== undefined && def.max_value !== null && num > def.max_value) {
          status = "invalid";
          fieldErrors.value = `Value cannot exceed maximum (${def.max_value}).`;
          validationMessage = fieldErrors.value;
          issues.push({
            condition_id: cond.conditionId,
            filter_id: cond.filterId,
            field_path: "value",
            code: "SCREENER_RANGE_INVALID",
            severity: "error",
            message: validationMessage,
          });
        }
      }
    }

    // Range BETWEEN validation
    if (cond.operator === "between") {
      const secStr = cond.secondaryValue?.trim() ?? "";
      if (secStr === "") {
        status = "incomplete";
        fieldErrors.secondaryValue = "Upper boundary required for range comparison.";
        validationMessage = "Upper bound required";
      } else {
        const secNum = Number(secStr);
        const lowerNum = Number(valStr);
        if (Number.isNaN(secNum) || !Number.isFinite(secNum)) {
          status = "invalid";
          fieldErrors.secondaryValue = "Upper boundary must be a valid number.";
          validationMessage = fieldErrors.secondaryValue;
        } else if (!Number.isNaN(lowerNum) && lowerNum > secNum) {
          status = "invalid";
          fieldErrors.secondaryValue = `Upper bound (${secNum}) cannot be less than lower bound (${lowerNum}).`;
          validationMessage = fieldErrors.secondaryValue;
          issues.push({
            condition_id: cond.conditionId,
            filter_id: cond.filterId,
            field_path: "secondaryValue",
            code: "SCREENER_RANGE_INVALID",
            severity: "error",
            message: validationMessage,
          });
        }
      }
    }

    return {
      ...cond,
      status,
      fieldErrors,
      validationMessage,
    };
  });

  // 3. Contradiction Detection across valid/complete conditions
  const contradictionIssues = detectContradictions(updatedConditions, filtersRegistry);
  for (const cIssue of contradictionIssues) {
    issues.push(cIssue);
    // Mark target condition as invalid
    const match = updatedConditions.find((c) => c.conditionId === cIssue.condition_id);
    if (match) {
      match.status = "invalid";
      match.validationMessage = cIssue.message;
    }
  }

  const hasFatalIssues = issues.some((i) => i.severity === "error");
  const hasIncomplete = updatedConditions.some((c) => c.status === "incomplete" || c.status === "invalid");
  const isValid = !hasFatalIssues && !hasIncomplete;

  return {
    updatedConditions,
    isValid,
    issues,
    warnings,
  };
}

/**
 * Normalizes input numeric string based on magnitude factor (e.g. Billions -> * 1e9).
 */
export function getMagnitudeMultiplier(
  magnitude?: "UNITS" | "THOUSANDS" | "MILLIONS" | "BILLIONS" | "TRILLIONS"
): number {
  switch (magnitude) {
    case "THOUSANDS":
      return 1e3;
    case "MILLIONS":
      return 1e6;
    case "BILLIONS":
      return 1e9;
    case "TRILLIONS":
      return 1e12;
    default:
      return 1;
  }
}
