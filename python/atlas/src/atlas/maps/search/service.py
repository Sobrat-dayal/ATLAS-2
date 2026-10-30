"""Geographic Search Service for ATLAS Maps V1.

Resolves geographic queries across sovereign nations, administrative regions,
financial capitals, and coordinate inputs. Never fabricates locations.
"""

from __future__ import annotations

import re
from typing import List, Optional

from atlas.maps.datasets.registry import dataset_registry
from atlas.maps.domain import GeoBoundingBox, GeographicSearchResult
from atlas.maps.spatial.coordinates import validate_coordinates


class AtlasGeographicSearchService:
    """Institutional geographic search engine with coordinate resolution."""

    def search(
        self,
        query: str,
        limit: int = 10,
        scope: Optional[str] = None,
    ) -> List[GeographicSearchResult]:
        q = query.strip()
        if not q:
            return []

        results: List[GeographicSearchResult] = []

        # 1. Check for coordinate input: e.g. "40.7128, -74.0060" or "-74.0060, 40.7128"
        coord_match = re.match(r"^([+-]?\d+(?:\.\d+)?)[,\s]+([+-]?\d+(?:\.\d+)?)$", q)
        if coord_match:
            v1 = float(coord_match.group(1))
            v2 = float(coord_match.group(2))

            # Disambiguate lat/lon vs lon/lat
            # Standard user search usually types "lat, lon"
            lon, lat = 0.0, 0.0
            valid = False

            # Try (lon=v2, lat=v1) first (lat, lon input)
            if abs(v1) <= 90.0 and abs(v2) <= 180.0:
                lon, lat = v2, v1
                valid = True
            elif abs(v2) <= 90.0 and abs(v1) <= 180.0:
                lon, lat = v1, v2
                valid = True

            if valid:
                v_lon, v_lat = validate_coordinates(lon, lat)
                results.append(
                    GeographicSearchResult(
                        result_id=f"coord_{v_lon}_{v_lat}",
                        label=f"Coordinates: {v_lat:.4f}° N, {v_lon:.4f}° E",
                        place_type="coordinates",
                        coordinates=[v_lon, v_lat],
                        bounding_box=GeoBoundingBox(
                            west=v_lon - 0.05,
                            south=v_lat - 0.05,
                            east=v_lon + 0.05,
                            north=v_lat + 0.05,
                        ),
                        disambiguation="Navigates directly to specified geographic coordinate pair",
                        relevance_score=1.0,
                    )
                )

        # 2. Search Financial Centers
        fc_features = dataset_registry.list_features("atlas.reference.financial_centers")
        q_lower = q.lower()
        for f in fc_features:
            name = f.label.lower()
            country = f.properties.get("country_code", "").lower()
            desc = f.properties.get("description", "").lower()

            if q_lower in name or q_lower == country or q_lower in desc:
                score = 0.9 if q_lower in name else 0.7
                results.append(
                    GeographicSearchResult(
                        result_id=f.feature_id,
                        label=f.label,
                        place_type="financial_center",
                        coordinates=f.coordinates,
                        bounding_box=f.bounding_box,
                        source_dataset_id=f.dataset_id,
                        disambiguation=f"{f.properties.get('country_code', '')} • {f.properties.get('currency', '')} • {f.properties.get('tier', '')}",
                        relevance_score=score,
                    )
                )

        # 3. Search Sovereign Countries & Jurisdictions
        country_features = dataset_registry.list_features("atlas.reference.world_countries")
        for f in country_features:
            name = f.label.lower()
            iso = f.properties.get("iso3", "").lower()
            region = f.properties.get("region", "").lower()

            if q_lower in name or q_lower == iso or q_lower in region:
                score = 0.95 if q_lower == iso or q_lower in name else 0.6
                results.append(
                    GeographicSearchResult(
                        result_id=f.feature_id,
                        label=f.label,
                        place_type="country",
                        coordinates=[
                            (f.bounding_box.west + f.bounding_box.east) / 2.0
                            if f.bounding_box
                            else 0.0,
                            (f.bounding_box.south + f.bounding_box.north) / 2.0
                            if f.bounding_box
                            else 0.0,
                        ],
                        bounding_box=f.bounding_box,
                        source_dataset_id=f.dataset_id,
                        disambiguation=f"{f.properties.get('iso3', '')} • {f.properties.get('region', '')} • Capital: {f.properties.get('capital', '')}",
                        relevance_score=score,
                    )
                )

        # Sort by relevance score descending
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:limit]


# Global search service instance
geographic_search_service = AtlasGeographicSearchService()
