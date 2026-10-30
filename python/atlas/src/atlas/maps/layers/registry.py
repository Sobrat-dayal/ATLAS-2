"""Map Layer Registry for ATLAS Maps V1.

Manages visual layer configurations, rendering styles, zoom thresholds,
categories, and permission constraints.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from atlas.maps.domain import GeometryType, MapLayerDefinition


class AtlasLayerRegistry:
    """Canonical registry of visual map layers."""

    def __init__(self):
        self._layers: Dict[str, MapLayerDefinition] = {}
        self._init_baseline_layers()

    def _init_baseline_layers(self) -> None:
        # 1. Global Financial Capitals
        self.register_layer(
            MapLayerDefinition(
                layer_id="atlas.layer.financial_centers",
                dataset_id="atlas.reference.financial_centers",
                layer_name="Global Financial Centers & Central Banks",
                geometry_type=GeometryType.POINT,
                source_type="vector",
                style_definition={
                    "type": "circle",
                    "paint": {
                        "circle-radius": 6,
                        "circle-color": "#38BDF8",
                        "circle-stroke-width": 2,
                        "circle-stroke-color": "#0284C7",
                    },
                },
                default_visibility=True,
                default_opacity=1.0,
                min_zoom=0.0,
                max_zoom=20.0,
                display_order=200,
                category="Financial Centers",
                license_reference="Open Data CC BY 4.0",
            )
        )

        # 2. Sovereign Boundaries
        self.register_layer(
            MapLayerDefinition(
                layer_id="atlas.layer.world_boundaries",
                dataset_id="atlas.reference.world_countries",
                layer_name="Sovereign States & Jurisdictions",
                geometry_type=GeometryType.POLYGON,
                source_type="vector",
                style_definition={
                    "type": "fill",
                    "paint": {
                        "fill-color": "#3B82F6",
                        "fill-opacity": 0.15,
                        "fill-outline-color": "#60A5FA",
                    },
                },
                default_visibility=True,
                default_opacity=0.8,
                min_zoom=0.0,
                max_zoom=20.0,
                display_order=100,
                category="Boundaries",
                license_reference="Natural Earth Public Domain / CC BY",
            )
        )

    def register_layer(self, layer: MapLayerDefinition) -> None:
        self._layers[layer.layer_id] = layer

    def get_layer(self, layer_id: str) -> Optional[MapLayerDefinition]:
        return self._layers.get(layer_id)

    def list_layers(self) -> List[MapLayerDefinition]:
        return sorted(self._layers.values(), key=lambda layer: layer.display_order)


# Global Singleton instance
layer_registry = AtlasLayerRegistry()
