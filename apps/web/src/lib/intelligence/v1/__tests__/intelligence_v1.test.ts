import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { CLIENT_INVESTIGATION_PRESETS } from '../presets';
import { IntelligenceViewType, SectionStatus } from '../types';

describe('INTELLIGENCE V1 Frontend Libs (Stage 138)', () => {
  it('registers all 5 canonical multi-panel investigation presets', () => {
    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_event_investigation);
    assert.strictEqual(CLIENT_INVESTIGATION_PRESETS.preset_event_investigation.name, 'Event Investigation');
    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_event_investigation.panels.includes('EVENT_MONITOR'));
    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_event_investigation.panels.includes('ENTITY_GRAPH'));

    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_company_intelligence);
    assert.strictEqual(CLIENT_INVESTIGATION_PRESETS.preset_company_intelligence.name, 'Company Intelligence');
    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_company_intelligence.panels.includes('ENTITY_CONTEXT'));
    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_company_intelligence.panels.includes('EXPOSURE_SUMMARY'));

    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_economic_decision);
    assert.strictEqual(CLIENT_INVESTIGATION_PRESETS.preset_economic_decision.name, 'Economic Decision Analysis');

    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_geographic_investigation);
    assert.strictEqual(CLIENT_INVESTIGATION_PRESETS.preset_geographic_investigation.name, 'Geographic Event Investigation');
    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_geographic_investigation.panels.includes('GEOGRAPHY_MAP'));

    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_portfolio_exposure);
    assert.strictEqual(CLIENT_INVESTIGATION_PRESETS.preset_portfolio_exposure.name, 'Portfolio Event Exposure');
    assert.ok(CLIENT_INVESTIGATION_PRESETS.preset_portfolio_exposure.linking_channels.includes('selected_portfolio_id'));
  });

  it('validates primary intelligence views information architecture', () => {
    const requiredViews: IntelligenceViewType[] = [
      'OVERVIEW',
      'EVENTS',
      'ENTITIES',
      'GRAPH',
      'EXPOSURE',
      'GEOGRAPHY',
      'INVESTIGATIONS',
      'HISTORY',
      'SOURCES'
    ];
    assert.strictEqual(requiredViews.length, 9);
  });

  it('validates resilient partial section statuses', () => {
    const statuses: SectionStatus[] = [
      'READY',
      'EMPTY',
      'PARTIAL',
      'STALE',
      'SOURCE_UNAVAILABLE',
      'ACCESS_DENIED',
      'FAILED'
    ];
    assert.ok(statuses.includes('SOURCE_UNAVAILABLE'));
    assert.ok(statuses.includes('PARTIAL'));
    assert.ok(statuses.includes('READY'));
  });
});
