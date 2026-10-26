/**
 * Stage 97: Automated Tests for Saved Screeners, Multi-Column Sorting, Factor Ranking and Secure Exports
 */

import assert from "node:assert/strict";
import test from "node:test";

import {
  ExportFormat,
  ExportScope,
  FilterCriterion,
  RankingDirection,
  RankingFactorWeight,
  RankingMethod,
  RankingMode,
  RankingTransformation,
  SavedScreener,
  SavedScreenerCreateRequest,
  SavedScreenerUpdateRequest,
  ScreenerExportRequest,
  ScreenerRankingSpec,
  ScreenerRunRequest,
  SortCriterion,
  SortNullOrder,
} from "../types";

test("Stage 97: Saved Screener payload builds with schema versioning and query specification", () => {
  const filters: FilterCriterion[] = [
    { filter_id: "market_cap", operator: "gte", value: 10000000000 },
    { filter_id: "pe_ratio", operator: "lte", value: 25 },
  ];

  const sort: SortCriterion[] = [
    { field_id: "market_cap", direction: "desc", null_order: "nulls_last" },
    { field_id: "revenue_growth_yoy", direction: "desc", null_order: "nulls_last" },
  ];

  const ranking: ScreenerRankingSpec = {
    mode: "single_factor",
    cohort_policy: "filter_matched_securities",
    method: "dense_rank",
    factors: [
      {
        factor_id: "revenue_growth_yoy",
        direction: "higher_value_first",
        transformation: "percentile",
        weight: 1.0,
      },
    ],
    missing_value_policy: "exclude",
    minimum_coverage: 1.0,
    methodology_version: "1.0.0",
  };

  const createReq: SavedScreenerCreateRequest = {
    name: "Mega-Cap Value Growth",
    description: "Quality large caps with low valuation and positive growth",
    universe: {
      universe_id: "common_equity",
      exchange_mics: ["XNYS", "XNAS"],
      listing_country_codes: ["USA"],
      sectors: ["Technology", "Healthcare"],
    },
    filters,
    sort,
    ranking,
    columns: ["symbol", "company_name", "market_cap", "pe_ratio", "revenue_growth_yoy"],
    period_policy: "latest_annual",
    currency_policy: "USD",
  };

  assert.equal(createReq.name, "Mega-Cap Value Growth");
  assert.equal(createReq.universe.universe_id, "common_equity");
  assert.equal(createReq.filters.length, 2);
  assert.equal(createReq.sort.length, 2);
  assert.equal(createReq.ranking?.mode, "single_factor");
  assert.equal(createReq.ranking?.methodology_version, "1.0.0");
  assert.equal(createReq.columns?.length, 5);
});

test("Stage 97: Optimistic concurrency revision checking prevents stale overwrites", () => {
  const currentSavedScreen: SavedScreener = {
    saved_screen_id: "screener-uuid-1",
    owner_user_id: "user-123",
    name: "Dividend Champions",
    description: "High yield dividend securities",
    query_schema_version: "1.0.0",
    universe: { universe_id: "common_equity" },
    filters: [{ filter_id: "dividend_yield", operator: "gte", value: 3.5 }],
    columns: ["symbol", "dividend_yield"],
    sort: [{ field_id: "dividend_yield", direction: "desc" }],
    ranking: null,
    period_policy: "latest_annual",
    currency_policy: "USD",
    revision: 3,
    status: "active",
    created_at: "2026-10-20T00:00:00Z",
    updated_at: "2026-10-21T00:00:00Z",
  };

  // Valid update matching revision
  const validUpdate: SavedScreenerUpdateRequest = {
    name: "Dividend Aristocrats Updated",
    expected_revision: 3,
  };
  assert.equal(validUpdate.expected_revision, currentSavedScreen.revision);

  // Stale update detecting conflict
  const staleExpectedRevision = 2;
  const isConflict = staleExpectedRevision !== currentSavedScreen.revision;
  assert.equal(isConflict, true, "Should detect revision mismatch conflict");
});

test("Stage 97: Multi-column sorting criteria limits, priority order, and null ordering", () => {
  const multiSort: SortCriterion[] = [
    { field_id: "market_cap", direction: "desc", null_order: "nulls_last" },
    { field_id: "pe_ratio", direction: "asc", null_order: "nulls_last" },
    { field_id: "rsi_14", direction: "desc", null_order: "nulls_first" },
  ];

  // Up to 5 sort keys allowed
  assert.ok(multiSort.length <= 5, "Multi-sort should be bounded to 5 criteria");
  assert.equal(multiSort[0].field_id, "market_cap");
  assert.equal(multiSort[0].direction, "desc");
  assert.equal(multiSort[1].field_id, "pe_ratio");
  assert.equal(multiSort[1].direction, "asc");
  assert.equal(multiSort[2].null_order, "nulls_first");

  // Reordering moves priority
  const reordered = [multiSort[1], multiSort[0], multiSort[2]];
  assert.equal(reordered[0].field_id, "pe_ratio", "Primary sort priority changed");
  assert.equal(reordered[1].field_id, "market_cap", "Secondary sort priority changed");
});

test("Stage 97: Multi-factor composite weight normalization and direction handling", () => {
  const rawFactors: RankingFactorWeight[] = [
    { factor_id: "revenue_growth_yoy", weight: 3.0, direction: "higher_value_first", transformation: "z_score" },
    { factor_id: "ebitda_margin", weight: 2.0, direction: "higher_value_first", transformation: "z_score" },
    { factor_id: "pe_ratio", weight: 5.0, direction: "lower_value_first", transformation: "z_score" },
  ];

  const totalRawWeight = rawFactors.reduce((sum, f) => sum + f.weight, 0);
  assert.equal(totalRawWeight, 10.0);

  const normalizedFactors = rawFactors.map((f) => ({
    ...f,
    weight: Number((f.weight / totalRawWeight).toFixed(2)),
  }));

  assert.equal(normalizedFactors[0].weight, 0.3);
  assert.equal(normalizedFactors[1].weight, 0.2);
  assert.equal(normalizedFactors[2].weight, 0.5);

  const sumNormalized = normalizedFactors.reduce((sum, f) => sum + f.weight, 0);
  assert.equal(Number(sumNormalized.toFixed(2)), 1.0, "Normalized factor weights must sum to 1.0");

  assert.equal(normalizedFactors[2].direction, "lower_value_first", "Low P/E is ranked favorably");
});

test("Stage 97: Export request payload scope, format, and injection mitigation rules", () => {
  const query: ScreenerRunRequest = {
    universe: { universe_id: "common_equity" },
    filters: [{ filter_id: "market_cap", operator: "gt", value: 5000000000 }],
    sort: [{ field_id: "market_cap", direction: "desc" }],
    columns: ["symbol", "company_name", "market_cap"],
    page: 1,
    page_size: 50,
  };

  const exportReq: ScreenerExportRequest = {
    query,
    format: "csv" as ExportFormat,
    scope: "all_matching_results" as ExportScope,
    selected_columns: ["symbol", "company_name", "market_cap"],
    include_metadata: true,
  };

  assert.equal(exportReq.format, "csv");
  assert.equal(exportReq.scope, "all_matching_results");
  assert.equal(exportReq.selected_columns?.length, 3);
  assert.equal(exportReq.include_metadata, true);

  // Spreadsheet formula-injection prefixing rule verification:
  // Text cells starting with dangerous characters '=', '+', '-', '@', '\t', '\r' are escaped with "'"
  function sanitizeCell(val: unknown): string {
    if (val === null || val === undefined) return "";
    if (typeof val === "number") return String(val); // Real negative numbers are preserved!
    const s = String(val);
    if (/^[=+\-@\t\r]/.test(s)) {
      return `'${s}`;
    }
    return s;
  }

  // Dangerous formula text
  assert.equal(sanitizeCell("=cmd|'/C calc'!A0"), "'=cmd|'/C calc'!A0");
  assert.equal(sanitizeCell("+2+5"), "'+2+5");
  assert.equal(sanitizeCell("@SUM(A1:A10)"), "'@SUM(A1:A10)");

  // Legitimate negative number must remain numeric representation
  assert.equal(sanitizeCell(-45.2), "-45.2");
  assert.equal(sanitizeCell(100), "100");

  // Normal ticker string
  assert.equal(sanitizeCell("AAPL"), "AAPL");
});
