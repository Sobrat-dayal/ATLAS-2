import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { formatEventTimestamp, computeRateChangeBps, getActiveClockTime } from '../temporal';
import { CATEGORY_METADATA, VERIFICATION_BADGES, LIFECYCLE_BADGES } from '../taxonomy';
import { AtlasUniversalEvent } from '../types';

describe('Stage 135 — Universal Event Model Frontend Tests', () => {
  it('formats exact timestamp and date-only precision properly', () => {
    const iso = '2026-07-25T20:30:00Z';
    const formattedExact = formatEventTimestamp(iso, 'EXACT_TIMESTAMP');
    assert.ok(formattedExact.includes('2026'));
    assert.ok(formattedExact.includes('20:30:00'));

    const formattedDateOnly = formatEventTimestamp('2026-07-25', 'DATE_ONLY');
    assert.ok(formattedDateOnly.includes('Jul'));
    assert.ok(formattedDateOnly.includes('25'));
    assert.ok(formattedDateOnly.includes('2026'));
  });

  it('computes monetary rate basis points correctly', () => {
    // 3.75 to 4.00 is +25 bps
    const bps1 = computeRateChangeBps(4.0, 3.75);
    assert.strictEqual(bps1, 25.0);

    // 5.50 to 5.00 is -50 bps
    const bps2 = computeRateChangeBps(5.0, 5.5);
    assert.strictEqual(bps2, -50.0);
  });

  it('extracts correct clock time from multi-clock event', () => {
    const mockEvent: Partial<AtlasUniversalEvent> = {
      occurred_at: '2026-06-14T04:12:00Z',
      announced_at: '2026-06-14T04:15:00Z',
      scheduled_for: '2026-06-15T00:00:00Z',
      source_published_at: '2026-06-14T04:15:00Z',
      first_ingested_at: '2026-06-14T04:16:00Z',
    };

    const occurred = getActiveClockTime(mockEvent as AtlasUniversalEvent, 'occurred_at');
    assert.strictEqual(occurred, '2026-06-14T04:12:00Z');

    const scheduled = getActiveClockTime(mockEvent as AtlasUniversalEvent, 'scheduled_for');
    assert.strictEqual(scheduled, '2026-06-15T00:00:00Z');
  });

  it('has comprehensive category and verification badge configurations', () => {
    assert.ok(CATEGORY_METADATA.FINANCIAL !== undefined);
    assert.ok(CATEGORY_METADATA.ECONOMIC !== undefined);
    assert.ok(CATEGORY_METADATA.MONETARY_POLICY !== undefined);
    assert.ok(CATEGORY_METADATA.SANCTIONS !== undefined);
    assert.ok(CATEGORY_METADATA.CORPORATE !== undefined);
    assert.ok(CATEGORY_METADATA.NATURAL_DISASTER !== undefined);

    assert.strictEqual(VERIFICATION_BADGES.OFFICIALLY_CONFIRMED.label, 'OFFICIALLY CONFIRMED');
    assert.ok(VERIFICATION_BADGES.CONFLICTED.className.includes('animate-pulse'));
    assert.strictEqual(LIFECYCLE_BADGES.SCHEDULED.label, 'SCHEDULED');
  });
});
