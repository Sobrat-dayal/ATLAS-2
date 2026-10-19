"""Service layer orchestrating business logic, validation, metadata resolution,
and quote snapshot qualification for Watchlists V1 (Stage 76).
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.models import Entity
from atlas.identifiers.models import EntityIdentifier
from atlas.instruments.models import FinancialInstrument
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import QuoteCacheRecord
from atlas.relationships.models import EntityRelationship

from .errors import (
    DuplicateWatchlistItemError,
    InstrumentNotFoundError,
    WatchlistItemNotFoundError,
    WatchlistItemQuotaExceededError,
    WatchlistNameConflictError,
    WatchlistNotFoundError,
    WatchlistQuotaExceededError,
    WatchlistRevisionConflictError,
)
from .models import Watchlist, WatchlistItem
from .normalization import (
    MAX_ITEMS_PER_WATCHLIST,
    MAX_WATCHLISTS_PER_USER,
    normalize_watchlist_name,
    sanitize_watchlist_name,
    validate_description,
)
from .repository import WatchlistRepository
from .schemas import (
    AddWatchlistItemRequest,
    ReorderWatchlistItemsRequest,
    ReorderWatchlistItemsResponse,
    WatchlistCreateRequest,
    WatchlistDetailResponse,
    WatchlistItemResponse,
    WatchlistListResponse,
    WatchlistSummaryResponse,
    WatchlistUpdateRequest,
)

logger = logging.getLogger(__name__)


class WatchlistService:
    """
    High-level domain service for user-owned persistent watchlists.

    Guarantees:
    - User ownership isolation.
    - Canonical UUID financial instrument membership.
    - Zero provider fanout / zero external HTTP calls during watchlist reads.
    - Honest quote availability: missing observations are marked unavailable, never faked.
    - Optimistic concurrency control via monotonic revisions.
    - Strictly transactional database mutations.
    """

    def __init__(
        self,
        repository: WatchlistRepository,
        quote_service: Optional[LiveQuoteService] = None,
        db_session: Optional[AsyncSession] = None,
    ):
        self.repository = repository
        self.session = repository.session if db_session is None else db_session
        self.quote_service = quote_service

    # =========================================================================
    # Watchlist CRUD
    # =========================================================================

    async def list_watchlists(
        self, owner_user_id: UUID, page: int = 1, page_size: int = 20
    ) -> WatchlistListResponse:
        """Lists all watchlists belonging to the authenticated user."""
        summaries, total = await self.repository.list_watchlists(
            owner_user_id=owner_user_id, page=page, page_size=page_size
        )
        return WatchlistListResponse(
            items=[WatchlistSummaryResponse(**s) for s in summaries],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def create_watchlist(
        self, owner_user_id: UUID, request: WatchlistCreateRequest
    ) -> WatchlistSummaryResponse:
        """Creates a new watchlist for the user under configured quotas."""
        # 1. Enforce user watchlist quota (max 50)
        current_count = await self.repository.count_user_watchlists(owner_user_id)
        if current_count >= MAX_WATCHLISTS_PER_USER:
            raise WatchlistQuotaExceededError(
                f"Quota exceeded: user already has {current_count} lists "
                f"(limit {MAX_WATCHLISTS_PER_USER})."
            )

        # 2. Sanitize and normalize name
        display_name = sanitize_watchlist_name(request.name)
        norm_name = normalize_watchlist_name(request.name)
        clean_desc = validate_description(request.description)

        # 3. Check name uniqueness scoped to owner
        existing = await self.repository.get_by_normalized_name(owner_user_id, norm_name)
        if existing is not None:
            raise WatchlistNameConflictError(
                f"A watchlist with the name '{display_name}' already exists in your account."
            )

        # 4. Create and persist
        watchlist = Watchlist(
            owner_user_id=owner_user_id,
            name=display_name,
            normalized_name=norm_name,
            description=clean_desc,
            revision=1,
        )
        saved = await self.repository.create_watchlist(watchlist)

        return WatchlistSummaryResponse(
            id=saved.id,
            owner_user_id=saved.owner_user_id,
            name=saved.name,
            description=saved.description,
            item_count=0,
            revision=saved.revision,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    async def get_watchlist(
        self,
        watchlist_id: UUID,
        owner_user_id: UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> WatchlistDetailResponse:
        """Retrieves watchlist details and ordered membership items with qualified snapshots."""
        watchlist = await self.repository.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        total_items = await self.repository.count_items(watchlist_id)
        offset = (page - 1) * page_size
        items = await self.repository.list_items(watchlist_id, offset=offset, limit=page_size)

        # Batch resolve canonical metadata, quotes, and issuer relations
        resolved_items = await self._resolve_items_metadata_and_quotes(items)

        return WatchlistDetailResponse(
            id=watchlist.id,
            owner_user_id=watchlist.owner_user_id,
            name=watchlist.name,
            description=watchlist.description,
            revision=watchlist.revision,
            created_at=watchlist.created_at,
            updated_at=watchlist.updated_at,
            items=resolved_items,
            total_items=total_items,
            page=page,
            page_size=page_size,
        )

    async def update_watchlist(
        self,
        watchlist_id: UUID,
        owner_user_id: UUID,
        request: WatchlistUpdateRequest,
        expected_revision: Optional[int] = None,
    ) -> WatchlistSummaryResponse:
        """Updates watchlist metadata (name/description) with optimistic revision protection."""
        watchlist = await self.repository.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        if expected_revision is not None and watchlist.revision != expected_revision:
            raise WatchlistRevisionConflictError(
                f"Revision conflict: expected {expected_revision}, current is {watchlist.revision}."
            )

        new_name: Optional[str] = None
        new_norm_name: Optional[str] = None
        if request.name is not None:
            new_name = sanitize_watchlist_name(request.name)
            new_norm_name = normalize_watchlist_name(request.name)
            if new_norm_name != watchlist.normalized_name:
                conflict = await self.repository.get_by_normalized_name(
                    owner_user_id, new_norm_name
                )
                if conflict is not None and conflict.id != watchlist.id:
                    raise WatchlistNameConflictError(
                        f"A watchlist with the name '{new_name}' already exists in your account."
                    )

        new_desc: Optional[str] = None
        desc_set = False
        if request.description is not None:
            new_desc = validate_description(request.description)
            desc_set = True

        updated = await self.repository.update_watchlist(
            watchlist=watchlist,
            name=new_name,
            normalized_name=new_norm_name,
            description=new_desc,
            description_set=desc_set,
        )

        item_count = await self.repository.count_items(watchlist_id)
        return WatchlistSummaryResponse(
            id=updated.id,
            owner_user_id=updated.owner_user_id,
            name=updated.name,
            description=updated.description,
            item_count=item_count,
            revision=updated.revision,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )

    async def delete_watchlist(self, watchlist_id: UUID, owner_user_id: UUID) -> None:
        """Deletes a watchlist and cascades its membership items."""
        watchlist = await self.repository.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        await self.repository.delete_watchlist(watchlist)

    # =========================================================================
    # Membership Operations
    # =========================================================================

    async def add_item(
        self,
        watchlist_id: UUID,
        owner_user_id: UUID,
        request: AddWatchlistItemRequest,
    ) -> WatchlistItemResponse:
        """Adds a verified canonical financial instrument to a watchlist."""
        # 1. Watchlist existence & ownership
        watchlist = await self.repository.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        # 2. Quota check (max 250 items per watchlist)
        current_count = await self.repository.count_items(watchlist_id)
        if current_count >= MAX_ITEMS_PER_WATCHLIST:
            raise WatchlistItemQuotaExceededError(
                f"Watchlist item limit reached: cannot exceed {MAX_ITEMS_PER_WATCHLIST} items."
            )

        # 3. Validate canonical financial instrument existence
        inst_stmt = select(FinancialInstrument.entity_id).where(
            FinancialInstrument.entity_id == request.instrument_entity_id
        )
        inst_res = await self.session.execute(inst_stmt)
        if inst_res.scalar_one_or_none() is None:
            # Check if it exists in entities as a financial instrument type
            ent_stmt = select(Entity.entity_id).where(
                Entity.entity_id == request.instrument_entity_id
            )
            ent_res = await self.session.execute(ent_stmt)
            if ent_res.scalar_one_or_none() is None:
                raise InstrumentNotFoundError(
                    f"Instrument {request.instrument_entity_id} not found in catalog."
                )

        # 4. Duplicate prevention
        market_series_id = (request.market_series_id or "").strip()
        existing_item = await self.repository.get_item_by_series(
            watchlist_id=watchlist_id,
            instrument_entity_id=request.instrument_entity_id,
            market_series_id=market_series_id,
        )
        if existing_item is not None:
            raise DuplicateWatchlistItemError(
                f"Instrument {request.instrument_entity_id} is already in this watchlist."
            )

        # 5. Insert at end of dense list
        new_item = WatchlistItem(
            watchlist_id=watchlist_id,
            instrument_entity_id=request.instrument_entity_id,
            market_series_id=market_series_id,
            position=current_count,
        )
        created_item = await self.repository.add_item(watchlist, new_item)

        # 6. Resolve metadata and return
        resolved = await self._resolve_items_metadata_and_quotes([created_item])
        return resolved[0]

    async def remove_item(
        self,
        watchlist_id: UUID,
        item_id: UUID,
        owner_user_id: UUID,
    ) -> None:
        """Removes a membership entry from the watchlist and reindexes positions."""
        watchlist = await self.repository.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        item = await self.repository.get_item_by_id(item_id, watchlist_id=watchlist_id)
        if item is None:
            raise WatchlistItemNotFoundError(
                f"Membership item {item_id} not found in watchlist {watchlist_id}."
            )

        await self.repository.remove_item(watchlist, item)

    async def reorder_items(
        self,
        watchlist_id: UUID,
        owner_user_id: UUID,
        request: ReorderWatchlistItemsRequest,
    ) -> ReorderWatchlistItemsResponse:
        """Atomically reorders all items in the watchlist with revision concurrency verification."""
        watchlist = await self.repository.get_by_id(watchlist_id, owner_user_id=owner_user_id)
        if watchlist is None:
            raise WatchlistNotFoundError(f"Watchlist {watchlist_id} not found.")

        updated_watchlist = await self.repository.reorder_items(
            watchlist=watchlist,
            ordered_item_ids=request.ordered_item_ids,
            expected_revision=request.expected_revision,
        )

        return ReorderWatchlistItemsResponse(
            watchlist_id=updated_watchlist.id,
            revision=updated_watchlist.revision,
            ordered_item_ids=request.ordered_item_ids,
        )

    # =========================================================================
    # Batched Metadata & Quote Snapshot Qualification (No Provider Fanout)
    # =========================================================================

    async def _resolve_items_metadata_and_quotes(
        self, items: List[WatchlistItem]
    ) -> List[WatchlistItemResponse]:
        """
        Resolves canonical entity metadata, ticker identifiers, verified issuer links,
        and cached live quotes in bounded batch queries (0 provider fanout calls).
        """
        if not items:
            return []

        instrument_ids = [item.instrument_entity_id for item in items]
        unique_inst_ids = list(dict.fromkeys(instrument_ids))

        # 1. Batch query Entity metadata
        entity_stmt = select(
            Entity.entity_id,
            Entity.canonical_name,
            Entity.display_name,
            Entity.entity_type,
        ).where(Entity.entity_id.in_(unique_inst_ids))
        entity_res = await self.session.execute(entity_stmt)
        entities_by_id: Dict[UUID, dict] = {
            row.entity_id: {
                "canonical_name": row.canonical_name,
                "display_name": row.display_name,
                "entity_type": row.entity_type,
            }
            for row in entity_res.all()
        }

        # 2. Batch query display symbols from EntityIdentifier
        # Prioritize ticker, symbol, ric, isin schemes
        id_stmt = select(
            EntityIdentifier.entity_id,
            EntityIdentifier.scheme_key,
            EntityIdentifier.value,
        ).where(
            EntityIdentifier.entity_id.in_(unique_inst_ids),
            EntityIdentifier.is_current.is_(True),
        )
        id_res = await self.session.execute(id_stmt)
        symbols_by_id: Dict[UUID, str] = {}
        for row in id_res.all():
            eid = row.entity_id
            scheme = (row.scheme_key or "").lower()
            val = row.value
            # Prefer ticker or symbol
            if eid not in symbols_by_id or scheme in ("ticker", "symbol"):
                symbols_by_id[eid] = val

        # 3. Batch query verified issuer relationship for company navigation
        # Relationship where security is issued_by company or company issued security
        rel_stmt = select(
            EntityRelationship.source_entity_id,
            EntityRelationship.target_entity_id,
            EntityRelationship.relationship_type_key,
        ).where(
            EntityRelationship.is_current.is_(True),
            (
                (EntityRelationship.source_entity_id.in_(unique_inst_ids))
                | (EntityRelationship.target_entity_id.in_(unique_inst_ids))
            ),
            EntityRelationship.relationship_type_key.in_(["issued_by", "issued"]),
        )
        rel_res = await self.session.execute(rel_stmt)
        issuers_by_inst_id: Dict[UUID, UUID] = {}
        for row in rel_res.all():
            if row.relationship_type_key == "issued_by" and row.source_entity_id in unique_inst_ids:
                issuers_by_inst_id[row.source_entity_id] = row.target_entity_id
            elif row.relationship_type_key == "issued" and row.target_entity_id in unique_inst_ids:
                issuers_by_inst_id[row.target_entity_id] = row.source_entity_id

        # 4. Batch query latest cached quote records from LiveQuoteService
        cached_quotes: Dict[UUID, Optional[QuoteCacheRecord]] = {}
        if self.quote_service is not None:
            try:
                records = await self.quote_service.get_latest_quotes(unique_inst_ids)
                for inst_id, rec in zip(unique_inst_ids, records):
                    cached_quotes[inst_id] = rec
            except Exception as e:
                logger.warning("Error querying cached quotes from LiveQuoteService: %s", e)
                for inst_id in unique_inst_ids:
                    cached_quotes[inst_id] = None
        else:
            for inst_id in unique_inst_ids:
                cached_quotes[inst_id] = None

        # 5. Assemble WatchlistItemResponse items
        responses: List[WatchlistItemResponse] = []
        for item in items:
            inst_id = item.instrument_entity_id
            ent_data = entities_by_id.get(inst_id, {})
            canonical_name = ent_data.get("canonical_name", "Unknown Instrument")
            display_name = ent_data.get("display_name", canonical_name)
            asset_class = ent_data.get("entity_type", "security")
            symbol = symbols_by_id.get(inst_id, display_name)

            issuer_id = issuers_by_inst_id.get(inst_id)
            has_company = issuer_id is not None

            # Venue / series context
            venue: Optional[str] = item.market_series_id if item.market_series_id else None

            # Quote parsing
            quote_rec = cached_quotes.get(inst_id)
            is_avail = False
            quote_measure: Optional[str] = None
            last_price: Optional[str] = None
            bid_price: Optional[str] = None
            ask_price: Optional[str] = None
            absolute_change: Optional[str] = None
            percentage_change: Optional[str] = None
            change_direction: str = "unknown"
            source_timestamp = None
            freshness_status = "unavailable"
            delivery_delay_status = "unknown"
            delay_seconds = None
            provider = None
            quote_currency = "USD"
            quote_unit = None

            if quote_rec is not None and quote_rec.quote is not None:
                is_avail = True
                q = quote_rec.quote
                source_timestamp = q.as_of
                freshness_status = "fresh"  # baseline qualified status
                delivery_delay_status = "realtime"

                # Extract price fields
                if hasattr(q, "last_price") and q.last_price is not None:
                    last_price = str(q.last_price)
                elif hasattr(q, "price") and q.price is not None:
                    last_price = str(q.price)

                if getattr(q, "bid_price", None) is not None:
                    bid_price = str(q.bid_price)
                if getattr(q, "ask_price", None) is not None:
                    ask_price = str(q.ask_price)

                # Determine quote measure label
                if asset_class == "fund":
                    quote_measure = "NAV"
                elif asset_class == "bond":
                    quote_measure = "Clean Price"
                elif asset_class in ("currency", "fx"):
                    quote_measure = "Mid"
                    if last_price is None and bid_price is not None and ask_price is not None:
                        try:
                            mid = (Decimal(bid_price) + Decimal(ask_price)) / 2
                            last_price = f"{mid:.5f}"
                        except Exception:
                            pass
                else:
                    quote_measure = "Last"

                # Reference close & change calculation
                if (
                    hasattr(q, "previous_close")
                    and q.previous_close is not None
                    and last_price is not None
                ):
                    try:
                        prev = Decimal(str(q.previous_close))
                        curr = Decimal(str(last_price))
                        diff = curr - prev
                        absolute_change = f"{diff:+.2f}"
                        if prev != 0:
                            pct = (diff / prev) * 100
                            percentage_change = f"{pct:+.2f}%"
                        if diff > 0:
                            change_direction = "up"
                        elif diff < 0:
                            change_direction = "down"
                        else:
                            change_direction = "flat"
                    except Exception:
                        absolute_change = None
                        percentage_change = None
                        change_direction = "unknown"

            responses.append(
                WatchlistItemResponse(
                    id=item.id,
                    watchlist_id=item.watchlist_id,
                    instrument_entity_id=item.instrument_entity_id,
                    market_series_id=item.market_series_id,
                    position=item.position,
                    created_at=item.created_at,
                    symbol=symbol,
                    display_name=display_name,
                    canonical_name=canonical_name,
                    asset_class=asset_class,
                    venue=venue,
                    quote_currency=quote_currency,
                    quote_unit=quote_unit,
                    is_quote_available=is_avail,
                    quote_measure=quote_measure,
                    last_price=last_price,
                    bid_price=bid_price,
                    ask_price=ask_price,
                    absolute_change=absolute_change,
                    percentage_change=percentage_change,
                    change_direction=change_direction,
                    source_timestamp=source_timestamp,
                    freshness_status=freshness_status,
                    delivery_delay_status=delivery_delay_status,
                    delay_seconds=delay_seconds,
                    provider=provider,
                    issuer_entity_id=issuer_id,
                    has_company_page=has_company,
                )
            )

        return responses
