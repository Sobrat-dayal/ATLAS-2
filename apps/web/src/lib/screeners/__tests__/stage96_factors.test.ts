/**
 * Stage 96: Automated Tests for Fundamental, Technical, and Multi-Factor Screener Filters
 */

import assert from "node:assert/strict";
import test from "node:test";

import {
  ScreenerFilterDefinition,
  ScreenerUniverseDefinition,
  VisualFilterCondition,
} from "../types";
import { validateVisualConditions } from "../validation";
import { formatConditionPlainEnglish, generateQueryPreview } from "../preview";

const mockUniverse: ScreenerUniverseDefinition = {
  universe_id: "all_us_equities",
  name: "All Listed Equities",
  description: "Comprehensive active security universe",
  asset_class: "EQUITY",
  eligible_security_types: ["common_stock"],
  eligible_listing_statuses: ["active"],
  is_default: true,
};

const mockStage96Registry: ScreenerFilterDefinition[] = [
  {
    filter_id: "revenue_growth_yoy",
    display_name: "Revenue Growth (YoY)",
    description: "Year-over-year revenue percentage expansion.",
    category: "growth",
    value_type: "percentage",
    unit_kind: "percent",
    allowed_operators: ["gt", "gte", "lt", "lte", "between"],
    default_operator: "gte",
    is_range_supported: true,
    editor_type: "percent_input",
    calculation_version: "1.0.0",
  },
  {
    filter_id: "fcf",
    display_name: "Free Cash Flow (FCF)",
    description: "Operating cash flow minus CapEx.",
    category: "cash_flow",
    value_type: "currency",
    unit_kind: "monetary",
    allowed_operators: ["gt", "gte", "lt", "lte", "between"],
    default_operator: "gte",
    is_range_supported: true,
    editor_type: "monetary_input",
    currency_options: ["USD"],
    magnitude_options: ["UNITS", "MILLIONS", "BILLIONS"],
    calculation_version: "1.0.0",
  },
  {
    filter_id: "sma_50",
    display_name: "50-Session Simple Moving Average",
    description: "Unweighted 50-session moving average of completed closes.",
    category: "technical_trend",
    value_type: "currency",
    unit_kind: "monetary",
    allowed_operators: ["gt", "gte", "lt", "lte", "between"],
    default_operator: "gte",
    is_range_supported: true,
    editor_type: "monetary_input",
    indicator_type: "sma",
    default_parameters: { period: 50 },
    allowed_parameters: { period: [20, 50, 100, 200] },
    minimum_lookback: 50,
    calculation_version: "1.0.0",
  },
  {
    filter_id: "rsi_14",
    display_name: "Relative Strength Index (14)",
    description: "14-session Wilder RSI bounded between 0 and 100.",
    category: "technical_momentum",
    value_type: "numeric",
    unit_kind: "dimensionless",
    allowed_operators: ["gt", "gte", "lt", "lte", "between"],
    default_operator: "lte",
    is_range_supported: true,
    min_value: 0,
    max_value: 100,
    editor_type: "decimal_input",
    indicator_type: "rsi",
    default_parameters: { period: 14 },
    allowed_parameters: { period: [9, 14, 21, 28] },
    minimum_lookback: 15,
    calculation_version: "1.0.0",
  },
  {
    filter_id: "price_above_sma200",
    display_name: "Price Above 200 SMA",
    description: "Latest completed close strictly above 200-session SMA.",
    category: "technical_trend",
    value_type: "boolean",
    unit_kind: "dimensionless",
    allowed_operators: ["eq", "ne"],
    default_operator: "eq",
    is_range_supported: false,
    editor_type: "boolean_select",
    indicator_type: "trend_state",
    calculation_version: "1.0.0",
  },
];

test("Stage 96: Parameter bounds validation accepts valid periods and rejects out-of-bound values", () => {
  // Valid condition with 50-bar period
  const validCond: VisualFilterCondition = {
    conditionId: "cond-1",
    filterId: "sma_50",
    operator: "gte",
    value: "150",
    parameters: { period: 50 },
    status: "valid",
  };

  const resValid = validateVisualConditions(
    [validCond],
    mockStage96Registry,
    "all_us_equities",
    [mockUniverse]
  );
  assert.equal(resValid.isValid, true);

  // Invalid condition with period 9999 (> 500 max bound)
  const invalidCond: VisualFilterCondition = {
    conditionId: "cond-2",
    filterId: "sma_50",
    operator: "gte",
    value: "150",
    parameters: { period: 9999 },
    status: "valid",
  };

  const resInvalid = validateVisualConditions(
    [invalidCond],
    mockStage96Registry,
    "all_us_equities",
    [mockUniverse]
  );
  assert.equal(resInvalid.isValid, false);
  assert.ok(resInvalid.issues.some((i) => i.code === "SCREENER_PARAMETER_INVALID"));
});

test("Stage 96: Boolean indicator state filter validates cleanly", () => {
  const boolCond: VisualFilterCondition = {
    conditionId: "cond-bool",
    filterId: "price_above_sma200",
    operator: "eq",
    value: "true",
    status: "valid",
  };

  const res = validateVisualConditions(
    [boolCond],
    mockStage96Registry,
    "all_us_equities",
    [mockUniverse]
  );
  assert.equal(res.isValid, true);
  assert.equal(res.issues.length, 0);

  const previewStr = formatConditionPlainEnglish(boolCond, mockStage96Registry);
  assert.equal(previewStr, "Price Above 200 SMA = True");
});

test("Stage 96: Multi-factor combination formatting in plain English", () => {
  const conditions: VisualFilterCondition[] = [
    {
      conditionId: "c1",
      filterId: "revenue_growth_yoy",
      operator: "gte",
      value: "15.0",
      status: "valid",
    },
    {
      conditionId: "c2",
      filterId: "price_above_sma200",
      operator: "eq",
      value: "true",
      status: "valid",
    },
    {
      conditionId: "c3",
      filterId: "rsi_14",
      operator: "lte",
      value: "65.0",
      parameters: { period: 14 },
      status: "valid",
    },
    {
      conditionId: "c4",
      filterId: "fcf",
      operator: "gt",
      value: "0",
      currency: "USD",
      status: "valid",
    },
  ];

  const preview = generateQueryPreview(
    conditions,
    mockStage96Registry,
    "all_us_equities",
    [mockUniverse],
    true,
    false,
    []
  );

  assert.equal(preview.conditionsCount, 4);
  assert.equal(preview.isValid, true);
  assert.equal(preview.plainEnglishPredicates[0], "Revenue Growth (YoY) >= 15.0%");
  assert.equal(preview.plainEnglishPredicates[1], "Price Above 200 SMA = True");
  assert.ok(preview.plainEnglishPredicates[2].includes("Relative Strength Index (14)"));
  assert.ok(preview.plainEnglishPredicates[2].includes("<= 65.0"));
  assert.equal(preview.plainEnglishPredicates[3], "Free Cash Flow (FCF) > 0 (USD)");
});
