"""Domain Models and Value Objects for ATLAS Maps V1 (Stage 129).

Defines canonical representations of geographic coordinates, bounding boxes,
camera projections, spatial datasets, features, layer definitions,
vector tile states, and persistent user map views.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class GeometryType(str, Enum):
    """Supported baseline geometry types under WGS84 / EPSG:4326."""

    POINT = "Point"
    MULTIPOINT = "MultiPoint"
    LINESTRING = "LineString"
    MULTILINESTRING = "MultiLineString"
    POLYGON = "Polygon"
    MULTIPOLYGON = "MultiPolygon"


class DatasetType(str, Enum):
    """Classification of geographic dataset sources."""

    REFERENCE_BOUNDARIES = "reference_boundaries"
    ADMINISTRATIVE_REGIONS = "administrative_regions"
    GEOGRAPHIC_FEATURES = "geographic_features"
    FINANCIAL_CENTERS = "financial_centers"
    CUSTOM_USER_LAYER = "custom_user_layer"


class SpatialPredicate(str, Enum):
    """Supported spatial relationship query predicates."""

    INTERSECTS = "intersects"
    WITHIN = "within"
    CONTAINS = "contains"
    DWITHIN = "dwithin"


class DataQualityStatus(str, Enum):
    """Data provenance and geometric accuracy status."""

    VERIFIED = "verified"
    PROVISIONAL = "provisional"
    APPROXIMATE = "approximate"
    UNCERTAIN = "uncertain"


class LicensingPolicy(str, Enum):
    """Licensing and redistribution compliance policy."""

    OPEN_DATA_CC_BY = "cc_by_4.0"
    ODBL = "odbl_1.0"
    PROPRIETARY_LICENSED = "proprietary_licensed"
    RESTRICTED_ACCESS = "restricted_access"


@dataclass(frozen=True)
class GeoBoundingBox:
    """Geographic bounding box defined by [west, south, east, north] in degrees."""

    west: float
    south: float
    east: float
    north: float

    def crosses_antimeridian(self) -> bool:
        """Determines if the bounding box spans across the International Date Line (180°)."""
        return self.west > self.east

    def to_list(self) -> List[float]:
        return [self.west, self.south, self.east, self.north]


@dataclass
class GeoCameraState:
    """Canonical map camera position, orientation, and zoom."""

    longitude: float
    latitude: float
    zoom: float
    bearing: float = 0.0
    pitch: float = 0.0
    bounds: Optional[GeoBoundingBox] = None
    projection: str = "mercator"
    revision: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "longitude": self.longitude,
            "latitude": self.latitude,
            "zoom": self.zoom,
            "bearing": self.bearing,
            "pitch": self.pitch,
            "bounds": self.bounds.to_list() if self.bounds else None,
            "projection": self.projection,
            "revision": self.revision,
        }


@dataclass
class GeoFeature:
    """Canonical spatial feature with geometry, attributes, and provenance."""

    feature_id: str
    dataset_id: str
    geometry_type: GeometryType
    coordinates: Any  # Valid GeoJSON coordinate structure: [lon, lat] or nested lists
    properties: Dict[str, Any]
    label: str
    source_reference: str
    bounding_box: Optional[GeoBoundingBox] = None
    data_quality: DataQualityStatus = DataQualityStatus.VERIFIED
    source_updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def to_geojson_feature(self) -> Dict[str, Any]:
        return {
            "type": "Feature",
            "id": self.feature_id,
            "geometry": {
                "type": self.geometry_type.value,
                "coordinates": self.coordinates,
            },
            "properties": {
                **self.properties,
                "feature_id": self.feature_id,
                "dataset_id": self.dataset_id,
                "label": self.label,
                "source_reference": self.source_reference,
                "data_quality": self.data_quality.value,
            },
        }


@dataclass
class GeoDataset:
    """Geographic dataset container and licensing contract."""

    dataset_id: str
    dataset_name: str
    description: str
    dataset_type: DatasetType
    source_id: str
    source_version: str
    geometry_types: List[GeometryType]
    srid: int = 4326
    bounding_box: Optional[GeoBoundingBox] = None
    feature_count: int = 0
    attribution: str = ""
    licensing_policy: LicensingPolicy = LicensingPolicy.OPEN_DATA_CC_BY
    is_public: bool = True
    owner_user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    data_quality_status: DataQualityStatus = DataQualityStatus.VERIFIED
    published_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    ingested_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class MapLayerDefinition:
    """Visual layer mapped to an underlying spatial dataset."""

    layer_id: str
    dataset_id: str
    layer_name: str
    geometry_type: GeometryType
    source_type: str = "vector"  # "vector" or "geojson"
    style_definition: Dict[str, Any] = field(default_factory=dict)
    default_visibility: bool = True
    default_opacity: float = 1.0
    min_zoom: float = 0.0
    max_zoom: float = 22.0
    display_order: int = 100
    category: str = "Boundaries"
    required_permissions: List[str] = field(default_factory=list)
    license_reference: str = ""
    version: int = 1


@dataclass
class MapLayerState:
    """User runtime layer configuration state."""

    layer_id: str
    visible: bool = True
    opacity: float = 1.0
    display_order: int = 100
    filter_expression: Optional[Dict[str, Any]] = None


@dataclass
class MapBasemapStyle:
    """Authorized MapLibre-compatible basemap style description."""

    style_id: str
    display_name: str
    provider_id: str
    style_url: str
    thumbnail_url: str = ""
    attribution: str = ""
    license_reference: str = ""
    requires_api_key: bool = False
    max_zoom: float = 22.0
    is_dark: bool = True
    is_available: bool = True


@dataclass
class UserMapView:
    """Persisted user map view for Saved integration and Workspace panels."""

    map_view_id: str
    owner_user_id: str
    name: str
    camera: GeoCameraState
    basemap_style_id: str
    visible_layers: List[str]
    layer_configurations: Dict[str, Dict[str, Any]]
    selected_feature_id: Optional[str] = None
    workspace_id: Optional[str] = None
    tenant_id: Optional[str] = None
    revision: int = 1
    map_schema_version: str = "1.0.0"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class GeoSourceManifest:
    """Provenance tracking record for geographic data sources."""

    source_id: str
    provider: str
    dataset_id: str
    dataset_version: str
    source_published_at: datetime.datetime
    ingested_at: datetime.datetime
    license: LicensingPolicy
    attribution: str
    data_quality: DataQualityStatus


@dataclass
class GeographicSearchResult:
    """Geographic search resolution result."""

    result_id: str
    label: str
    place_type: str  # "country", "region", "city", "financial_center", "coordinates"
    coordinates: List[float]  # [longitude, latitude]
    bounding_box: Optional[GeoBoundingBox] = None
    source_dataset_id: str = "atlas.reference.search"
    disambiguation: str = ""
    relevance_score: float = 1.0

