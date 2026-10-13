"""Domain service for Personal Tasks (Stage 54)."""

import base64
import datetime
import logging
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.activity.canonical_modules import CANONICAL_MODULES
from atlas.entities.models import Entity

from .enums import TaskStatus, TaskStatusFilter
from .errors import (
    InvalidTaskPayloadError,
    InvalidTaskTransitionError,
    TaskConflictError,
    TaskIdempotencyConflictError,
    TaskNotFoundError,
)
from .models import (
    CreateTaskRequest,
    TaskCountsResponse,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
    UserTask,
)
from .repository import TaskRepository

logger = logging.getLogger(__name__)


def encode_task_cursor(created_at: datetime.datetime, task_id: uuid.UUID) -> str:
    """Encode keyset cursor as Base64 string."""
    raw = f"{created_at.isoformat()}|{str(task_id)}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def decode_task_cursor(cursor_str: str) -> tuple[datetime.datetime, uuid.UUID]:
    """Decode keyset cursor string into (created_at, task_id)."""
    try:
        raw = base64.urlsafe_b64decode(cursor_str.encode("utf-8")).decode("utf-8")
        parts = raw.split("|")
        if len(parts) != 2:
            raise ValueError("Malformed cursor structure")
        created_at = datetime.datetime.fromisoformat(parts[0])
        task_id = uuid.UUID(parts[1])
        return created_at, task_id
    except Exception as exc:
        raise InvalidTaskPayloadError(f"Invalid pagination cursor: {exc}") from exc


class PersonalTaskService:
    """Business logic and validation for personal tasks."""

    def __init__(
        self,
        session: AsyncSession,
        repository: TaskRepository,
    ) -> None:
        self.session = session
        self.repository = repository

    async def create_task(
        self,
        owner_user_id: uuid.UUID,
        request: CreateTaskRequest,
    ) -> TaskResponse:
        """
        Create a new personal task.
        Supports client idempotency via (owner_user_id, idempotency_key).
        """
        # 1. Check idempotency if key provided
        if request.idempotency_key:
            existing = await self.repository.get_by_idempotency_key(
                owner_user_id=owner_user_id,
                idempotency_key=request.idempotency_key,
            )
            if existing:
                # Validate matching payload
                if existing.title != request.title or existing.module_id != request.module_id:
                    raise TaskIdempotencyConflictError(
                        "Conflicting task payload for provided idempotency_key"
                    )
                return await self._to_task_response(existing)

        # 2. Validate canonical module ID if provided
        if request.module_id and request.module_id not in CANONICAL_MODULES:
            raise InvalidTaskPayloadError(
                f"Invalid module_id '{request.module_id}'. Must be a canonical ATLAS module."
            )

        # 3. Validate canonical Entity ID if provided
        if request.entity_id:
            ent_stmt = select(Entity).where(Entity.entity_id == request.entity_id)
            ent_res = await self.session.execute(ent_stmt)
            if not ent_res.scalar_one_or_none():
                raise InvalidTaskPayloadError(
                    f"Entity '{request.entity_id}' not found in canonical entities store."
                )

        now = datetime.datetime.now(datetime.timezone.utc)
        task = UserTask(
            task_id=uuid.uuid4(),
            owner_user_id=owner_user_id,
            title=request.title,
            description=request.description,
            status=TaskStatus.OPEN.value,
            due_at=request.due_at,
            module_id=request.module_id,
            entity_id=request.entity_id,
            created_at=now,
            updated_at=now,
            completed_at=None,
            cancelled_at=None,
            version=1,
            idempotency_key=request.idempotency_key,
        )

        await self.repository.create_task(task)
        await self.session.commit()
        return await self._to_task_response(task)

    async def update_task(
        self,
        owner_user_id: uuid.UUID,
        task_id: uuid.UUID,
        request: UpdateTaskRequest,
    ) -> TaskResponse:
        """
        Update mutable fields of an existing task with optimistic locking.
        """
        task = await self.repository.get_by_id(task_id, owner_user_id, for_update=True)
        if not task:
            raise TaskNotFoundError(str(task_id))

        if request.expected_version is not None and task.version != request.expected_version:
            raise TaskConflictError(
                f"Task version conflict. Expected {request.expected_version}, "
                f"but task is at version {task.version}."
            )

        # Module validation
        if request.clear_module_id:
            task.module_id = None
        elif request.module_id is not None:
            if request.module_id not in CANONICAL_MODULES:
                raise InvalidTaskPayloadError(
                    f"Invalid module_id '{request.module_id}'. Must be a canonical ATLAS module."
                )
            task.module_id = request.module_id

        # Entity validation
        if request.clear_entity_id:
            task.entity_id = None
        elif request.entity_id is not None:
            ent_stmt = select(Entity).where(Entity.entity_id == request.entity_id)
            ent_res = await self.session.execute(ent_stmt)
            if not ent_res.scalar_one_or_none():
                raise InvalidTaskPayloadError(
                    f"Entity '{request.entity_id}' not found in canonical entities store."
                )
            task.entity_id = request.entity_id

        # Title & description
        if request.title is not None:
            task.title = request.title
        if request.description is not None:
            task.description = request.description

        # Due date
        if request.clear_due_at:
            task.due_at = None
        elif request.due_at is not None:
            task.due_at = request.due_at

        task.updated_at = datetime.datetime.now(datetime.timezone.utc)
        task.version += 1

        await self.repository.update_task(task)
        await self.session.commit()
        return await self._to_task_response(task)

    async def complete_task(
        self,
        owner_user_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> TaskResponse:
        """
        Mark an OPEN task as COMPLETED.
        Idempotent if already COMPLETED.
        Rejects if CANCELLED.
        """
        task = await self.repository.get_by_id(task_id, owner_user_id, for_update=True)
        if not task:
            raise TaskNotFoundError(str(task_id))

        if task.status == TaskStatus.COMPLETED.value:
            # Idempotent return
            return await self._to_task_response(task)

        if task.status == TaskStatus.CANCELLED.value:
            raise InvalidTaskTransitionError(
                current_status=task.status,
                target_status=TaskStatus.COMPLETED.value,
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        task.status = TaskStatus.COMPLETED.value
        task.completed_at = now
        task.updated_at = now
        task.version += 1

        await self.repository.update_task(task)
        await self.session.commit()
        return await self._to_task_response(task)

    async def reopen_task(
        self,
        owner_user_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> TaskResponse:
        """
        Reopen a COMPLETED task back to OPEN.
        Idempotent if already OPEN.
        Rejects if CANCELLED.
        """
        task = await self.repository.get_by_id(task_id, owner_user_id, for_update=True)
        if not task:
            raise TaskNotFoundError(str(task_id))

        if task.status == TaskStatus.OPEN.value:
            # Idempotent return
            return await self._to_task_response(task)

        if task.status == TaskStatus.CANCELLED.value:
            raise InvalidTaskTransitionError(
                current_status=task.status,
                target_status=TaskStatus.OPEN.value,
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        task.status = TaskStatus.OPEN.value
        task.completed_at = None
        task.updated_at = now
        task.version += 1

        await self.repository.update_task(task)
        await self.session.commit()
        return await self._to_task_response(task)

    async def cancel_task(
        self,
        owner_user_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> TaskResponse:
        """
        Cancel an OPEN task.
        Idempotent if already CANCELLED.
        Rejects if COMPLETED.
        """
        task = await self.repository.get_by_id(task_id, owner_user_id, for_update=True)
        if not task:
            raise TaskNotFoundError(str(task_id))

        if task.status == TaskStatus.CANCELLED.value:
            # Idempotent return
            return await self._to_task_response(task)

        if task.status == TaskStatus.COMPLETED.value:
            raise InvalidTaskTransitionError(
                current_status=task.status,
                target_status=TaskStatus.CANCELLED.value,
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        task.status = TaskStatus.CANCELLED.value
        task.cancelled_at = now
        task.updated_at = now
        task.version += 1

        await self.repository.update_task(task)
        await self.session.commit()
        return await self._to_task_response(task)

    async def list_tasks(
        self,
        owner_user_id: uuid.UUID,
        status_filter: TaskStatusFilter = TaskStatusFilter.OPEN,
        limit: int = 10,
        cursor: Optional[str] = None,
    ) -> TaskListResponse:
        """
        List user tasks using keyset pagination.
        Includes authoritative open and overdue counts.
        """
        bounded_limit = max(1, min(limit, 50))
        now = datetime.datetime.now(datetime.timezone.utc)

        cursor_created_at = None
        cursor_id = None
        if cursor:
            cursor_created_at, cursor_id = decode_task_cursor(cursor)

        # Fetch limit + 1 to detect has_more
        tasks = await self.repository.list_tasks(
            owner_user_id=owner_user_id,
            status_filter=status_filter,
            limit=bounded_limit + 1,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
        )

        has_more = len(tasks) > bounded_limit
        page_tasks = list(tasks[:bounded_limit])

        # Batch resolve entities (zero N+1)
        entity_ids = [t.entity_id for t in page_tasks if t.entity_id is not None]
        entity_map: dict[uuid.UUID, Entity] = {}
        if entity_ids:
            ent_stmt = select(Entity).where(Entity.entity_id.in_(entity_ids))
            ent_res = await self.session.execute(ent_stmt)
            entity_map = {ent.entity_id: ent for ent in ent_res.scalars().all()}

        items: list[TaskResponse] = []
        for task in page_tasks:
            items.append(self._build_task_response(task, entity_map.get(task.entity_id), now))

        next_cursor = None
        if has_more and page_tasks:
            last_task = page_tasks[-1]
            next_cursor = encode_task_cursor(last_task.created_at, last_task.task_id)

        open_count, overdue_count = await self.repository.get_counts(owner_user_id, now)

        return TaskListResponse(
            schema_version="1.0",
            items=items,
            open_count=open_count,
            overdue_count=overdue_count,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def get_counts(self, owner_user_id: uuid.UUID) -> TaskCountsResponse:
        """Return real counts for open and overdue tasks."""
        now = datetime.datetime.now(datetime.timezone.utc)
        open_count, overdue_count = await self.repository.get_counts(owner_user_id, now)
        return TaskCountsResponse(
            open_count=open_count,
            overdue_count=overdue_count,
        )

    async def _to_task_response(self, task: UserTask) -> TaskResponse:
        """Build a single TaskResponse resolving metadata if needed."""
        now = datetime.datetime.now(datetime.timezone.utc)
        entity = None
        if task.entity_id:
            ent_stmt = select(Entity).where(Entity.entity_id == task.entity_id)
            ent_res = await self.session.execute(ent_stmt)
            entity = ent_res.scalar_one_or_none()
        return self._build_task_response(task, entity, now)

    def _build_task_response(
        self,
        task: UserTask,
        entity: Optional[Entity],
        now: datetime.datetime,
    ) -> TaskResponse:
        """Helper to construct TaskResponse."""
        mod_label = None
        if task.module_id:
            mod_info = CANONICAL_MODULES.get(task.module_id)
            mod_label = mod_info.label if mod_info else task.module_id

        ent_name = None
        ent_type = None
        if task.entity_id:
            if entity:
                ent_name = entity.display_name
                ent_type = entity.entity_type
            else:
                ent_name = "Unavailable Entity"
                ent_type = "unknown"

        is_overdue = (
            task.status == TaskStatus.OPEN.value and task.due_at is not None and task.due_at < now
        )
        is_due_soon = (
            task.status == TaskStatus.OPEN.value
            and task.due_at is not None
            and now <= task.due_at <= (now + datetime.timedelta(hours=24))
        )

        return TaskResponse(
            task_id=task.task_id,
            owner_user_id=task.owner_user_id,
            title=task.title,
            description=task.description,
            status=TaskStatus(task.status),
            due_at=task.due_at,
            module_id=task.module_id,
            module_label=mod_label,
            entity_id=task.entity_id,
            entity_display_name=ent_name,
            entity_type=ent_type,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            cancelled_at=task.cancelled_at,
            version=task.version,
            is_overdue=is_overdue,
            is_due_soon=is_due_soon,
        )
