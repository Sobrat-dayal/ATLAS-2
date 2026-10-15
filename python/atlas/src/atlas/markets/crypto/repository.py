"""Repository for ATLAS Cryptocurrency Markets V1 (Stage 60).

Handles deterministic catalog queries, filtering by base/quote/venue,
asset lookup, and keyset pagination.
"""

import base64
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .config import (
    DEFAULT_CRYPTO_ASSET_CATALOG,
    DEFAULT_CRYPTO_SPOT_CATALOG,
    DEFAULT_CRYPTO_VENUES,
    CanonicalCryptoAssetConfig,
    CanonicalCryptoSpotMarketConfig,
    CryptoVenueConfig,
)
from .models import (
    CryptoAssetItem,
    CryptoCoverageSummary,
    CryptoFilterOptionsResponse,
    CryptoVenueItem,
)


class CryptoMarketRepository:
    """Repository accessing canonical digital assets and spot market instruments."""

    def __init__(self, db_session: Optional[AsyncSession] = None) -> None:
        self.session = db_session
        self._assets: Dict[UUID, CanonicalCryptoAssetConfig] = {
            a.asset_entity_id: a for a in DEFAULT_CRYPTO_ASSET_CATALOG
        }
        self._asset_by_symbol: Dict[str, CanonicalCryptoAssetConfig] = {
            a.symbol.upper(): a for a in DEFAULT_CRYPTO_ASSET_CATALOG
        }
        self._spot_markets: Dict[UUID, CanonicalCryptoSpotMarketConfig] = {
            m.instrument_entity_id: m for m in DEFAULT_CRYPTO_SPOT_CATALOG
        }
        self._venues: Dict[str, CryptoVenueConfig] = dict(DEFAULT_CRYPTO_VENUES)

    def get_asset(self, identifier: UUID | str) -> Optional[CryptoAssetItem]:
        """Look up canonical digital asset by UUID or canonical symbol."""
        if isinstance(identifier, UUID):
            config = self._assets.get(identifier)
        else:
            config = self._asset_by_symbol.get(identifier.upper().strip())

        if not config:
            return None

        return CryptoAssetItem(
            asset_entity_id=config.asset_entity_id,
            symbol=config.symbol,
            name=config.name,
            asset_kind=config.asset_kind.value,
            network_id=config.network_id,
            contract_address=config.contract_address,
            token_standard=config.token_standard,
            decimals=config.decimals,
            description=config.description,
        )

    def list_assets(
        self,
        query: Optional[str] = None,
        asset_kind: Optional[str] = None,
        network: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> Tuple[List[CryptoAssetItem], int, Optional[str]]:
        """List and search digital assets with pagination."""
        all_assets = list(self._assets.values())

        if query:
            q = query.lower().strip()
            all_assets = [
                a
                for a in all_assets
                if q in a.symbol.lower()
                or q in a.name.lower()
                or (a.contract_address and q in a.contract_address.lower())
            ]

        if asset_kind:
            kind_clean = asset_kind.lower().strip()
            all_assets = [a for a in all_assets if a.asset_kind.value == kind_clean]

        if network:
            net_clean = network.lower().strip()
            all_assets = [a for a in all_assets if a.network_id and a.network_id == net_clean]

        # Deterministic sorting
        all_assets.sort(key=lambda a: (a.symbol, str(a.asset_entity_id)))

        total_count = len(all_assets)
        offset = 0
        if cursor:
            try:
                decoded = base64.b64decode(cursor.encode("ascii")).decode("utf-8")
                parts = decoded.split(":")
                if len(parts) == 2 and parts[0] == "asset_offset":
                    offset = int(parts[1])
            except Exception:
                offset = 0

        sliced = all_assets[offset : offset + limit]
        next_offset = offset + len(sliced)
        next_cursor = None
        if next_offset < total_count:
            next_cursor = base64.b64encode(f"asset_offset:{next_offset}".encode("utf-8")).decode(
                "ascii"
            )

        items = [
            CryptoAssetItem(
                asset_entity_id=a.asset_entity_id,
                symbol=a.symbol,
                name=a.name,
                asset_kind=a.asset_kind.value,
                network_id=a.network_id,
                contract_address=a.contract_address,
                token_standard=a.token_standard,
                decimals=a.decimals,
                description=a.description,
            )
            for a in sliced
        ]
        return items, total_count, next_cursor

    def get_spot_market(
        self, instrument_entity_id: UUID
    ) -> Optional[CanonicalCryptoSpotMarketConfig]:
        """Look up canonical spot market by instrument UUID."""
        return self._spot_markets.get(instrument_entity_id)

    def list_spot_markets(
        self,
        query: Optional[str] = None,
        base_asset: Optional[str] = None,
        quote_asset: Optional[str] = None,
        venue: Optional[str] = None,
        quote_asset_type: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> Tuple[List[CanonicalCryptoSpotMarketConfig], int, Optional[str]]:
        """List and search canonical spot markets with filtering and pagination."""
        markets = list(self._spot_markets.values())

        if query:
            q = query.lower().strip()
            markets = [
                m
                for m in markets
                if q in m.market_symbol.lower()
                or q in m.venue_market_symbol.lower()
                or q in m.base_asset_symbol.lower()
                or q in m.quote_asset_symbol.lower()
                or q in m.venue_name.lower()
                or any(q in alias.lower() for alias in m.provider_aliases)
            ]

        if base_asset:
            b = base_asset.upper().strip()
            markets = [m for m in markets if m.base_asset_symbol == b]

        if quote_asset:
            q_sym = quote_asset.upper().strip()
            markets = [m for m in markets if m.quote_asset_symbol == q_sym]

        if venue:
            v_clean = venue.lower().strip()
            markets = [
                m
                for m in markets
                if m.venue_id.lower() == v_clean or m.venue_name.lower() == v_clean
            ]

        if quote_asset_type:
            qt_clean = quote_asset_type.lower().strip()
            markets = [m for m in markets if m.quote_asset_type.value == qt_clean]

        # Deterministic sorting
        markets.sort(
            key=lambda m: (
                m.base_asset_symbol,
                m.quote_asset_symbol,
                m.venue_id,
                str(m.instrument_entity_id),
            )
        )

        total_count = len(markets)
        offset = 0
        if cursor:
            try:
                decoded = base64.b64decode(cursor.encode("ascii")).decode("utf-8")
                parts = decoded.split(":")
                if len(parts) == 2 and parts[0] == "spot_offset":
                    offset = int(parts[1])
            except Exception:
                offset = 0

        sliced = markets[offset : offset + limit]
        next_offset = offset + len(sliced)
        next_cursor = None
        if next_offset < total_count:
            next_cursor = base64.b64encode(f"spot_offset:{next_offset}".encode("utf-8")).decode(
                "ascii"
            )

        return sliced, total_count, next_cursor

    def get_filter_options(self) -> CryptoFilterOptionsResponse:
        """Derive active filter options from the configured spot market catalog."""
        base_assets = sorted(list({m.base_asset_symbol for m in self._spot_markets.values()}))
        quote_assets = sorted(list({m.quote_asset_symbol for m in self._spot_markets.values()}))
        quote_types = sorted(list({m.quote_asset_type.value for m in self._spot_markets.values()}))

        venue_items = [
            CryptoVenueItem(
                venue_id=v.venue_id,
                name=v.name,
                venue_type=v.venue_type,
                jurisdiction=v.jurisdiction,
            )
            for v in self._venues.values()
        ]
        venue_items.sort(key=lambda v: v.name)

        return CryptoFilterOptionsResponse(
            base_assets=base_assets,
            quote_assets=quote_assets,
            venues=venue_items,
            quote_asset_types=quote_types,
        )

    def get_coverage_summary(
        self,
        markets_with_quotes: int = 0,
        markets_with_bid_ask: int = 0,
        markets_with_volume: int = 0,
        markets_with_24h_change: int = 0,
    ) -> CryptoCoverageSummary:
        """Aggregate verified coverage counts for current catalog."""
        return CryptoCoverageSummary(
            total_assets=len(self._assets),
            total_spot_markets=len(self._spot_markets),
            total_venues=len(self._venues),
            markets_with_quotes=markets_with_quotes,
            markets_with_bid_ask=markets_with_bid_ask,
            markets_with_volume=markets_with_volume,
            markets_with_24h_change=markets_with_24h_change,
            scope="ATLAS_CONFIGURED_CRYPTO_SPOT",
        )
