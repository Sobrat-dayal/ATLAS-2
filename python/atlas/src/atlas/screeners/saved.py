"""Saved Screeners Domain Service and Persistence (Stage 97).

Provides user-owned saved screener persistence, versioned query serialization,
optimistic concurrency control, quota enforcement, and tenant isolation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import UUID, uuid4

from atlas.screeners.enums import SavedScreenerStatus
from atlas.screeners.errors import (
    SavedScreenerConflictError,
    SavedScreenerNameInvalidError,
    SavedScreenerNotFoundError,
    SavedScreenerQuotaExceededError,
)
from atlas.screeners.schemas import (
    SavedScreenerCreateRequestDTO,
    SavedScreenerDTO,
    SavedScreenerListResponseDTO,
    SavedScreenerUpdateRequestDTO,
)


class SavedScreenerRepository:
    """In-memory persistent repository for user-owned saved screeners with tenant isolation."""

    MAX_SCREENS_PER_USER = 100
    MAX_NAME_LENGTH = 120
    MAX_DESCRIPTION_LENGTH = 1000

    def __init__(self) -> None:
        # Keyed by (owner_user_id, saved_screen_id)
        self._store: Dict[UUID, Dict[UUID, SavedScreenerDTO]] = {}

    def list(
        self,
        owner_user_id: UUID,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> SavedScreenerListResponseDTO:
        user_screens = list(self._store.get(owner_user_id, {}).values())
        # Filter active
        active_screens = [s for s in user_screens if s.status != SavedScreenerStatus.DELETED]

        if search:
            q = search.lower().strip()
            active_screens = [
                s
                for s in active_screens
                if q in s.name.lower() or (s.description and q in s.description.lower())
            ]

        # Sort by updated_at descending
        active_screens.sort(key=lambda s: s.updated_at, reverse=True)

        total = len(active_screens)
        start = (page - 1) * page_size
        end = start + page_size
        items = active_screens[start:end]

        return SavedScreenerListResponseDTO(
            total=total,
            page=page,
            page_size=page_size,
            items=items,
        )

    def get(self, owner_user_id: UUID, saved_screen_id: UUID) -> SavedScreenerDTO:
        user_store = self._store.get(owner_user_id, {})
        screen = user_store.get(saved_screen_id)
        if not screen or screen.status == SavedScreenerStatus.DELETED:
            raise SavedScreenerNotFoundError(str(saved_screen_id))
        return screen

    def create(
        self,
        owner_user_id: UUID,
        request: SavedScreenerCreateRequestDTO,
    ) -> SavedScreenerDTO:
        name = self._validate_name(request.name)
        desc = self._validate_description(request.description)

        user_store = self._store.setdefault(owner_user_id, {})
        active_count = sum(
            1 for s in user_store.values() if s.status != SavedScreenerStatus.DELETED
        )
        if active_count >= self.MAX_SCREENS_PER_USER:
            raise SavedScreenerQuotaExceededError(self.MAX_SCREENS_PER_USER)

        screen_id = uuid4()
        now = datetime.now(timezone.utc)

        default_columns = request.columns or [
            "ticker",
            "canonical_security_name",
            "last_price",
            "market_cap",
            "pe_ratio",
            "volume_24h",
        ]

        screen = SavedScreenerDTO(
            saved_screen_id=screen_id,
            owner_user_id=owner_user_id,
            name=name,
            description=desc,
            query_schema_version="1.0.0",
            universe=request.universe,
            filters=request.filters,
            columns=default_columns,
            sort=request.sort,
            ranking=request.ranking,
            period_policy=request.period_policy,
            currency_policy=request.currency_policy,
            revision=1,
            status=SavedScreenerStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            last_executed_at=None,
        )

        user_store[screen_id] = screen
        return screen

    def update(
        self,
        owner_user_id: UUID,
        saved_screen_id: UUID,
        request: SavedScreenerUpdateRequestDTO,
    ) -> SavedScreenerDTO:
        screen = self.get(owner_user_id, saved_screen_id)

        # Optimistic concurrency verification
        if screen.revision != request.expected_revision:
            raise SavedScreenerConflictError(
                expected_revision=request.expected_revision,
                actual_revision=screen.revision,
            )

        new_name = self._validate_name(request.name) if request.name is not None else screen.name
        new_desc = (
            self._validate_description(request.description)
            if request.description is not None
            else screen.description
        )

        now = datetime.now(timezone.utc)
        updated_screen = screen.model_copy(
            update={
                "name": new_name,
                "description": new_desc,
                "universe": request.universe if request.universe is not None else screen.universe,
                "filters": request.filters if request.filters is not None else screen.filters,
                "columns": request.columns if request.columns is not None else screen.columns,
                "sort": request.sort if request.sort is not None else screen.sort,
                "ranking": request.ranking if request.ranking is not None else screen.ranking,
                "period_policy": request.period_policy
                if request.period_policy is not None
                else screen.period_policy,
                "currency_policy": request.currency_policy
                if request.currency_policy is not None
                else screen.currency_policy,
                "revision": screen.revision + 1,
                "updated_at": now,
            }
        )

        self._store[owner_user_id][saved_screen_id] = updated_screen
        return updated_screen

    def rename(
        self,
        owner_user_id: UUID,
        saved_screen_id: UUID,
        name: str,
        expected_revision: Optional[int] = None,
    ) -> SavedScreenerDTO:
        screen = self.get(owner_user_id, saved_screen_id)
        if expected_revision is not None and screen.revision != expected_revision:
            raise SavedScreenerConflictError(expected_revision, screen.revision)

        validated_name = self._validate_name(name)
        now = datetime.now(timezone.utc)
        updated = screen.model_copy(
            update={
                "name": validated_name,
                "revision": screen.revision + 1,
                "updated_at": now,
            }
        )
        self._store[owner_user_id][saved_screen_id] = updated
        return updated

    def duplicate(
        self,
        owner_user_id: UUID,
        saved_screen_id: UUID,
        new_name: Optional[str] = None,
    ) -> SavedScreenerDTO:
        screen = self.get(owner_user_id, saved_screen_id)

        user_store = self._store.setdefault(owner_user_id, {})
        active_count = sum(
            1 for s in user_store.values() if s.status != SavedScreenerStatus.DELETED
        )
        if active_count >= self.MAX_SCREENS_PER_USER:
            raise SavedScreenerQuotaExceededError(self.MAX_SCREENS_PER_USER)

        copy_name = new_name or f"{screen.name} (Copy)"
        validated_name = self._validate_name(copy_name)
        new_id = uuid4()
        now = datetime.now(timezone.utc)

        duplicated = screen.model_copy(
            update={
                "saved_screen_id": new_id,
                "name": validated_name,
                "revision": 1,
                "created_at": now,
                "updated_at": now,
                "last_executed_at": None,
            }
        )
        user_store[new_id] = duplicated
        return duplicated

    def delete(self, owner_user_id: UUID, saved_screen_id: UUID) -> None:
        screen = self.get(owner_user_id, saved_screen_id)
        # Soft delete
        updated = screen.model_copy(
            update={"status": SavedScreenerStatus.DELETED, "updated_at": datetime.now(timezone.utc)}
        )
        self._store[owner_user_id][saved_screen_id] = updated

    def mark_executed(self, owner_user_id: UUID, saved_screen_id: UUID) -> None:
        user_store = self._store.get(owner_user_id, {})
        screen = user_store.get(saved_screen_id)
        if screen:
            updated = screen.model_copy(update={"last_executed_at": datetime.now(timezone.utc)})
            user_store[saved_screen_id] = updated

    def _validate_name(self, name: Optional[str]) -> str:
        if not name or not name.strip():
            raise SavedScreenerNameInvalidError("Screen name cannot be empty.")
        clean = name.strip()
        if len(clean) > self.MAX_NAME_LENGTH:
            raise SavedScreenerNameInvalidError(
                f"Screen name exceeds maximum length of {self.MAX_NAME_LENGTH} characters."
            )
        return clean

    def _validate_description(self, desc: Optional[str]) -> Optional[str]:
        if not desc:
            return None
        clean = desc.strip()
        if len(clean) > self.MAX_DESCRIPTION_LENGTH:
            clean = clean[: self.MAX_DESCRIPTION_LENGTH]
        return clean


# Singleton repository
saved_screener_repository = SavedScreenerRepository()
