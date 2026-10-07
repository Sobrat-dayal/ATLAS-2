# Canonical Economic Data Architecture

## Overview

ATLAS owns the canonical Economic Data schema. Provider-specific observations must be normalized into ATLAS models. The architecture strictly separates the Provider's representation of an economic observation from the internal canonical model.

```text
Provider-specific Economic Data
            │
            ▼
        Provider Adapter
            │
            ▼
ATLAS Canonical Economic Models
            │
            ▼
         Domain Services
```

## Stage 20 / Stage 35 Boundary

Stage 20 defined the identity and descriptive metadata of an economic series:
```text
Economic Series Entity
=
identity + metadata
```

Stage 35 builds the canonical observation/data layer underneath it:
```text
Economic Observation
=
value + period + revision
```

## Canonical Economic Series Identity

The canonical identity of an Economic Data time series is the existing Stage 20 Economic Series `entity_id` (a UUID).

FRED, World Bank, OECD, and IMF codes are **not** canonical identity. They remain external identifiers (Stage 21).

## Economic Series Metadata Reuse

- **Frequency**: Reused existing `EconomicFrequency`.
- **Unit Label**: Reused existing `unit_label`.
- **Value Representation**: Reused existing `EconomicValueRepresentation`.
- **Seasonal Adjustment**: Reused existing `SeasonalAdjustment`.
- **Scope Geographic Entity**: Reused existing `scope_geographic_entity_id`.

## Numeric Precision Policy

- **Economic Value**: `CanonicalDecimal` (a string-based Decimal equivalent to preserve exact precision).
- **Missing Value**: `None`
- **Count-like values**: `CanonicalDecimal`

## Float Policy

Binary float input in canonical models is rejected. Provider adapters must intentionally normalize external float values to string-based `Decimal` representations when the Provider gives no safer representation.

## Decimal Serialization

```json
{
  "value": "325.421"
}
```

## Zero vs Missing

Zero is a valid Economic Observation value.
- **Available observation**: `value = "0"`, `availability = "available"`
- **Missing observation**: `value = null`, `availability = "missing"`

## Negative Values

Negative economic values are supported and valid.

## Percentage Semantics

`5.25` is preserved as `5.25 percent` when the series representation says percent. It is not automatically converted to `0.0525`.

## Economic Observation Period

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `reference_date` | `date` | Yes | Source/canonical observation label date |
| `period_start` | `date` | No | Optional period start boundary |
| `period_end` | `date` | No | Optional period end boundary |

**Period Boundary Policy**: ATLAS does not fabricate start/end dates. If the source only provides a reference date, boundaries remain absent.

## Observation Availability

| Value | Meaning | Value Rule |
|-------|---------|------------|
| `available` | Observation is available | `value` must not be None |
| `missing` | Observation is explicitly missing | `value` must be None |

## Revision Status

- `preliminary`
- `revised`
- `final`
- `unknown`

## Revision Policy

| Policy | Meaning |
|--------|---------|
| `latest_available` | Latest available version for each observation period |
| `as_of` | Version available as of a specific date |
| `all_vintages` | Multiple historical revisions/vintages |

**As-of Semantics**: `as_of_date` is strictly validated to be present when policy is `AS_OF` and absent otherwise.

## Economic Data Origin

| Field | Type | Purpose |
|-------|------|---------|
| `provider_key` | `str` | Identifies the provider |
| `upstream_source` | `str` | Name of the upstream data source |
| `retrieved_at` | `datetime` | Timezone-aware UTC retrieval time |
| `source_reference` | `str` | Optional bounded source reference |

**Origin vs Provenance**:
```text
EconomicDataOrigin
=
runtime Provider/source lineage

Stage 24 Provenance
=
persistent evidence lineage
```

## Economic Observation

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `economic_series_id` | `uuid.UUID` | Yes | Canonical Stage 20 UUID |
| `period` | `EconomicObservationPeriod` | Yes | Reference period |
| `availability` | `EconomicObservationAvailability` | Yes | Available or missing |
| `value` | `CanonicalDecimal` | No | Required if available |
| `revision_status` | `EconomicRevisionStatus` | Yes | Defaults to unknown |
| `released_at` | `datetime` | No | Source official release time |
| `vintage_date` | `date` | No | Provider vintage date |

**Timestamp Semantics**:
- `released_at` is the official release time and is not `retrieved_at`.
- `vintage_date` is the data's vintage and is separate from release time.

## Derived Analytics Boundary

`EconomicObservation` does not calculate or store: YoY, MoM, QoQ, annualized growth, surprise, forecast error, z-score, etc.

## Economic Data Operations

| Operation | Purpose |
|-----------|---------|
| `observations` | Fetch historical/standard observations |
| `latest_observations` | Fetch latest observation for a batch of series |

## Economic Provider Capabilities

`ProviderDomain.ECONOMICS` simply means the Provider is in the Economics family. `EconomicDataOperation` explicitly defines which canonical operations are supported. 
Revision capabilities (`revision_policies`) explicitly declare supported revision semantics.

## Registered Provider Operation Support

- OpenBB: Economics Domain? Yes. Canonical Operations: None. Revision Policies: None.

## Economic Observations Request

Request by Series UUID, start date, end date, limit, and revision selection.
Bounds: Require at least a date range or limit (max 10,000).

## Latest Economic Observations Request

Request by a batch of Series UUIDs (max 100). Duplicate IDs are rejected.

## Observation Ordering

Observations are ordered by `reference_date` ascending.
- **Latest-Available**: Multiple observations for the same period are rejected.
- **As-Of**: Multiple observations for the same period are rejected.
- **All-Vintages**: Multiple observations for the same period are allowed, sorted by `vintage_date` ascending. Exact duplicates are rejected.

## Latest Economic Observation Item

Fields:
- `economic_series_id`
- `observation` (Optional)

Absence is represented as `observation = None` without fabricating zero/missing periods.

## Economic Provider Protocols

- `EconomicObservationsProvider`: `async def get_economic_observations(request: EconomicObservationsRequest) -> EconomicObservationsResponse`
- `LatestEconomicObservationsProvider`: `async def get_latest_economic_observations(request: LatestEconomicObservationsRequest) -> LatestEconomicObservationsResponse`

Stage 35 did not introduce a generic `execute_economic(operation, payload)` executor.

## Boundaries

- **Provider Routing**: Remains outside Economic request models.
- **Provider Health**: No health state in Economic models.
- **Credentials**: No Provider credentials or secret references in Economic models.
- **OpenBB Boundary**: Canonical OpenBB operations are currently empty.
- **FRED/World Bank/OECD/IMF Boundaries**: Stage 35 performs no real Provider requests.
- **Economic Calendar Boundary**: `released_at` metadata != Economic Calendar. Stage 92 deferred.
- **Transformation Boundary**: No interpolation, forward fill, resampling, seasonal adjustment, index rebasing, currency conversion.
- **Forecast/Consensus Boundary**: No forecast, consensus, surprise implemented.

## Future Stages
- **Stage 89**: Economics V1 (UI)
- **Stage 92**: Economic Calendar / Release System
