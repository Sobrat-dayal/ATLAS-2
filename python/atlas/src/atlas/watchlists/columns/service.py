"""Service layer for Watchlist Columns and Preferences (Stage 77).

Orchestrates:
- Column registry discovery
- Column configuration validation and normalization
- Per-watchlist preference persistence and optimistic concurrency control
- Batched canonical projection of watchlist rows into typed cell values
- Safe multi-asset sorting with tie breaking and missing-values-last semantics
"""

import datetime
import logging
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from atlas.watchlists.enrichment import WatchlistEnrichmentService, is_enrichment_column
from atlas.watchlists.enrichment.planner import EnrichmentItemContext
from atlas.watchlists.models import WatchlistItem
from atlas.watchlists.repository import WatchlistRepository
from atlas.watchlists.service import WatchlistService

from .errors import (
    ColumnNotFoundError,
)
from .registry import (
    get_column_definition,
    get_default_column_config,
    list_all_column_definitions,
    normalize_and_validate_column_config,
)
from .repository import WatchlistColumnPreferenceRepository
from .schemas import (
    WatchlistColumnConfigV1,
    WatchlistColumnDefinitionResponse,
    WatchlistColumnPreferencesResponse,
    WatchlistColumnPreferencesUpdateRequest,
    WatchlistRowCellValue,
    WatchlistRowProjection,
    WatchlistRowsResponse,
)
from .sorting import WatchlistSortingEngine

logger = logging.getLogger(__name__)


class WatchlistColumnService:
    """Domain service for Stage 77 Advanced Watchlist Columns."""

    def __init__(
        self,
        preference_repository: WatchlistColumnPreferenceRepository,
        watchlist_repository: WatchlistRepository,
        watchlist_service: WatchlistService,
    ):
        self.pref_repo = preference_repository
        self.watchlist_repo = watchlist_repository
        self.watchlist_service = watchlist_service

    # =========================================================================
    # Registry Discovery
    # =========================================================================

    def list_column_definitions(self) -> List[WatchlistColumnDefinitionResponse]:
        """Returns the full catalog of approved column definitions."""
        defs = list_all_column_definitions()
        return [WatchlistColumnDefinitionResponse(**d.to_dict()) for d in defs]

    def get_column_definition(self, column_id: str) -> WatchlistColumnDefinitionResponse:
        """Returns a single approved column definition or raises ColumnNotFoundError."""
        col_def = get_column_definition(column_id)
        if col_def is None:
            raise ColumnNotFoundError(f"Column '{column_id}' is not in the column registry.")
        return WatchlistColumnDefinitionResponse(**col_def.to_dict())

    # =========================================================================
    # Preferences Management
    # =========================================================================

    async def get_preferences(
        self, watchlist_id: UUID, owner_user_id: UUID
    ) -> WatchlistColumnPreferencesResponse:
        """Retrieves column preferences for a watchlist, or returns default config if none saved."""
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            from atlas.watchlists.errors import WatchlistNotFoundError

            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        pref = await self.pref_repo.get_by_watchlist_id(watchlist_id)
        if pref is None:
            default_config = get_default_column_config()
            now = datetime.datetime.now(datetime.timezone.utc)
            return WatchlistColumnPreferencesResponse(
                watchlist_id=watchlist_id,
                configuration_schema_version=1,
                revision=0,
                configuration=WatchlistColumnConfigV1(**default_config),
                is_default=True,
                created_at=watchlist.created_at or now,
                updated_at=watchlist.updated_at or now,
            )

        config_data = pref.configuration_jsonb
        return WatchlistColumnPreferencesResponse(
            watchlist_id=pref.watchlist_id,
            configuration_schema_version=pref.configuration_schema_version,
            revision=pref.revision,
            configuration=WatchlistColumnConfigV1(**config_data),
            is_default=False,
            created_at=pref.created_at,
            updated_at=pref.updated_at,
        )

    async def update_preferences(
        self,
        watchlist_id: UUID,
        owner_user_id: UUID,
        request: WatchlistColumnPreferencesUpdateRequest,
    ) -> WatchlistColumnPreferencesResponse:
        """Updates column preferences with validation, normalization, and revision protection."""
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            from atlas.watchlists.errors import WatchlistNotFoundError

            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        # Validate and normalize payload against registry rules
        normalized = normalize_and_validate_column_config(request.configuration.model_dump())

        # Persist atomically
        saved = await self.pref_repo.save_preferences(
            watchlist_id=watchlist_id,
            configuration=normalized,
            expected_revision=request.expected_revision,
        )

        return WatchlistColumnPreferencesResponse(
            watchlist_id=saved.watchlist_id,
            configuration_schema_version=saved.configuration_schema_version,
            revision=saved.revision,
            configuration=WatchlistColumnConfigV1(**saved.configuration_jsonb),
            is_default=False,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def reset_preferences(
        self, watchlist_id: UUID, owner_user_id: UUID
    ) -> WatchlistColumnPreferencesResponse:
        """Resets column preferences for a watchlist back to default."""
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            from atlas.watchlists.errors import WatchlistNotFoundError

            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        await self.pref_repo.reset_preferences(watchlist_id)
        default_config = get_default_column_config()
        now = datetime.datetime.now(datetime.timezone.utc)
        return WatchlistColumnPreferencesResponse(
            watchlist_id=watchlist_id,
            configuration_schema_version=1,
            revision=0,
            configuration=WatchlistColumnConfigV1(**default_config),
            is_default=True,
            created_at=now,
            updated_at=now,
        )

    # =========================================================================
    # Data Projection and Sorting
    # =========================================================================

    async def get_projected_rows(
        self,
        watchlist_id: UUID,
        owner_user_id: UUID,
        page: int = 1,
        page_size: int = 50,
        sort_column_id: Optional[str] = None,
        sort_direction: Optional[str] = None,
    ) -> WatchlistRowsResponse:
        """
        Projects watchlist rows into typed cell values for selected columns.

        Guarantees:
        - Whole-watchlist sorting: Sort operates over complete authorized items (up to 250),
          never misleadingly sorting only the current pagination page.
        - Zero extra provider requests: Reuses Stage 76's batched resolver.
        - Safe missing-values-last and deterministic tie-breaker sorting.
        """
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            from atlas.watchlists.errors import WatchlistNotFoundError

            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        # 1. Fetch active preferences to know selected columns and default sort
        pref_response = await self.get_preferences(watchlist_id, owner_user_id)
        config = pref_response.configuration

        # Effective sort configuration
        effective_sort_col = sort_column_id or config.sort.column_id
        effective_sort_dir = sort_direction or config.sort.direction
        if effective_sort_dir not in ("asc", "desc"):
            effective_sort_dir = None
            effective_sort_col = None

        # 2. Fetch all watchlist membership items to allow complete-dataset sorting
        # (bounded to 250 items max by Stage 76 business rule)
        total_items = await self.watchlist_repo.count_items(watchlist_id)
        all_items: List[WatchlistItem] = await self.watchlist_repo.list_items(
            watchlist_id, offset=0, limit=250
        )

        # 3. Batch resolve canonical metadata and quotes using existing WatchlistService
        resolved_items = await self.watchlist_service._resolve_items_metadata_and_quotes(all_items)

        # 4. Project each item into typed cell values across all registered columns
        # (ensuring all needed fields for sorting and display are computed)
        selected_columns = config.visible_column_ids
        if "instrument.symbol" not in selected_columns:
            selected_columns = ["instrument.symbol"] + [
                c for c in selected_columns if c != "instrument.symbol"
            ]

        projections: List[WatchlistRowProjection] = []
        for item_resp in resolved_items:
            values: Dict[str, WatchlistRowCellValue] = {}

            # Symbol
            values["instrument.symbol"] = WatchlistRowCellValue(
                status="AVAILABLE",
                value=item_resp.symbol,
            )

            # Name
            values["instrument.name"] = WatchlistRowCellValue(
                status="AVAILABLE",
                value=item_resp.display_name or item_resp.canonical_name,
            )

            # Asset Class
            values["instrument.asset_class"] = WatchlistRowCellValue(
                status="AVAILABLE",
                value=item_resp.asset_class,
            )

            # Subtype
            values["instrument.subtype"] = WatchlistRowCellValue(
                status="AVAILABLE",
                value=item_resp.asset_class.capitalize() if item_resp.asset_class else "Equity",
            )

            # Identifier
            values["instrument.identifier"] = WatchlistRowCellValue(
                status="AVAILABLE",
                value=item_resp.symbol,
            )

            # Venue
            if item_resp.venue:
                values["market.venue"] = WatchlistRowCellValue(
                    status="AVAILABLE",
                    value=item_resp.venue,
                )
            else:
                values["market.venue"] = WatchlistRowCellValue(
                    status="NOT_APPLICABLE",
                    value=None,
                    reason="Venue unspecified",
                )

            # Currency
            values["market.currency"] = WatchlistRowCellValue(
                status="AVAILABLE",
                value=item_resp.quote_currency or "USD",
                unit=item_resp.quote_currency or "USD",
            )

            # Country
            values["market.listing_country"] = WatchlistRowCellValue(
                status="AVAILABLE",
                value="US",  # Default canonical listing country
            )

            # Latest Measure
            if item_resp.is_quote_available and item_resp.last_price is not None:
                values["quote.latest_measure"] = WatchlistRowCellValue(
                    status="AVAILABLE",
                    value=item_resp.last_price,
                    unit=item_resp.quote_currency or "USD",
                    measure_kind=item_resp.quote_measure or "Last",
                    observed_at=item_resp.source_timestamp,
                )
            else:
                values["quote.latest_measure"] = WatchlistRowCellValue(
                    status="UNAVAILABLE",
                    value=None,
                    reason="Quote observation unavailable",
                )

            # Change
            if item_resp.is_quote_available and item_resp.percentage_change is not None:
                values["quote.change"] = WatchlistRowCellValue(
                    status="AVAILABLE",
                    value=item_resp.percentage_change,
                    unit="%",
                    observed_at=item_resp.source_timestamp,
                )
            else:
                values["quote.change"] = WatchlistRowCellValue(
                    status="UNAVAILABLE",
                    value=None,
                    reason="Reference close unavailable",
                )

            # Quote Kind
            if item_resp.is_quote_available and item_resp.quote_measure:
                values["quote.kind"] = WatchlistRowCellValue(
                    status="AVAILABLE",
                    value=item_resp.quote_measure,
                )
            else:
                values["quote.kind"] = WatchlistRowCellValue(
                    status="UNAVAILABLE",
                    value=None,
                )

            # As Of
            if item_resp.is_quote_available and item_resp.source_timestamp:
                values["quote.as_of"] = WatchlistRowCellValue(
                    status="AVAILABLE",
                    value=item_resp.source_timestamp,
                    observed_at=item_resp.source_timestamp,
                )
            else:
                values["quote.as_of"] = WatchlistRowCellValue(
                    status="UNAVAILABLE",
                    value=None,
                )

            # Freshness
            values["quality.freshness"] = WatchlistRowCellValue(
                status="AVAILABLE",
                value=item_resp.freshness_status or "unavailable",
            )

            # Source
            values["quality.source"] = WatchlistRowCellValue(
                status="AVAILABLE",
                value=item_resp.provider or "CANONICAL",
            )

            proj = WatchlistRowProjection(
                item_id=item_resp.id,
                instrument_entity_id=item_resp.instrument_entity_id,
                market_series_id=item_resp.market_series_id,
                manual_position=item_resp.position,
                values=values,
                has_company_page=item_resp.has_company_page,
                issuer_id=item_resp.issuer_entity_id,
            )
            projections.append(proj)

        # Stage 79: Batch Enrich Projected Rows
        enrichment_cols_needed = [
            c
            for c in (
                set(selected_columns)
                | ({effective_sort_col} if effective_sort_col else set())
            )
            if is_enrichment_column(c)
        ]
        if enrichment_cols_needed and all_items:
            session = getattr(self.watchlist_repo, "session", None)
            enrichment_service = WatchlistEnrichmentService(session=session)

            enrich_items = []
            quotes_map = {}
            for item_resp in resolved_items:
                inst_id = item_resp.instrument_entity_id
                if item_resp.last_price is not None:
                    try:
                        quotes_map[inst_id] = Decimal(str(item_resp.last_price))
                    except Exception:
                        pass
                enrich_items.append(
                    EnrichmentItemContext(
                        item_id=item_resp.id,
                        instrument_id=inst_id,
                        market_series_id=item_resp.market_series_id,
                        asset_class=item_resp.asset_class or "equity",
                        quote_currency=item_resp.quote_currency or "USD",
                        company_id=item_resp.issuer_entity_id,
                    )
                )

            enrich_results = await enrichment_service.batch_enrich_items(
                items=enrich_items,
                requested_column_ids=enrichment_cols_needed,
                quotes_map=quotes_map,
            )

            for proj in projections:
                item_enriched = enrich_results.get(proj.item_id, {})
                for col_id, enrich_val in item_enriched.items():
                    proj.values[col_id] = WatchlistRowCellValue(**enrich_val.to_row_cell_dict())

        # 5. Apply sorting across full dataset if sort is requested
        incompatible_detected = False
        is_sorted = False
        if effective_sort_col and effective_sort_dir:
            sorted_rows, incompatible_detected = WatchlistSortingEngine.sort_rows(
                rows=projections,
                sort_column_id=effective_sort_col,
                direction=effective_sort_dir,
            )
            projections = sorted_rows
            is_sorted = True

        # 6. Paginate sorted rows
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paged_rows = projections[start_idx:end_idx]

        return WatchlistRowsResponse(
            watchlist_id=watchlist_id,
            membership_revision=watchlist.revision,
            selected_columns=selected_columns,
            total_items=total_items,
            page=page,
            page_size=page_size,
            rows=paged_rows,
            is_sorted=is_sorted,
            sort_column_id=effective_sort_col,
            sort_direction=effective_sort_dir,
            incompatible_units_detected=incompatible_detected,
        )
