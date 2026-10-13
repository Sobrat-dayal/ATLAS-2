import json
import uuid
from typing import Any, Optional, Sequence

from .errors import (
    InvalidPreferenceKeyError,
    InvalidPreferencePayloadError,
    PreferenceConflictError,
    PreferenceNotFoundError,
    PreferenceTooLargeError,
    UnsupportedPreferenceVersionError,
)
from .models import UserPreference
from .repository import UserPreferenceRepository

# Canonical Registry of valid account-sync preferences
VALID_PREFERENCE_KEYS = {
    "global.general",
    "global.appearance",
    "global.accessibility",
    "home.activity_history_enabled",
    "section.home",
    "section.markets",
    "section.charts",
    "section.watchlists",
    "section.screeners",
    "section.companies",
    "section.economics",
    "section.news",
    "section.research",
    "section.maps",
    "section.intelligence",
    "section.options",
    "section.trading",
    "section.portfolios",
    "section.risk",
    "section.ai",
    "section.data",
    "section.saved",
    "section.workspaces",
    "section.agents",
}

MAX_PAYLOAD_SIZE_BYTES = 64 * 1024  # 64 KB


class UserPreferenceService:
    def __init__(self, repository: UserPreferenceRepository):
        self.repository = repository

    def _validate_key(self, key: str) -> None:
        if key not in VALID_PREFERENCE_KEYS:
            raise InvalidPreferenceKeyError(key)

    def _validate_payload(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise InvalidPreferencePayloadError("Payload must be a JSON object.")

        # Check size limits
        try:
            serialized = json.dumps(payload)
            if len(serialized.encode("utf-8")) > MAX_PAYLOAD_SIZE_BYTES:
                raise PreferenceTooLargeError()
        except Exception as e:
            if isinstance(e, PreferenceTooLargeError):
                raise
            raise InvalidPreferencePayloadError("Payload is not serializable.")

    def _validate_schema_version(self, version: int) -> None:
        if version < 1:
            raise UnsupportedPreferenceVersionError(version)

    async def list_preferences(self, user_id: uuid.UUID) -> Sequence[UserPreference]:
        return await self.repository.list_preferences(user_id)

    async def get_preference(self, user_id: uuid.UUID, key: str) -> UserPreference:
        self._validate_key(key)
        pref = await self.repository.get_preference(user_id, key)
        if not pref:
            raise PreferenceNotFoundError(key)
        return pref

    async def set_preference(
        self,
        user_id: uuid.UUID,
        key: str,
        schema_version: int,
        payload: dict[str, Any],
        expected_revision: Optional[int] = None,
    ) -> UserPreference:
        self._validate_key(key)
        self._validate_schema_version(schema_version)
        self._validate_payload(payload)

        # Update
        if expected_revision is not None:
            new_revision = await self.repository.update_preference(
                user_id, key, expected_revision, schema_version, payload
            )
            if new_revision is None:
                # Check if it even exists
                existing = await self.repository.get_preference(user_id, key)
                if not existing:
                    raise PreferenceNotFoundError(key)
                raise PreferenceConflictError(key)

            # Fetch the updated row to return it
            return await self.repository.get_preference(user_id, key)

        # Create
        existing = await self.repository.get_preference(user_id, key)
        if existing:
            raise PreferenceConflictError(key)

        return await self.repository.create_preference(user_id, key, schema_version, payload)

    async def delete_preference(self, user_id: uuid.UUID, key: str) -> None:
        self._validate_key(key)
        deleted = await self.repository.delete_preference(user_id, key)
        if not deleted:
            raise PreferenceNotFoundError(key)

    async def reset_all_preferences(self, user_id: uuid.UUID) -> int:
        return await self.repository.delete_all_preferences(user_id)
