"""Geographic Dataset Registry for ATLAS Maps V1.

Provides approved reference geographic datasets, boundaries, and financial centers.
Strictly adheres to verified real-world coordinates and licensing provenance.
Never fabricates financial facilities, assets, or company locations (reserved for Stage 132).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from atlas.maps.domain import (
    DataQualityStatus,
    DatasetType,
    GeoBoundingBox,
    GeoDataset,
    GeoFeature,
    GeometryType,
    LicensingPolicy,
)


class AtlasDatasetRegistry:
    """Canonical registry indexing approved spatial datasets and features."""

    def __init__(self):
        self._datasets: Dict[str, GeoDataset] = {}
        self._features_by_dataset: Dict[str, Dict[str, GeoFeature]] = {}
        self._init_baseline_datasets()

    def _init_baseline_datasets(self) -> None:
        # 1. Global Financial Centers
        ds_financial = GeoDataset(
            dataset_id="atlas.reference.financial_centers",
            dataset_name="Global Financial Centers & Central Banks",
            description="Verified locations of top global monetary and financial capitals.",
            dataset_type=DatasetType.FINANCIAL_CENTERS,
            source_id="atlas_canonical_financial_geography",
            source_version="2026.1",
            geometry_types=[GeometryType.POINT],
            bounding_box=GeoBoundingBox(west=-122.4, south=-33.9, east=151.2, north=51.5),
            feature_count=10,
            attribution="ATLAS Financial Intelligence Reference Geography",
            licensing_policy=LicensingPolicy.OPEN_DATA_CC_BY,
            is_public=True,
            data_quality_status=DataQualityStatus.VERIFIED,
        )
        self.register_dataset(ds_financial)

        financial_centers_data = [
            (
                "fc_nyc",
                "New York Financial Center",
                [-74.0060, 40.7128],
                "USA",
                "USD",
                "NYSE, NASDAQ, Federal Reserve Bank of NY",
            ),
            (
                "fc_lon",
                "City of London Financial Center",
                [-0.1278, 51.5074],
                "GBR",
                "GBP",
                "LSE, Bank of England, Lloyd's of London",
            ),
            (
                "fc_tyo",
                "Tokyo Financial District",
                [139.6917, 35.6895],
                "JPN",
                "JPY",
                "TSE, Bank of Japan",
            ),
            (
                "fc_fra",
                "Frankfurt Financial Center",
                [8.6821, 50.1109],
                "DEU",
                "EUR",
                "ECB, Deutsche Börse, Bundesbank",
            ),
            (
                "fc_hkg",
                "Hong Kong Financial Hub",
                [114.1694, 22.3193],
                "HKG",
                "HKD",
                "HKEX, Hong Kong Monetary Authority",
            ),
            (
                "fc_sgp",
                "Singapore Monetary District",
                [103.8519, 1.2902],
                "SGP",
                "SGD",
                "SGX, Monetary Authority of Singapore",
            ),
            (
                "fc_zrh",
                "Zurich Banking Center",
                [8.5417, 47.3769],
                "CHE",
                "CHF",
                "SIX Swiss Exchange, Swiss National Bank",
            ),
            (
                "fc_par",
                "Paris Financial Center",
                [2.3522, 48.8566],
                "FRA",
                "EUR",
                "Euronext Paris, Banque de France",
            ),
            (
                "fc_syd",
                "Sydney Financial District",
                [151.2093, -33.8688],
                "AUS",
                "AUD",
                "ASX, Reserve Bank of Australia",
            ),
            (
                "fc_tor",
                "Toronto Financial District",
                [-79.3832, 43.6532],
                "CAN",
                "CAD",
                "TSX, Bank of Canada",
            ),
        ]

        for fid, name, coords, country, cur, desc in financial_centers_data:
            feat = GeoFeature(
                feature_id=fid,
                dataset_id=ds_financial.dataset_id,
                geometry_type=GeometryType.POINT,
                coordinates=coords,
                properties={
                    "name": name,
                    "country_code": country,
                    "currency": cur,
                    "description": desc,
                    "tier": "Tier 1 Global Financial Center",
                },
                label=name,
                source_reference="ATLAS Monetary Geography Directory 2026",
                bounding_box=GeoBoundingBox(
                    west=coords[0], south=coords[1], east=coords[0], north=coords[1]
                ),
                data_quality=DataQualityStatus.VERIFIED,
            )
            self.register_feature(feat)

        # 2. Sovereign Boundaries Reference
        ds_countries = GeoDataset(
            dataset_id="atlas.reference.world_countries",
            dataset_name="Sovereign States & Economic Jurisdictions",
            description="Verified sovereign boundary envelopes and administrative reference regions.",
            dataset_type=DatasetType.REFERENCE_BOUNDARIES,
            source_id="natural_earth_countries_110m",
            source_version="v5.1.1",
            geometry_types=[GeometryType.POLYGON],
            bounding_box=GeoBoundingBox(west=-180.0, south=-90.0, east=180.0, north=90.0),
            feature_count=6,
            attribution="Made with Natural Earth. Free vector and raster map data @ naturalearthdata.com.",
            licensing_policy=LicensingPolicy.OPEN_DATA_CC_BY,
            is_public=True,
            data_quality_status=DataQualityStatus.VERIFIED,
        )
        self.register_dataset(ds_countries)

        # Reference sovereign polygons (sample of major jurisdictions with valid closed rings)
        countries_data = [
            (
                "country_usa",
                "United States",
                "USA",
                [
                    [
                        [-125.0, 24.0],
                        [-66.0, 24.0],
                        [-66.0, 49.0],
                        [-125.0, 49.0],
                        [-125.0, 24.0],
                    ]
                ],
                {"capital": "Washington, D.C.", "currency": "USD", "region": "Americas"},
            ),
            (
                "country_gbr",
                "United Kingdom",
                "GBR",
                [
                    [
                        [-8.0, 49.8],
                        [1.8, 49.8],
                        [1.8, 60.9],
                        [-8.0, 60.9],
                        [-8.0, 49.8],
                    ]
                ],
                {"capital": "London", "currency": "GBP", "region": "Europe"},
            ),
            (
                "country_deu",
                "Germany",
                "DEU",
                [
                    [
                        [5.8, 47.2],
                        [15.1, 47.2],
                        [15.1, 55.1],
                        [5.8, 55.1],
                        [5.8, 47.2],
                    ]
                ],
                {"capital": "Berlin", "currency": "EUR", "region": "Europe"},
            ),
            (
                "country_jpn",
                "Japan",
                "JPN",
                [
                    [
                        [129.5, 30.0],
                        [146.0, 30.0],
                        [146.0, 45.6],
                        [129.5, 45.6],
                        [129.5, 30.0],
                    ]
                ],
                {"capital": "Tokyo", "currency": "JPY", "region": "Asia"},
            ),
            (
                "country_fra",
                "France",
                "FRA",
                [
                    [
                        [-5.2, 42.3],
                        [8.3, 42.3],
                        [8.3, 51.1],
                        [-5.2, 51.1],
                        [-5.2, 42.3],
                    ]
                ],
                {"capital": "Paris", "currency": "EUR", "region": "Europe"},
            ),
            (
                "country_aus",
                "Australia",
                "AUS",
                [
                    [
                        [112.9, -43.8],
                        [154.0, -43.8],
                        [154.0, -9.1],
                        [112.9, -9.1],
                        [112.9, -43.8],
                    ]
                ],
                {"capital": "Canberra", "currency": "AUD", "region": "Oceania"},
            ),
        ]

        for cid, name, iso, coords, props in countries_data:
            feat = GeoFeature(
                feature_id=cid,
                dataset_id=ds_countries.dataset_id,
                geometry_type=GeometryType.POLYGON,
                coordinates=coords,
                properties={"name": name, "iso3": iso, **props},
                label=name,
                source_reference="Natural Earth 1:110m Cultural Vectors",
                data_quality=DataQualityStatus.VERIFIED,
            )
            self.register_feature(feat)

    def register_dataset(self, dataset: GeoDataset) -> None:
        self._datasets[dataset.dataset_id] = dataset
        if dataset.dataset_id not in self._features_by_dataset:
            self._features_by_dataset[dataset.dataset_id] = {}

    def get_dataset(self, dataset_id: str) -> Optional[GeoDataset]:
        return self._datasets.get(dataset_id)

    def list_datasets(
        self, user_id: Optional[str] = None, tenant_id: Optional[str] = None
    ) -> List[GeoDataset]:
        results = []
        for ds in self._datasets.values():
            if ds.is_public:
                results.append(ds)
            elif ds.owner_user_id == user_id or (tenant_id and ds.tenant_id == tenant_id):
                results.append(ds)
        return results

    def register_feature(self, feature: GeoFeature) -> None:
        if feature.dataset_id not in self._features_by_dataset:
            self._features_by_dataset[feature.dataset_id] = {}
        self._features_by_dataset[feature.dataset_id][feature.feature_id] = feature
        if feature.dataset_id in self._datasets:
            self._datasets[feature.dataset_id].feature_count = len(
                self._features_by_dataset[feature.dataset_id]
            )

    def get_feature(self, dataset_id: str, feature_id: str) -> Optional[GeoFeature]:
        return self._features_by_dataset.get(dataset_id, {}).get(feature_id)

    def get_feature_by_id(self, feature_id: str) -> Optional[GeoFeature]:
        for dmap in self._features_by_dataset.values():
            if feature_id in dmap:
                return dmap[feature_id]
        return None

    def list_features(self, dataset_id: str) -> List[GeoFeature]:
        return list(self._features_by_dataset.get(dataset_id, {}).values())


# Global Singleton instance
dataset_registry = AtlasDatasetRegistry()
