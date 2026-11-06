"""
Reusable Ecosystem Templates Service for Stage 149.
Provides preconfigured, institutional starter templates for Agents, Multi-Agent Teams,
and Visual Workflows that instantiate safely in DRAFT state without auto-execution.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from atlas.agents.domain import AgentDefinition
from atlas.agents.service import AgentRegistryService
from atlas.ecosystem.domain import EcosystemTemplate
from atlas.ecosystem.errors import EcosystemError


class EcosystemTemplateService:
    """
    Manages institutional agent, team, and workflow template registry.
    """

    def __init__(self, agent_service: Optional[AgentRegistryService] = None) -> None:
        self._agent_service = agent_service or AgentRegistryService()
        self._templates: Dict[str, EcosystemTemplate] = {}
        self._seed_templates()

    def _seed_templates(self) -> None:
        """Seeds institutional agent, team, and workflow templates."""
        templates = [
            # Agent Templates
            EcosystemTemplate(
                template_id="tmpl.agent.research_analyst",
                name="Institutional Research Analyst",
                description="Specialized in SEC EDGAR filings, 10-K risk factor extraction, and corporate earnings analysis.",
                kind="AGENT",
                version="1.0.0",
                category="Research & Intelligence",
                publisher_id="atlas-official",
                required_capabilities=("text-generation", "structured-output"),
                required_tools=("atlas.research.sec_filings_search",),
                required_permissions=("tools:sec_read",),
                default_payload={
                    "role": "RESEARCHER",
                    "model_id": "atlas-intelligence-v1",
                    "instructions": "You are an institutional research analyst. Synthesize SEC filings, management discussion, and footnotes with zero speculation.",
                    "execution_limits": {"max_tokens": 4096, "timeout_seconds": 30},
                },
            ),
            EcosystemTemplate(
                template_id="tmpl.agent.financial_modeler",
                name="DCF & Fundamental Valuation Modeler",
                description="Performs discounted cash flow, WACC, and multi-scenario fundamental valuations.",
                kind="AGENT",
                version="1.0.0",
                category="Corporate Finance",
                publisher_id="atlas-official",
                required_capabilities=("text-generation", "structured-output"),
                required_tools=("atlas.custom.discounted_cash_flow", "atlas.custom.wacc_calculator"),
                required_permissions=("tools:calculate",),
                default_payload={
                    "role": "ANALYST",
                    "model_id": "atlas-intelligence-v1",
                    "instructions": "You are a quantitative valuation modeler. Derive enterprise value, cost of capital, and equity value from cash flows.",
                    "execution_limits": {"max_tokens": 4096, "timeout_seconds": 30},
                },
            ),
            EcosystemTemplate(
                template_id="tmpl.agent.secops_reviewer",
                name="SecOps & Cybersecurity Code Auditor",
                description="Inspects software configurations, detects dependency vulnerabilities, and enforces least privilege.",
                kind="AGENT",
                version="1.0.0",
                category="Engineering & Security",
                publisher_id="atlas-official",
                required_capabilities=("text-generation", "code-inspection"),
                required_tools=(),
                required_permissions=("tools:audit",),
                default_payload={
                    "role": "SECURITY_REVIEWER",
                    "model_id": "atlas-reasoning-v1",
                    "instructions": "You are a SecOps auditor. Verify access controls, input sanitization, and cryptographic integrity.",
                    "execution_limits": {"max_tokens": 4096, "timeout_seconds": 30},
                },
            ),
            EcosystemTemplate(
                template_id="tmpl.agent.macro_economist",
                name="Global Macroeconomic Strategist",
                description="Analyzes Federal Reserve policy rates, CPI/PPI inflation trends, and sovereign yield curves.",
                kind="AGENT",
                version="1.0.0",
                category="Macroeconomics",
                publisher_id="atlas-official",
                required_capabilities=("text-generation", "structured-output"),
                required_tools=("atlas.research.macro_timeseries",),
                required_permissions=("tools:macro_read",),
                default_payload={
                    "role": "FINANCIAL_ANALYST",
                    "model_id": "atlas-intelligence-v1",
                    "instructions": "You are a global macro strategist. Formulate economic regimes based on central bank actions and real rates.",
                    "execution_limits": {"max_tokens": 4096, "timeout_seconds": 30},
                },
            ),

            # Team Templates
            EcosystemTemplate(
                template_id="tmpl.team.fundamental_equity",
                name="Fundamental Equity Research Squad",
                description="Collaborative team pairing an Executive Coordinator, SEC Filings Analyst, DCF Modeler, and Independent Reviewer.",
                kind="TEAM",
                version="1.0.0",
                category="Equity Research",
                publisher_id="atlas-official",
                required_capabilities=("multi-agent-collaboration",),
                required_tools=("atlas.research.sec_filings_search", "atlas.custom.discounted_cash_flow"),
                default_payload={
                    "objective": "Produce thorough equity research notes combining filings, DCF valuations, and peer comparisons.",
                    "budget_limit_usd": 150.0,
                    "max_concurrency": 4,
                    "review_required": True,
                    "roles_needed": ["COORDINATOR", "RESEARCHER", "ANALYST", "REVIEWER"],
                },
            ),
            EcosystemTemplate(
                template_id="tmpl.team.secops_governance",
                name="SecOps & Compliance Governance Team",
                description="Institutional multi-agent team enforcing code audits, access policy compliance, and audit trails.",
                kind="TEAM",
                version="1.0.0",
                category="Enterprise Governance",
                publisher_id="atlas-official",
                required_capabilities=("multi-agent-collaboration",),
                default_payload={
                    "objective": "Review architectural changes, verify security postures, and flag policy violations.",
                    "budget_limit_usd": 100.0,
                    "max_concurrency": 3,
                    "review_required": True,
                    "roles_needed": ["COORDINATOR", "SECURITY_REVIEWER", "REVIEWER"],
                },
            ),

            # Workflow Templates
            EcosystemTemplate(
                template_id="tmpl.workflow.sec_filings_pipeline",
                name="Automated SEC 10-K Ingestion & Analysis Flow",
                description="Visual graph pipeline: SEC EDGAR Trigger -> XBRL Facts Ingestion -> DCF Valuation -> PDF Research Report.",
                kind="WORKFLOW",
                version="1.0.0",
                category="Workflows",
                publisher_id="atlas-official",
                required_capabilities=("graph-execution",),
                default_payload={
                    "nodes": ["trigger-filing", "mcp-edgar-fetch", "custom-dcf-eval", "generate-brief"],
                    "entrypoint": "trigger-filing",
                },
            ),
        ]
        for t in templates:
            self._templates[t.template_id] = t

    def list_templates(self, kind: Optional[str] = None) -> List[EcosystemTemplate]:
        if kind:
            return [t for t in self._templates.values() if t.kind.upper() == kind.upper()]
        return list(self._templates.values())

    def get_template(self, template_id: str) -> EcosystemTemplate:
        template = self._templates.get(template_id)
        if not template:
            raise EcosystemError(f"Template '{template_id}' was not found.")
        return template

    def instantiate_agent(
        self,
        *,
        template_id: str,
        tenant_id: str,
        owner_id: str,
        custom_name: Optional[str] = None,
    ) -> AgentDefinition:
        """Instantiates an Agent from a template in DRAFT state (zero auto-execution)."""
        template = self.get_template(template_id)
        if template.kind != "AGENT":
            raise EcosystemError(f"Template '{template_id}' is a {template.kind}, not an AGENT template.")

        payload = template.default_payload
        name = custom_name or template.name
        agent = self._agent_service.create_agent(
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=name,
            description=template.description,
            role=payload.get("role", "RESEARCHER"),
            model_id=payload.get("model_id", "gpt-4o"),
            instructions=payload.get("instructions", "Follow institutional guidelines."),
            tool_ids=list(template.required_tools),
            execution_limits=payload.get("execution_limits", {"max_tokens": 4096}),
        )
        return agent

