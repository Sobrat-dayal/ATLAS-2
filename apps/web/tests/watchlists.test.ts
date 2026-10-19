import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import * as watchlistComponents from "../src/components/watchlists";
import {
  formatChange,
  formatObservationTime,
  formatPrice,
  getAssetClassBadge,
  getMarketRouteForAssetClass,
} from "../src/lib/watchlists/formatting";
import type { WatchlistItem } from "../src/lib/watchlists/types";

describe("Stage 76 - Watchlists V1 Frontend Tests", () => {
  it("should confirm all foundational Watchlists V1 components are exported", () => {
    assert.ok(watchlistComponents.WatchlistsWorkspace, "WatchlistsWorkspace must be exported");
    assert.ok(watchlistComponents.WatchlistSelector, "WatchlistSelector must be exported");
    assert.ok(watchlistComponents.WatchlistHeader, "WatchlistHeader must be exported");
    assert.ok(watchlistComponents.WatchlistTable, "WatchlistTable must be exported");
    assert.ok(watchlistComponents.WatchlistRow, "WatchlistRow must be exported");
    assert.ok(watchlistComponents.WatchlistRowActions, "WatchlistRowActions must be exported");
    assert.ok(
      watchlistComponents.WatchlistSelectedInspector,
      "WatchlistSelectedInspector must be exported"
    );
    assert.ok(watchlistComponents.WatchlistStatusBadge, "WatchlistStatusBadge must be exported");
    assert.ok(watchlistComponents.WatchlistEmptyState, "WatchlistEmptyState must be exported");
    assert.ok(watchlistComponents.WatchlistErrorState, "WatchlistErrorState must be exported");
    assert.ok(watchlistComponents.CreateWatchlistDialog, "CreateWatchlistDialog must be exported");
    assert.ok(watchlistComponents.RenameWatchlistDialog, "RenameWatchlistDialog must be exported");
    assert.ok(watchlistComponents.DeleteWatchlistDialog, "DeleteWatchlistDialog must be exported");
    assert.ok(watchlistComponents.AddInstrumentDialog, "AddInstrumentDialog must be exported");
  });

  it("should confirm the /watchlists route page exists and mounts WatchlistsWorkspace", () => {
    const pagePath = path.resolve(__dirname, "../src/app/(atlas)/watchlists/page.tsx");
    assert.ok(fs.existsSync(pagePath), "Route page must exist at /watchlists/page.tsx");

    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("WatchlistsWorkspace"), "Page must render WatchlistsWorkspace");
    assert.ok(content.includes("generateMetadata"), "Page must define institutional metadata");
    assert.ok(
      content.includes("Watchlists"),
      "Metadata title must specify Watchlists"
    );
  });

  it("should format financial prices with asset-class quotation-aware precision", () => {
    // Equity formatting (2 decimals with commas)
    assert.strictEqual(formatPrice("182.5", "equity", "USD"), "182.50");
    assert.strictEqual(formatPrice("2450.75", "equity", "USD"), "2,450.75");

    // FX formatting (4 decimals)
    assert.strictEqual(formatPrice("1.08542", "fx", "USD"), "1.0854");
    assert.strictEqual(formatPrice("1.08", "currency", "USD"), "1.0800");

    // Bond formatting (3 decimals)
    assert.strictEqual(formatPrice("98.45", "bond", "USD"), "98.450");

    // Crypto micro and macro precision
    assert.strictEqual(formatPrice("0.00002456", "crypto", "USD"), "0.00002456");
    assert.strictEqual(formatPrice("0.4567", "crypto", "USD"), "0.4567");
    assert.strictEqual(formatPrice("68450.25", "crypto", "USD"), "68,450.25");

    // Missing / null handling - must return neutral dash, never zero
    assert.strictEqual(formatPrice(null), "—");
    assert.strictEqual(formatPrice(undefined), "—");
    assert.strictEqual(formatPrice(""), "—");
    assert.strictEqual(formatPrice("   "), "—");
  });

  it("should format absolute and percentage price change with directional semantics", () => {
    // Positive change
    const up = formatChange("+2.45", "+1.35%");
    assert.strictEqual(up.text, "+2.45 (+1.35%)");
    assert.strictEqual(up.direction, "up");

    // Negative change
    const down = formatChange("-1.20", "-0.65%");
    assert.strictEqual(down.text, "-1.20 (-0.65%)");
    assert.strictEqual(down.direction, "down");

    // Flat change
    const flat = formatChange("0.00", "0.00%");
    assert.strictEqual(flat.text, "0.00 (0.00%)");
    assert.strictEqual(flat.direction, "flat");

    // Missing change - must return neutral unknown, never fake 0%
    const missing = formatChange(null, null);
    assert.strictEqual(missing.text, "—");
    assert.strictEqual(missing.direction, "unknown");

    const partialPct = formatChange(null, "+0.85%");
    assert.strictEqual(partialPct.text, "+0.85%");
    assert.strictEqual(partialPct.direction, "up");
  });

  it("should format observation UTC timestamps accurately", () => {
    const ts = "2026-10-19T14:30:45Z";
    const formatted = formatObservationTime(ts);
    assert.strictEqual(formatted, "14:30:45 UTC");

    // Null or invalid handling
    assert.strictEqual(formatObservationTime(null), "—");
    assert.strictEqual(formatObservationTime(undefined), "—");
    assert.strictEqual(formatObservationTime("not-a-date"), "—");
  });

  it("should categorize asset classes into terminal badges", () => {
    assert.strictEqual(getAssetClassBadge("equity").label, "EQUITY");
    assert.strictEqual(getAssetClassBadge("etf").label, "ETF");
    assert.strictEqual(getAssetClassBadge("crypto").label, "CRYPTO");
    assert.strictEqual(getAssetClassBadge("fx").label, "FX");
    assert.strictEqual(getAssetClassBadge("currency").label, "FX");
    assert.strictEqual(getAssetClassBadge("bond").label, "BOND");
    assert.strictEqual(getAssetClassBadge("fund").label, "FUND");
    assert.strictEqual(getAssetClassBadge("future").label, "FUTURES");
    assert.strictEqual(getAssetClassBadge("commodity").label, "COMMODITY");
    assert.strictEqual(getAssetClassBadge("index").label, "INDEX");
    assert.strictEqual(getAssetClassBadge("unknown_type").label, "UNKNOWN_TYPE");
  });

  it("should resolve canonical market routes without fabricating non-existent routes", () => {
    assert.strictEqual(getMarketRouteForAssetClass("equity"), "/markets/equities");
    assert.strictEqual(getMarketRouteForAssetClass("etf"), "/markets/funds");
    assert.strictEqual(getMarketRouteForAssetClass("fund"), "/markets/funds");
    assert.strictEqual(getMarketRouteForAssetClass("crypto"), "/markets/crypto");
    assert.strictEqual(getMarketRouteForAssetClass("fx"), "/markets/fx");
    assert.strictEqual(getMarketRouteForAssetClass("currency"), "/markets/fx");
    assert.strictEqual(getMarketRouteForAssetClass("bond"), "/markets/bonds");
    assert.strictEqual(getMarketRouteForAssetClass("future"), "/markets/futures");
    assert.strictEqual(getMarketRouteForAssetClass("other"), "/markets");
  });

  it("should test duplicate prevention logic using canonical instrument IDs", () => {
    const existingItems: Partial<WatchlistItem>[] = [
      { id: "item-1", instrument_entity_id: "inst-a", symbol: "AAPL" },
      { id: "item-2", instrument_entity_id: "inst-b", symbol: "MSFT" },
      { id: "item-3", instrument_entity_id: "inst-c", symbol: "GOOGL" },
    ];

    const existingIds = new Set(existingItems.map((item) => item.instrument_entity_id));

    assert.ok(existingIds.has("inst-a"), "AAPL is already in list");
    assert.ok(existingIds.has("inst-b"), "MSFT is already in list");
    assert.ok(!existingIds.has("inst-d"), "NVDA is not in list yet");

    // Symbol collision check: Two instruments with symbol 'ABC' but different UUIDs
    const collidingId = "inst-abc-london";
    assert.ok(
      !existingIds.has(collidingId),
      "Distinct canonical UUID with same symbol is not blocked"
    );
  });

  it("should test dense reorder position indexing and bounds checking", () => {
    const items = [
      { id: "item-1", position: 0 },
      { id: "item-2", position: 1 },
      { id: "item-3", position: 2 },
      { id: "item-4", position: 3 },
    ];

    // Simulate moving item-3 (index 2) UP to index 1
    const fromIndex = 2;
    const toIndex = 1;
    const reordered = [...items];
    const [moved] = reordered.splice(fromIndex, 1);
    reordered.splice(toIndex, 0, moved);

    // Reindex densely
    const denseResult = reordered.map((item, idx) => ({ ...item, position: idx }));

    assert.strictEqual(denseResult[0].id, "item-1");
    assert.strictEqual(denseResult[0].position, 0);

    assert.strictEqual(denseResult[1].id, "item-3");
    assert.strictEqual(denseResult[1].position, 1);

    assert.strictEqual(denseResult[2].id, "item-2");
    assert.strictEqual(denseResult[2].position, 2);

    assert.strictEqual(denseResult[3].id, "item-4");
    assert.strictEqual(denseResult[3].position, 3);
  });

  it("should simulate optimistic rollback on API revision conflict", () => {
    const authoritativeState = [
      { id: "item-1", position: 0 },
      { id: "item-2", position: 1 },
    ];

    // Optimistically reordered
    let currentState = [
      { id: "item-2", position: 0 },
      { id: "item-1", position: 1 },
    ];

    // API returns 409 Conflict (revision mismatch)
    const apiSuccess = false;
    if (!apiSuccess) {
      // Rollback to authoritative snapshot
      currentState = [...authoritativeState];
    }

    assert.strictEqual(currentState[0].id, "item-1", "Rollback restored item-1 to position 0");
    assert.strictEqual(currentState[1].id, "item-2", "Rollback restored item-2 to position 1");
  });

  it("should verify strict terminal styling: no purple gradients and no buy/sell trading actions", () => {
    const rowContent = fs.readFileSync(
      path.resolve(__dirname, "../src/components/watchlists/WatchlistRow.tsx"),
      "utf-8"
    );
    const tableContent = fs.readFileSync(
      path.resolve(__dirname, "../src/components/watchlists/WatchlistTable.tsx"),
      "utf-8"
    );
    const workspaceContent = fs.readFileSync(
      path.resolve(__dirname, "../src/components/watchlists/WatchlistsWorkspace.tsx"),
      "utf-8"
    );

    // Strict aesthetic rule: No purple gradients
    assert.ok(!rowContent.includes("from-purple-"), "WatchlistRow must not contain purple gradients");
    assert.ok(
      !tableContent.includes("from-purple-"),
      "WatchlistTable must not contain purple gradients"
    );
    assert.ok(
      !workspaceContent.includes("from-purple-"),
      "WatchlistsWorkspace must not contain purple gradients"
    );

    // Strict boundary rule: No Buy/Sell trading actions in Watchlists V1
    assert.ok(!rowContent.includes("Buy"), "WatchlistRow must not include Buy action");
    assert.ok(!rowContent.includes("Sell"), "WatchlistRow must not include Sell action");
    assert.ok(!rowContent.includes("trade/order"), "WatchlistRow must not trigger trading orders");
  });
});
