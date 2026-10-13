"""Service layer managing user activity recording, consent, and workspace continuity."""

import base64
import datetime
import json
import logging
import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.models import Entity
from atlas.preferences.errors import PreferenceNotFoundError
from atlas.preferences.service import UserPreferenceService

from .canonical_modules import CANONICAL_MODULES, is_valid_module_id
from .enums import ActivityEventType
from .errors import (
    ActivityHistoryDisabledError,
    IdempotencyConflictError,
    InvalidCursorError,
    InvalidEntityError,
    InvalidModuleIdError,
    ModuleAccessDeniedError,
)
from .models import (
    ActivityConsentResponse,
    ClearActivityResponse,
    RecordActivityEventRequest,
    UserActivityEvent,
    UserActivityItem,
    UserActivityListResponse,
)
from .repository import UserActivityRepository

logger = logging.getLogger(__name__)

PREFERENCE_KEY_CONSENT = "home.activity_history_enabled"
MAX_USER_RETAINED_EVENTS = 1000
RETENTION_DAYS = 90


def encode_cursor(occurred_at: datetime.datetime, activity_id: uuid.UUID) -> str:
    """Encodes pagination keyset cursor into a base64 string."""
    payload = {"t": occurred_at.isoformat(), "id": str(activity_id)}
    raw = json.dumps(payload)
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str) -> tuple[datetime.datetime, uuid.UUID]:
    """
    Decodes pagination keyset cursor from a base64 string.
    Raises InvalidCursorError on invalid input.
    """
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        payload = json.loads(raw)
        occurred_at = datetime.datetime.fromisoformat(payload["t"])
        activity_id = uuid.UUID(payload["id"])
        return occurred_at, activity_id
    except Exception as exc:
        raise InvalidCursorError() from exc


class UserActivityService:
    """Coordinates business logic and policies for user activity."""

    def __init__(
        self,
        session: AsyncSession,
        repository: UserActivityRepository,
        preference_service: UserPreferenceService,
        authz_service: Optional[Any] = None,
    ):
        self.session = session
        self.repository = repository
        self.preference_service = preference_service
        self.authz_service = authz_service

    async def is_history_enabled(self, user_id: uuid.UUID) -> bool:
        """
        Checks authoritative Stage 15 user preference.
        Defaults to False (disabled) for new users and unconfigured users.
        """
        try:
            pref = await self.preference_service.get_preference(user_id, PREFERENCE_KEY_CONSENT)
            if pref and isinstance(pref.payload, dict):
                return bool(pref.payload.get("enabled", False))
            return False
        except PreferenceNotFoundError:
            return False
        except Exception as exc:
            logger.warning("Error checking activity history consent for %s: %s", user_id, exc)
            return False

    async def set_consent(self, user_id: uuid.UUID, enabled: bool) -> ActivityConsentResponse:
        """
        Updates user consent preference atomically in Stage 15.
        When disabling (enabled=False), transactionally purges previously recorded activity rows.
        """
        try:
            existing = await self.preference_service.get_preference(user_id, PREFERENCE_KEY_CONSENT)
            pref = await self.preference_service.set_preference(
                user_id=user_id,
                key=PREFERENCE_KEY_CONSENT,
                schema_version=1,
                payload={"enabled": enabled},
                expected_revision=existing.revision,
            )
        except PreferenceNotFoundError:
            pref = await self.preference_service.set_preference(
                user_id=user_id,
                key=PREFERENCE_KEY_CONSENT,
                schema_version=1,
                payload={"enabled": enabled},
            )

        if not enabled:
            # Atomic purge on consent revocation
            await self.repository.delete_all_for_user(user_id)

        await self.session.commit()
        return ActivityConsentResponse(
            enabled=enabled,
            updated_at=pref.updated_at,
        )

    async def record_event(
        self,
        user_id: uuid.UUID,
        request: RecordActivityEventRequest,
    ) -> UserActivityEvent:
        """
        Validates and records an explicit user action.
        Best-effort, idempotent, and enforces retention limits.
        """
        # 1. Recheck authoritative consent
        if not await self.is_history_enabled(user_id):
            raise ActivityHistoryDisabledError()

        # 2. Validate canonical module if MODULE_OPENED
        if request.event_type == ActivityEventType.MODULE_OPENED:
            if not request.module_id or not is_valid_module_id(request.module_id):
                raise InvalidModuleIdError(request.module_id or "unknown")
            if self.authz_service and hasattr(self.authz_service, "can_view_module"):
                can_view = await self.authz_service.can_view_module(user_id, request.module_id)
                if not can_view:
                    raise ModuleAccessDeniedError(request.module_id)

        # 3. Validate canonical entity if ENTITY_SELECTED
        elif request.event_type == ActivityEventType.ENTITY_SELECTED:
            stmt = select(Entity).where(Entity.entity_id == request.entity_id)
            res = await self.session.execute(stmt)
            entity = res.scalar_one_or_none()
            if not entity:
                raise InvalidEntityError(str(request.entity_id))

        # 4. Enforce idempotency: (user_id, client_event_id)
        existing = await self.repository.get_by_client_event_id(user_id, request.client_event_id)
        if existing:
            if (
                existing.event_type == request.event_type.value
                and existing.module_id == request.module_id
                and existing.entity_id == request.entity_id
            ):
                return existing
            raise IdempotencyConflictError(str(request.client_event_id))

        # 5. Insert event with server UTC timestamp
        now = datetime.datetime.now(datetime.timezone.utc)
        event = await self.repository.create_event(
            user_id=user_id,
            event_type=request.event_type.value,
            client_event_id=request.client_event_id,
            module_id=request.module_id,
            entity_id=request.entity_id,
            occurred_at=now,
        )

        # 6. Enforce per-user event cap
        await self.repository.prune_user_cap(user_id, max_retained=MAX_USER_RETAINED_EVENTS)

        await self.session.commit()
        return event

    async def list_activity(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
        cursor: Optional[str] = None,
    ) -> UserActivityListResponse:
        """
        Lists recent activity events for the authenticated user using keyset pagination.
        Filters records older than 90 days. Batch resolves entity metadata.
        """
        enabled = await self.is_history_enabled(user_id)
        if not enabled:
            return UserActivityListResponse(
                schema_version=1,
                enabled=False,
                items=[],
                next_cursor=None,
                has_more=False,
            )

        bounded_limit = max(1, min(limit, 50))
        retention_cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            days=RETENTION_DAYS
        )

        cursor_occurred_at = None
        cursor_activity_id = None
        if cursor:
            cursor_occurred_at, cursor_activity_id = decode_cursor(cursor)

        events = await self.repository.list_events(
            user_id=user_id,
            limit=bounded_limit + 1,
            cursor_occurred_at=cursor_occurred_at,
            cursor_activity_id=cursor_activity_id,
            retention_cutoff=retention_cutoff,
        )

        has_more = len(events) > bounded_limit
        page_events = list(events[:bounded_limit])

        # Batch resolve referenced entities (avoid N+1 queries)
        entity_ids = [e.entity_id for e in page_events if e.entity_id is not None]
        entity_map: dict[uuid.UUID, Entity] = {}
        if entity_ids:
            ent_stmt = select(Entity).where(Entity.entity_id.in_(entity_ids))
            ent_res = await self.session.execute(ent_stmt)
            entity_map = {ent.entity_id: ent for ent in ent_res.scalars().all()}

        items: list[UserActivityItem] = []
        for event in page_events:
            event_type = ActivityEventType(event.event_type)
            if event_type == ActivityEventType.MODULE_OPENED:
                mod_info = CANONICAL_MODULES.get(event.module_id or "")
                label = mod_info.label if mod_info else (event.module_id or "Module")
                route = mod_info.route if mod_info else f"/{event.module_id}"
                items.append(
                    UserActivityItem(
                        activity_id=event.activity_id,
                        event_type=event_type,
                        module_id=event.module_id,
                        module_label=label,
                        entity_id=None,
                        entity_display_name=None,
                        entity_type=None,
                        occurred_at=event.occurred_at,
                        resume_target=route,
                        is_accessible=True,
                    )
                )
            elif event_type == ActivityEventType.ENTITY_SELECTED:
                ent = entity_map.get(event.entity_id) if event.entity_id else None
                if ent:
                    items.append(
                        UserActivityItem(
                            activity_id=event.activity_id,
                            event_type=event_type,
                            module_id=None,
                            module_label=None,
                            entity_id=ent.entity_id,
                            entity_display_name=ent.display_name,
                            entity_type=ent.entity_type,
                            occurred_at=event.occurred_at,
                            resume_target=f"/entities/{ent.entity_id}",
                            is_accessible=True,
                        )
                    )
                else:
                    items.append(
                        UserActivityItem(
                            activity_id=event.activity_id,
                            event_type=event_type,
                            module_id=None,
                            module_label=None,
                            entity_id=event.entity_id,
                            entity_display_name="Unavailable Entity",
                            entity_type=None,
                            occurred_at=event.occurred_at,
                            resume_target="",
                            is_accessible=False,
                        )
                    )

        next_cursor = None
        if has_more and page_events:
            last = page_events[-1]
            next_cursor = encode_cursor(last.occurred_at, last.activity_id)

        return UserActivityListResponse(
            schema_version=1,
            enabled=True,
            items=items,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def clear_history(self, user_id: uuid.UUID) -> ClearActivityResponse:
        """Securely erases all Stage 53 activity records belonging to the authenticated user."""
        count = await self.repository.delete_all_for_user(user_id)
        await self.session.commit()
        return ClearActivityResponse(deleted_count=count, cleared=True)
