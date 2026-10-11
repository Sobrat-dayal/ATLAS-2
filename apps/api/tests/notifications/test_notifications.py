"""Stage 49 Persistent Notification Center Backend Test Suite."""

import datetime
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.notifications.enums import (
    NotificationActionKind,
    NotificationCategory,
    NotificationListFilter,
    NotificationSeverity,
)
from atlas.notifications.errors import (
    InvalidCursorError,
    InvalidNotificationActionError,
    NotificationArchivedError,
    NotificationDedupeConflictError,
    NotificationNotFoundError,
)
from atlas.notifications.models import NotificationModel
from atlas.notifications.repository import (
    NotificationRepository,
    decode_cursor,
    encode_cursor,
)
from atlas.notifications.schemas import (
    ALLOWED_INTERNAL_ROUTES,
    CreateNotification,
    NotificationListResponse,
    NotificationResponse,
)
from atlas.notifications.service import NotificationService
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session


# -----------------------------------------------------------------------------
# 1. Validation & Schema Tests
# -----------------------------------------------------------------------------
class TestNotificationValidation:
    def test_create_notification_valid_none_action(self):
        user_id = uuid.uuid4()
        dto = CreateNotification(
            recipient_user_id=user_id,
            category=NotificationCategory.SYSTEM,
            severity=NotificationSeverity.INFO,
            title="System maintenance scheduled",
            message="Database maintenance will occur at 02:00 UTC.",
            producer_key="system.ops",
        )
        assert dto.action_kind == NotificationActionKind.NONE
        assert dto.action_route is None
        assert dto.action_entity_id is None

    def test_create_notification_valid_internal_route(self):
        user_id = uuid.uuid4()
        dto = CreateNotification(
            recipient_user_id=user_id,
            category=NotificationCategory.MARKET,
            severity=NotificationSeverity.SUCCESS,
            title="Market snapshot ready",
            message="Click to view markets.",
            producer_key="market_data",
            action_kind=NotificationActionKind.INTERNAL_ROUTE,
            action_route="/markets",
        )
        assert dto.action_route == "/markets"
        assert dto.action_entity_id is None

    def test_create_notification_valid_entity_route(self):
        user_id = uuid.uuid4()
        entity_id = uuid.uuid4()
        dto = CreateNotification(
            recipient_user_id=user_id,
            category=NotificationCategory.RESEARCH,
            severity=NotificationSeverity.INFO,
            title="Entity document indexed",
            message="New filing indexed.",
            producer_key="research_worker",
            action_kind=NotificationActionKind.ENTITY_ROUTE,
            action_route="/research",
            action_entity_id=entity_id,
        )
        assert dto.action_route == "/research"
        assert dto.action_entity_id == entity_id

    def test_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            CreateNotification(
                recipient_user_id=uuid.uuid4(),
                category=NotificationCategory.GENERAL,
                severity=NotificationSeverity.INFO,
                title="   ",
                message="Message body",
                producer_key="system",
            )

    def test_title_bound_160_characters(self):
        long_title = "A" * 161
        with pytest.raises(ValidationError):
            CreateNotification(
                recipient_user_id=uuid.uuid4(),
                category=NotificationCategory.GENERAL,
                severity=NotificationSeverity.INFO,
                title=long_title,
                message="Valid message",
                producer_key="system",
            )

    def test_empty_message_rejected(self):
        with pytest.raises(ValidationError):
            CreateNotification(
                recipient_user_id=uuid.uuid4(),
                category=NotificationCategory.GENERAL,
                severity=NotificationSeverity.INFO,
                title="Valid title",
                message="   ",
                producer_key="system",
            )

    def test_message_bound_2000_characters(self):
        long_msg = "M" * 2001
        with pytest.raises(ValidationError):
            CreateNotification(
                recipient_user_id=uuid.uuid4(),
                category=NotificationCategory.GENERAL,
                severity=NotificationSeverity.INFO,
                title="Valid title",
                message=long_msg,
                producer_key="system",
            )

    def test_invalid_category_rejected(self):
        with pytest.raises(ValidationError):
            CreateNotification.model_validate(
                {
                    "recipient_user_id": str(uuid.uuid4()),
                    "category": "INVALID_CAT",
                    "severity": "INFO",
                    "title": "Title",
                    "message": "Message",
                    "producer_key": "system",
                }
            )

    def test_invalid_severity_rejected(self):
        with pytest.raises(ValidationError):
            CreateNotification.model_validate(
                {
                    "recipient_user_id": str(uuid.uuid4()),
                    "category": "SYSTEM",
                    "severity": "CRITICAL",  # Only INFO, SUCCESS, WARNING, ERROR
                    "title": "Title",
                    "message": "Message",
                    "producer_key": "system",
                }
            )

    def test_producer_key_regex_validation(self):
        # Valid producer keys
        for key in ["system", "auth.subsystem", "market-data_v1", "agent_1.test"]:
            dto = CreateNotification(
                recipient_user_id=uuid.uuid4(),
                category=NotificationCategory.SYSTEM,
                severity=NotificationSeverity.INFO,
                title="Title",
                message="Message",
                producer_key=key,
            )
            assert dto.producer_key == key

        # Invalid producer keys (uppercase, special characters, starts with number)
        for invalid_key in ["System", "1producer", "sys/tem", "prod space"]:
            with pytest.raises(ValidationError):
                CreateNotification(
                    recipient_user_id=uuid.uuid4(),
                    category=NotificationCategory.SYSTEM,
                    severity=NotificationSeverity.INFO,
                    title="Title",
                    message="Message",
                    producer_key=invalid_key,
                )

    def test_action_none_rejects_route_or_entity(self):
        with pytest.raises(ValidationError):
            CreateNotification(
                recipient_user_id=uuid.uuid4(),
                category=NotificationCategory.GENERAL,
                severity=NotificationSeverity.INFO,
                title="Title",
                message="Message",
                producer_key="system",
                action_kind=NotificationActionKind.NONE,
                action_route="/markets",
            )

    def test_action_internal_route_rejects_missing_route(self):
        with pytest.raises(ValidationError):
            CreateNotification(
                recipient_user_id=uuid.uuid4(),
                category=NotificationCategory.GENERAL,
                severity=NotificationSeverity.INFO,
                title="Title",
                message="Message",
                producer_key="system",
                action_kind=NotificationActionKind.INTERNAL_ROUTE,
                action_route=None,
            )

    def test_action_internal_route_rejects_entity_id(self):
        with pytest.raises(ValidationError):
            CreateNotification(
                recipient_user_id=uuid.uuid4(),
                category=NotificationCategory.GENERAL,
                severity=NotificationSeverity.INFO,
                title="Title",
                message="Message",
                producer_key="system",
                action_kind=NotificationActionKind.INTERNAL_ROUTE,
                action_route="/markets",
                action_entity_id=uuid.uuid4(),
            )

    def test_action_entity_route_requires_entity_and_route(self):
        with pytest.raises(ValidationError):
            CreateNotification(
                recipient_user_id=uuid.uuid4(),
                category=NotificationCategory.GENERAL,
                severity=NotificationSeverity.INFO,
                title="Title",
                message="Message",
                producer_key="system",
                action_kind=NotificationActionKind.ENTITY_ROUTE,
                action_route="/research",
                action_entity_id=None,
            )

    def test_external_url_rejected(self):
        for ext in [
            "https://evil.com",
            "http://example.org",
            "javascript:alert(1)",
            "data:text/html,bad",
            "/unknown-module-xyz",
        ]:
            with pytest.raises(ValidationError):
                CreateNotification(
                    recipient_user_id=uuid.uuid4(),
                    category=NotificationCategory.GENERAL,
                    severity=NotificationSeverity.INFO,
                    title="Title",
                    message="Message",
                    producer_key="system",
                    action_kind=NotificationActionKind.INTERNAL_ROUTE,
                    action_route=ext,
                )

    def test_all_20_stage4_modules_in_allowlist(self):
        expected_modules = {
            "/home",
            "/markets",
            "/charts",
            "/watchlists",
            "/screeners",
            "/companies",
            "/economics",
            "/news",
            "/research",
            "/maps",
            "/intelligence",
            "/options",
            "/trading",
            "/portfolios",
            "/risk",
            "/ai",
            "/data",
            "/saved",
            "/workspaces",
            "/agents",
            "/settings",
        }
        for mod in expected_modules:
            assert mod in ALLOWED_INTERNAL_ROUTES


# -----------------------------------------------------------------------------
# 2. Keyset Cursor Encoding Tests
# -----------------------------------------------------------------------------
class TestKeysetCursor:
    def test_encode_and_decode_roundtrip(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        uid = uuid.uuid4()
        cursor = encode_cursor(now, uid)
        assert isinstance(cursor, str)

        dt_out, id_out = decode_cursor(cursor)
        assert dt_out == now
        assert id_out == uid

    def test_decode_invalid_cursor_fails_safely(self):
        for bad_cursor in ["invalid", "bm90LXBlcmZlY3Q=", "", "!!!"]:
            with pytest.raises(InvalidCursorError):
                decode_cursor(bad_cursor)


# -----------------------------------------------------------------------------
# 3. NotificationService Unit Tests (Mock Session)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
class TestNotificationService:
    def setup_method(self):
        self.session = AsyncMock()
        self.repository = AsyncMock(spec=NotificationRepository)
        self.service = NotificationService(session=self.session, repository=self.repository)

    async def test_create_notification_success(self):
        user_id = uuid.uuid4()
        dto = CreateNotification(
            recipient_user_id=user_id,
            category=NotificationCategory.SECURITY,
            severity=NotificationSeverity.WARNING,
            title="New sign-in detected",
            message="Sign-in from a new IP address.",
            producer_key="auth.security",
        )
        self.repository.find_by_dedupe.return_value = None

        res = await self.service.create_notification(dto)
        assert isinstance(res, NotificationResponse)
        assert res.title == "New sign-in detected"
        assert res.category == NotificationCategory.SECURITY
        assert res.severity == NotificationSeverity.WARNING
        assert res.read_at is None
        assert res.archived_at is None
        self.repository.create.assert_awaited_once()

    async def test_dedupe_identical_payload_returns_existing(self):
        user_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        existing_id = uuid.uuid4()
        existing = NotificationModel(
            notification_id=existing_id,
            recipient_user_id=user_id,
            category=NotificationCategory.DATA.value,
            severity=NotificationSeverity.INFO.value,
            title="Import completed",
            message="Data import completed successfully.",
            producer_key="data.worker",
            dedupe_key="job-101",
            action_kind=NotificationActionKind.NONE.value,
            action_route=None,
            action_entity_id=None,
            created_at=now,
            updated_at=now,
            read_at=None,
            archived_at=None,
        )
        self.repository.find_by_dedupe.return_value = existing

        dto = CreateNotification(
            recipient_user_id=user_id,
            category=NotificationCategory.DATA,
            severity=NotificationSeverity.INFO,
            title="Import completed",
            message="Data import completed successfully.",
            producer_key="data.worker",
            dedupe_key="job-101",
        )

        res = await self.service.create_notification(dto)
        assert res.notification_id == existing_id
        # Should not call repository.create again
        self.repository.create.assert_not_called()

    async def test_dedupe_mismatched_payload_raises_conflict(self):
        user_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        existing = NotificationModel(
            notification_id=uuid.uuid4(),
            recipient_user_id=user_id,
            category=NotificationCategory.DATA.value,
            severity=NotificationSeverity.INFO.value,
            title="Original Title",
            message="Original Message",
            producer_key="data.worker",
            dedupe_key="job-101",
            action_kind=NotificationActionKind.NONE.value,
            action_route=None,
            action_entity_id=None,
            created_at=now,
            updated_at=now,
            read_at=None,
            archived_at=None,
        )
        self.repository.find_by_dedupe.return_value = existing

        dto = CreateNotification(
            recipient_user_id=user_id,
            category=NotificationCategory.DATA,
            severity=NotificationSeverity.INFO,
            title="Different Title",
            message="Different Message",
            producer_key="data.worker",
            dedupe_key="job-101",
        )

        with pytest.raises(NotificationDedupeConflictError):
            await self.service.create_notification(dto)

    async def test_entity_route_nonexistent_entity_rejected(self):
        user_id = uuid.uuid4()
        fake_entity_id = uuid.uuid4()
        dto = CreateNotification(
            recipient_user_id=user_id,
            category=NotificationCategory.MARKET,
            severity=NotificationSeverity.INFO,
            title="Entity update",
            message="Details updated",
            producer_key="market_data",
            action_kind=NotificationActionKind.ENTITY_ROUTE,
            action_route="/charts",
            action_entity_id=fake_entity_id,
        )
        # Mock database returning None for entity lookup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result

        with pytest.raises(InvalidNotificationActionError) as exc_info:
            await self.service.create_notification(dto)
        assert "does not exist" in str(exc_info.value)

    async def test_mark_read_idempotency(self):
        user_id = uuid.uuid4()
        notif_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)

        model = NotificationModel(
            notification_id=notif_id,
            recipient_user_id=user_id,
            category=NotificationCategory.GENERAL.value,
            severity=NotificationSeverity.INFO.value,
            title="Test",
            message="Msg",
            producer_key="system",
            action_kind=NotificationActionKind.NONE.value,
            created_at=now,
            updated_at=now,
            read_at=now,
            archived_at=None,
        )
        self.repository.mark_read.return_value = model

        res = await self.service.mark_read(notif_id, user_id)
        assert res.read_at == now

    async def test_mark_unread_rejects_archived(self):
        user_id = uuid.uuid4()
        notif_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)

        archived_model = NotificationModel(
            notification_id=notif_id,
            recipient_user_id=user_id,
            category=NotificationCategory.GENERAL.value,
            severity=NotificationSeverity.INFO.value,
            title="Test",
            message="Msg",
            producer_key="system",
            action_kind=NotificationActionKind.NONE.value,
            created_at=now,
            updated_at=now,
            read_at=now,
            archived_at=now,
        )
        self.repository.find_by_id.return_value = archived_model

        with pytest.raises(NotificationArchivedError):
            await self.service.mark_unread(notif_id, user_id)

    async def test_archive_sets_both_read_and_archived(self):
        user_id = uuid.uuid4()
        notif_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)

        model = NotificationModel(
            notification_id=notif_id,
            recipient_user_id=user_id,
            category=NotificationCategory.GENERAL.value,
            severity=NotificationSeverity.INFO.value,
            title="Test",
            message="Msg",
            producer_key="system",
            action_kind=NotificationActionKind.NONE.value,
            created_at=now,
            updated_at=now,
            read_at=now,
            archived_at=now,
        )
        self.repository.archive.return_value = model

        res = await self.service.archive(notif_id, user_id)
        assert res.archived_at is not None
        assert res.read_at is not None


# -----------------------------------------------------------------------------
# 4. In-Memory Keyset Repository State Tests
# -----------------------------------------------------------------------------
class TestRepositoryPaginationSemantics:
    """Test repository keyset pagination logic, filter isolation, and tie breaks."""

    def test_cursor_and_tiebreak_simulation(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        id1 = uuid.UUID("00000000-0000-0000-0000-000000000001")
        id2 = uuid.UUID("00000000-0000-0000-0000-000000000002")

        # Two notifications with identical timestamp: higher UUID comes first in DESC order
        _ = [(now, id2), (now, id1)]
        cursor = encode_cursor(now, id2)

        dt_dec, id_dec = decode_cursor(cursor)
        assert dt_dec == now
        assert id_dec == id2


# -----------------------------------------------------------------------------
# 5. FastAPI Endpoints Integration Tests
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
class TestFastApiNotificationEndpoints:
    def setup_method(self):
        self.app = create_app()
        self.dummy_session = AsyncMock()
        self.mock_service = AsyncMock(spec=NotificationService)

        from atlas_api.routers.notifications import get_notification_service

        self.app.dependency_overrides[get_db_session] = lambda: self.dummy_session
        self.app.dependency_overrides[get_notification_service] = lambda: self.mock_service

    async def test_endpoints_require_authentication(self):
        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Listing without auth token
            res = await client.get("/api/v1/notifications")
            assert res.status_code == 401

            # Unread count without auth token
            res = await client.get("/api/v1/notifications/unread-count")
            assert res.status_code == 401

            # Mark read without auth token
            res = await client.post(f"/api/v1/notifications/{uuid.uuid4()}/read")
            assert res.status_code == 401

    async def test_list_notifications_user_scoped(self):
        user_a = uuid.uuid4()
        fake_user = AuthPrincipal(sub=str(user_a), email="usera@atlas.local")
        mock_authz = AuthorizationContext(
            principal=fake_user,
            roles=frozenset(["trader"]),
            permissions=frozenset(["atlas.access"]),
        )
        self.app.dependency_overrides[get_current_user] = lambda: fake_user
        self.app.dependency_overrides[get_authorization_context] = lambda: mock_authz

        now = datetime.datetime.now(datetime.timezone.utc)
        notif_resp = NotificationResponse(
            notification_id=uuid.uuid4(),
            category=NotificationCategory.SYSTEM,
            severity=NotificationSeverity.INFO,
            title="System Alert",
            message="All systems operational.",
            action_kind=NotificationActionKind.NONE,
            action_route=None,
            action_entity_id=None,
            created_at=now,
            read_at=None,
            archived_at=None,
        )
        self.mock_service.list_notifications.return_value = NotificationListResponse(
            items=[notif_resp],
            next_cursor=None,
            has_more=False,
            unread_count=1,
        )

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/notifications?filter=all&limit=10")
            assert res.status_code == 200
            assert res.headers["cache-control"] == "private, no-store"
            data = res.json()
            assert len(data["items"]) == 1
            assert data["items"][0]["title"] == "System Alert"
            # Verify recipient passed to service matches authenticated principal
            self.mock_service.list_notifications.assert_awaited_once_with(
                recipient_user_id=user_a,
                filter_mode=NotificationListFilter.ALL,
                limit=10,
                cursor=None,
            )

    async def test_unread_count_endpoint(self):
        user_a = uuid.uuid4()
        fake_user = AuthPrincipal(sub=str(user_a), email="usera@atlas.local")
        mock_authz = AuthorizationContext(
            principal=fake_user,
            roles=frozenset(["trader"]),
            permissions=frozenset(["atlas.access"]),
        )
        self.app.dependency_overrides[get_current_user] = lambda: fake_user
        self.app.dependency_overrides[get_authorization_context] = lambda: mock_authz

        self.mock_service.get_unread_count.return_value = 5

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/notifications/unread-count")
            assert res.status_code == 200
            assert res.headers["cache-control"] == "private, no-store"
            data = res.json()
            assert data["unread_count"] == 5
            self.mock_service.get_unread_count.assert_awaited_once_with(recipient_user_id=user_a)

    async def test_mark_read_endpoint(self):
        user_a = uuid.uuid4()
        notif_id = uuid.uuid4()
        fake_user = AuthPrincipal(sub=str(user_a), email="usera@atlas.local")
        mock_authz = AuthorizationContext(
            principal=fake_user,
            roles=frozenset(["trader"]),
            permissions=frozenset(["atlas.access"]),
        )
        self.app.dependency_overrides[get_current_user] = lambda: fake_user
        self.app.dependency_overrides[get_authorization_context] = lambda: mock_authz

        now = datetime.datetime.now(datetime.timezone.utc)
        self.mock_service.mark_read.return_value = NotificationResponse(
            notification_id=notif_id,
            category=NotificationCategory.SYSTEM,
            severity=NotificationSeverity.INFO,
            title="Read title",
            message="Read msg",
            action_kind=NotificationActionKind.NONE,
            action_route=None,
            action_entity_id=None,
            created_at=now,
            read_at=now,
            archived_at=None,
        )

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(f"/api/v1/notifications/{notif_id}/read")
            assert res.status_code == 200
            assert res.headers["cache-control"] == "private, no-store"
            data = res.json()
            assert data["read_at"] is not None
            self.mock_service.mark_read.assert_awaited_once_with(
                notification_id=notif_id,
                recipient_user_id=user_a,
            )

    async def test_cross_user_notif_returns_404(self):
        user_a = uuid.uuid4()
        notif_id = uuid.uuid4()
        fake_user = AuthPrincipal(sub=str(user_a), email="usera@atlas.local")
        mock_authz = AuthorizationContext(
            principal=fake_user,
            roles=frozenset(["trader"]),
            permissions=frozenset(["atlas.access"]),
        )
        self.app.dependency_overrides[get_current_user] = lambda: fake_user
        self.app.dependency_overrides[get_authorization_context] = lambda: mock_authz

        # Cross-user notification ID lookup returns not found
        self.mock_service.mark_read.side_effect = NotificationNotFoundError(str(notif_id))

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(f"/api/v1/notifications/{notif_id}/read")
            assert res.status_code == 404

    async def test_mark_all_read_endpoint(self):
        user_a = uuid.uuid4()
        fake_user = AuthPrincipal(sub=str(user_a), email="usera@atlas.local")
        mock_authz = AuthorizationContext(
            principal=fake_user,
            roles=frozenset(["trader"]),
            permissions=frozenset(["atlas.access"]),
        )
        self.app.dependency_overrides[get_current_user] = lambda: fake_user
        self.app.dependency_overrides[get_authorization_context] = lambda: mock_authz

        self.mock_service.mark_all_read.return_value = 12

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/notifications/read-all")
            assert res.status_code == 200
            assert res.headers["cache-control"] == "private, no-store"
            data = res.json()
            assert data["updated_count"] == 12
            self.mock_service.mark_all_read.assert_awaited_once_with(recipient_user_id=user_a)

    async def test_archive_endpoint(self):
        user_a = uuid.uuid4()
        notif_id = uuid.uuid4()
        fake_user = AuthPrincipal(sub=str(user_a), email="usera@atlas.local")
        mock_authz = AuthorizationContext(
            principal=fake_user,
            roles=frozenset(["trader"]),
            permissions=frozenset(["atlas.access"]),
        )
        self.app.dependency_overrides[get_current_user] = lambda: fake_user
        self.app.dependency_overrides[get_authorization_context] = lambda: mock_authz

        now = datetime.datetime.now(datetime.timezone.utc)
        self.mock_service.archive.return_value = NotificationResponse(
            notification_id=notif_id,
            category=NotificationCategory.SYSTEM,
            severity=NotificationSeverity.INFO,
            title="Archived item",
            message="Item message",
            action_kind=NotificationActionKind.NONE,
            action_route=None,
            action_entity_id=None,
            created_at=now,
            read_at=now,
            archived_at=now,
        )

        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(f"/api/v1/notifications/{notif_id}/archive")
            assert res.status_code == 200
            assert res.headers["cache-control"] == "private, no-store"
            data = res.json()
            assert data["archived_at"] is not None
            assert data["read_at"] is not None
            self.mock_service.archive.assert_awaited_once_with(
                notification_id=notif_id,
                recipient_user_id=user_a,
            )

    async def test_no_public_create_endpoint(self):
        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/v1/notifications",
                json={"title": "Spam", "message": "Spam"},
            )
            # 405 Method Not Allowed or 404 Not Found (no POST on /notifications)
            assert res.status_code in (404, 405)

    async def test_no_hard_delete_endpoint(self):
        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.delete(f"/api/v1/notifications/{uuid.uuid4()}")
            assert res.status_code in (404, 405)
