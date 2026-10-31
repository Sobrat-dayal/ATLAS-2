/**
 * Frontend Unit Test Suite for ATLAS Stage 133 - Global Physical Infrastructure Intelligence.
 *
 * Validates canonical fixtures, capacity dimensional safety (MW vs MWh),
 * sector taxonomy, and topology crossing separation invariants.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  areMetricsDimensionallyCompatible,
  formatCapacityDisplay,
  BASIS_LABELS,
  METRIC_LABELS,
} from '../capacityUnits';
import { SECTOR_VISUALS } from '../sectorStyles';
import { InfrastructureSector } from '../types';

describe('Stage 133 — Physical Infrastructure Intelligence Frontend Tests', () => {
  // --------------------------------------------------------------------------
  // Fixture B: MW vs MWh Dimensional Integrity
  // --------------------------------------------------------------------------
  it('Fixture B: validates strict separation between Power (MW) and Stored Energy (MWh)', () => {
    // Compatible power units
    assert.equal(areMetricsDimensionallyCompatible('power_mw', 'power_gw'), true);
    assert.equal(areMetricsDimensionallyCompatible('power_mw', 'power_kw'), true);

    // Compatible energy units
    assert.equal(areMetricsDimensionallyCompatible('energy_mwh', 'energy_gwh'), true);

    // Incompatible: Power vs Energy (Never sum 100 MW + 400 MWh = 500 MW!)
    assert.equal(areMetricsDimensionallyCompatible('power_mw', 'energy_mwh'), false);
    assert.equal(areMetricsDimensionallyCompatible('power_gw', 'energy_gwh'), false);

    // Incompatible: Power vs Container throughput
    assert.equal(areMetricsDimensionallyCompatible('power_mw', 'throughput_teu_year'), false);
  });

  // --------------------------------------------------------------------------
  // Fixture F: Capacity Reporting Bases
  // --------------------------------------------------------------------------
  it('Fixture F: formats capacity records preserving reporting basis', () => {
    const formattedNameplate = formatCapacityDisplay(500, 'power_mw', 'nameplate', 'MW');
    assert.equal(formattedNameplate, '500 MW (Nameplate)');

    const formattedNet = formatCapacityDisplay(450, 'power_mw', 'net_summer', 'MW');
    assert.equal(formattedNet, '450 MW (Net Summer)');

    // Ensure bases are recognized in dictionary
    assert.equal(BASIS_LABELS['nameplate'], 'Nameplate');
    assert.equal(BASIS_LABELS['net_summer'], 'Net Summer');
    assert.equal(BASIS_LABELS['design'], 'Design');
  });

  // --------------------------------------------------------------------------
  // Fixture K: Unknown Capacity Displays "Not available"
  // --------------------------------------------------------------------------
  it('Fixture K: displays "Not available" when throughput is missing without fabricating numbers', () => {
    assert.equal(formatCapacityDisplay(null, 'passengers_year'), 'Not available');
    assert.equal(formatCapacityDisplay(undefined, 'cargo_tonnes_year'), 'Not available');
  });

  // --------------------------------------------------------------------------
  // Sector Taxonomy Coverage (All 9 Sectors)
  // --------------------------------------------------------------------------
  it('validates coverage across all 9 institutional physical infrastructure sectors', () => {
    const requiredSectors: InfrastructureSector[] = [
      'ports_maritime',
      'airports_aviation',
      'power_generation',
      'electricity_networks',
      'oil_gas',
      'mining',
      'data_centers',
      'railways',
      'logistics_industrial',
    ];

    for (const sec of requiredSectors) {
      const meta = SECTOR_VISUALS[sec];
      assert.ok(meta, `Sector ${sec} must have visual metadata`);
      assert.ok(meta.color, `Sector ${sec} must have a primary accent color`);
      assert.ok(meta.label, `Sector ${sec} must have a human-readable label`);
      assert.ok(meta.iconName, `Sector ${sec} must have an icon identifier`);
    }
  });

  // --------------------------------------------------------------------------
  // Conduits and Metric Labels
  // --------------------------------------------------------------------------
  it('verifies specialized infrastructure metrics exist in catalog', () => {
    assert.ok(METRIC_LABELS['throughput_teu_year'].includes('TEU'));
    assert.ok(METRIC_LABELS['throughput_bpd'].includes('bpd'));
    assert.ok(METRIC_LABELS['data_center_it_load_mw'].includes('IT Load'));
    assert.ok(METRIC_LABELS['run_of_mine_tonnes_year'].includes('Run-of-Mine'));
  });
});
