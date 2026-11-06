"""
Marketplace Catalog and Publisher Registry Service for Stage 149.
Provides authentic discovery, search, filtering, and publisher verification
for institutional agents, teams, workflows, tools, and plugins without fabricated metrics.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from atlas.ecosystem.domain import (
    Publisher,
    VerificationStatus,
    utc_now,
)
from atlas.ecosystem.errors import EcosystemError


@dataclass(frozen=True, slots=True)
class MarketplaceItem:
    item_id: str
    kind: str  # AGENT, TEAM, WORKFLOW, TOOL, MCP, PLUGIN
    name: str
    description: str
    version: str
    category: str
    publisher_id: str
    publisher_name: str
    verification_status: VerificationStatus
    required_permissions: Tuple[str, ...]
    required_dependencies: Tuple[str, ...]
    license: str
    is_installed: bool = False
    created_at: datetime = field(default_factory=utc_now)


class MarketplaceService:
    """
    Institutional marketplace catalog and publisher registry.
    """

    def __init__(self) -> None:
        self._publishers: Dict[str, Publisher] = {}
        self._catalog: Dict[str, MarketplaceItem] = {}
        self._seed_publishers_and_catalog()

    def _seed_publishers_and_catalog(self) -> None:
        """Seeds authentic institutional publishers and initial catalog entries."""
        publishers = [
            Publisher(
                publisher_id="atlas-official",
                owner_id="system-owner",
                tenant_id="system-tenant",
                display_name="ATLAS Official Labs",
                description="Core AI research, financial intelligence, and quantitative engineering team.",
                verification_status=VerificationStatus.OFFICIAL_ATLAS,
                contact_email="ecosystem@atlas.internal",
            ),
            Publisher(
                publisher_id="sec-partner",
                owner_id="partner-sec",
                tenant_id="partner-tenant",
                display_name="Financial Regulatory Data Partners",
                description="Specialized in SEC EDGAR XBRL data models and company filings integration.",
                verification_status=VerificationStatus.VERIFIED_PARTNER,
                contact_email="filings@edgar-partner.org",
            ),
            Publisher(
                publisher_id="quant-lab",
                owner_id="partner-quant",
                tenant_id="partner-tenant",
                display_name="Quantitative Research Collective",
                description="Algorithmic trading frameworks and statistical risk model providers.",
                verification_status=VerificationStatus.VERIFIED_PARTNER,
                contact_email="connect@quant-lab.io",
            ),
        ]
        for pub in publishers:
            self._publishers[pub.publisher_id] = pub

        items = [
            MarketplaceItem(
                item_id="pkg.sec-filings-intelligence",
                kind="AGENT",
                name="SEC EDGAR Research Specialist",
                description="Source-grounded financial analyst for 10-K, 10-Q disclosures, footnotes, and risk factors.",
                version="1.2.0",
                category="Research & SEC",
                publisher_id="atlas-official",
                publisher_name="ATLAS Official Labs",
                verification_status=VerificationStatus.OFFICIAL_ATLAS,
                required_permissions=("tools:sec_read", "storage:research_read"),
                required_dependencies=("atlas.research.sec_filings_search",),
                license="MIT",
            ),
            MarketplaceItem(
                item_id="pkg.dcf-valuation-modeler",
                kind="AGENT",
                name="DCF & WACC Fundamental Modeler",
                description="Automated enterprise valuation deriving implied share prices from free cash flow projections.",
                version="1.0.0",
                category="Corporate Finance",
                publisher_id="atlas-official",
                publisher_name="ATLAS Official Labs",
                verification_status=VerificationStatus.OFFICIAL_ATLAS,
                required_permissions=("tools:calculate",),
                required_dependencies=("atlas.custom.discounted_cash_flow",),
                license="MIT",
            ),
            MarketplaceItem(
                item_id="mcp.sec-edgar-filings",
                kind="MCP",
                name="SEC EDGAR Financial Filings MCP",
                description="Streamable HTTP MCP connector for SEC EDGAR company facts, disclosures, and RSS feeds.",
                version="1.0.0",
                category="Regulatory Data",
                publisher_id="sec-partner",
                publisher_name="Financial Regulatory Data Partners",
                verification_status=VerificationStatus.VERIFIED_PARTNER,
                required_permissions=("mcp:connect",),
                required_dependencies=(),
                license="Apache-2.0",
            ),
            MarketplaceItem(
                item_id="plugin.macro-analytics",
                kind="PLUGIN",
                name="Global Macroeconomic Analytics Plugin",
                version="2.0.1",
                category="Macroeconomics",
                publisher_id="atlas-official",
                publisher_name="ATLAS Official Labs",
                verification_status=VerificationStatus.OFFICIAL_ATLAS,
                required_permissions=("tools:macro_read",),
                required_dependencies=(),
                license="Apache-2.0",
                description="Yield curve analytics, Federal Reserve policy trackers, and global CPI inflation metrics.",
            ),
            MarketplaceItem(
                item_id="team.equity-research-squad",
                kind="TEAM",
                name="Fundamental Equity Research Squad",
                description="Autonomous multi-agent team pairing a Coordinator, SEC Researcher, DCF Modeler, and Reviewer.",
                version="1.0.0",
                category="Multi-Agent Teams",
                publisher_id="atlas-official",
                publisher_name="ATLAS Official Labs",
                verification_status=VerificationStatus.OFFICIAL_ATLAS,
                required_permissions=("agents:teams",),
                required_dependencies=("pkg.sec-filings-intelligence", "pkg.dcf-valuation-modeler"),
                license="MIT",
            ),
        ]
        for item in items:
            self._catalog[item.item_id] = item

    # -----------------------------------------------------------------------
    # Publisher Management
    # -----------------------------------------------------------------------

    def register_publisher(
        self,
        *,
        publisher_id: str,
        owner_id: str,
        tenant_id: str,
        display_name: str,
        description: str,
        contact_email: str = "",
        verification_status: VerificationStatus = VerificationStatus.COMMUNITY,
    ) -> Publisher:
        pub = Publisher(
            publisher_id=publisher_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
            display_name=display_name,
            description=description,
            verification_status=verification_status,
            contact_email=contact_email,
        )
        self._publishers[publisher_id] = pub
        return pub

    def get_publisher(self, publisher_id: str) -> Publisher:
        pub = self._publishers.get(publisher_id)
        if not pub:
            raise EcosystemError(f"Publisher '{publisher_id}' was not found.")
        return pub

    def list_publishers(self) -> List[Publisher]:
        return list(self._publishers.values())

    # -----------------------------------------------------------------------
    # Catalog Search & Retrieval
    # -----------------------------------------------------------------------

    def search_catalog(
        self,
        query: Optional[str] = None,
        kind: Optional[str] = None,
        category: Optional[str] = None,
        publisher_id: Optional[str] = None,
    ) -> List[MarketplaceItem]:
        """
        Searches the institutional catalog. Never returns fabricated adoption stats or fake stars.
        """
        results = list(self._catalog.values())

        if kind:
            results = [i for i in results if i.kind.upper() == kind.upper()]

        if category:
            results = [i for i in results if category.lower() in i.category.lower()]

        if publisher_id:
            results = [i for i in results if i.publisher_id == publisher_id]

        if query:
            q_lower = query.lower()
            results = [
                i for i in results
                if q_lower in i.name.lower() or q_lower in i.description.lower() or q_lower in i.category.lower()
            ]

        return results

    def get_item(self, item_id: str) -> MarketplaceItem:
        item = self._catalog.get(item_id)
        if not item:
            raise EcosystemError(f"Marketplace item '{item_id}' was not found.")
        return item

