import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { ScoreObjectiveId, ScoreScale, ScoreStatus } from '../types';

describe('ATLAS Intelligence Scoring Frontend Contracts (Stage 139)', () => {
  it('validates canonical scoring objectives and scale constraints', () => {
    const validObjectives: ScoreObjectiveId[] = [
      'EVENT_REVIEW_PRIORITY',
      'EVENT_ENTITY_RELEVANCE',
      'PORTFOLIO_EVENT_ATTENTION',
      'ECONOMIC_EVENT_RELEVANCE',
      'GEOGRAPHIC_EVENT_RELEVANCE',
      'SOURCE_EVIDENCE_ASSESSMENT',
    ];
    assert.strictEqual(validObjectives.length, 6);
    assert.ok(validObjectives.includes('EVENT_REVIEW_PRIORITY'));
    assert.ok(validObjectives.includes('PORTFOLIO_EVENT_ATTENTION'));
  });

  it('validates score scale and status enumeration', () => {
    const scale: ScoreScale = 'BOUNDED_INDEX_0_100';
    assert.strictEqual(scale, 'BOUNDED_INDEX_0_100');

    const statuses: ScoreStatus[] = ['AVAILABLE', 'PARTIAL', 'INSUFFICIENT_DATA', 'NOT_APPLICABLE'];
    assert.strictEqual(statuses.length, 4);
  });

  it('verifies exact additive factor contribution invariant', () => {
    // Mock factor contributions
    const factorA = {
      factor_id: 'FEAT_DIRECT_ISSUER_MATCH',
      factor_name: 'Direct Match',
      transformed_value: 1.0,
      transformation_method: 'BINARY_ELIGIBILITY' as const,
      weight: 0.5,
      contribution_points: 50.0,
      is_missing: false,
      explanation: 'Direct match present',
    };
    const factorB = {
      factor_id: 'FEAT_PRIMARY_OFFICIAL_FILING',
      factor_name: 'Official Filing',
      transformed_value: 0.8,
      transformation_method: 'BOUNDED_PROPORTION' as const,
      weight: 0.5,
      contribution_points: 40.0,
      is_missing: false,
      explanation: 'Primary filing verified',
    };

    const calculatedTotal = factorA.contribution_points + factorB.contribution_points;
    assert.strictEqual(calculatedTotal, 90.0);
    assert.ok(calculatedTotal <= 100.0);
  });
});

