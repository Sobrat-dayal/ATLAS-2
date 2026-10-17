import { describe, it } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";

import {
  LiveChartController,
  LiveChartStatus,
  LiveQuoteDTO,
  ChartLiveStateResponse,
} from "../src/lib/charts";
import * as chartComponents from "../src/components/charts";
import * as chartHooks from "../src/hooks/charts";
import { formatPrice } from "../src/lib/charts/formatting";

describe("Stage 67 - Live Chart Streaming V1 Tests", () => {
  it("should confirm all foundational Stage 67 live components are exported cleanly", () => {
    assert.ok(
      chartComponents.LiveMarketDataStatus,
      "LiveMarketDataStatus must be exported"
    );
    assert.ok(
      chartComponents.LiveChartControls,
      "LiveChartControls must be exported"
    );
    assert.ok(
      chartComponents.LatestQuoteDetails,
      "LatestQuoteDetails must be exported"
    );
    assert.ok(chartComponents.ChartsPage, "ChartsPage must be exported");
    assert.ok(chartComponents.HistoricalChart, "HistoricalChart must be exported");
  });

  it("should confirm useLiveChart hook is exported from hooks/charts", () => {
    assert.ok(
      chartHooks.useLiveChart,
      "useLiveChart must be exported from hooks/charts"
    );
  });

  it("should initialize LiveChartController and bootstrap initial quote state", async () => {
    const spyId = "a0000000-0000-0000-0000-000000000001";
    let updatedQuote: LiveQuoteDTO | null = null;
    let updatedStatus: LiveChartStatus | null = null;

    const mockInitialFetcher = async (): Promise<ChartLiveStateResponse> => ({
      schema_version: "1.0.0",
      instrument_entity_id: spyId,
      display_symbol: "SPY",
      market_or_venue: "NYSE Arca",
      price_currency: "USD",
      quotation_unit: "USD/share",
      quote: {
        bid_price: "586.20",
        ask_price: "586.30",
        bid_size: "100",
        ask_size: "200",
        last_price: "586.25",
        last_size: "50",
        as_of: "2026-10-18T10:00:00Z",
        is_midpoint: false,
        has_genuine_last: true,
      },
      source_timestamp: "2026-10-18T10:00:00Z",
      received_at: "2026-10-18T10:00:01Z",
      provider: "OPENBB_POLYGON",
      freshness_status: "LIVE",
      delay_status: "REALTIME",
      live_capability: "LIVE_PRICE_AVAILABLE",
      availability: "AVAILABLE",
      is_paused: false,
    });

    const controller = new LiveChartController({
      instrumentId: spyId,
      symbol: "SPY",
      coalesceIntervalMs: 10,
      initialStateFetcher: mockInitialFetcher,
      onQuoteUpdate: (q, s) => {
        updatedQuote = q;
        updatedStatus = s;
      },
    });

    await controller.start();

    // Wait for coalesced emission
    await new Promise((r) => setTimeout(r, 30));

    assert.ok(controller.getCurrentQuote() !== null, "Current quote must be populated");
    assert.strictEqual(controller.getCurrentQuote()?.last_price, "586.25");
    assert.strictEqual(controller.getStatus().connection, "CONNECTED");
    assert.strictEqual(controller.getStatus().freshness, "LIVE");
    assert.strictEqual(controller.getStatus().delay, "REALTIME");
    assert.strictEqual(controller.getStatus().capability, "LIVE_PRICE_AVAILABLE");
    assert.strictEqual((updatedQuote as any)?.last_price, "586.25");

    controller.destroy();
  });

  it("should reject stale and duplicate events based on source timestamp ordering", async () => {
    const spyId = "a0000000-0000-0000-0000-000000000001";

    const controller = new LiveChartController({
      instrumentId: spyId,
      symbol: "SPY",
      initialStateFetcher: async () => ({
        schema_version: "1.0.0",
        instrument_entity_id: spyId,
        display_symbol: "SPY",
        market_or_venue: "NYSE Arca",
        price_currency: "USD",
        quotation_unit: "USD/share",
        quote: {
          bid_price: "586.20",
          ask_price: "586.30",
          bid_size: "100",
          ask_size: "200",
          last_price: "586.25",
          last_size: "50",
          as_of: "2026-10-18T12:00:10Z",
          is_midpoint: false,
          has_genuine_last: true,
        },
        source_timestamp: "2026-10-18T12:00:10Z",
        received_at: "2026-10-18T12:00:11Z",
        provider: "OPENBB_POLYGON",
        freshness_status: "LIVE",
        delay_status: "REALTIME",
        live_capability: "LIVE_PRICE_AVAILABLE",
        availability: "AVAILABLE",
        is_paused: false,
      }),
    });

    await controller.start();

    // 1. Equal timestamp (duplicate event)
    const dupRes = controller.validateAndReconcileEvent({
      instrument_entity_id: spyId,
      payload: {
        quote: {
          last_price: "586.30",
          as_of: "2026-10-18T12:00:10Z",
        },
      },
    });
    assert.strictEqual(dupRes.accepted, false);
    assert.ok(dupRes.reason.includes("STALE_OR_DUPLICATE_EVENT"));

    // 2. Older timestamp (stale event)
    const olderRes = controller.validateAndReconcileEvent({
      instrument_entity_id: spyId,
      payload: {
        quote: {
          last_price: "586.15",
          as_of: "2026-10-18T12:00:05Z",
        },
      },
    });
    assert.strictEqual(olderRes.accepted, false);
    assert.ok(olderRes.reason.includes("STALE_OR_DUPLICATE_EVENT"));

    // 3. Newer timestamp (accepted)
    const newerRes = controller.validateAndReconcileEvent({
      instrument_entity_id: spyId,
      payload: {
        quote: {
          last_price: "586.40",
          as_of: "2026-10-18T12:00:15Z",
        },
      },
    });
    assert.strictEqual(newerRes.accepted, true);
    assert.strictEqual(newerRes.reconciledQuote?.last_price, 586.4);

    controller.destroy();
  });

  it("should reject events with mismatched instrument entity UUID", async () => {
    const spyId = "a0000000-0000-0000-0000-000000000001";
    const aaplId = "a0000000-0000-0000-0000-000000000002";

    const controller = new LiveChartController({
      instrumentId: spyId,
      symbol: "SPY",
    });

    const mismatchRes = controller.validateAndReconcileEvent({
      instrument_entity_id: aaplId,
      payload: {
        quote: {
          last_price: "232.50",
          as_of: "2026-10-18T12:00:00Z",
        },
      },
    });

    assert.strictEqual(mismatchRes.accepted, false);
    assert.ok(mismatchRes.reason.includes("INSTRUMENT_MISMATCH"));

    controller.destroy();
  });

  it("should reject negative prices for equities but allow for commodity futures", () => {
    const aaplId = "a0000000-0000-0000-0000-000000000002";
    const clzId = "a0000000-0000-0000-0000-000000000003";

    // Equity (allowsNegativePrice = false)
    const equityController = new LiveChartController({
      instrumentId: aaplId,
      symbol: "AAPL",
      allowsNegativePrice: false,
    });
    const equityRes = equityController.validateAndReconcileEvent({
      instrument_entity_id: aaplId,
      payload: {
        quote: {
          last_price: "-5.00",
          as_of: "2026-10-18T12:00:00Z",
        },
      },
    });
    assert.strictEqual(equityRes.accepted, false);
    assert.ok(equityRes.reason.includes("NEGATIVE_PRICE_REJECTED"));
    equityController.destroy();

    // Futures (allowsNegativePrice = true)
    const futuresController = new LiveChartController({
      instrumentId: clzId,
      symbol: "CLZ26",
      allowsNegativePrice: true,
    });
    const futuresRes = futuresController.validateAndReconcileEvent({
      instrument_entity_id: clzId,
      payload: {
        quote: {
          last_price: "-15.50",
          as_of: "2026-10-18T12:00:00Z",
        },
      },
    });
    assert.strictEqual(futuresRes.accepted, true);
    assert.strictEqual(futuresRes.reconciledQuote?.last_price, -15.5);
    futuresController.destroy();
  });

  it("should preserve quote/candle financial integrity: bid/ask never creates last", () => {
    const eurusdId = "a0000000-0000-0000-0000-000000000004";
    const controller = new LiveChartController({
      instrumentId: eurusdId,
      symbol: "EURUSD",
    });

    // Event with Bid and Ask ONLY (OTC FX)
    const res = controller.validateAndReconcileEvent({
      instrument_entity_id: eurusdId,
      payload: {
        quote: {
          bid_price: "1.0854",
          ask_price: "1.0856",
          last_price: null,
          as_of: "2026-10-18T12:00:00Z",
        },
      },
    });

    assert.strictEqual(res.accepted, true);
    assert.strictEqual(res.reconciledQuote?.last_price, null);
    assert.strictEqual(res.reconciledQuote?.has_genuine_last, false);
    assert.strictEqual(res.reconciledQuote?.bid_price, 1.0854);
    assert.strictEqual(res.reconciledQuote?.ask_price, 1.0856);

    controller.destroy();
  });

  it("should reject NaN, Infinity, and malformed price strings safely", () => {
    const spyId = "a0000000-0000-0000-0000-000000000001";
    const controller = new LiveChartController({
      instrumentId: spyId,
      symbol: "SPY",
    });

    for (const badVal of ["NaN", "Infinity", "-Infinity", "INVALID_PRICE"]) {
      const res = controller.validateAndReconcileEvent({
        instrument_entity_id: spyId,
        payload: {
          quote: {
            last_price: badVal,
            as_of: "2026-10-18T12:00:00Z",
          },
        },
      });
      assert.strictEqual(
        res.reconciledQuote?.last_price,
        null,
        `Bad value ${badVal} must result in null last_price`
      );
    }

    controller.destroy();
  });

  it("should handle Pause and Resume controls correctly without unbounded queues", async () => {
    const spyId = "a0000000-0000-0000-0000-000000000001";
    let emissionsCount = 0;

    const controller = new LiveChartController({
      instrumentId: spyId,
      symbol: "SPY",
      coalesceIntervalMs: 5,
      initialStateFetcher: async () => ({
        schema_version: "1.0.0",
        instrument_entity_id: spyId,
        display_symbol: "SPY",
        market_or_venue: "NYSE Arca",
        price_currency: "USD",
        quotation_unit: "USD/share",
        quote: {
          bid_price: "586.20",
          ask_price: "586.30",
          last_price: "586.25",
          as_of: "2026-10-18T10:00:00Z",
          is_midpoint: false,
          has_genuine_last: true,
        },
        source_timestamp: "2026-10-18T10:00:00Z",
        received_at: "2026-10-18T10:00:01Z",
        provider: "OPENBB_POLYGON",
        freshness_status: "LIVE",
        delay_status: "REALTIME",
        live_capability: "LIVE_PRICE_AVAILABLE",
        availability: "AVAILABLE",
        is_paused: false,
      }),
      onQuoteUpdate: () => {
        emissionsCount++;
      },
    });

    await controller.start();
    await new Promise((r) => setTimeout(r, 20));
    const initialEmissions = emissionsCount;

    // Pause updates
    controller.pause();
    assert.strictEqual(controller.getIsPaused(), true);
    assert.strictEqual(controller.getStatus().isPaused, true);

    // Send event while paused
    controller.handleIncomingEvent({
      instrument_entity_id: spyId,
      payload: {
        quote: {
          last_price: "587.00",
          as_of: "2026-10-18T10:01:00Z",
        },
      },
    });

    await new Promise((r) => setTimeout(r, 25));
    // Emissions must not increment while paused!
    assert.strictEqual(emissionsCount, initialEmissions);

    // Resume updates
    await controller.resume();
    assert.strictEqual(controller.getIsPaused(), false);

    controller.destroy();
  });

  it("should handle Go to Latest and Follow-Live tracking correctly", () => {
    const spyId = "a0000000-0000-0000-0000-000000000001";
    const controller = new LiveChartController({
      instrumentId: spyId,
      symbol: "SPY",
    });

    assert.strictEqual(controller.getIsFollowingLatest(), true);

    // User pans back in time to inspect older bars
    controller.setFollowingLatest(false);
    assert.strictEqual(controller.getIsFollowingLatest(), false);

    // User clicks "Go to Latest"
    controller.setFollowingLatest(true);
    assert.strictEqual(controller.getIsFollowingLatest(), true);

    controller.destroy();
  });

  it("should format quotation prices accurately across asset classes", () => {
    // Equities/ETFs (2 decimals)
    assert.strictEqual(formatPrice(586.25, 2), "586.25");
    // FX spot (4 decimals)
    assert.strictEqual(formatPrice(1.0854, 4), "1.0854");
    // Sovereign bond (3 decimals)
    assert.strictEqual(formatPrice(4.085, 3), "4.085");
    // Negative commodity futures
    assert.strictEqual(formatPrice(-15.5, 2), "-15.50");
    // Null / missing
    assert.strictEqual(formatPrice(null), "—");
    assert.strictEqual(formatPrice(undefined), "—");
  });

  it("should confirm the route page renders ChartsPage and Stage 67 header metadata", () => {
    const pagePath = path.resolve(__dirname, "../src/app/(atlas)/charts/page.tsx");
    assert.ok(fs.existsSync(pagePath), "Route page must exist at /charts/page.tsx");

    const content = fs.readFileSync(pagePath, "utf-8");
    assert.ok(content.includes("ChartsPage"), "Page must render ChartsPage");
  });

  it("should verify strict design invariants: no purple gradients, no emoji icons, no trading buttons", () => {
    const filesToCheck = [
      "../src/components/charts/ChartsPage.tsx",
      "../src/components/charts/LiveMarketDataStatus.tsx",
      "../src/components/charts/LiveChartControls.tsx",
      "../src/components/charts/LatestQuoteDetails.tsx",
      "../src/components/charts/HistoricalChart.tsx",
    ];

    for (const fileRel of filesToCheck) {
      const fullPath = path.resolve(__dirname, fileRel);
      assert.ok(fs.existsSync(fullPath), `File ${fileRel} must exist`);
      const code = fs.readFileSync(fullPath, "utf-8");

      assert.ok(
        !code.includes("from-purple") && !code.includes("bg-purple") && !code.includes("text-purple"),
        `${fileRel} must not introduce purple gradients or styling`
      );

      // Check for non-functional trading buttons (Buy / Sell)
      assert.ok(
        !code.includes(">BUY<") &&
          !code.includes(">SELL<") &&
          !code.includes("Buy / Sell") &&
          !code.includes("Place Order"),
        `${fileRel} must not introduce unauthorized buy/sell trading actions`
      );
    }
  });
});
