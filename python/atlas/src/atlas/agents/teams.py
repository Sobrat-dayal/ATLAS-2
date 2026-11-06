"""Stage 148 team-definition contracts and registry with department integration and lifecycle controls."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum

from atlas.agents.domain import AgentStatus, utc_now
from atlas.agents.errors import AgentNotFoundError, AgentValidationError
from atlas.agents.service import AgentRegistryService


class TeamStatus(StrEnum):
    DRAFT = "DRAFT"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


class TeamRole(StrEnum):
    COORDINATOR = "COORDINATOR"
    SPECIALIST = "SPECIALIST"
    REVIEWER = "REVIEWER"
    PLANNER = "PLANNER"
    RESEARCHER = "RESEARCHER"
    ANALYST = "ANALYST"
    DEVELOPER = "DEVELOPER"
    TESTER = "TESTER"
    DESIGNER = "DESIGNER"
    WRITER = "WRITER"
    SECURITY_REVIEWER = "SECURITY_REVIEWER"
    PROJECT_MANAGER = "PROJECT_MANAGER"
    DATA_SPECIALIST = "DATA_SPECIALIST"
    FINANCIAL_ANALYST = "FINANCIAL_ANALYST"
    GENERAL_SPECIALIST = "GENERAL_SPECIALIST"


@dataclass(frozen=True, slots=True)
class TeamMember:
    agent_id: str
    role: TeamRole
    max_concurrency: int = 1
    capability_profile_id: str | None = None


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
    department_id: str | None = None
    coordinator_agent_id: str = ""
    budget_limit_usd: float = 100.0
    max_concurrency: int = 5
    review_required: bool = True
    execution_enabled: bool = False
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


class TeamRegistryService:
    """Team registry managing multi-agent teams, memberships, and versioned definitions."""

    MAX_MEMBERS = 25

    def __init__(self, agents: AgentRegistryService) -> None:
        self._agents = agents
        self._teams: dict[str, TeamDefinition] = {}
        # (team_id, version) -> TeamDefinition for immutable version pinned execution
        self._versions: dict[tuple[str, int], TeamDefinition] = {}

    def create(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        name: str,
        description: str,
        objective: str,
        members: list[TeamMember],
        department_id: str | None = None,
        budget_limit_usd: float = 100.0,
        max_concurrency: int = 5,
        review_required: bool = True,
    ) -> TeamDefinition:
        self._validate_members(members, tenant_id, owner_id)
        if budget_limit_usd < 0:
            raise AgentValidationError("Team budget limit must be non-negative.")

        coordinator_id = next(
            (m.agent_id for m in members if m.role == TeamRole.COORDINATOR), ""
        )
        now = utc_now()
        team = TeamDefinition(
            team_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=name.strip(),
            description=description.strip(),
            objective=objective.strip(),
            status=TeamStatus.DRAFT,
            members=tuple(members),
            version=1,
            department_id=department_id,
            coordinator_agent_id=coordinator_id,
            budget_limit_usd=budget_limit_usd,
            max_concurrency=max_concurrency,
            review_required=review_required,
            execution_enabled=False,
            created_at=now,
            updated_at=now,
        )
        self._teams[team.team_id] = team
        self._versions[(team.team_id, 1)] = team
        return team

    def list(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        department_id: str | None = None,
    ) -> list[TeamDefinition]:
        return [
            team
            for team in self._teams.values()
            if team.tenant_id == tenant_id
            and team.owner_id == owner_id
            and (department_id is None or team.department_id == department_id)
        ]

    def get(self, *, team_id: str, tenant_id: str, owner_id: str) -> TeamDefinition:
        team = self._teams.get(team_id)
        if team is None or team.tenant_id != tenant_id or team.owner_id != owner_id:
            raise AgentNotFoundError(f"Team '{team_id}' was not found.")
        return team

    def get_version(
        self, *, team_id: str, version: int, tenant_id: str, owner_id: str
    ) -> TeamDefinition:
        team = self._versions.get((team_id, version))
        if team is None or team.tenant_id != tenant_id or team.owner_id != owner_id:
            raise AgentNotFoundError(f"Team '{team_id}' version {version} was not found.")
        return team

    def update(
        self,
        *,
        team_id: str,
        tenant_id: str,
        owner_id: str,
        name: str | None = None,
        description: str | None = None,
        objective: str | None = None,
        members: list[TeamMember] | None = None,
        department_id: str | None = None,
        budget_limit_usd: float | None = None,
        max_concurrency: int | None = None,
    ) -> TeamDefinition:
        team = self.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
        updates: dict = {"updated_at": utc_now()}
        if name is not None:
            if not name.strip():
                raise AgentValidationError("Team name cannot be empty.")
            updates["name"] = name.strip()
        if description is not None:
            updates["description"] = description.strip()
        if objective is not None:
            updates["objective"] = objective.strip()
        if department_id is not None:
            updates["department_id"] = department_id
        if budget_limit_usd is not None:
            if budget_limit_usd < 0:
                raise AgentValidationError("Team budget limit must be non-negative.")
            updates["budget_limit_usd"] = budget_limit_usd
        if max_concurrency is not None:
            if max_concurrency < 1:
                raise AgentValidationError("max_concurrency must be at least 1.")
            updates["max_concurrency"] = max_concurrency
        if members is not None:
            self._validate_members(members, tenant_id, owner_id)
            updates["members"] = tuple(members)
            updates["coordinator_agent_id"] = next(
                (m.agent_id for m in members if m.role == TeamRole.COORDINATOR), ""
            )

        updated = replace(team, **updates)
        self._teams[team_id] = updated
        return updated

    def publish(self, *, team_id: str, tenant_id: str, owner_id: str) -> TeamDefinition:
        team = self.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
        self._validate_members(list(team.members), tenant_id, owner_id)
        published = replace(team, status=TeamStatus.PUBLISHED, updated_at=utc_now())
        self._teams[team_id] = published
        self._versions[(team_id, published.version)] = published
        return published

    def activate(self, *, team_id: str, tenant_id: str, owner_id: str) -> TeamDefinition:
        team = self.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
        self._validate_members(list(team.members), tenant_id, owner_id)
        activated = replace(team, status=TeamStatus.ACTIVE, updated_at=utc_now())
        self._teams[team_id] = activated
        self._versions[(team_id, activated.version)] = activated
        return activated

    def pause(self, *, team_id: str, tenant_id: str, owner_id: str) -> TeamDefinition:
        team = self.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
        paused = replace(team, status=TeamStatus.PAUSED, updated_at=utc_now())
        self._teams[team_id] = paused
        return paused

    def disable(self, *, team_id: str, tenant_id: str, owner_id: str) -> TeamDefinition:
        team = self.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
        disabled = replace(team, status=TeamStatus.DISABLED, updated_at=utc_now())
        self._teams[team_id] = disabled
        return disabled

    def create_version(
        self,
        *,
        team_id: str,
        tenant_id: str,
        owner_id: str,
        new_members: list[TeamMember] | None = None,
        new_objective: str | None = None,
    ) -> TeamDefinition:
        team = self.get(team_id=team_id, tenant_id=tenant_id, owner_id=owner_id)
        members = list(team.members) if new_members is None else new_members
        self._validate_members(members, tenant_id, owner_id)
        new_version = team.version + 1
        coordinator_id = next(
            (m.agent_id for m in members if m.role == TeamRole.COORDINATOR), ""
        )
        versioned = replace(
            team,
            version=new_version,
            members=tuple(members),
            objective=new_objective.strip() if new_objective else team.objective,
            coordinator_agent_id=coordinator_id,
            status=TeamStatus.DRAFT,
            updated_at=utc_now(),
        )
        self._teams[team_id] = versioned
        self._versions[(team_id, new_version)] = versioned
        return versioned

    def _validate_members(
        self, members: list[TeamMember], tenant_id: str, owner_id: str
    ) -> None:
        if not members:
            raise AgentValidationError("A team requires at least one member.")
        if len(members) > self.MAX_MEMBERS:
            raise AgentValidationError(
                f"A team cannot contain more than {self.MAX_MEMBERS} members."
            )
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
