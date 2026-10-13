"""Repository for user personal tasks (Stage 54)."""

import datetime
import uuid
from typing import Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .enums import TaskStatus, TaskStatusFilter
from .models import UserTask


class TaskRepository:
    """Encapsulates all database operations for personal tasks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        task_id: uuid.UUID,
        owner_user_id: uuid.UUID,
        for_update: bool = False,
    ) -> Optional[UserTask]:
        """Fetch a task by ID ensuring user ownership."""
        stmt = select(UserTask).where(
            UserTask.task_id == task_id,
            UserTask.owner_user_id == owner_user_id,
        )
        if for_update:
            stmt = stmt.with_for_update()
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_idempotency_key(
        self,
        owner_user_id: uuid.UUID,
        idempotency_key: str,
    ) -> Optional[UserTask]:
        """Lookup an existing task by user and idempotency key."""
        stmt = select(UserTask).where(
            UserTask.owner_user_id == owner_user_id,
            UserTask.idempotency_key == idempotency_key,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_task(self, task: UserTask) -> UserTask:
        """Insert a new personal task."""
        self.session.add(task)
        await self.session.flush()
        return task

    async def update_task(self, task: UserTask) -> UserTask:
        """Flush changes on an existing task."""
        await self.session.flush()
        return task

    async def list_tasks(
        self,
        owner_user_id: uuid.UUID,
        status_filter: TaskStatusFilter,
        limit: int,
        cursor_created_at: Optional[datetime.datetime] = None,
        cursor_id: Optional[uuid.UUID] = None,
    ) -> list[UserTask]:
        """
        List personal tasks using keyset pagination.
        Ordered by created_at DESC, task_id DESC.
        """
        stmt = select(UserTask).where(UserTask.owner_user_id == owner_user_id)

        if status_filter != TaskStatusFilter.ALL:
            stmt = stmt.where(UserTask.status == status_filter.value)

        # Keyset pagination condition: (created_at, task_id) < (cursor_created_at, cursor_id)
        if cursor_created_at is not None and cursor_id is not None:
            stmt = stmt.where(
                or_(
                    UserTask.created_at < cursor_created_at,
                    and_(
                        UserTask.created_at == cursor_created_at,
                        UserTask.task_id < cursor_id,
                    ),
                )
            )

        stmt = stmt.order_by(
            UserTask.created_at.desc(),
            UserTask.task_id.desc(),
        ).limit(limit)

        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_counts(
        self,
        owner_user_id: uuid.UUID,
        now: datetime.datetime,
    ) -> tuple[int, int]:
        """
        Return authoritative counts: (open_count, overdue_count).
        Overdue is defined as status == 'OPEN' and due_at < now.
        """
        # 1. Total open tasks
        stmt_open = (
            select(func.count())
            .select_from(UserTask)
            .where(
                UserTask.owner_user_id == owner_user_id,
                UserTask.status == TaskStatus.OPEN.value,
            )
        )
        res_open = await self.session.execute(stmt_open)
        open_count = res_open.scalar_one() or 0

        # 2. Overdue open tasks
        stmt_overdue = (
            select(func.count())
            .select_from(UserTask)
            .where(
                UserTask.owner_user_id == owner_user_id,
                UserTask.status == TaskStatus.OPEN.value,
                UserTask.due_at.isnot(None),
                UserTask.due_at < now,
            )
        )
        res_overdue = await self.session.execute(stmt_overdue)
        overdue_count = res_overdue.scalar_one() or 0

        return open_count, overdue_count
