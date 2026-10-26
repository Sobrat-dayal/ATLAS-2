/**
 * Stage 95: Comprehensive Automated Tests for Visual Screener Filter Utilities
 */

import assert from "node:assert/strict";
import test from "node:test";

import {
  ScreenerFilterDefinition,
  ScreenerUniverseDefinition,
  VisualFilterCondition,
} from "../types";
import { validateVisualConditions, getMagnitudeMultiplier } from "../validation";
import { detectContradictions } from "../contradictions";
import { generateQueryPreview, formatConditionPlainEnglish } from "../preview";
import { serializeScreenerState, deserializeScreenerState } from "../url-state";

// Mock Filter Registry
const mockFiltersRegistry: ScreenerFilterDefinition[] = [
  {
    filter_id: "market_cap",
    display_name: "Market Capitalization",
    description: "Total institutional equity market cap.",
    category: "market_data",
    value_type: "currency",
    unit_kind: "monetary",
    allowed_operators: ["gt", "gte", "lt", "lte", "between"],
    default_operator: "gte",
    is_range_supported: true,
    min_value: 0,
    editor_type: "monetary_input",
    currency_options: ["USD", "EUR", "GBP"],
    magnitude_options: ["UNITS", "MILLIONS", "BILLIONS"],
  },
  {
    filter_id: "last_price",
    display_name: "Last Price",
    description: "Latest closing price.",
    category: "market_data",
    value_type: "currency",
    unit_kind: "monetary",
    allowed_operators: ["gt", "gte", "lt", "lte", "between", "eq"],
    default_operator: "gte",
    is_range_supported: true,
    min_value: 0,
    editor_type: "monetary_input",
  },
  {
    filter_id: "pe_ratio",
    display_name: "P/E Ratio",
    description: "Trailing price to earnings.",
    category: "valuation",
    value_type: "numeric",
    unit_kind: "multiple",
    allowed_operators: ["gt", "gte", "lt", "lte", "between"],
    default_operator: "lte",
    is_range_supported: true,
    min_value: 0,
    editor_type: "multiple_input",
  },
  {
    filter_id: "sector",
    display_name: "Sector",
    description: "Industry sector.",
    category: "industry",
    value_type: "enum",
    unit_kind: "dimensionless",
    allowed_operators: ["eq", "in", "ne"],
    default_operator: "in",
    is_range_supported: false,
    editor_type: "enum_multi_select",
  },
];

const mockUniverses: ScreenerUniverseDefinition[] = [
  {
    universe_id: "common_equity",
    name: "Common Equities",
    description: "Global listed common equity.",
    asset_class: "EQUITY",
    eligible_security_types: ["common_stock"],
    eligible_listing_statuses: ["active"],
    is_default: true,
  },
];

// 1. Magnitude Multiplier Tests
test("getMagnitudeMultiplier converts scales correctly", () => {
  assert.equal(getMagnitudeMultiplier("UNITS"), 1);
  assert.equal(getMagnitudeMultiplier("THOUSANDS"), 1e3);
  assert.equal(getMagnitudeMultiplier("MILLIONS"), 1e6);
  assert.equal(getMagnitudeMultiplier("BILLIONS"), 1e9);
  assert.equal(getMagnitudeMultiplier("TRILLIONS"), 1e12);
  assert.equal(getMagnitudeMultiplier(undefined), 1);
});

// 2. Client Validation Tests
test("validateVisualConditions marks complete valid conditions as valid", () => {
  const conditions: VisualFilterCondition[] = [
    {
      conditionId: "c1",
      filterId: "last_price",
      operator: "gte",
      value: "50.25",
      status: "incomplete",
    },
    {
      conditionId: "c2",
      filterId: "pe_ratio",
      operator: "lte",
      value: "25.0",
      status: "incomplete",
    },
  ];

  const res = validateVisualConditions(conditions, mockFiltersRegistry, "common_equity", mockUniverses);
  assert.equal(res.isValid, true);
  assert.equal(res.issues.length, 0);
  assert.equal(res.updatedConditions[0].status, "valid");
  assert.equal(res.updatedConditions[1].status, "valid");
});

test("validateVisualConditions flags incomplete draft conditions without fatal errors", () => {
  const conditions: VisualFilterCondition[] = [
    {
      conditionId: "c1",
      filterId: "last_price",
      operator: "gte",
      value: "",
      status: "incomplete",
    },
  ];

  const res = validateVisualConditions(conditions, mockFiltersRegistry, "common_equity", mockUniverses);
  assert.equal(res.isValid, false);
  assert.equal(res.updatedConditions[0].status, "incomplete");
  assert.equal(res.updatedConditions[0].validationMessage, "Threshold required");
});

test("validateVisualConditions rejects non-finite NaN and Infinity", () => {
  const conditions: VisualFilterCondition[] = [
    {
      conditionId: "c1",
      filterId: "last_price",
      operator: "gte",
      value: "NaN",
      status: "incomplete",
    },
    {
      conditionId: "c2",
      filterId: "last_price",
      operator: "gte",
      value: "Infinity",
      status: "incomplete",
    },
  ];

  const res = validateVisualConditions(conditions, mockFiltersRegistry, "common_equity", mockUniverses);
  assert.equal(res.isValid, false);
  assert.equal(res.updatedConditions[0].status, "invalid");
  assert.equal(res.updatedConditions[1].status, "invalid");
});

test("validateVisualConditions validates between range bounds", () => {
  const invalidRange: VisualFilterCondition[] = [
    {
      conditionId: "c1",
      filterId: "last_price",
      operator: "between",
      value: "100",
      secondaryValue: "50",
      status: "incomplete",
    },
  ];

  const res = validateVisualConditions(invalidRange, mockFiltersRegistry, "common_equity", mockUniverses);
  assert.equal(res.isValid, false);
  assert.equal(res.updatedConditions[0].status, "invalid");
  assert.match(res.updatedConditions[0].validationMessage || "", /strictly exceeds upper bound|cannot be less than lower bound/i);
});

// 3. Contradiction Detection Tests
test("detectContradictions detects lower bound exceeding upper bound", () => {
  const conditions: VisualFilterCondition[] = [
    {
      conditionId: "c-gt",
      filterId: "last_price",
      operator: "gt",
      value: "200",
      status: "valid",
    },
    {
      conditionId: "c-lt",
      filterId: "last_price",
      operator: "lt",
      value: "100",
      status: "valid",
    },
  ];

  const issues = detectContradictions(conditions, mockFiltersRegistry);
  assert.equal(issues.length, 1);
  assert.equal(issues[0].code, "SCREENER_CONTRADICTORY_CONDITIONS");
  assert.match(issues[0].message, /strictly exceeds upper bound/i);
});

test("detectContradictions detects unsatisfiable strict boundary on same value", () => {
  const conditions: VisualFilterCondition[] = [
    {
      conditionId: "c-gt",
      filterId: "last_price",
      operator: "gt",
      value: "100",
      status: "valid",
    },
    {
      conditionId: "c-lt",
      filterId: "last_price",
      operator: "lt",
      value: "100",
      status: "valid",
    },
  ];

  const issues = detectContradictions(conditions, mockFiltersRegistry);
  assert.equal(issues.length, 1);
  assert.match(issues[0].message, /strict inequality boundary at 100 cannot be satisfied/i);
});

test("detectContradictions allows valid overlapping boundaries", () => {
  const conditions: VisualFilterCondition[] = [
    {
      conditionId: "c-gte",
      filterId: "last_price",
      operator: "gte",
      value: "100",
      status: "valid",
    },
    {
      conditionId: "c-lte",
      filterId: "last_price",
      operator: "lte",
      value: "100",
      status: "valid",
    },
  ];

  const issues = detectContradictions(conditions, mockFiltersRegistry);
  assert.equal(issues.length, 0);
});

test("detectContradictions detects conflicting equality on single-valued classifications", () => {
  const conditions: VisualFilterCondition[] = [
    {
      conditionId: "c-sec-1",
      filterId: "sector",
      operator: "eq",
      value: "Technology",
      status: "valid",
    },
    {
      conditionId: "c-sec-2",
      filterId: "sector",
      operator: "eq",
      value: "Healthcare",
      status: "valid",
    },
  ];

  const issues = detectContradictions(conditions, mockFiltersRegistry);
  assert.equal(issues.length, 1);
  assert.match(issues[0].message, /cannot equal both/i);
});

// 4. Query Transparency Preview Tests
test("formatConditionPlainEnglish formats diverse metric kinds deterministically", () => {
  const monetaryCond: VisualFilterCondition = {
    conditionId: "c1",
    filterId: "market_cap",
    operator: "gte",
    value: "10",
    magnitude: "BILLIONS",
    currency: "USD",
    status: "valid",
  };
  assert.equal(
    formatConditionPlainEnglish(monetaryCond, mockFiltersRegistry),
    "Market Capitalization >= 10 BILLIONS (USD)"
  );

  const multipleCond: VisualFilterCondition = {
    conditionId: "c2",
    filterId: "pe_ratio",
    operator: "lte",
    value: "20.5",
    status: "valid",
  };
  assert.equal(
    formatConditionPlainEnglish(multipleCond, mockFiltersRegistry),
    "P/E Ratio <= 20.5x"
  );

  const rangeCond: VisualFilterCondition = {
    conditionId: "c3",
    filterId: "last_price",
    operator: "between",
    value: "50",
    secondaryValue: "150",
    currency: "USD",
    status: "valid",
  };
  assert.equal(
    formatConditionPlainEnglish(rangeCond, mockFiltersRegistry),
    "Last Price BETWEEN 50 AND 150 USD"
  );
});

test("generateQueryPreview produces structured summary", () => {
  const conditions: VisualFilterCondition[] = [
    {
      conditionId: "c1",
      filterId: "market_cap",
      operator: "gte",
      value: "50",
      magnitude: "BILLIONS",
      currency: "USD",
      status: "valid",
    },
  ];

  const summary = generateQueryPreview(
    conditions,
    mockFiltersRegistry,
    "common_equity",
    mockUniverses,
    true,
    false,
    []
  );

  assert.equal(summary.universeName, "Common Equities");
  assert.equal(summary.conditionsCount, 1);
  assert.equal(summary.plainEnglishPredicates.length, 1);
  assert.equal(summary.isValid, true);
  assert.equal(summary.contradictionsDetected, false);
});

// 5. URL State Round-Trip Tests
test("serializeScreenerState and deserializeScreenerState round-trip cleanly", () => {
  const originalConditions: VisualFilterCondition[] = [
    {
      conditionId: "orig-1",
      filterId: "market_cap",
      operator: "gte",
      value: "100",
      magnitude: "BILLIONS",
      currency: "USD",
      status: "valid",
    },
    {
      conditionId: "orig-2",
      filterId: "pe_ratio",
      operator: "lte",
      value: "25",
      status: "valid",
    },
  ];

  const sort = [{ field_id: "market_cap", direction: "desc" as const }];
  const urlEncoded = serializeScreenerState("common_equity", originalConditions, sort);
  assert.ok(urlEncoded.length > 0);

  const deserialized = deserializeScreenerState(urlEncoded, mockFiltersRegistry);
  assert.equal(deserialized.universeId, "common_equity");
  assert.equal(deserialized.conditions.length, 2);
  assert.equal(deserialized.conditions[0].filterId, "market_cap");
  assert.equal(deserialized.conditions[0].operator, "gte");
  assert.equal(deserialized.conditions[0].value, "100");
  assert.equal(deserialized.conditions[0].magnitude, "BILLIONS");
  assert.equal(deserialized.conditions[1].filterId, "pe_ratio");
  assert.equal(deserialized.conditions[1].value, "25");
  assert.equal(deserialized.sort?.[0].field_id, "market_cap");
});

test("deserializeScreenerState safely rejects unknown filters and operators", () => {
  const maliciousPayload = {
    v: 1,
    u: "common_equity",
    filters: [
      { f: "non_existent_exploit", op: "gte", v: "100" },
      { f: "pe_ratio", op: "unsupported_hack", v: "25" },
    ],
  };
  const encoded = encodeURIComponent(JSON.stringify(maliciousPayload));
  const res = deserializeScreenerState(encoded, mockFiltersRegistry);
  assert.equal(res.conditions.length, 0);
  assert.equal(res.warnings.length, 2);
});
