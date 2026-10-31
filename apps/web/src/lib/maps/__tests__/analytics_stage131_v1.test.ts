/**
 * Frontend Unit Test Suite for Stage 131: deck.gl + H3 Spatial Analytics.
 *
 * Validates:
 * - Fixture A: H3 indexing, coordinates, boundary closed rings, resolution
 * - Fixture B: Parent and child hierarchy traversal
 * - Fixture D: Area-normalized density calculation
 * - Fixture E: H3 pentagon identification and 5-vertex boundaries
 * - Fixture F: Antimeridian wrapping normalization
 * - Fixture G: Centroid-based polygon to cells conversion
 * - Color scales & suppressed styling
 * - Cesium 3D adapter entity conversion
 * - Error taxonomy message formatting
 */

import assert from 'node:assert/strict';
import test from 'node:test';

import { getColorForValue, getCssGradient, SUPPRESSED_COLOR } from '../analytics/colorScales';
import { convertH3AggregatesToCesiumEntities } from '../analytics/cesiumAdapter';
import { formatSpatialAnalyticsErrorMessage } from '../analytics/errors';
import {
  cellAreaKm2,
  cellToChildren,
  cellToGeoJsonBoundary,
  cellToLatLng,
  cellToParent,
  getResolution,
  isPentagon,
  isValidCell,
  latLngToCell,
  polygonToCells,
} from '../analytics/h3';
import { AtlasH3Aggregate } from '../analytics/types';

test('Stage 131 — deck.gl + H3 Spatial Analytics Frontend Tests', async (t) => {
  await t.test('Fixture A: validates single cell indexing, resolution, and boundary ring', () => {
    const lat = 51.5074;
    const lng = -0.1278;
    const res = 7;
    const cellId = latLngToCell(lat, lng, res);

    assert.equal(typeof cellId, 'string');
    assert.equal(isValidCell(cellId), true);
    assert.equal(getResolution(cellId), 7);

    const [cLat, cLng] = cellToLatLng(cellId);
    assert.ok(Math.abs(cLat - lat) < 0.05);
    assert.ok(Math.abs(cLng - lng) < 0.05);

    const boundary = cellToGeoJsonBoundary(cellId);
    assert.ok(boundary.length >= 6);
    // Closed polygon ring: first point equals last point
    assert.deepEqual(boundary[0], boundary[boundary.length - 1]);
  });

  await t.test('Fixture B: validates parent/child hierarchy traversal', () => {
    const cellId = latLngToCell(40.7128, -74.006, 6); // NYC res 6
    const parent = cellToParent(cellId, 5);
    assert.equal(getResolution(parent), 5);

    const children = cellToChildren(cellId, 7);
    assert.equal(children.length, 7);
    for (const child of children) {
      assert.equal(getResolution(child), 7);
    }
  });

  await t.test('Fixture D: calculates accurate cell area and density', () => {
    const cellId = latLngToCell(48.8566, 2.3522, 6); // Paris res 6
    const area = cellAreaKm2(cellId);
    assert.ok(area > 20 && area < 50); // H3 res 6 average ~36 km²

    const count = 100;
    const density = count / area;
    assert.ok(density > 0);
  });

  await t.test('Fixture E: handles H3 pentagons correctly', () => {
    // Canonical resolution 0 pentagon
    const pentagon = '8009fffffffffff';
    assert.equal(isPentagon(pentagon), true);

    const boundary = cellToGeoJsonBoundary(pentagon);
    // 5 vertices + 1 closing vertex = 6 coordinates
    assert.equal(boundary.length, 6);
    assert.deepEqual(boundary[0], boundary[boundary.length - 1]);
  });

  await t.test('Fixture F: handles antimeridian coordinate wrapping', () => {
    const cell = latLngToCell(-16.5, 179.9, 5);
    const boundary = cellToGeoJsonBoundary(cell);
    assert.ok(boundary.length >= 6);

    const lons = boundary.map((p) => p[0]);
    assert.ok(Math.max(...lons) - Math.min(...lons) < 180);
  });

  await t.test('Fixture G: converts polygon coordinates into covering cells', () => {
    const polyCoords: [number, number][] = [
      [-0.15, 51.5],
      [-0.1, 51.5],
      [-0.1, 51.53],
      [-0.15, 51.53],
      [-0.15, 51.5],
    ];
    const cells = polygonToCells(polyCoords, 8);
    assert.ok(cells.length > 0);
    for (const c of cells) {
      assert.equal(isValidCell(c), true);
    }
  });

  await t.test('Color Scales: maps numeric values and privacy suppression cleanly', () => {
    const color = getColorForValue(50, 0, 100, 'viridis', false);
    assert.equal(color.length, 4);
    assert.ok(color[0] >= 0 && color[0] <= 255);

    // Suppressed cell returns distinct muted gray
    const suppressed = getColorForValue(50, 0, 100, 'viridis', true);
    assert.deepEqual(suppressed, SUPPRESSED_COLOR);

    // Null value returns suppressed color
    const nullColor = getColorForValue(null, 0, 100, 'viridis', false);
    assert.deepEqual(nullColor, SUPPRESSED_COLOR);

    const gradient = getCssGradient('viridis');
    assert.ok(gradient.startsWith('linear-gradient('));
  });

  await t.test('Cesium 3D Adapter: converts H3 aggregates into 3D polygon entities', () => {
    const sampleAggregates: AtlasH3Aggregate[] = [
      {
        h3_cell_id: latLngToCell(51.5, -0.1, 6),
        h3_resolution: 6,
        metric_id: 'market_capital_intensity',
        aggregation_method: 'sum',
        value: 150000000,
        record_count: 12,
        non_null_count: 12,
        cell_area_km2: 36.2,
        unit: 'USD',
        is_suppressed: false,
        data_quality: 'verified',
      },
    ];

    const entities = convertH3AggregatesToCesiumEntities(sampleAggregates, {
      palette: 'viridis',
      minVal: 0,
      maxVal: 200000000,
      extruded: true,
      elevationScale: 50,
    });

    assert.equal(entities.length, 1);
    assert.ok(entities[0].positionsDegrees.length >= 12); // At least 6 vertices * 2 coordinates
    assert.ok(entities[0].extrudedHeightMeters > 0);
    assert.equal(entities[0].rgbaColor.length, 4);
  });

  await t.test('Error Taxonomy: formats typed error messages accurately', () => {
    assert.equal(
      formatSpatialAnalyticsErrorMessage('INVALID_H3_CELL'),
      'The specified H3 hexagonal cell identifier is malformed or invalid.'
    );
    assert.equal(
      formatSpatialAnalyticsErrorMessage('PRIVACY_SUPPRESSED'),
      'Detailed observations for this cell are protected by minimum-contributor privacy suppression.'
    );
    assert.equal(
      formatSpatialAnalyticsErrorMessage('UNAUTHORIZED_SPATIAL_DATASET'),
      'Access to this proprietary analytical spatial dataset is restricted under your organization policy.'
    );
  });
});

