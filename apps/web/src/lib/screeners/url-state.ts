/**
 * URL State Synchronization & Safe Query Reconstruction (Stage 95).
 */

import {
  FilterOperator,
  ScreenerFilterDefinition,
  SortCriterion,
  VisualFilterCondition,
} from "./types";

const MAX_URL_QUERY_LENGTH = 2048;

export interface DeserializedScreenerState {
  universeId?: string;
  conditions: VisualFilterCondition[];
  sort?: SortCriterion[];
  warnings: string[];
}

export function serializeScreenerState(
  universeId: string,
  conditions: VisualFilterCondition[],
  sort: SortCriterion[]
): string {
  try {
    const compactFilters = conditions.map((c) => ({
      f: c.filterId,
      op: c.operator,
      v: c.value,
      s: c.secondaryValue || undefined,
      cur: c.currency || undefined,
      m: c.magnitude || undefined,
    }));

    const payload = {
      v: 1, // schema version
      u: universeId,
      filters: compactFilters,
      sort: sort.map((s) => ({ id: s.field_id, dir: s.direction })),
    };

    const json = JSON.stringify(payload);
    const encoded = encodeURIComponent(json);
    if (encoded.length > MAX_URL_QUERY_LENGTH) {
      console.warn("Screener query exceeds safe URL length budget. Skipping URL sync.");
      return "";
    }
    return encoded;
  } catch (err) {
    console.warn("Failed to serialize screener query to URL:", err);
    return "";
  }
}

interface SerializedFilterItem {
  f?: string;
  filter_id?: string;
  op?: string;
  operator?: string;
  v?: string | number;
  value?: string | number;
  s?: string | null;
  secondary_value?: string | null;
  cur?: string | null;
  currency?: string | null;
  m?: "UNITS" | "THOUSANDS" | "MILLIONS" | "BILLIONS" | "TRILLIONS";
  magnitude?: "UNITS" | "THOUSANDS" | "MILLIONS" | "BILLIONS" | "TRILLIONS";
}

interface SerializedSortItem {
  id?: string;
  dir?: "asc" | "desc";
}

export function deserializeScreenerState(
  encodedQuery: string | null,
  filtersRegistry: ScreenerFilterDefinition[]
): DeserializedScreenerState {
  if (!encodedQuery || !encodedQuery.trim()) {
    return { conditions: [], warnings: [] };
  }

  const warnings: string[] = [];
  const filterMap = new Map<string, ScreenerFilterDefinition>(
    filtersRegistry.map((f) => [f.filter_id, f])
  );

  try {
    const decoded = decodeURIComponent(encodedQuery);
    const parsed = JSON.parse(decoded);

    if (parsed.v !== 1 && parsed.v !== undefined) {
      warnings.push(`Unsupported query schema version (${parsed.v}).`);
    }

    const conditions: VisualFilterCondition[] = [];
    if (Array.isArray(parsed.filters)) {
      parsed.filters.forEach((item: SerializedFilterItem, idx: number) => {
        const filterId = item.f || item.filter_id;
        if (!filterId) return;
        const operator = (item.op || item.operator) as FilterOperator;
        const value = String(item.v !== undefined ? item.v : item.value || "");
        const secondaryValue = item.s || item.secondary_value || null;
        const currency = item.cur || item.currency || null;
        const magnitude = item.m || item.magnitude || "UNITS";

        const def = filterMap.get(filterId);
        if (!def) {
          warnings.push(`Filter '${filterId}' from URL is not registered.`);
          return;
        }

        if (!def.allowed_operators.includes(operator)) {
          warnings.push(`Operator '${operator}' in URL is invalid for '${def.display_name}'.`);
          return;
        }

        conditions.push({
          conditionId: `url-cond-${idx + 1}-${Date.now()}`,
          filterId,
          operator,
          value,
          secondaryValue,
          currency,
          magnitude,
          status: "valid",
        });
      });
    }

    const sort: SortCriterion[] = [];
    if (Array.isArray(parsed.sort)) {
      parsed.sort.forEach((s: SerializedSortItem) => {
        if (s.id && (s.dir === "asc" || s.dir === "desc")) {
          sort.push({ field_id: s.id, direction: s.dir });
        }
      });
    }

    return {
      universeId: parsed.u || undefined,
      conditions,
      sort: sort.length > 0 ? sort : undefined,
      warnings,
    };
  } catch {
    warnings.push("Failed to parse screener query from URL state.");
    return { conditions: [], warnings };
  }
}
