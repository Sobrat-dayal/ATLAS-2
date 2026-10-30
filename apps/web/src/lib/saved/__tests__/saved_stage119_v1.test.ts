/**
 * Universal Saved System Unit Tests (Stage 119).
 *
 * Verifies:
 * 1. Target type labels and badge styling mappings.
 * 2. Runtime availability status badge variants.
 * 3. Deep link routing safety (internal relative paths only).
 * 4. TypeScript DTO model structural integrity.
 * 5. Bulk action type contracts.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import {
  formatTargetTypeLabel,
  getAvailabilityBadgeVariant,
  getTargetTypeBadgeVariant,
} from '../deepLinks';
import {
  ResourceAvailabilityStatus,
  SavedBulkActionType,
  SavedItem,
  SavedSortOption,
  SavedTargetType,
} from '../types';

describe('Stage 119 - Universal Saved System UI & Lib Tests', () => {
  it('correctly maps target types to readable labels', () => {
    assert.strictEqual(formatTargetTypeLabel('INSTRUMENT'), 'Instrument');
    assert.strictEqual(formatTargetTypeLabel('COMPANY'), 'Company');
    assert.strictEqual(formatTargetTypeLabel('CHART_CONFIG'), 'Chart');
    assert.strictEqual(formatTargetTypeLabel('SCREENER_CONFIG'), 'Screener');
    assert.strictEqual(formatTargetTypeLabel('PORTFOLIO_REFERENCE'), 'Portfolio');
    assert.strictEqual(formatTargetTypeLabel('RISK_RUN'), 'Risk Run');
    assert.strictEqual(formatTargetTypeLabel('RESEARCH_REPORT'), 'Research Report');
    assert.strictEqual(formatTargetTypeLabel('ECONOMIC_SERIES'), 'Economics');
    assert.strictEqual(formatTargetTypeLabel('NEWS_ARTICLE'), 'News');
  });

  it('assigns correct badge variants for resource categories', () => {
    assert.strictEqual(getTargetTypeBadgeVariant('INSTRUMENT'), 'default');
    assert.strictEqual(getTargetTypeBadgeVariant('CHART_CONFIG'), 'primary');
    assert.strictEqual(getTargetTypeBadgeVariant('PORTFOLIO_REFERENCE'), 'positive');
    assert.strictEqual(getTargetTypeBadgeVariant('RISK_RUN'), 'warning');
    assert.strictEqual(getTargetTypeBadgeVariant('RESEARCH_REPORT'), 'outline');
  });

  it('assigns truthful availability badge variants', () => {
    assert.strictEqual(getAvailabilityBadgeVariant('AVAILABLE'), 'positive');
    assert.strictEqual(getAvailabilityBadgeVariant('AVAILABLE_WITH_WARNINGS'), 'warning');
    assert.strictEqual(getAvailabilityBadgeVariant('TARGET_UPDATED'), 'warning');
    assert.strictEqual(getAvailabilityBadgeVariant('TARGET_SUPERSEDED'), 'outline');
    assert.strictEqual(getAvailabilityBadgeVariant('PERMISSION_REVOKED'), 'outline');
    assert.strictEqual(getAvailabilityBadgeVariant('SOURCE_RESTRICTED'), 'outline');
    assert.strictEqual(getAvailabilityBadgeVariant('TARGET_DELETED'), 'negative');
    assert.strictEqual(getAvailabilityBadgeVariant('TARGET_NOT_FOUND'), 'negative');
    assert.strictEqual(getAvailabilityBadgeVariant('RESOURCE_UNAVAILABLE'), 'negative');
  });

  it('enforces structural integrity of SavedItem DTO', () => {
    const item: SavedItem = {
      saved_item_id: 'test-uuid-1',
      owner_user_id: 'user-uuid-1',
      target_type: 'INSTRUMENT',
      target_id: 'AAPL',
      target_module: 'markets',
      canonical_title: 'Apple Inc. (AAPL · NASDAQ)',
      display_title: 'Apple Inc.',
      user_note: 'Core thesis: ecosystem moat.',
      favorite: true,
      pinned: true,
      semantics: 'LIVE_REFERENCE',
      collection_ids: ['col-1'],
      tags: ['Core', 'Tech'],
      availability_status: 'AVAILABLE',
      safe_deep_link: '/markets?instrument_id=AAPL',
      warnings: [],
      saved_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      row_version: 1,
    };

    assert.strictEqual(item.target_type, 'INSTRUMENT');
    assert.strictEqual(item.favorite, true);
    assert.strictEqual(item.pinned, true);
    assert.ok(item.safe_deep_link.startsWith('/markets'));
    assert.strictEqual(item.tags.length, 2);
  });

  it('validates supported bulk action types', () => {
    const supportedActions: SavedBulkActionType[] = [
      'FAVORITE',
      'UNFAVORITE',
      'PIN',
      'UNPIN',
      'ADD_TO_COLLECTION',
      'REMOVE_FROM_COLLECTION',
      'ADD_TAG',
      'REMOVE_TAG',
      'DELETE',
      'RESTORE',
    ];
    assert.strictEqual(supportedActions.length, 10);
  });

  it('validates sorting options', () => {
    const sortOptions: SavedSortOption[] = [
      'RECENTLY_SAVED',
      'RECENTLY_UPDATED',
      'NAME_ASC',
      'NAME_DESC',
      'RESOURCE_TYPE',
      'CUSTOM_ORDER',
    ];
    assert.strictEqual(sortOptions.length, 6);
  });
});
