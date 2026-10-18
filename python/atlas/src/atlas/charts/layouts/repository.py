"""PostgreSQL Database Repository for Saved Chart Layouts (Stage 74).

Implements:
- Owner-scoped isolation for all queries (zero cross-user leakage)
- Keyset / offset pagination and name search
- Atomic conditional optimistic updates:
    UPDATE chart_layouts
    SET layout_document = :doc, revision = revision + 1, updated_at = NOW()
    WHERE id = :id AND owner_user_id = :uid AND revision = :expected_revision
- Single-default layout transactional enforcement
"""

import uuid
from typing import Any, Dict, Optional, Sequence

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ChartLayoutModel


class ChartLayoutRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_layouts(
        self,
        owner_user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> Sequence[ChartLayoutModel]:
        """Lists layouts belonging to the owner, sorted by updated_at descending."""
        stmt = select(ChartLayoutModel).where(ChartLayoutModel.owner_user_id == owner_user_id)

        if search:
            search_clean = f"%{search.strip().lower()}%"
            stmt = stmt.where(ChartLayoutModel.normalized_name.ilike(search_clean))

        stmt = stmt.order_by(ChartLayoutModel.updated_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_layouts(
        self,
        owner_user_id: uuid.UUID,
        search: Optional[str] = None,
    ) -> int:
        """Counts total layouts belonging to the owner matching search filter."""
        stmt = select(func.count(ChartLayoutModel.id)).where(
            ChartLayoutModel.owner_user_id == owner_user_id
        )

        if search:
            search_clean = f"%{search.strip().lower()}%"
            stmt = stmt.where(ChartLayoutModel.normalized_name.ilike(search_clean))

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def get_by_id(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
    ) -> Optional[ChartLayoutModel]:
        """Fetches a layout strictly scoped to the owner."""
        stmt = select(ChartLayoutModel).where(
            ChartLayoutModel.id == layout_id,
            ChartLayoutModel.owner_user_id == owner_user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_normalized_name(
        self,
        owner_user_id: uuid.UUID,
        normalized_name: str,
    ) -> Optional[ChartLayoutModel]:
        """Fetches a layout by normalized name within the user's scope."""
        stmt = select(ChartLayoutModel).where(
            ChartLayoutModel.owner_user_id == owner_user_id,
            ChartLayoutModel.normalized_name == normalized_name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_default(
        self,
        owner_user_id: uuid.UUID,
    ) -> Optional[ChartLayoutModel]:
        """Fetches the designated default layout for the user, if one is set."""
        stmt = select(ChartLayoutModel).where(
            ChartLayoutModel.owner_user_id == owner_user_id,
            ChartLayoutModel.is_default.is_(True),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_layout(
        self,
        owner_user_id: uuid.UUID,
        name: str,
        normalized_name: str,
        description: Optional[str],
        document: Dict[str, Any],
        is_default: bool = False,
        layout_id: Optional[uuid.UUID] = None,
    ) -> ChartLayoutModel:
        """Persists a new user-owned chart layout."""
        model = ChartLayoutModel(
            id=layout_id or uuid.uuid4(),
            owner_user_id=owner_user_id,
            name=name,
            normalized_name=normalized_name,
            description=description,
            document_schema_version=document.get("schema_version", 1),
            revision=1,
            layout_document=document,
            is_default=is_default,
        )
        self.session.add(model)
        await self.session.flush()
        return model

    async def update_layout(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
        expected_revision: int,
        document: Dict[str, Any],
    ) -> Optional[ChartLayoutModel]:
        """
        Atomic conditional optimistic concurrency update.
        Increments revision by 1 only if expected_revision matches.
        Returns the updated model or None if revision precondition failed / not found.
        """
        new_revision = expected_revision + 1
        stmt = (
            update(ChartLayoutModel)
            .where(
                ChartLayoutModel.id == layout_id,
                ChartLayoutModel.owner_user_id == owner_user_id,
                ChartLayoutModel.revision == expected_revision,
            )
            .values(
                layout_document=document,
                document_schema_version=document.get("schema_version", 1),
                revision=new_revision,
                updated_at=func.now(),
            )
            .returning(ChartLayoutModel)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def patch_metadata(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
        name: Optional[str] = None,
        normalized_name: Optional[str] = None,
        description: Optional[str] = None,
        is_default: Optional[bool] = None,
    ) -> Optional[ChartLayoutModel]:
        """Updates layout metadata without mutating the layout document."""
        values: Dict[str, Any] = {"updated_at": func.now()}
        if name is not None:
            values["name"] = name
        if normalized_name is not None:
            values["normalized_name"] = normalized_name
        if description is not None:
            values["description"] = description
        if is_default is not None:
            values["is_default"] = is_default

        stmt = (
            update(ChartLayoutModel)
            .where(
                ChartLayoutModel.id == layout_id,
                ChartLayoutModel.owner_user_id == owner_user_id,
            )
            .values(**values)
            .returning(ChartLayoutModel)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def clear_default(
        self,
        owner_user_id: uuid.UUID,
        except_layout_id: Optional[uuid.UUID] = None,
    ) -> None:
        """Clears is_default on other layouts for this user to enforce at most one default."""
        stmt = update(ChartLayoutModel).where(
            ChartLayoutModel.owner_user_id == owner_user_id,
            ChartLayoutModel.is_default.is_(True),
        )
        if except_layout_id:
            stmt = stmt.where(ChartLayoutModel.id != except_layout_id)

        stmt = stmt.values(is_default=False)
        await self.session.execute(stmt)

    async def delete_layout(
        self,
        layout_id: uuid.UUID,
        owner_user_id: uuid.UUID,
    ) -> bool:
        """Deletes a layout owned by the user."""
        stmt = delete(ChartLayoutModel).where(
            ChartLayoutModel.id == layout_id,
            ChartLayoutModel.owner_user_id == owner_user_id,
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0
