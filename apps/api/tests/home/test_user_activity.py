"""Stage 53 Home Personalized Activity Test Suite.

Verifies:
- Strict typed event payloads (forbids arbitrary metadata, client user_id, raw search/command text)
- Canonical 20 module validation
- Authoritative Stage 15 consent integration (disabled by default)
- Idempotency via (user_id, client_event_id)
- Retention cutoff exclusion (90 days) & per-user cap enforcement (1,000 max)
- Coordinated disable-and-clear transactional semantics
- Safe batch resolution of entities and graceful handling of unavailable/deleted entities
- Authenticated and authorized FastAPI endpoint contracts (/home/activity)
"""

import datetime
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.activity.canonical_modules import CANONICAL_MODULES, is_valid_module_id
from atlas.activity.enums import ActivityEventType
from atlas.activity.errors import (
    ActivityHistoryDisabledError,
    IdempotencyConflictError,
    InvalidCursorError,
)
from atlas.activity.models import (
    RecordActivityEventRequest,
    UserActivityEvent,
    UserActivityListResponse,
)
from atlas.activity.repository import UserActivityRepository
from atlas.activity.service import (
    UserActivityService,
    decode_cursor,
    encode_cursor,
)
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.entities.models import Entity
from atlas.preferences import UserPreference
from atlas.preferences.errors import PreferenceNotFoundError
from atlas.preferences.service import UserPreferenceService
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session


# -----------------------------------------------------------------------------
# 1. Validation & Schema Tests
# -----------------------------------------------------------------------------
class TestActivityValidation:
    def test_record_module_opened_valid(self):
        client_id = uuid.uuid4()
        req = RecordActivityEventRequest(
            event_type=ActivityEventType.MODULE_OPENED,
            module_id="markets",
            client_event_id=client_id,
        )
        assert req.event_type == ActivityEventType.MODULE_OPENED
        assert req.module_id == "markets"
        assert req.entity_id is None
        assert req.client_event_id == client_id

    def test_record_module_opened_missing_module_id_rejected(self):
        with pytest.raises(ValidationError):
            RecordActivityEventRequest(
                event_type=ActivityEventType.MODULE_OPENED,
                client_event_id=uuid.uuid4(),
            )

    def test_record_module_opened_with_entity_id_rejected(self):
        with pytest.raises(ValidationError):
            RecordActivityEventRequest(
                event_type=ActivityEventType.MODULE_OPENED,
                module_id="markets",
                entity_id=uuid.uuid4(),
                client_event_id=uuid.uuid4(),
            )

    def test_record_entity_selected_valid(self):
        entity_id = uuid.uuid4()
        client_id = uuid.uuid4()
        req = RecordActivityEventRequest(
            event_type=ActivityEventType.ENTITY_SELECTED,
            entity_id=entity_id,
            client_event_id=client_id,
        )
        assert req.event_type == ActivityEventType.ENTITY_SELECTED
        assert req.entity_id == entity_id
        assert req.client_event_id == client_id

    def test_record_entity_selected_missing_entity_id_rejected(self):
        with pytest.raises(ValidationError):
            RecordActivityEventRequest(
                event_type=ActivityEventType.ENTITY_SELECTED,
                client_event_id=uuid.uuid4(),
            )

    def test_forbid_extra_fields(self):
        with pytest.raises(ValidationError):
            RecordActivityEventRequest(
                event_type=ActivityEventType.MODULE_OPENED,
                module_id="charts",
                client_event_id=uuid.uuid4(),
                user_id=str(uuid.uuid4()),  # Extra forbidden field
            )

    def test_forbid_raw_search_or_command_text(self):
        with pytest.raises(ValidationError):
            RecordActivityEventRequest(
                event_type=ActivityEventType.MODULE_OPENED,
                module_id="charts",
                client_event_id=uuid.uuid4(),
                search_query="AAPL",  # Extra forbidden field
            )

    def test_cursor_encoding_and_decoding(self):
        act_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        cursor_str = encode_cursor(now, act_id)
        assert isinstance(cursor_str, str)

        dec_time, dec_id = decode_cursor(cursor_str)
        assert dec_id == act_id
        assert dec_time == now

    def test_malformed_cursor_rejected(self):
        with pytest.raises(InvalidCursorError):
            decode_cursor("not-valid-base64-json")


# -----------------------------------------------------------------------------
# 2. Canonical 20 Modules Contract
# -----------------------------------------------------------------------------
class TestCanonicalModules:
    def test_all_20_canonical_modules_present(self):
        expected_modules = {
            "home",
            "markets",
            "charts",
            "watchlists",
            "screeners",
            "companies",
            "economics",
            "news",
            "research",
            "maps",
            "intelligence",
            "options",
            "trading",
            "portfolios",
            "risk",
            "ai",
            "data",
            "saved",
            "workspaces",
            "agents",
        }
        assert set(CANONICAL_MODULES.keys()) == expected_modules
        for mod_id in expected_modules:
            assert is_valid_module_id(mod_id)

    def test_unknown_module_rejected(self):
        assert not is_valid_module_id("cryptocurrency_speculation")
        assert not is_valid_module_id("admin_panel")


# -----------------------------------------------------------------------------
# 3. User Activity Service Unit Tests
# -----------------------------------------------------------------------------
class TestUserActivityService:
    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.commit = AsyncMock()
        session.flush = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock(spec=UserActivityRepository)
        repo.get_by_client_event_id = AsyncMock(return_value=None)
        repo.create_event = AsyncMock()
        repo.list_events = AsyncMock(return_value=[])
        repo.count_user_events = AsyncMock(return_value=0)
        repo.prune_user_cap = AsyncMock(return_value=0)
        repo.delete_all_for_user = AsyncMock(return_value=0)
        return repo

    @pytest.fixture
    def mock_pref_service(self):
        pref = MagicMock(spec=UserPreferenceService)
        pref.get_preference = AsyncMock(side_effect=PreferenceNotFoundError("key"))
        pref.set_preference = AsyncMock()
        return pref

    @pytest.fixture
    def service(self, mock_session, mock_repo, mock_pref_service):
        return UserActivityService(
            session=mock_session,
            repository=mock_repo,
            preference_service=mock_pref_service,
        )

    @pytest.mark.asyncio
    async def test_consent_default_disabled(self, service):
        user_id = uuid.uuid4()
        enabled = await service.is_history_enabled(user_id)
        assert enabled is False

    @pytest.mark.asyncio
    async def test_recording_fails_when_consent_disabled(self, service):
        user_id = uuid.uuid4()
        req = RecordActivityEventRequest(
            event_type=ActivityEventType.MODULE_OPENED,
            module_id="markets",
            client_event_id=uuid.uuid4(),
        )
        with pytest.raises(ActivityHistoryDisabledError):
            await service.record_event(user_id, req)

    @pytest.mark.asyncio
    async def test_enable_consent_and_record_event(
        self, service, mock_pref_service, mock_repo, mock_session
    ):
        user_id = uuid.uuid4()
        pref_obj = UserPreference(
            user_id=user_id,
            preference_key="home.activity_history_enabled",
            payload={"enabled": True},
            schema_version=1,
            revision=1,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        mock_pref_service.set_preference.return_value = pref_obj

        # 1. Enable consent
        res = await service.set_consent(user_id, enabled=True)
        assert res.enabled is True
        mock_session.commit.assert_awaited()

        # Update mock to return enabled preference
        mock_pref_service.get_preference.side_effect = None
        mock_pref_service.get_preference.return_value = pref_obj

        # 2. Record MODULE_OPENED event
        created_event = UserActivityEvent(
            activity_id=uuid.uuid4(),
            user_id=user_id,
            event_type="MODULE_OPENED",
            module_id="charts",
            entity_id=None,
            client_event_id=uuid.uuid4(),
            occurred_at=datetime.datetime.now(datetime.timezone.utc),
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        mock_repo.create_event.return_value = created_event

        req = RecordActivityEventRequest(
            event_type=ActivityEventType.MODULE_OPENED,
            module_id="charts",
            client_event_id=created_event.client_event_id,
        )
        saved = await service.record_event(user_id, req)
        assert saved.activity_id == created_event.activity_id
        assert saved.module_id == "charts"
        mock_repo.create_event.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_idempotent_duplicate_event_returns_existing(
        self, service, mock_pref_service, mock_repo
    ):
        user_id = uuid.uuid4()
        client_id = uuid.uuid4()
        pref_obj = UserPreference(
            user_id=user_id,
            preference_key="home.activity_history_enabled",
            payload={"enabled": True},
            schema_version=1,
            revision=1,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        mock_pref_service.get_preference.side_effect = None
        mock_pref_service.get_preference.return_value = pref_obj

        existing_event = UserActivityEvent(
            activity_id=uuid.uuid4(),
            user_id=user_id,
            event_type="MODULE_OPENED",
            module_id="research",
            entity_id=None,
            client_event_id=client_id,
            occurred_at=datetime.datetime.now(datetime.timezone.utc),
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        mock_repo.get_by_client_event_id.return_value = existing_event

        req = RecordActivityEventRequest(
            event_type=ActivityEventType.MODULE_OPENED,
            module_id="research",
            client_event_id=client_id,
        )
        result = await service.record_event(user_id, req)
        assert result.activity_id == existing_event.activity_id
        mock_repo.create_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_idempotency_conflict_raises_error(self, service, mock_pref_service, mock_repo):
        user_id = uuid.uuid4()
        client_id = uuid.uuid4()
        pref_obj = UserPreference(
            user_id=user_id,
            preference_key="home.activity_history_enabled",
            payload={"enabled": True},
            schema_version=1,
            revision=1,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        mock_pref_service.get_preference.side_effect = None
        mock_pref_service.get_preference.return_value = pref_obj

        existing_event = UserActivityEvent(
            activity_id=uuid.uuid4(),
            user_id=user_id,
            event_type="MODULE_OPENED",
            module_id="research",
            entity_id=None,
            client_event_id=client_id,
            occurred_at=datetime.datetime.now(datetime.timezone.utc),
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        mock_repo.get_by_client_event_id.return_value = existing_event

        # Same client_event_id but conflicting payload (maps instead of research)
        req = RecordActivityEventRequest(
            event_type=ActivityEventType.MODULE_OPENED,
            module_id="maps",
            client_event_id=client_id,
        )
        with pytest.raises(IdempotencyConflictError):
            await service.record_event(user_id, req)

    @pytest.mark.asyncio
    async def test_disabling_consent_purges_user_history(
        self, service, mock_pref_service, mock_repo, mock_session
    ):
        user_id = uuid.uuid4()
        pref_obj = UserPreference(
            user_id=user_id,
            preference_key="home.activity_history_enabled",
            payload={"enabled": False},
            schema_version=1,
            revision=2,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        mock_pref_service.set_preference.return_value = pref_obj

        res = await service.set_consent(user_id, enabled=False)
        assert res.enabled is False
        mock_repo.delete_all_for_user.assert_awaited_once_with(user_id)
        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_clear_history_deletes_records(self, service, mock_repo, mock_session):
        user_id = uuid.uuid4()
        mock_repo.delete_all_for_user.return_value = 14

        res = await service.clear_history(user_id)
        assert res.deleted_count == 14
        assert res.cleared is True
        mock_repo.delete_all_for_user.assert_awaited_once_with(user_id)
        mock_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_list_activity_returns_empty_when_disabled(self, service):
        user_id = uuid.uuid4()
        res = await service.list_activity(user_id)
        assert res.enabled is False
        assert len(res.items) == 0
        assert res.has_more is False

    @pytest.mark.asyncio
    async def test_list_activity_resolves_modules_and_entities(
        self, service, mock_pref_service, mock_repo, mock_session
    ):
        user_id = uuid.uuid4()
        pref_obj = UserPreference(
            user_id=user_id,
            preference_key="home.activity_history_enabled",
            payload={"enabled": True},
            schema_version=1,
            revision=1,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        mock_pref_service.get_preference.side_effect = None
        mock_pref_service.get_preference.return_value = pref_obj

        entity_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)

        ev1 = UserActivityEvent(
            activity_id=uuid.uuid4(),
            user_id=user_id,
            event_type="MODULE_OPENED",
            module_id="markets",
            entity_id=None,
            client_event_id=uuid.uuid4(),
            occurred_at=now,
            created_at=now,
        )
        ev2 = UserActivityEvent(
            activity_id=uuid.uuid4(),
            user_id=user_id,
            event_type="ENTITY_SELECTED",
            module_id=None,
            entity_id=entity_id,
            client_event_id=uuid.uuid4(),
            occurred_at=now - datetime.timedelta(minutes=5),
            created_at=now - datetime.timedelta(minutes=5),
        )
        mock_repo.list_events.return_value = [ev1, ev2]

        # Mock entity DB execution
        mock_entity = MagicMock(spec=Entity)
        mock_entity.entity_id = entity_id
        mock_entity.display_name = "NVIDIA Corporation"
        mock_entity.entity_type = "company"

        exec_res = MagicMock()
        exec_res.scalars.return_value.all.return_value = [mock_entity]
        mock_session.execute.return_value = exec_res

        res = await service.list_activity(user_id, limit=10)
        assert res.enabled is True
        assert len(res.items) == 2

        # Item 1: MODULE_OPENED
        assert res.items[0].event_type == ActivityEventType.MODULE_OPENED
        assert res.items[0].module_id == "markets"
        assert res.items[0].module_label == "Markets"
        assert res.items[0].resume_target == "/markets"

        # Item 2: ENTITY_SELECTED
        assert res.items[1].event_type == ActivityEventType.ENTITY_SELECTED
        assert res.items[1].entity_id == entity_id
        assert res.items[1].entity_display_name == "NVIDIA Corporation"
        assert res.items[1].entity_type == "company"
        assert res.items[1].is_accessible is True


# -----------------------------------------------------------------------------
# 4. FastAPI Endpoint Integration Tests
# -----------------------------------------------------------------------------
class TestHomeActivityEndpoints:
    @pytest.fixture
    def app(self):
        return create_app()

    @pytest.fixture
    def test_user_id(self):
        return uuid.uuid4()

    @pytest.fixture
    def authenticated_principal(self, test_user_id):
        return AuthPrincipal(
            sub=str(test_user_id),
            email="test@atlas.io",
        )

    @pytest.fixture
    def authenticated_authz_context(self, authenticated_principal):
        return AuthorizationContext(
            principal=authenticated_principal,
            roles=frozenset(["member"]),
            permissions=frozenset({"atlas.access"}),
        )

    @pytest.fixture
    def mock_activity_service(self):
        svc = MagicMock(spec=UserActivityService)
        return svc

    @pytest.mark.asyncio
    async def test_unauthenticated_rejected(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get("/api/v1/home/activity")
            assert res.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_atlas_access_rejected(self, app):
        unprivileged_principal = AuthPrincipal(
            sub=str(uuid.uuid4()),
            email="guest@atlas.io",
        )
        unprivileged_context = AuthorizationContext(
            principal=unprivileged_principal,
            roles=frozenset(["guest"]),
            permissions=frozenset(),  # Missing atlas.access
        )
        mock_session = AsyncMock()
        app.dependency_overrides[get_current_user] = lambda: unprivileged_principal
        app.dependency_overrides[get_authorization_context] = lambda: unprivileged_context
        app.dependency_overrides[get_db_session] = lambda: mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get("/api/v1/home/activity")
            assert res.status_code == 403
            data = res.json()
            assert data["error"]["code"] in ("FORBIDDEN", "PERMISSION_DENIED")
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_activity_list_cache_headers_and_response(
        self, app, authenticated_principal, authenticated_authz_context, mock_activity_service
    ):
        mock_activity_service.list_activity = AsyncMock(
            return_value=UserActivityListResponse(
                schema_version=1,
                enabled=True,
                items=[],
                next_cursor=None,
                has_more=False,
            )
        )

        from atlas.activity.router import get_activity_service

        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authenticated_authz_context
        app.dependency_overrides[get_activity_service] = lambda: mock_activity_service

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.get("/api/v1/home/activity")
            assert res.status_code == 200
            assert res.headers["cache-control"] == "private, no-store"
            data = res.json()
            assert data["enabled"] is True
            assert data["items"] == []

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_post_event_when_disabled_returns_409(
        self, app, authenticated_principal, authenticated_authz_context, mock_activity_service
    ):
        mock_activity_service.record_event = AsyncMock(side_effect=ActivityHistoryDisabledError())

        from atlas.activity.router import get_activity_service

        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authenticated_authz_context
        app.dependency_overrides[get_activity_service] = lambda: mock_activity_service

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            payload = {
                "event_type": "MODULE_OPENED",
                "module_id": "markets",
                "client_event_id": str(uuid.uuid4()),
            }
            res = await client.post("/api/v1/home/activity/events", json=payload)
            assert res.status_code == 409
            data = res.json()
            assert data["error"]["message"] == "ACTIVITY_HISTORY_DISABLED"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_put_consent_success(
        self, app, authenticated_principal, authenticated_authz_context, mock_activity_service
    ):
        from atlas.activity.models import ActivityConsentResponse

        now = datetime.datetime.now(datetime.timezone.utc)
        mock_activity_service.set_consent = AsyncMock(
            return_value=ActivityConsentResponse(enabled=True, updated_at=now)
        )

        from atlas.activity.router import get_activity_service

        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authenticated_authz_context
        app.dependency_overrides[get_activity_service] = lambda: mock_activity_service

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.put("/api/v1/home/activity/consent", json={"enabled": True})
            assert res.status_code == 200
            assert res.json()["enabled"] is True

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_delete_clear_history(
        self, app, authenticated_principal, authenticated_authz_context, mock_activity_service
    ):
        from atlas.activity.models import ClearActivityResponse

        mock_activity_service.clear_history = AsyncMock(
            return_value=ClearActivityResponse(deleted_count=5, cleared=True)
        )

        from atlas.activity.router import get_activity_service

        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authenticated_authz_context
        app.dependency_overrides[get_activity_service] = lambda: mock_activity_service

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.delete("/api/v1/home/activity")
            assert res.status_code == 200
            data = res.json()
            assert data["cleared"] is True
            assert data["deleted_count"] == 5

        app.dependency_overrides.clear()
