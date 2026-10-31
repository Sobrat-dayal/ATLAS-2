import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { PREDICATE_REGISTRY, PROHIBITED_PREDICATES } from '../predicates';
import { NODE_TYPE_CONFIGS } from '../nodeTypes';
import { GraphPath, PredicateType } from '../types';

describe('Event-to-Entity Knowledge Graph Frontend Libs (Stage 136)', () => {
  it('enforces prohibited predicates', () => {
    assert.ok(PROHIBITED_PREDICATES.includes('AFFECTS'));
    assert.ok(PROHIBITED_PREDICATES.includes('DAMAGED'));
    assert.ok(PROHIBITED_PREDICATES.includes('CAUSED_LOSS'));
    assert.ok(PROHIBITED_PREDICATES.includes('EXPOSED_TO'));
  });

  it('provides approved predicate metadata without prohibited items', () => {
    for (const prohibited of PROHIBITED_PREDICATES) {
      assert.strictEqual(PREDICATE_REGISTRY[prohibited as unknown as PredicateType], undefined);
    }

    assert.ok(PREDICATE_REGISTRY.DIRECT_SUBJECT);
    assert.ok(PREDICATE_REGISTRY.ANNOUNCED_BY);
    assert.ok(PREDICATE_REGISTRY.OFFICIALLY_DESIGNATES);
    assert.ok(PREDICATE_REGISTRY.GEOGRAPHICALLY_NEAR);
    assert.ok(PREDICATE_REGISTRY.SUBSIDIARY_OF);
  });

  it('maps all canonical graph node types to display configs', () => {
    const requiredTypes = [
      'EVENT',
      'COMPANY',
      'ISSUER',
      'LEGAL_ENTITY',
      'FINANCIAL_INSTRUMENT',
      'SECTOR',
      'COUNTRY',
      'CENTRAL_BANK',
      'REGULATORY_AUTHORITY',
      'CORPORATE_FACILITY',
      'INFRASTRUCTURE_ASSET',
    ] as const;

    for (const t of requiredTypes) {
      const cfg = NODE_TYPE_CONFIGS[t];
      assert.ok(cfg, `Missing config for node type ${t}`);
      assert.ok(cfg.color);
      assert.ok(cfg.label);
    }
  });

  it('validates factual multi-hop path formatting invariant', () => {
    const dummyPath: GraphPath = {
      path_id: 'path-test-1',
      source_node: {
        node_type: 'EVENT',
        entity_id: 'EVT-01',
        canonical_name: 'Test Pipeline Event',
        identifier_map: {},
      },
      target_node: {
        node_type: 'COMPANY',
        entity_id: 'COMP-01',
        canonical_name: 'Operator Corp',
        identifier_map: {},
      },
      hops: [
        {
          hop_number: 1,
          from_node: {
            node_type: 'EVENT',
            entity_id: 'EVT-01',
            canonical_name: 'Test Pipeline Event',
            identifier_map: {},
          },
          to_node: {
            node_type: 'INFRASTRUCTURE_ASSET',
            entity_id: 'ASSET-01',
            canonical_name: 'Line 1 Pipeline',
            identifier_map: {},
          },
          predicate: 'REFERENCES_INFRASTRUCTURE_ASSET',
          relationship_id: 'rel-1',
          verification_status: 'VERIFIED_DIRECT',
          evidence_ids: ['EVID-1'],
          explanation: 'Event references Line 1 Pipeline.',
        },
        {
          hop_number: 2,
          from_node: {
            node_type: 'INFRASTRUCTURE_ASSET',
            entity_id: 'ASSET-01',
            canonical_name: 'Line 1 Pipeline',
            identifier_map: {},
          },
          to_node: {
            node_type: 'COMPANY',
            entity_id: 'COMP-01',
            canonical_name: 'Operator Corp',
            identifier_map: {},
          },
          predicate: 'OPERATED_BY',
          relationship_id: 'rel-2',
          verification_status: 'VERIFIED_DIRECT',
          evidence_ids: ['EVID-2'],
          explanation: 'Line 1 Pipeline is operated by Operator Corp.',
        },
      ],
      total_hops: 2,
      factual_explanation:
        'Test Pipeline Event references Line 1 Pipeline, which is operated by Operator Corp (Verified).',
    };

    assert.strictEqual(dummyPath.total_hops, 2);
    assert.strictEqual(dummyPath.hops[0].predicate, 'REFERENCES_INFRASTRUCTURE_ASSET');
    assert.strictEqual(dummyPath.hops[1].predicate, 'OPERATED_BY');
    assert.ok(dummyPath.factual_explanation.includes('Operator Corp'));
  });
});

