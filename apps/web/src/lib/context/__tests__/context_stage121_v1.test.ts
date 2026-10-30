/**
 * Comprehensive Unit Tests for ATLAS Stage 121: Global Workspace Linking.
 *
 * Validates:
 * 1. Fixture A: Four linked widgets (Watchlist -> Chart, Company, News).
 * 2. Fixture B: Independent panel isolation (unlinked panel remains unaffected).
 * 3. Fixture C: Separate channel isolation (Channel A updates do not affect Channel B).
 * 4. Fixture D: Per-dimension linking (Chart A keeps 1D, Chart B keeps 1W when Instrument updates).
 * 5. Fixture E: Event ordering and monotonic revision tracking (newest revision wins).
 * 6. Fixture F: Loop prevention and echo suppression.
 * 7. Fixture G: Cross-entity canonical transformations (Instrument -> Company, Option -> Underlying).
 * 8. Fixture H: Panel capability registry contracts.
 * 9. Fixture I: Event deduplication cache.
 */

import { describe, it, beforeEach } from 'node:test';
import assert from 'node:assert';
import { globalEventBus } from '../eventBus';
import { transformEntityLocal } from '../transformations';
import { getPanelCapability, isDimensionSubscribable } from '../capabilityRegistry';
import {
  ContextDimension,
  ContextSelectionEvent,
  LinkChannel,
} from '../types';

describe('Stage 121 - Global Workspace Linking Unit Tests', () => {
  beforeEach(() => {
    globalEventBus.clear();
  });

  it('Fixture A: synchronizes 4 linked widgets upon Watchlist Instrument selection', () => {
    const channelId = 'chan_fixture_a';
    globalEventBus.setChannelRevision(channelId, 1);

    const receivedEvents: Record<string, ContextSelectionEvent[]> = {
      chart: [],
      company: [],
      news: [],
    };

    // Chart A: Subscribes to INSTRUMENT
    globalEventBus.subscribe(channelId, 'panel_chart_a', ['INSTRUMENT'], (evt) => {
      receivedEvents.chart.push(evt);
    });

    // Company A: Subscribes to INSTRUMENT & COMPANY
    globalEventBus.subscribe(channelId, 'panel_company_a', ['INSTRUMENT', 'COMPANY'], (evt) => {
      receivedEvents.company.push(evt);
    });

    // News A: Subscribes to INSTRUMENT
    globalEventBus.subscribe(channelId, 'panel_news_a', ['INSTRUMENT'], (evt) => {
      receivedEvents.news.push(evt);
    });

    // User selects MSFT in Watchlist A
    const event: ContextSelectionEvent = {
      event_id: 'evt_sel_msft_001',
      origin_panel_instance_id: 'panel_watchlist_a',
      channel_id: channelId,
      scope: 'WORKSPACE',
      dimension: 'INSTRUMENT',
      canonical_target_id: 'inst_msft_us',
      target_type: 'INSTRUMENT',
      payload: { symbol: 'MSFT' },
      context_revision: 2,
      emitted_at: new Date().toISOString(),
    };

    const res = globalEventBus.publish(event);
    assert.strictEqual(res.status, 'DELIVERED');
    assert.strictEqual(res.deliveredCount, 3);

    // Verify all 3 subscribers received MSFT
    assert.strictEqual(receivedEvents.chart.length, 1);
    assert.strictEqual(receivedEvents.chart[0].canonical_target_id, 'inst_msft_us');

    assert.strictEqual(receivedEvents.company.length, 1);
    const transformedCompany = transformEntityLocal(receivedEvents.company[0].payload.symbol as string, 'INSTRUMENT_TO_COMPANY');
    assert.ok(transformedCompany);
    assert.strictEqual(transformedCompany.entity_id, 'comp_microsoft_us');

    assert.strictEqual(receivedEvents.news.length, 1);
    assert.strictEqual(receivedEvents.news[0].payload.symbol, 'MSFT');
  });

  it('Fixture B: preserves independent panel state when linked channel updates', () => {
    const channelId = 'chan_fixture_b';
    globalEventBus.setChannelRevision(channelId, 1);

    let independentChartSymbol = 'NVDA';
    let linkedChartSymbol = 'AAPL';

    // Linked Chart subscribed to channel
    globalEventBus.subscribe(channelId, 'panel_linked_chart', ['INSTRUMENT'], (evt) => {
      linkedChartSymbol = evt.payload.symbol as string;
    });

    // Independent Chart does NOT subscribe to channelId
    // Channel A publishes MSFT
    const event: ContextSelectionEvent = {
      event_id: 'evt_fixture_b_01',
      channel_id: channelId,
      scope: 'WORKSPACE',
      dimension: 'INSTRUMENT',
      canonical_target_id: 'inst_msft_us',
      target_type: 'INSTRUMENT',
      payload: { symbol: 'MSFT' },
      context_revision: 2,
      emitted_at: new Date().toISOString(),
    };

    globalEventBus.publish(event);

    assert.strictEqual(linkedChartSymbol, 'MSFT');
    assert.strictEqual(independentChartSymbol, 'NVDA'); // Independent remains untouched!
  });

  it('Fixture C: isolates separate link channels (Channel A vs Channel B)', () => {
    const channelA = 'chan_group_a';
    const channelB = 'chan_group_b';
    globalEventBus.setChannelRevision(channelA, 1);
    globalEventBus.setChannelRevision(channelB, 1);

    let chartASymbol = 'MSFT';
    let chartBSymbol = 'NVDA';

    globalEventBus.subscribe(channelA, 'panel_chart_a', ['INSTRUMENT'], (evt) => {
      chartASymbol = evt.payload.symbol as string;
    });

    globalEventBus.subscribe(channelB, 'panel_chart_b', ['INSTRUMENT'], (evt) => {
      chartBSymbol = evt.payload.symbol as string;
    });

    // Channel A updates to AAPL
    globalEventBus.publish({
      event_id: 'evt_chan_a_update',
      channel_id: channelA,
      scope: 'WORKSPACE',
      dimension: 'INSTRUMENT',
      canonical_target_id: 'inst_aapl_us',
      target_type: 'INSTRUMENT',
      payload: { symbol: 'AAPL' },
      context_revision: 2,
      emitted_at: new Date().toISOString(),
    });

    assert.strictEqual(chartASymbol, 'AAPL');
    assert.strictEqual(chartBSymbol, 'NVDA'); // Channel B unaffected!
  });

  it('Fixture D: maintains per-dimension independence (different timeframes)', () => {
    const channelId = 'chan_fixture_d';
    globalEventBus.setChannelRevision(channelId, 1);

    const chartA = { symbol: 'AAPL', timeframe: '1D' };
    const chartB = { symbol: 'AAPL', timeframe: '1W' };

    // Both subscribe ONLY to INSTRUMENT, keeping local timeframe
    globalEventBus.subscribe(channelId, 'panel_chart_1d', ['INSTRUMENT'], (evt) => {
      chartA.symbol = evt.payload.symbol as string;
    });
    globalEventBus.subscribe(channelId, 'panel_chart_1w', ['INSTRUMENT'], (evt) => {
      chartB.symbol = evt.payload.symbol as string;
    });

    // Instrument changes to MSFT
    globalEventBus.publish({
      event_id: 'evt_fixture_d_change',
      channel_id: channelId,
      scope: 'WORKSPACE',
      dimension: 'INSTRUMENT',
      canonical_target_id: 'inst_msft_us',
      target_type: 'INSTRUMENT',
      payload: { symbol: 'MSFT' },
      context_revision: 2,
      emitted_at: new Date().toISOString(),
    });

    assert.strictEqual(chartA.symbol, 'MSFT');
    assert.strictEqual(chartA.timeframe, '1D'); // Retained local timeframe!

    assert.strictEqual(chartB.symbol, 'MSFT');
    assert.strictEqual(chartB.timeframe, '1W'); // Retained local timeframe!
  });

  it('Fixture E: enforces monotonic event ordering and drops stale revisions', () => {
    const channelId = 'chan_fixture_e';
    globalEventBus.setChannelRevision(channelId, 1);

    const history: string[] = [];
    globalEventBus.subscribe(channelId, 'panel_subscriber', ['INSTRUMENT'], (evt) => {
      history.push(evt.payload.symbol as string);
    });

    // Rev 1 -> AAPL
    globalEventBus.publish({
      event_id: 'evt_rev_1',
      channel_id: channelId,
      scope: 'WORKSPACE',
      dimension: 'INSTRUMENT',
      canonical_target_id: 'inst_aapl_us',
      payload: { symbol: 'AAPL' },
      context_revision: 1,
      emitted_at: new Date().toISOString(),
    });

    // Rev 3 -> NVDA
    globalEventBus.publish({
      event_id: 'evt_rev_3',
      channel_id: channelId,
      scope: 'WORKSPACE',
      dimension: 'INSTRUMENT',
      canonical_target_id: 'inst_nvda_us',
      payload: { symbol: 'NVDA' },
      context_revision: 3,
      emitted_at: new Date().toISOString(),
    });

    // Stale Rev 2 arrives late -> MSFT
    const staleRes = globalEventBus.publish({
      event_id: 'evt_rev_2_late',
      channel_id: channelId,
      scope: 'WORKSPACE',
      dimension: 'INSTRUMENT',
      canonical_target_id: 'inst_msft_us',
      payload: { symbol: 'MSFT' },
      context_revision: 2,
      emitted_at: new Date().toISOString(),
    });

    assert.strictEqual(staleRes.status, 'STALE_DROPPED');
    assert.deepStrictEqual(history, ['AAPL', 'NVDA']); // NVDA was not overwritten by stale Rev 2!
  });

  it('Fixture F: prevents echo loops back to originating panel', () => {
    const channelId = 'chan_fixture_f';
    globalEventBus.setChannelRevision(channelId, 1);

    let originDeliveryCount = 0;
    let peerDeliveryCount = 0;

    globalEventBus.subscribe(channelId, 'panel_origin_watchlist', ['INSTRUMENT'], () => {
      originDeliveryCount++;
    });

    globalEventBus.subscribe(channelId, 'panel_peer_chart', ['INSTRUMENT'], () => {
      peerDeliveryCount++;
    });

    // Origin panel emits
    globalEventBus.publish({
      event_id: 'evt_echo_prevent_1',
      origin_panel_instance_id: 'panel_origin_watchlist',
      channel_id: channelId,
      scope: 'WORKSPACE',
      dimension: 'INSTRUMENT',
      canonical_target_id: 'inst_aapl_us',
      payload: { symbol: 'AAPL' },
      context_revision: 2,
      emitted_at: new Date().toISOString(),
    });

    assert.strictEqual(originDeliveryCount, 0); // Origin never echoes to itself
    assert.strictEqual(peerDeliveryCount, 1);
  });

  it('Fixture G: performs verified cross-entity canonical transformations', () => {
    // 1. Instrument -> Company
    const comp = transformEntityLocal('AAPL', 'INSTRUMENT_TO_COMPANY');
    assert.ok(comp);
    assert.strictEqual(comp.entity_id, 'comp_apple_us');
    assert.strictEqual(comp.canonical_name, 'Apple Inc.');

    // 2. Company -> Primary Listing
    const listing = transformEntityLocal('comp_microsoft_us', 'COMPANY_TO_PRIMARY_LISTING');
    assert.ok(listing);
    assert.strictEqual(listing.symbol, 'MSFT');

    // 3. Option -> Underlying
    const underlying = transformEntityLocal('NVDA250117C00150000', 'OPTION_TO_UNDERLYING');
    assert.ok(underlying);
    assert.strictEqual(underlying.symbol, 'NVDA');

    // 4. Portfolio -> Benchmark
    const bench = transformEntityLocal('port_institutional_alpha', 'PORTFOLIO_TO_BENCHMARK');
    assert.ok(bench);
    assert.strictEqual(bench.symbol, 'SPX');
  });

  it('Fixture H: verifies panel capability contracts', () => {
    assert.strictEqual(isDimensionSubscribable('INSTRUMENT_CHART', 'INSTRUMENT'), true);
    assert.strictEqual(isDimensionSubscribable('INSTRUMENT_CHART', 'TIMEFRAME'), true);
    assert.strictEqual(isDimensionSubscribable('COMPANY_OVERVIEW', 'COMPANY'), true);
    assert.strictEqual(isDimensionSubscribable('ECONOMIC_SERIES', 'ECONOMIC_SERIES'), true);
    assert.strictEqual(isDimensionSubscribable('NEWS_FEED', 'INSTRUMENT'), true);
    assert.strictEqual(isDimensionSubscribable('WATCHLIST', 'INSTRUMENT'), false); // Watchlist publishes only

    const chartCap = getPanelCapability('INSTRUMENT_CHART');
    assert.ok(chartCap);
    assert.strictEqual(chartCap.supports_as_of, true);
    assert.strictEqual(chartCap.supports_currency, true);
  });

  it('Fixture I: deduplicates repeated event IDs', () => {
    const channelId = 'chan_fixture_i';
    globalEventBus.setChannelRevision(channelId, 1);

    let deliverCount = 0;
    globalEventBus.subscribe(channelId, 'sub_panel', ['INSTRUMENT'], () => {
      deliverCount++;
    });

    const event: ContextSelectionEvent = {
      event_id: 'evt_dedup_unique_42',
      channel_id: channelId,
      scope: 'WORKSPACE',
      dimension: 'INSTRUMENT',
      canonical_target_id: 'inst_aapl_us',
      payload: { symbol: 'AAPL' },
      context_revision: 2,
      emitted_at: new Date().toISOString(),
    };

    const first = globalEventBus.publish(event);
    assert.strictEqual(first.status, 'DELIVERED');
    assert.strictEqual(deliverCount, 1);

    // Duplicate delivery
    const second = globalEventBus.publish(event);
    assert.strictEqual(second.status, 'DUPLICATE_DROPPED');
    assert.strictEqual(deliverCount, 1); // No repeated callback execution!
  });
});

