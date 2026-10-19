"""SQLAlchemy database repository for Watchlists V1 (Stage 76)."""

import uuid
from typing import List, Optional, Tuple

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .errors import (
    InvalidReorderRequestError,
    WatchlistRevisionConflictError,
)
from .models import Watchlist, WatchlistItem


class WatchlistRepository:
    """Handles PostgreSQL storage operations for watchlists and membership items."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_user_watchlists(self, owner_user_id: uuid.UUID) -> int:
        """Returns total watchlists owned by the specified user."""
        stmt = select(func.count(Watchlist.id)).where(Watchlist.owner_user_id == owner_user_id)
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def get_by_id(
        self, watchlist_id: uuid.UUID, owner_user_id: Optional[uuid.UUID] = None
    ) -> Optional[Watchlist]:
        """Retrieves a single watchlist by ID, optionally scoped to owner."""
        stmt = (
            select(Watchlist)
            .options(selectinload(Watchlist.items))
            .where(Watchlist.id == watchlist_id)
        )
        if owner_user_id is not None:
            stmt = stmt.where(Watchlist.owner_user_id == owner_user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_normalized_name(
        self, owner_user_id: uuid.UUID, normalized_name: str
    ) -> Optional[Watchlist]:
        """Retrieves a watchlist by normalized name scoped to the owner."""
        stmt = select(Watchlist).where(
            Watchlist.owner_user_id == owner_user_id,
            Watchlist.normalized_name == normalized_name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_watchlists(
        self, owner_user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """
        Lists summary metadata for user's watchlists with item counts.
        Returns (list_of_summary_dicts, total_count).
        """
        # 1. Total count
        total_count = await self.count_user_watchlists(owner_user_id)
        if total_count == 0:
            return [], 0

        # 2. Query page with item counts
        offset = (page - 1) * page_size
        item_count_subq = (
            select(func.count(WatchlistItem.id))
            .where(WatchlistItem.watchlist_id == Watchlist.id)
            .correlate(Watchlist)
            .scalar_subquery()
        )

        stmt = (
            select(
                Watchlist.id,
                Watchlist.owner_user_id,
                Watchlist.name,
                Watchlist.description,
                Watchlist.revision,
                Watchlist.created_at,
                Watchlist.updated_at,
                item_count_subq.label("item_count"),
            )
            .where(Watchlist.owner_user_id == owner_user_id)
            .order_by(Watchlist.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        res = await self.session.execute(stmt)
        rows = res.all()
        summaries = [
            {
                "id": row.id,
                "owner_user_id": row.owner_user_id,
                "name": row.name,
                "description": row.description,
                "item_count": int(row.item_count or 0),
                "revision": row.revision,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for row in rows
        ]
        return summaries, total_count

    async def create_watchlist(self, watchlist: Watchlist) -> Watchlist:
        """Persists a new watchlist record."""
        self.session.add(watchlist)
        await self.session.flush()
        return watchlist

    async def update_watchlist(
        self,
        watchlist: Watchlist,
        name: Optional[str] = None,
        normalized_name: Optional[str] = None,
        description: Optional[str] = None,
        description_set: bool = False,
    ) -> Watchlist:
        """Updates watchlist name or description and increments revision."""
        if name is not None:
            watchlist.name = name
        if normalized_name is not None:
            watchlist.normalized_name = normalized_name
        if description_set:
            watchlist.description = description

        watchlist.revision += 1
        await self.session.flush()
        return watchlist

    async def delete_watchlist(self, watchlist: Watchlist) -> None:
        """Deletes a watchlist and cascades its items."""
        await self.session.delete(watchlist)
        await self.session.flush()

    async def count_items(self, watchlist_id: uuid.UUID) -> int:
        """Returns total count of items in a watchlist."""
        stmt = select(func.count(WatchlistItem.id)).where(
            WatchlistItem.watchlist_id == watchlist_id
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def get_item_by_id(
        self, item_id: uuid.UUID, watchlist_id: Optional[uuid.UUID] = None
    ) -> Optional[WatchlistItem]:
        """Retrieves a single membership item by ID."""
        stmt = select(WatchlistItem).where(WatchlistItem.id == item_id)
        if watchlist_id is not None:
            stmt = stmt.where(WatchlistItem.watchlist_id == watchlist_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_item_by_series(
        self, watchlist_id: uuid.UUID, instrument_entity_id: uuid.UUID, market_series_id: str
    ) -> Optional[WatchlistItem]:
        """Checks if exact canonical instrument/series combination is already present."""
        stmt = select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.instrument_entity_id == instrument_entity_id,
            WatchlistItem.market_series_id == market_series_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_items(
        self, watchlist_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> List[WatchlistItem]:
        """Retrieves ordered membership items for a watchlist."""
        stmt = (
            select(WatchlistItem)
            .where(WatchlistItem.watchlist_id == watchlist_id)
            .order_by(WatchlistItem.position.asc())
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_item(self, watchlist: Watchlist, item: WatchlistItem) -> WatchlistItem:
        """Appends an item at dense position and increments watchlist revision."""
        self.session.add(item)
        watchlist.revision += 1
        await self.session.flush()
        return item

    async def remove_item(self, watchlist: Watchlist, item: WatchlistItem) -> None:
        """
        Removes an item, re-indexes subsequent positions to maintain dense 0..N-1 ordering,
        and increments watchlist revision.
        """
        deleted_position = item.position
        await self.session.delete(item)

        # Shift all items with position > deleted_position down by 1
        shift_stmt = (
            update(WatchlistItem)
            .where(
                WatchlistItem.watchlist_id == watchlist.id,
                WatchlistItem.position > deleted_position,
            )
            .values(position=WatchlistItem.position - 1)
        )
        await self.session.execute(shift_stmt)

        watchlist.revision += 1
        await self.session.flush()

    async def reorder_items(
        self, watchlist: Watchlist, ordered_item_ids: List[uuid.UUID], expected_revision: int
    ) -> Watchlist:
        """
        Atomically reorders all items in the watchlist using dense integer positions (0..N-1).
        Verifies expected revision for optimistic concurrency control.
        """
        if watchlist.revision != expected_revision:
            raise WatchlistRevisionConflictError(
                f"Revision conflict: expected {expected_revision}, current is {watchlist.revision}"
            )

        # Load all items for this watchlist
        stmt = select(WatchlistItem).where(WatchlistItem.watchlist_id == watchlist.id)
        res = await self.session.execute(stmt)
        current_items = list(res.scalars().all())

        if len(ordered_item_ids) != len(current_items):
            raise InvalidReorderRequestError(
                f"Reorder count mismatch: expected {len(current_items)} item IDs, "
                f"got {len(ordered_item_ids)}"
            )

        items_by_id = {item.id: item for item in current_items}
        for item_id in ordered_item_ids:
            if item_id not in items_by_id:
                raise InvalidReorderRequestError(
                    f"Item ID {item_id} does not belong to watchlist {watchlist.id}"
                )

        # Assign new dense positions
        for new_pos, item_id in enumerate(ordered_item_ids):
            item = items_by_id[item_id]
            item.position = new_pos

        watchlist.revision += 1
        await self.session.flush()
        return watchlist
