import { describe, it } from "node:test";
import assert from "node:assert";

import {
  SharedWebSocketClient,
  formatSubscriptionKey,
} from "../src/lib/realtime/client";
import {
  validateCanonicalQuoteEvent,
  EventOrderingTracker,
  SnapshotStreamReconciler,
  calculateDesiredSubscriptionPlan,
  RenderBatcher,
  WatchlistLiveController,
  CanonicalLiveQuote,
} from "../src/lib/watchlists/live";
import { WatchlistItem } from "../src/lib/watchlists/types";

describe("Stage 78 - Live Watchlist Updates V1 Tests", () => {
  // =========================================================================
  // 1. SHARED WEBSOCKET CLIENT & REFERENCE COUNTING
  // =========================================================================

  it("should share subscriptions across multiple consumers and reference count correctly", () => {
    const sentMessages: string[] = [];
    const mockSocket = {
      readyState: 1, // OPEN
      send: (data: string) => {
        sentMessages.push(data);
      },
      close: () => {},
    };

    const client = new SharedWebSocketClient({
      webSocketFactory: () => mockSocket as unknown as WebSocket,
    });

    const aaplId = "a0000000-0000-0000-0000-000000000001";
    const seriesAapl = { instrument_entity_id: aaplId, symbol: "AAPL" };
    const key = formatSubscriptionKey(seriesAapl);

    // Consumer 1 (Watchlist View A) subscribes
    const unsub1 = client.subscribe("consumer_watchlist_a", [seriesAapl], {});
    assert.strictEqual(client.getActiveSubscriptionCount(), 1);
    assert.strictEqual(client.getReferenceCount(key), 1);

    // Consumer 2 (Charts Panel 1) subscribes to the SAME series
    const unsub2 = client.subscribe("consumer_chart_panel_1", [seriesAapl], {});
    assert.strictEqual(client.getActiveSubscriptionCount(), 1, "Must reuse active series without duplicate subscription");
    assert.strictEqual(client.getReferenceCount(key), 2, "Reference count must increase to 2");

    // Consumer 1 unsubscribes
    unsub1();
    assert.strictEqual(client.getActiveSubscriptionCount(), 1, "Subscription must remain active for consumer 2");
    assert.strictEqual(client.getReferenceCount(key), 1, "Reference count must drop to 1");

    // Consumer 2 unsubscribes
    unsub2();
    assert.strictEqual(client.getActiveSubscriptionCount(), 0, "Subscription must be released when ref count reaches 0");
    assert.strictEqual(client.getReferenceCount(key), 0);

    client.destroy();
  });

  // =========================================================================
  // 2. VIEWPORT-AWARE SUBSCRIPTION PLANNING & OVERSCAN
  // =========================================================================

  it("should calculate subscription plan prioritizing visible rows with bounded overscan", () => {
    // 50 dummy items
    const items: WatchlistItem[] = Array.from({ length: 50 }, (_, i) => ({
      id: `item-${i}`,
      watchlist_id: "w-1",
      instrument_entity_id: `b0000000-0000-0000-0000-${String(i).padStart(12, "0")}`,
      market_series_id: `ms-${i}`,
      position: i,
      created_at: "2026-10-18T00:00:00Z",
      symbol: `SYM${i}`,
      display_name: `Symbol ${i}`,
      canonical_name: `Symbol ${i} Corp`,
      asset_class: "equity",
      venue: "NASDAQ",
      quote_currency: "USD",
      quote_unit: "USD/share",
      is_quote_available: true,
      quote_measure: "Last",
      last_price: "100.00",
      bid_price: "99.90",
      ask_price: "100.10",
      absolute_change: "+1.00",
      percentage_change: "+1.01%",
      change_direction: "up",
      source_timestamp: "2026-10-18T10:00:00Z",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      delay_seconds: 0,
      provider: "OPENBB_POLYGON",
      issuer_entity_id: null,
      has_company_page: false,
    }));

    // Viewport shows rows 10..20 with overscan = 5
    const plan = calculateDesiredSubscriptionPlan(items, { startIndex: 10, endIndex: 20 }, { overscan: 5 });
    // Expected range: [5, 25] -> 20 items
    assert.strictEqual(plan.length, 20);
    assert.strictEqual(plan[0].symbol, "SYM5");
    assert.strictEqual(plan[plan.length - 1].symbol, "SYM24");

    // Background tab suspension: should return empty plan
    const backgroundPlan = calculateDesiredSubscriptionPlan(
      items,
      { startIndex: 10, endIndex: 20 },
      { overscan: 5, isTabVisible: false }
    );
    assert.strictEqual(backgroundPlan.length, 0, "Background tab must suspend subscriptions");
  });

  // =========================================================================
  // 3. EVENT VALIDATION & FINANCIAL INTEGRITY
  // =========================================================================

  it("should validate canonical quote event schema, finite decimals, and negative prices", () => {
    const validEvent = {
      schema_version: 1,
      event_type: "market.quote.updated",
      instrument_entity_id: "c0000000-0000-0000-0000-000000000001",
      payload: {
        quote: {
          last_price: "232.50",
          bid_price: "232.40",
          ask_price: "232.60",
          as_of: "2026-10-18T12:00:00Z",
        },
      },
    };

    const res = validateCanonicalQuoteEvent(validEvent);
    assert.strictEqual(res.accepted, true);
    assert.strictEqual(res.sanitizedQuote?.last_price, "232.50");

    // Rejects unsupported schema version
    const badVersion = { ...validEvent, schema_version: 2 };
    assert.strictEqual(validateCanonicalQuoteEvent(badVersion).accepted, false);

    // Rejects NaN and malformed decimals
    const nanEvent = {
      ...validEvent,
      payload: { quote: { last_price: "NaN" } },
    };
    assert.strictEqual(validateCanonicalQuoteEvent(nanEvent).accepted, false);

    // Rejects negative price on equities
    const negEvent = {
      ...validEvent,
      payload: { quote: { last_price: "-15.20" } },
    };
    assert.strictEqual(validateCanonicalQuoteEvent(negEvent, { allowsNegativePrice: false }).accepted, false);

    // Allows negative price on commodity futures (e.g. CLZ26)
    assert.strictEqual(validateCanonicalQuoteEvent(negEvent, { allowsNegativePrice: true }).accepted, true);

    // Preserves genuine zero price (e.g. expired option/defaulted debt)
    const zeroEvent = {
      ...validEvent,
      payload: { quote: { last_price: "0.00" } },
    };
    const zeroRes = validateCanonicalQuoteEvent(zeroEvent);
    assert.strictEqual(zeroRes.accepted, true);
    assert.strictEqual(zeroRes.sanitizedQuote?.last_price, "0.00");
  });

  // =========================================================================
  // 4. EVENT ORDERING & DEDUPLICATION
  // =========================================================================

  it("should enforce chronological source-scoped ordering and reject stale/duplicate events", () => {
    const tracker = new EventOrderingTracker(100);
    const instId = "d0000000-0000-0000-0000-000000000001";

    // 1. Initial event at 10:00:00
    const dec1 = tracker.evaluate(instId, "evt-1", "2026-10-18T10:00:00Z", "1");
    assert.strictEqual(dec1.accepted, true);

    // 2. Duplicate event ID
    const decDup = tracker.evaluate(instId, "evt-1", "2026-10-18T10:00:05Z", "2");
    assert.strictEqual(decDup.accepted, false);
    assert.strictEqual(decDup.isDuplicate, true);

    // 3. Stale / older observation timestamp (09:59:00)
    const decOld = tracker.evaluate(instId, "evt-2", "2026-10-18T09:59:00Z", "3");
    assert.strictEqual(decOld.accepted, false);
    assert.strictEqual(decOld.isOutOfOrder, true);

    // 4. Chronologically newer observation (10:00:05)
    const decNew = tracker.evaluate(instId, "evt-3", "2026-10-18T10:00:05Z", "2");
    assert.strictEqual(decNew.accepted, true);

    // 5. Sequence gap detection (next expected was 3, but received 10)
    const decGap = tracker.evaluate(instId, "evt-4", "2026-10-18T10:00:10Z", "10");
    assert.strictEqual(decGap.accepted, true);
    assert.strictEqual(decGap.hasSequenceGap, true);
  });

  // =========================================================================
  // 5. SNAPSHOT-AND-STREAM RACE RECONCILIATION
  // =========================================================================

  it("should prevent stale snapshot from overwriting newer streamed quote during startup race", () => {
    const reconciler = new SnapshotStreamReconciler({ maxBufferSize: 10 });
    const tracker = new EventOrderingTracker(100);
    const instId = "e0000000-0000-0000-0000-000000000001";

    reconciler.markSnapshotPending();

    // While snapshot is in-flight, stream delivers a newer event at 10:05:00
    const streamEvent = {
      schema_version: 1,
      event_id: "evt-live-1",
      event_type: "market.quote.updated",
      instrument_entity_id: instId,
      payload: {
        quote: {
          last_price: "500.00",
          as_of: "2026-10-18T10:05:00Z",
        },
      },
    };
    reconciler.bufferEvent(streamEvent);

    // Snapshot arrives late with older timestamp at 10:00:00
    const snapshotTs = "2026-10-18T10:00:00Z";
    const result = reconciler.reconcileOnSnapshotLoaded(snapshotTs, instId, tracker);

    // Snapshot MUST NOT be applied because buffered stream event is newer!
    assert.strictEqual(result.applySnapshot, false, "Older snapshot must not overwrite newer streamed quote");
    assert.strictEqual(result.pendingEventsToReplay.length, 1);
  });

  // =========================================================================
  // 6. RENDER BATCHING & COALESCING
  // =========================================================================

  it("should coalesce high-frequency quote updates into batched emissions", async () => {
    const emittedBatches: Map<string, CanonicalLiveQuote>[] = [];
    const batcher = new RenderBatcher({
      batchIntervalMs: 25,
      onFlush: (batch) => {
        emittedBatches.push(batch);
      },
    });

    const instA = "f0000000-0000-0000-0000-000000000001";
    const instB = "f0000000-0000-0000-0000-000000000002";

    const makeQuote = (id: string, price: string): CanonicalLiveQuote => ({
      instrument_entity_id: id,
      symbol: id.slice(0, 4),
      market_series_id: `ms-${id}`,
      quote_measure: "Last",
      last_price: price,
      bid_price: null,
      ask_price: null,
      previous_close: null,
      absolute_change: null,
      percentage_change: null,
      change_direction: "flat",
      source_timestamp: "2026-10-18T10:00:00Z",
      received_at: "2026-10-18T10:00:00Z",
      freshness_status: "fresh",
      delivery_delay_status: "realtime",
      delay_seconds: 0,
      provider: "OPENBB",
      venue: "NYSE",
      quote_currency: "USD",
      quote_unit: "USD/share",
    });

    // Enqueue 10 rapid updates across 2 instruments
    for (let i = 1; i <= 5; i++) {
      batcher.enqueue(makeQuote(instA, `10${i}.00`));
      batcher.enqueue(makeQuote(instB, `20${i}.00`));
    }

    assert.strictEqual(batcher.getPendingCount(), 2, "Updates must collapse per instrument in accumulator");

    // Wait for flush timer
    await new Promise((r) => setTimeout(r, 45));

    assert.strictEqual(emittedBatches.length, 1, "Should emit exactly 1 coalesced batch");
    const flushed = emittedBatches[0];
    assert.strictEqual(flushed.get(instA)?.last_price, "105.00", "Must contain the latest price");
    assert.strictEqual(flushed.get(instB)?.last_price, "205.00");

    batcher.destroy();
  });

  // =========================================================================
  // 7. FINANCIAL SEMANTICS & WATCHLIST LIVE CONTROLLER
  // =========================================================================

  it("should distinguish quote measures and calculate directional movement cues", () => {
    const instId = "10000000-0000-0000-0000-000000000001";
    const items: WatchlistItem[] = [
      {
        id: "item-1",
        watchlist_id: "w-1",
        instrument_entity_id: instId,
        market_series_id: "ms-1",
        position: 0,
        created_at: "2026-10-18T00:00:00Z",
        symbol: "EURUSD",
        display_name: "Euro / US Dollar",
        canonical_name: "EUR/USD Currency Pair",
        asset_class: "fx",
        venue: "FXCM",
        quote_currency: "USD",
        quote_unit: "USD/EUR",
        is_quote_available: true,
        quote_measure: "Mid",
        last_price: "1.0850",
        bid_price: "1.0849",
        ask_price: "1.0851",
        absolute_change: "+0.0010",
        percentage_change: "+0.09%",
        change_direction: "up",
        source_timestamp: "2026-10-18T10:00:00Z",
        freshness_status: "fresh",
        delivery_delay_status: "realtime",
        delay_seconds: 0,
        provider: "OPENBB",
        issuer_entity_id: null,
        has_company_page: false,
      },
    ];

    const controller = new WatchlistLiveController({
      watchlistId: "w-1",
      items,
      onQuoteBatch: (batch) => {
        void batch;
      },
    });

    controller.start();

    // Initial state check
    const initial = controller.getCurrentQuotes().get(instId);
    assert.ok(initial);
    assert.strictEqual(initial.quote_measure, "Mid", "FX asset class must preserve Mid quote measure");
    assert.strictEqual(initial.last_price, "1.0850");

    // Incoming trade tick up to 1.0860
    controller.handleIncomingLiveEvent({
      type: "live.event",
      protocol_version: 1,
      stream_id: "100-1",
      event: {
        schema_version: 1,
        event_id: "evt-tick-1",
        event_type: "market.quote.updated",
        emitted_at: "2026-10-18T10:01:00Z",
        instrument_entity_id: instId,
        provider_key: "OPENBB",
        payload: {
          quote: {
            last_price: "1.0860",
            bid_price: "1.0859",
            ask_price: "1.0861",
            previous_close: "1.0840",
            as_of: "2026-10-18T10:01:00Z",
          },
        },
      },
    });

    const updated = controller.getCurrentQuotes().get(instId);
    assert.ok(updated);
    assert.strictEqual(updated.last_price, "1.0860");
    assert.strictEqual(updated.last_movement_cue, "up", "Tick up from 1.0850 to 1.0860 must set movement cue to up");
    assert.strictEqual(updated.absolute_change, "+0.00"); // 1.0860 - 1.0840 = 0.002 -> +0.00 with 2dp

    controller.destroy();
    SharedWebSocketClient.resetInstance();
  });
});
