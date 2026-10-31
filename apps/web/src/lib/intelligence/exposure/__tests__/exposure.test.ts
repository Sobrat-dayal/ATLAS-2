import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { CLIENT_MEASURE_DEFINITIONS } from '../measureDefinitions';
import { formatCurrencyAmount, formatPercentage, formatRatio, formatExposureAmount } from '../units';

describe('Financial and Economic Exposure Engine Frontend Libs (Stage 137)', () => {
  it('registers canonical exposure measure definitions with explicit formulas', () => {
    assert.ok(CLIENT_MEASURE_DEFINITIONS.REV_GEO_SHARE_V1);
    assert.strictEqual(CLIENT_MEASURE_DEFINITIONS.REV_GEO_SHARE_V1.domain, 'GEOGRAPHIC');
    assert.strictEqual(CLIENT_MEASURE_DEFINITIONS.REV_GEO_SHARE_V1.unit_dimension, 'PERCENT');
    assert.ok(CLIENT_MEASURE_DEFINITIONS.REV_GEO_SHARE_V1.numerator_definition);
    assert.ok(CLIENT_MEASURE_DEFINITIONS.REV_GEO_SHARE_V1.denominator_definition);

    assert.ok(CLIENT_MEASURE_DEFINITIONS.PORTFOLIO_NAV_WEIGHT_V1);
    assert.strictEqual(CLIENT_MEASURE_DEFINITIONS.PORTFOLIO_NAV_WEIGHT_V1.domain, 'PORTFOLIO');

    assert.ok(CLIENT_MEASURE_DEFINITIONS.FACILITY_COUNT_V1);
    assert.strictEqual(CLIENT_MEASURE_DEFINITIONS.FACILITY_COUNT_V1.unit_dimension, 'COUNT');

    assert.ok(CLIENT_MEASURE_DEFINITIONS.CORP_GROUP_CONSOLIDATED_REV_V1);
    assert.strictEqual(CLIENT_MEASURE_DEFINITIONS.CORP_GROUP_CONSOLIDATED_REV_V1.domain, 'CORPORATE_GROUP');
  });

  it('formats currency amounts accurately with fallback for null/unavailable', () => {
    const formatted = formatCurrencyAmount(1234567.89, 'USD');
    assert.ok(formatted.includes('1,234,567.89'));

    assert.strictEqual(formatCurrencyAmount(null), 'UNAVAILABLE');
    assert.strictEqual(formatCurrencyAmount(undefined), 'UNAVAILABLE');
    assert.strictEqual(formatCurrencyAmount('not_a_number'), 'UNAVAILABLE');
  });

  it('formats percentages with exact decimal precision and symbol', () => {
    assert.strictEqual(formatPercentage(40.0), '40.00%');
    assert.strictEqual(formatPercentage('12.345'), '12.35%');
    assert.strictEqual(formatPercentage(null), 'UNAVAILABLE');
    assert.strictEqual(formatPercentage(undefined), 'UNAVAILABLE');
  });

  it('formats ratios to percentage strings', () => {
    assert.strictEqual(formatRatio(0.85), '85.0%');
    assert.strictEqual(formatRatio(1.0), '100.0%');
    assert.strictEqual(formatRatio(null), 'N/A');
  });

  it('formats exposure amounts based on unit dimensions', () => {
    assert.strictEqual(formatExposureAmount(15, 'COUNT'), '15 facilities');
    assert.strictEqual(formatExposureAmount(25.5, 'KM'), '25.5 km');
    assert.strictEqual(formatExposureAmount(33.33, 'PERCENT'), '33.33%');
    assert.strictEqual(formatExposureAmount(null, 'QUALITATIVE'), 'UNAVAILABLE');
    assert.strictEqual(formatExposureAmount(100, 'QUALITATIVE'), 'Documented Qualitative');
  });
});
