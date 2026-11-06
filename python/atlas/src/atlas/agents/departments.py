"""Stage 148 AI Department Registry and Specialized Department Templates."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum

from atlas.agents.domain import utc_now
from atlas.agents.errors import DepartmentNotFoundError, DepartmentValidationError


class DepartmentStatus(StrEnum):
    DRAFT = "DRAFT"
    READY = "READY"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True, slots=True)
class DepartmentTemplate:
    template_id: str
    name: str
    description: str
    purpose: str
    recommended_roles: tuple[str, ...]
    default_tools: tuple[str, ...]
    knowledge_scope: str


DEPARTMENT_TEMPLATES: tuple[DepartmentTemplate, ...] = (
    DepartmentTemplate(
        template_id="executive_operations",
        name="Executive Operations",
        description="Goal breakdown, operational summaries, cross-team routing, and escalation management.",
        purpose="Coordinate cross-department strategic goals and enforce top-level policy governance.",
        recommended_roles=("COORDINATOR", "PLANNER", "PROJECT_MANAGER", "REVIEWER"),
        default_tools=("atlas_workspace_read", "atlas_governance_audit"),
        knowledge_scope="TENANT_SHARED",
    ),
    DepartmentTemplate(
        template_id="research_development",
        name="Research and Development",
        description="Scientific and technical literature review, source-grounded hypothesis analysis, prototype recommendations.",
        purpose="Conduct evidence-backed deep research, feasibility studies, and technical discovery.",
        recommended_roles=("COORDINATOR", "RESEARCHER", "ANALYST", "REVIEWER"),
        default_tools=("atlas_research_query", "atlas_document_intelligence"),
        knowledge_scope="DEPARTMENT_ONLY",
    ),
    DepartmentTemplate(
        template_id="software_engineering",
        name="Software Engineering",
        description="Requirements analysis, architecture review, implementation planning, code review, test planning.",
        purpose="Architect, review, and plan resilient software implementations within authorized repositories.",
        recommended_roles=("COORDINATOR", "DEVELOPER", "TESTER", "REVIEWER"),
        default_tools=("atlas_repo_inspect", "atlas_schema_validator"),
        knowledge_scope="DEPARTMENT_ONLY",
    ),
    DepartmentTemplate(
        template_id="quality_assurance",
        name="Quality Assurance",
        description="Test-case generation, regression review, defect triage, and acceptance verification.",
        purpose="Ensure platform stability, verify test evidence, and prevent false completion claims.",
        recommended_roles=("COORDINATOR", "TESTER", "REVIEWER"),
        default_tools=("atlas_test_analyzer", "atlas_schema_validator"),
        knowledge_scope="DEPARTMENT_ONLY",
    ),
    DepartmentTemplate(
        template_id="cybersecurity",
        name="Cybersecurity",
        description="Defensive security review, dependency vulnerability analysis, threat modeling, and configuration checks.",
        purpose="Analyze security architecture, audit dependencies, and prevent privilege escalation.",
        recommended_roles=("COORDINATOR", "SECURITY_REVIEWER", "REVIEWER"),
        default_tools=("atlas_security_audit", "atlas_dependency_checker"),
        knowledge_scope="DEPARTMENT_ONLY",
    ),
    DepartmentTemplate(
        template_id="marketing",
        name="Marketing",
        description="Campaign research, audience analysis, channel strategy, and draft content generation.",
        purpose="Plan data-driven marketing campaigns and evaluate audience engagement research.",
        recommended_roles=("COORDINATOR", "RESEARCHER", "WRITER", "ANALYST"),
        default_tools=("atlas_research_query",),
        knowledge_scope="DEPARTMENT_ONLY",
    ),
    DepartmentTemplate(
        template_id="content_media",
        name="Content and Media",
        description="Editorial planning, research, script drafting, review, and multi-platform publishing preparation.",
        purpose="Draft and review high-quality informational content with strict human-in-the-loop publishing approval.",
        recommended_roles=("COORDINATOR", "WRITER", "REVIEWER"),
        default_tools=("atlas_research_query",),
        knowledge_scope="DEPARTMENT_ONLY",
    ),
    DepartmentTemplate(
        template_id="sales_business_development",
        name="Sales and Business Development",
        description="Authorized prospect research, account analysis, outreach drafting, and pipeline summaries.",
        purpose="Prepare customer briefings, analyze business partnerships, and synthesize pipeline trends.",
        recommended_roles=("COORDINATOR", "ANALYST", "WRITER"),
        default_tools=("atlas_research_query",),
        knowledge_scope="DEPARTMENT_ONLY",
    ),
    DepartmentTemplate(
        template_id="business_intelligence",
        name="Business Intelligence",
        description="Market analysis, competitor analysis, industry trend summaries, and business-model comparison.",
        purpose="Synthesize company and industry competitive landscape from authorized financial intelligence.",
        recommended_roles=("COORDINATOR", "ANALYST", "RESEARCHER", "REVIEWER"),
        default_tools=("atlas_companies_read", "atlas_research_query"),
        knowledge_scope="TENANT_SHARED",
    ),
    DepartmentTemplate(
        template_id="financial_research",
        name="Financial Research",
        description="Market research, company fundamental analysis, macroeconomics, portfolio research, and risk evaluation.",
        purpose="Conduct disciplined financial research and simulated backtesting with strict live-trading prohibition.",
        recommended_roles=("COORDINATOR", "FINANCIAL_ANALYST", "ANALYST", "REVIEWER"),
        default_tools=("atlas_markets_read", "atlas_economics_read", "atlas_companies_read"),
        knowledge_scope="TENANT_SHARED",
    ),
    DepartmentTemplate(
        template_id="data_analytics",
        name="Data and Analytics",
        description="Data quality assessment, schema validation, statistical analysis, and operational reporting.",
        purpose="Validate source schemas, assess data pipelines, and compute rigorous statistical summaries.",
        recommended_roles=("COORDINATOR", "DATA_SPECIALIST", "ANALYST", "REVIEWER"),
        default_tools=("atlas_schema_validator", "atlas_data_analyzer"),
        knowledge_scope="TENANT_SHARED",
    ),
    DepartmentTemplate(
        template_id="design_ux",
        name="Design and User Experience",
        description="UI analysis, design-system review, accessibility checks, component specifications.",
        purpose="Review user flows, verify accessibility compliance, and plan component architectures.",
        recommended_roles=("COORDINATOR", "DESIGNER", "REVIEWER"),
        default_tools=("atlas_workspace_read",),
        knowledge_scope="DEPARTMENT_ONLY",
    ),
    DepartmentTemplate(
        template_id="customer_operations",
        name="Customer Operations",
        description="Support-ticket classification, FAQ research, issue escalation, and service quality summaries.",
        purpose="Triage operational issues, draft help documentation, and escalate blocking defects.",
        recommended_roles=("COORDINATOR", "GENERAL_SPECIALIST", "REVIEWER"),
        default_tools=("atlas_workspace_read",),
        knowledge_scope="DEPARTMENT_ONLY",
    ),
    DepartmentTemplate(
        template_id="finance_operations",
        name="Finance and Operations",
        description="Expense analysis, budget monitoring, cost reporting, and resource allocation recommendations.",
        purpose="Monitor workforce compute expenditures and ensure departmental budget conformance.",
        recommended_roles=("COORDINATOR", "FINANCIAL_ANALYST", "ANALYST"),
        default_tools=("atlas_governance_audit",),
        knowledge_scope="TENANT_SHARED",
    ),
    DepartmentTemplate(
        template_id="compliance_policy",
        name="Compliance and Policy Research",
        description="Policy research, regulatory change summaries, internal control documentation, and compliance checklists.",
        purpose="Verify that agent workflows adhere to legal, tenant, and data-protection boundaries.",
        recommended_roles=("COORDINATOR", "RESEARCHER", "REVIEWER"),
        default_tools=("atlas_governance_audit", "atlas_research_query"),
        knowledge_scope="TENANT_SHARED",
    ),
)


@dataclass(frozen=True, slots=True)
class DepartmentDefinition:
    department_id: str
    tenant_id: str
    owner_id: str
    name: str
    description: str
    purpose: str
    status: DepartmentStatus
    knowledge_scope: str = "DEPARTMENT_ONLY"
    budget_limit_usd: float = 500.0
    template_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


class DepartmentRegistryService:
    """Manages persistent AI Department registrations scoped to tenant and owner."""

    def __init__(self) -> None:
        self._departments: dict[str, DepartmentDefinition] = {}

    def create(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        name: str,
        description: str,
        purpose: str,
        knowledge_scope: str = "DEPARTMENT_ONLY",
        budget_limit_usd: float = 500.0,
        template_id: str | None = None,
    ) -> DepartmentDefinition:
        name_clean = name.strip()
        if not name_clean:
            raise DepartmentValidationError("Department name cannot be empty.")
        if budget_limit_usd < 0:
            raise DepartmentValidationError("Department budget limit cannot be negative.")
        
        now = utc_now()
        department = DepartmentDefinition(
            department_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=name_clean,
            description=description.strip(),
            purpose=purpose.strip() or description.strip() or name_clean,
            status=DepartmentStatus.DRAFT,
            knowledge_scope=knowledge_scope,
            budget_limit_usd=budget_limit_usd,
            template_id=template_id,
            created_at=now,
            updated_at=now,
        )
        self._departments[department.department_id] = department
        return department

    def create_from_template(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        template_id: str,
        budget_limit_usd: float = 500.0,
    ) -> DepartmentDefinition:
        tmpl = next((t for t in DEPARTMENT_TEMPLATES if t.template_id == template_id), None)
        if tmpl is None:
            raise DepartmentValidationError(f"Department template '{template_id}' was not found.")
        return self.create(
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=tmpl.name,
            description=tmpl.description,
            purpose=tmpl.purpose,
            knowledge_scope=tmpl.knowledge_scope,
            budget_limit_usd=budget_limit_usd,
            template_id=tmpl.template_id,
        )

    def list(self, *, tenant_id: str, owner_id: str) -> list[DepartmentDefinition]:
        return [
            d
            for d in self._departments.values()
            if d.tenant_id == tenant_id and d.owner_id == owner_id
        ]

    def get(self, *, department_id: str, tenant_id: str, owner_id: str) -> DepartmentDefinition:
        d = self._departments.get(department_id)
        if d is None or d.tenant_id != tenant_id or d.owner_id != owner_id:
            raise DepartmentNotFoundError(f"Department '{department_id}' was not found.")
        return d

    def update(
        self,
        *,
        department_id: str,
        tenant_id: str,
        owner_id: str,
        name: str | None = None,
        description: str | None = None,
        purpose: str | None = None,
        budget_limit_usd: float | None = None,
        knowledge_scope: str | None = None,
    ) -> DepartmentDefinition:
        dept = self.get(department_id=department_id, tenant_id=tenant_id, owner_id=owner_id)
        updates: dict = {"updated_at": utc_now()}
        if name is not None:
            if not name.strip():
                raise DepartmentValidationError("Department name cannot be empty.")
            updates["name"] = name.strip()
        if description is not None:
            updates["description"] = description.strip()
        if purpose is not None:
            updates["purpose"] = purpose.strip()
        if budget_limit_usd is not None:
            if budget_limit_usd < 0:
                raise DepartmentValidationError("Department budget limit cannot be negative.")
            updates["budget_limit_usd"] = budget_limit_usd
        if knowledge_scope is not None:
            updates["knowledge_scope"] = knowledge_scope

        updated = replace(dept, **updates)
        self._departments[department_id] = updated
        return updated

    def activate(self, *, department_id: str, tenant_id: str, owner_id: str) -> DepartmentDefinition:
        dept = self.get(department_id=department_id, tenant_id=tenant_id, owner_id=owner_id)
        activated = replace(dept, status=DepartmentStatus.ACTIVE, updated_at=utc_now())
        self._departments[department_id] = activated
        return activated

    def pause(self, *, department_id: str, tenant_id: str, owner_id: str) -> DepartmentDefinition:
        dept = self.get(department_id=department_id, tenant_id=tenant_id, owner_id=owner_id)
        paused = replace(dept, status=DepartmentStatus.PAUSED, updated_at=utc_now())
        self._departments[department_id] = paused
        return paused

    def disable(self, *, department_id: str, tenant_id: str, owner_id: str) -> DepartmentDefinition:
        dept = self.get(department_id=department_id, tenant_id=tenant_id, owner_id=owner_id)
        disabled = replace(dept, status=DepartmentStatus.DISABLED, updated_at=utc_now())
        self._departments[department_id] = disabled
        return disabled

    def get_templates(self) -> list[DepartmentTemplate]:
        return list(DEPARTMENT_TEMPLATES)
