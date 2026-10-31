"""Canonical Physical Infrastructure Asset Registry (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from atlas.maps.infrastructure.assets.history import get_asset_state_at
from atlas.maps.infrastructure.capacity.units import convert_to_canonical_unit
from atlas.maps.infrastructure.domain import (
    CapacityMetric,
    EntityRole,
    InfrastructureAsset,
    InfrastructureAssetType,
    InfrastructureSector,
    InfrastructureStatus,
    LicensingClass,
)
from atlas.maps.infrastructure.errors import (
    AssetNotFoundError,
    CommercialUseProhibitedError,
    EntitlementRevokedError,
    SensitiveAssetAccessDeniedError,
)


class InfrastructureAssetRegistry:
    """Registry indexing global physical infrastructure assets with governance and security checks."""

    def __init__(self) -> None:
        self._assets: Dict[str, InfrastructureAsset] = {}
        self._revoked_source_ids: Set[str] = set()

    def register_asset(self, asset: InfrastructureAsset) -> None:
        """Register or update an infrastructure asset."""
        self._assets[asset.asset_id] = asset

    def revoke_source_entitlement(self, source_id: str) -> None:
        """Revoke dataset entitlement, hiding records and derived analytics (Fixture N)."""
        self._revoked_source_ids.add(source_id)

    def restore_source_entitlement(self, source_id: str) -> None:
        """Restore dataset entitlement."""
        self._revoked_source_ids.discard(source_id)

    def get_asset(
        self,
        asset_id: str,
        actor_tenant_id: Optional[str] = None,
        is_commercial_context: bool = False,
    ) -> InfrastructureAsset:
        """Retrieve an asset by ID with tenant security and licensing validation."""
        asset = self._assets.get(asset_id)
        if not asset:
            raise AssetNotFoundError(asset_id)

        # Entitlement check (Fixture N)
        if asset.source_id in self._revoked_source_ids:
            raise EntitlementRevokedError(asset.source_id)

        # Tenant isolation check (Fixture L)
        if asset.is_private:
            if not actor_tenant_id or asset.tenant_id != actor_tenant_id:
                raise SensitiveAssetAccessDeniedError(asset_id, actor_tenant_id)

        # Licensing restriction check (Fixture M)
        if is_commercial_context and asset.source_license == LicensingClass.NON_COMMERCIAL_ONLY:
            raise CommercialUseProhibitedError(asset.source_id)

        return asset

    def list_assets(
        self,
        sector: Optional[InfrastructureSector] = None,
        asset_type: Optional[InfrastructureAssetType] = None,
        country: Optional[str] = None,
        company_id: Optional[str] = None,
        operator_id: Optional[str] = None,
        status: Optional[InfrastructureStatus] = None,
        min_capacity: Optional[float] = None,
        max_capacity: Optional[float] = None,
        capacity_metric: Optional[CapacityMetric] = None,
        as_of_date: Optional[str] = None,
        bbox: Optional[Tuple[float, float, float, float]] = None,  # (min_lng, min_lat, max_lng, max_lat)
        actor_tenant_id: Optional[str] = None,
        is_commercial_context: bool = False,
        limit: int = 200,
    ) -> List[InfrastructureAsset]:
        """Query assets with multi-parameter filtering, licensing checks, and tenant boundaries."""
        results: List[InfrastructureAsset] = []

        for asset in self._assets.values():
            # Check revoked source (Fixture N)
            if asset.source_id in self._revoked_source_ids:
                continue

            # Check tenant isolation (Fixture L)
            if asset.is_private:
                if not actor_tenant_id or asset.tenant_id != actor_tenant_id:
                    continue

            # Check commercial licensing (Fixture M)
            if is_commercial_context and asset.source_license == LicensingClass.NON_COMMERCIAL_ONLY:
                continue

            # Sector filter
            if sector and asset.sector != sector:
                continue

            # Asset type filter
            if asset_type and asset.asset_type != asset_type:
                continue

            # Country filter
            if country and asset.country != country:
                continue

            # Company filter (Owner or general link)
            if company_id:
                has_company = any(
                    link.entity_id == company_id
                    for link in asset.entity_links
                )
                if not has_company:
                    continue

            # Operator filter
            if operator_id:
                has_operator = any(
                    link.entity_id == operator_id and link.role == EntityRole.OPERATOR
                    for link in asset.entity_links
                )
                if not has_operator:
                    continue

            # Historical status filter (Fixture J)
            current_or_historical_status = (
                get_asset_state_at(asset, as_of_date) if as_of_date else asset.status
            )
            if status and current_or_historical_status != status:
                continue

            # Capacity filter
            if min_capacity is not None or max_capacity is not None:
                matches_capacity = False
                for rec in asset.capacity_records:
                    if capacity_metric:
                        c_rec_metric, val = convert_to_canonical_unit(rec.metric, rec.value)
                        c_target_metric, _ = convert_to_canonical_unit(capacity_metric, 1.0)
                        if c_rec_metric != c_target_metric:
                            continue
                    else:
                        val = rec.value

                    if min_capacity is not None and val < min_capacity:
                        continue
                    if max_capacity is not None and val > max_capacity:
                        continue

                    matches_capacity = True
                    break

                if not matches_capacity and (min_capacity is not None or max_capacity is not None):
                    continue

            # BBox filter
            if bbox:
                min_lng, min_lat, max_lng, max_lat = bbox
                if not (min_lng <= asset.longitude <= max_lng and min_lat <= asset.latitude <= max_lat):
                    continue

            results.append(asset)
            if len(results) >= limit:
                break

        return results

    def clear(self) -> None:
        self._assets.clear()
        self._revoked_source_ids.clear()


asset_registry = InfrastructureAssetRegistry()
