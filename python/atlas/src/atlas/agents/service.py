"""Tenant-scoped agent registry and non-dispatching run ledger."""

from __future__ import annotations

import uuid
from dataclasses import replace
from typing import Any

from atlas.agents.domain import (
    AgentDefinition,
    AgentRun,
    AgentRunEvent,
    AgentRunStatus,
    AgentStatus,
    AgentVersion,
    utc_now,
)
from atlas.agents.errors import AgentNotFoundError, AgentValidationError
from atlas.ai.providers.registry import get_model_capability
from atlas.ai.tools.registry import AtlasAiToolRegistry


class AgentRegistryService:
    """In-memory registry used until durable agent repositories and workers exist."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentDefinition] = {}
        self._runs: dict[str, AgentRun] = {}

    def create_agent(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        name: str,
        description: str,
        role: str,
        model_id: str,
        instructions: str,
        tool_ids: list[str],
        execution_limits: dict[str, int],
    ) -> AgentDefinition:
        self._validate_configuration(model_id, tool_ids, execution_limits)
        now = utc_now()
        agent_id = str(uuid.uuid4())
        version = AgentVersion(
            version_id=str(uuid.uuid4()),
            agent_id=agent_id,
            version=1,
            model_id=model_id,
            instructions=instructions,
            tool_ids=tuple(sorted(set(tool_ids))),
            execution_limits=dict(execution_limits),
            created_at=now,
        )
        agent = AgentDefinition(
            agent_id=agent_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=name,
            description=description,
            role=role,
            status=AgentStatus.DRAFT,
            versions=(version,),
            created_at=now,
            updated_at=now,
        )
        self._agents[agent_id] = agent
        return agent

    def list_agents(self, *, tenant_id: str, owner_id: str) -> list[AgentDefinition]:
        return [
            agent
            for agent in self._agents.values()
            if agent.tenant_id == tenant_id and agent.owner_id == owner_id
        ]

    def get_agent(self, *, agent_id: str, tenant_id: str, owner_id: str) -> AgentDefinition:
        agent = self._agents.get(agent_id)
        if agent is None or agent.tenant_id != tenant_id or agent.owner_id != owner_id:
            raise AgentNotFoundError(f"Agent '{agent_id}' was not found.")
        return agent

    def publish_agent(self, *, agent_id: str, tenant_id: str, owner_id: str) -> AgentDefinition:
        agent = self.get_agent(agent_id=agent_id, tenant_id=tenant_id, owner_id=owner_id)
        updated = replace(agent, status=AgentStatus.PUBLISHED, updated_at=utc_now())
        self._agents[agent_id] = updated
        return updated

    def create_run(
        self,
        *,
        agent_id: str,
        tenant_id: str,
        owner_id: str,
        input_data: dict[str, Any],
    ) -> AgentRun:
        agent = self.get_agent(agent_id=agent_id, tenant_id=tenant_id, owner_id=owner_id)
        if agent.status is not AgentStatus.PUBLISHED:
            raise AgentValidationError("Only published agents can create runs.")
        version = agent.versions[-1]
        run_id = str(uuid.uuid4())
        created_at = utc_now()
        event = AgentRunEvent(
            event_id=str(uuid.uuid4()),
            run_id=run_id,
            event_type="RUN_QUEUED",
            created_at=created_at,
            metadata={"reason": "EXECUTION_WORKER_UNAVAILABLE"},
        )
        run = AgentRun(
            run_id=run_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            agent_id=agent_id,
            version_id=version.version_id,
            status=AgentRunStatus.QUEUED,
            execution_enabled=False,
            input=dict(input_data),
            created_at=created_at,
            events=(event,),
        )
        self._runs[run_id] = run
        return run

    def get_run(self, *, run_id: str, tenant_id: str, owner_id: str) -> AgentRun:
        run = self._runs.get(run_id)
        if run is None or run.tenant_id != tenant_id or run.owner_id != owner_id:
            raise AgentNotFoundError(f"Run '{run_id}' was not found.")
        return run

    @staticmethod
    def _validate_configuration(
        model_id: str,
        tool_ids: list[str],
        execution_limits: dict[str, int],
    ) -> None:
        try:
            get_model_capability(model_id)
        except Exception as exc:
            raise AgentValidationError(f"Model '{model_id}' is not eligible.") from exc

        registry = AtlasAiToolRegistry.get_instance()
        for tool_id in tool_ids:
            if not registry.is_registered(tool_id):
                raise AgentValidationError(f"Tool '{tool_id}' is not registered.")

        for key, value in execution_limits.items():
            if value < 0:
                raise AgentValidationError(f"Execution limit '{key}' must be non-negative.")
