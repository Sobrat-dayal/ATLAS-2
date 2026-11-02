"""Stage 148 team-definition contracts and registry."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, replace
from enum import StrEnum

from atlas.agents.domain import AgentStatus
from atlas.agents.errors import AgentNotFoundError, AgentValidationError
from atlas.agents.service import AgentRegistryService


class TeamStatus(StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    DISABLED = "DISABLED"


class TeamRole(StrEnum):
    COORDINATOR = "COORDINATOR"
    SPECIALIST = "SPECIALIST"
    REVIEWER = "REVIEWER"


@dataclass(frozen=True, slots=True)
class TeamMember:
    agent_id: str
    role: TeamRole
    max_concurrency: int = 1


@dataclass(frozen=True, slots=True)
class TeamDefinition:
    team_id: str
    tenant_id: str
    owner_id: str
    name: str
    description: str
    objective: str
    status: TeamStatus
    members: tuple[TeamMember, ...]
    version: int = 1


class TeamRegistryService:
    """In-memory team registry until durable collaboration storage exists."""

    MAX_MEMBERS = 25

    def __init__(self, agents: AgentRegistryService) -> None:
        self._agents = agents
        self._teams: dict[str, TeamDefinition] = {}

    def create(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        name: str,
        description: str,
        objective: str,
        members: list[TeamMember],
    ) -> TeamDefinition:
        self._validate_members(members, tenant_id, owner_id)
        team = TeamDefinition(
            team_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=name,
            description=description,
            objective=objective,
            status=TeamStatus.DRAFT,
            members=tuple(members),
        )
        self._teams[team.team_id] = team
        return team

    def list(self, *, tenant_id: str, owner_id: str) -> list[TeamDefinition]:
        return [
            team
            for team in self._teams.values()
            if team.tenant_id == tenant_id and team.owner_id == owner_id
        ]

    def get(self, *, team_id: str, tenant_id: str, owner_id: str) -> TeamDefinition:
        team = self._teams.get(team_id)
        if team is None or team.tenant_id != tenant_id or team.owner_id != owner_id:
            raise AgentNotFoundError(f"Team '{team_id}' was not found.")
        return team

    def publish(self, *, team_id: str, tenant_id: str, owner_id: str) -> TeamDefinition:
        team = self.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
        self._validate_members(list(team.members), tenant_id, owner_id)
        published = replace(team, status=TeamStatus.PUBLISHED)
        self._teams[team_id] = published
        return published

    def disable(self, *, team_id: str, tenant_id: str, owner_id: str) -> TeamDefinition:
        team = self.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
        disabled = replace(team, status=TeamStatus.DISABLED)
        self._teams[team_id] = disabled
        return disabled

    def _validate_members(
        self, members: list[TeamMember], tenant_id: str, owner_id: str
    ) -> None:
        if not members:
            raise AgentValidationError("A team requires at least one member.")
        if len(members) > self.MAX_MEMBERS:
            raise AgentValidationError(f"A team cannot contain more than {self.MAX_MEMBERS} members.")
        if len({member.agent_id for member in members}) != len(members):
            raise AgentValidationError("An agent may appear only once in a team.")
        if sum(member.role is TeamRole.COORDINATOR for member in members) != 1:
            raise AgentValidationError("A team requires exactly one coordinator.")
        for member in members:
            if member.max_concurrency < 1:
                raise AgentValidationError("Member max_concurrency must be at least one.")
            agent = self._agents.get_agent(
                agent_id=member.agent_id,
                tenant_id=tenant_id,
                owner_id=owner_id,
            )
            if agent.status is not AgentStatus.PUBLISHED:
                raise AgentValidationError(
                    f"Agent '{member.agent_id}' must be published before team assignment."
                )
