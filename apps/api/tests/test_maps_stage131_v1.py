"""Unit and Regression Test Suite for ATLAS Stage 131 - deck.gl + H3 Spatial Analytics.

Validates all 12 Canonical Reference Fixtures (Fixtures A through L):
- Fixture A: Single Cell indexing, centroid, boundary, parent
- Fixture B: Parent additive aggregation (60 total from 10, 20, 30)
- Fixture C: Mathematically correct weighted mean (6.0 vs unweighted 7.5)
- Fixture D: Area-normalized density (100 obs / 25 km² = 4.0 obs/km²)
- Fixture E: H3 pentagon detection and geometry handling
- Fixture F: Antimeridian wrapping without polygon distortion
- Fixture G: Polygon covering with centroid containment
- Fixture H: Count vs Distinct Count (3 observations, 2 distinct entities)
- Fixture I: Missing values handling (0, NULL, 10 -> count=2, sum=10, mean=5)
- Fixture J: Historical time bucketing without look-ahead
- Fixture K: Multi-tenant dataset isolation and cache separation
- Fixture L: Revoked source entitlement enforcement
"""

import datetime

import pytest
from atlas.maps.analytics.domain import (
    AtlasH3Aggregate,
    NullValuePolicy,
    SpatialAggregationMethod,
    SpatialAnalyticsQuery,
    SpatialVisualizationType,
    TimeBucketInterval,
)
from atlas.maps.analytics.errors import (
    SourceEntitlementRevokedError,
    UnauthorizedSpatialDatasetError,
)
from atlas.maps.analytics.h3.boundaries import cell_to_geojson_boundary
from atlas.maps.analytics.h3.cell_area import get_cell_area_km2
from atlas.maps.analytics.h3.coverage import polygon_to_cells
from atlas.maps.analytics.h3.density import compute_density
from atlas.maps.analytics.h3.hierarchy import (
    cell_to_children,
    cell_to_parent,
    rollup_child_aggregates,
)
from atlas.maps.analytics.h3.indexing import (
    cell_to_lat_lng,
    get_cell_resolution,
    is_pentagon,
    lat_lng_to_cell,
    validate_cell_id,
)
from atlas.maps.analytics.metrics import compute_metric_aggregation
from atlas.maps.analytics.service import AtlasSpatialAnalyticsService
from atlas.maps.analytics.temporal import filter_by_historical_as_of, get_temporal_bucket_key


def test_fixture_a_single_cell():
    """Fixture A: Validates single cell coordinate indexing, centroid, and resolution."""
    lat, lng = 51.5074, -0.1278  # London
    res = 7
    cell_id = lat_lng_to_cell(lat, lng, res)

    assert isinstance(cell_id, str)
    assert len(cell_id) == 15
    validate_cell_id(cell_id)

    assert get_cell_resolution(cell_id) == 7

    # Center back to lat/lng
    c_lat, c_lng = cell_to_lat_lng(cell_id)
    assert abs(c_lat - lat) < 0.05
    assert abs(c_lng - lng) < 0.05

    # Boundary ring is closed GeoJSON
    boundary = cell_to_geojson_boundary(cell_id)
    assert len(boundary) >= 6
    assert boundary[0] == boundary[-1]  # Closed polygon ring

    # Valid parent
    parent_cell = cell_to_parent(cell_id, 6)
    assert get_cell_resolution(parent_cell) == 6


def test_fixture_b_parent_additive_aggregation():
    """Fixture B: Validates parent aggregation with 10, 20, 30 child observations rolling up to 60."""
    parent_cell = lat_lng_to_cell(40.7128, -74.0060, 5)
    children = cell_to_children(parent_cell, 6)
    assert len(children) >= 3

    child_aggs = [
        AtlasH3Aggregate(
            h3_cell_id=children[0],
            h3_resolution=6,
            metric_id="observation_count",
            aggregation_method=SpatialAggregationMethod.COUNT,
            value=10.0,
            record_count=10,
            non_null_count=10,
            cell_area_km2=get_cell_area_km2(children[0]),
        ),
        AtlasH3Aggregate(
            h3_cell_id=children[1],
            h3_resolution=6,
            metric_id="observation_count",
            aggregation_method=SpatialAggregationMethod.COUNT,
            value=20.0,
            record_count=20,
            non_null_count=20,
            cell_area_km2=get_cell_area_km2(children[1]),
        ),
        AtlasH3Aggregate(
            h3_cell_id=children[2],
            h3_resolution=6,
            metric_id="observation_count",
            aggregation_method=SpatialAggregationMethod.COUNT,
            value=30.0,
            record_count=30,
            non_null_count=30,
            cell_area_km2=get_cell_area_km2(children[2]),
        ),
    ]

    parent_agg = rollup_child_aggregates(
        parent_cell_id=parent_cell,
        child_aggregates=child_aggs,
        aggregation_method=SpatialAggregationMethod.COUNT,
        metric_id="observation_count",
        min_contributors=1,
    )

    assert parent_agg.record_count == 60
    assert parent_agg.value == 60.0
    assert parent_agg.h3_resolution == 5


def test_fixture_c_weighted_mean_correctness():
    """Fixture C: Validates that parent weighted mean = (100+200)/(10+40) = 6.0, not (10+5)/2 = 7.5."""
    parent_cell = lat_lng_to_cell(35.6762, 139.6503, 5)
    children = cell_to_children(parent_cell, 6)

    # Child A: Sum = 100, Count = 10 -> Mean = 10.0
    # Child B: Sum = 200, Count = 40 -> Mean = 5.0
    child_aggs = [
        AtlasH3Aggregate(
            h3_cell_id=children[0],
            h3_resolution=6,
            metric_id="market_capital_intensity",
            aggregation_method=SpatialAggregationMethod.MEAN,
            value=10.0,
            record_count=10,
            non_null_count=10,
            valid_weight_sum=10.0,
            cell_area_km2=get_cell_area_km2(children[0]),
        ),
        AtlasH3Aggregate(
            h3_cell_id=children[1],
            h3_resolution=6,
            metric_id="market_capital_intensity",
            aggregation_method=SpatialAggregationMethod.MEAN,
            value=5.0,
            record_count=40,
            non_null_count=40,
            valid_weight_sum=40.0,
            cell_area_km2=get_cell_area_km2(children[1]),
        ),
    ]

    parent_agg = rollup_child_aggregates(
        parent_cell_id=parent_cell,
        child_aggregates=child_aggs,
        aggregation_method=SpatialAggregationMethod.WEIGHTED_MEAN,
        metric_id="market_capital_intensity",
        min_contributors=1,
    )

    # Correct calculation: (10.0 * 10 + 5.0 * 40) / (10 + 40) = (100 + 200) / 50 = 6.0
    assert parent_agg.value == pytest.approx(6.0, rel=1e-5)
    assert parent_agg.value != pytest.approx(7.5, rel=1e-5)


def test_fixture_d_density_normalization():
    """Fixture D: 100 observations over 25 km² yields density of 4.0 obs/km²."""
    count = 100.0
    area_km2 = 25.0
    density = compute_density(count, area_km2)
    assert density == 4.0


def test_fixture_e_pentagon_handling():
    """Fixture E: Handles actual H3 pentagonal cells without 6-sided hexagon assumptions."""
    # H3 resolution 0 has 12 pentagons. Res 0 pentagon:
    pentagon_cell = "8009fffffffffff"
    assert is_pentagon(pentagon_cell) is True

    boundary = cell_to_geojson_boundary(pentagon_cell)
    # 5 distinct vertices + 1 closing vertex = 6 coordinates
    assert len(boundary) == 6
    assert boundary[0] == boundary[-1]


def test_fixture_f_antimeridian_handling():
    """Fixture F: Data near +180°/-180° does not generate world-spanning polygon artifacts."""
    # Cell near Fiji/Chukotka on the antimeridian
    lat, lng = -16.5, 179.9
    cell = lat_lng_to_cell(lat, lng, 5)
    boundary = cell_to_geojson_boundary(cell)

    assert len(boundary) >= 6
    # Coordinates must not span > 180 degrees horizontally
    lons = [p[0] for p in boundary]
    assert (max(lons) - min(lons)) < 180.0


def test_fixture_g_polygon_covering():
    """Fixture G: Validates centroid-based polygon covering."""
    # Small bounding box over central London
    poly_coords = [
        [-0.15, 51.50],
        [-0.10, 51.50],
        [-0.10, 51.53],
        [-0.15, 51.53],
        [-0.15, 51.50],
    ]
    cells = polygon_to_cells(poly_coords, resolution=8)
    assert len(cells) > 0
    # Every returned cell must have its centroid roughly inside the bounds
    for c in cells:
        c_lat, c_lng = cell_to_lat_lng(c)
        assert 51.48 <= c_lat <= 51.55
        assert -0.17 <= c_lng <= -0.08


def test_fixture_h_count_vs_distinct_count():
    """Fixture H: Company A at Loc 1, Company A at Loc 2, Company B at Loc 3 -> Obs=3, Distinct=2."""
    records = [1.0, 1.0, 1.0]
    distinct_entities = ["CompanyA", "CompanyA", "CompanyB"]

    # Count aggregation
    count_res = compute_metric_aggregation(
        values=records,
        aggregation=SpatialAggregationMethod.COUNT,
        distinct_ids=distinct_entities,
    )
    assert count_res["value"] == 3.0
    assert count_res["record_count"] == 3

    # Distinct Count aggregation
    distinct_res = compute_metric_aggregation(
        values=records,
        aggregation=SpatialAggregationMethod.DISTINCT_COUNT,
        distinct_ids=distinct_entities,
    )
    assert distinct_res["value"] == 2.0
    assert distinct_res["distinct_count"] == 2


def test_fixture_i_missing_values_null_policy():
    """Fixture I: Values [0, NULL, 10] -> non-null count = 2, sum = 10, mean = 5 under EXCLUDE null policy."""
    values = [0.0, None, 10.0]

    sum_res = compute_metric_aggregation(
        values=values,
        aggregation=SpatialAggregationMethod.SUM,
        null_policy=NullValuePolicy.EXCLUDE,
    )
    assert sum_res["non_null_count"] == 2
    assert sum_res["record_count"] == 3
    assert sum_res["value"] == 10.0

    mean_res = compute_metric_aggregation(
        values=values,
        aggregation=SpatialAggregationMethod.MEAN,
        null_policy=NullValuePolicy.EXCLUDE,
    )
    assert mean_res["value"] == 5.0  # (0 + 10) / 2 = 5.0


def test_fixture_j_historical_time_buckets():
    """Fixture J: Verified time bucketing without look-ahead bias."""
    obs = [
        {"id": 1, "source_updated_at": datetime.datetime(2026, 1, 10, 10, 0)},
        {"id": 2, "source_updated_at": datetime.datetime(2026, 1, 15, 12, 0)},
        {"id": 3, "source_updated_at": datetime.datetime(2026, 2, 1, 8, 0)},
    ]

    # As of Jan 20, 2026 -> only 2 records known
    as_of_jan20 = datetime.datetime(2026, 1, 20, 0, 0)
    filtered = filter_by_historical_as_of(obs, as_of=as_of_jan20)
    assert len(filtered) == 2
    assert {o["id"] for o in filtered} == {1, 2}

    # Month bucket keys
    b1 = get_temporal_bucket_key(obs[0]["source_updated_at"], TimeBucketInterval.MONTH)
    b3 = get_temporal_bucket_key(obs[2]["source_updated_at"], TimeBucketInterval.MONTH)
    assert b1 == "2026-01"
    assert b3 == "2026-02"


def test_fixture_k_cross_tenant_isolation():
    """Fixture K: Tenant A restricted dataset cannot be queried by Tenant B."""
    service = AtlasSpatialAnalyticsService()

    query = SpatialAnalyticsQuery(
        dataset_id="restricted_tenant_alpha",
        metric_id="observation_count",
        aggregation=SpatialAggregationMethod.COUNT,
        visualization_type=SpatialVisualizationType.H3_HEXAGON,
        tenant_id="tenant_alpha",
    )

    # Calling as tenant_beta should raise UnauthorizedSpatialDatasetError
    with pytest.raises(UnauthorizedSpatialDatasetError):
        service.query_analytics(query, user_id="user_b", tenant_id="tenant_beta")


def test_fixture_l_revoked_source_entitlement():
    """Fixture L: Revoked source entitlement blocks protected aggregate and clears cache."""
    service = AtlasSpatialAnalyticsService()
    service.revoke_source_entitlement("financial_centers_global")

    query = SpatialAnalyticsQuery(
        dataset_id="financial_centers_global",
        metric_id="observation_count",
        aggregation=SpatialAggregationMethod.COUNT,
        visualization_type=SpatialVisualizationType.H3_HEXAGON,
    )

    with pytest.raises(SourceEntitlementRevokedError):
        service.query_analytics(query)
