import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.providers.health.db_models import ProviderHealthCheck, ProviderHealthState
from atlas.providers.health.models import (
    ProviderHealthCheckResult,
    ProviderHealthTargetType,
)

class ProviderHealthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_integration_state(self, provider_key: str) -> Optional[ProviderHealthState]:
        stmt = select(ProviderHealthState).where(
            ProviderHealthState.provider_key == provider_key,
            ProviderHealthState.target_type == ProviderHealthTargetType.INTEGRATION.value,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_configuration_state(self, configuration_id: UUID) -> Optional[ProviderHealthState]:
        stmt = select(ProviderHealthState).where(
            ProviderHealthState.configuration_id == configuration_id,
            ProviderHealthState.target_type == ProviderHealthTargetType.CONFIGURATION.value,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def upsert_state(self, state: ProviderHealthState) -> ProviderHealthState:
        # Check if exists
        if state.target_type == ProviderHealthTargetType.INTEGRATION.value:
            existing = await self.get_integration_state(state.provider_key)
        else:
            existing = await self.get_configuration_state(state.configuration_id) # type: ignore

        if existing:
            # Update existing
            existing.status = state.status
            existing.coverage = state.coverage
            existing.components = state.components
            existing.checked_at = state.checked_at
            existing.last_success_at = state.last_success_at
            existing.last_failure_at = state.last_failure_at
            existing.latency_ms = state.latency_ms
            existing.consecutive_successes = state.consecutive_successes
            existing.consecutive_failures = state.consecutive_failures
            existing.probe_version = state.probe_version
            self.session.add(existing)
            return existing
        else:
            # Insert new
            self.session.add(state)
            return state

    async def append_check(self, check: ProviderHealthCheck) -> ProviderHealthCheck:
        self.session.add(check)
        return check

    async def list_history(
        self,
        provider_key: str,
        target_type: ProviderHealthTargetType,
        configuration_id: Optional[UUID] = None,
        limit: int = 25,
    ) -> list[ProviderHealthCheck]:
        stmt = select(ProviderHealthCheck).where(
            ProviderHealthCheck.provider_key == provider_key,
            ProviderHealthCheck.target_type == target_type.value,
        ).order_by(ProviderHealthCheck.started_at.desc()).limit(limit)

        if target_type == ProviderHealthTargetType.CONFIGURATION:
            if not configuration_id:
                raise ValueError("configuration_id is required for configuration history")
            stmt = stmt.where(ProviderHealthCheck.configuration_id == configuration_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def prune_history_before(self, cutoff: datetime.datetime) -> int:
        stmt = delete(ProviderHealthCheck).where(ProviderHealthCheck.started_at < cutoff)
        result = await self.session.execute(stmt)
        return result.rowcount or 0
