"""Research Report Context Adapter for Stage 125."""

from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)
from atlas.ai.context.errors import AiContextTargetAccessDeniedError


class ResearchContextAdapter(BaseAiContextAdapter):
    """Extracts authorized research report revisions, methodology summaries, and bounded excerpts."""

    @property
    def adapter_id(self) -> str:
        return "adapter_research"

    @property
    def context_type(self) -> ContextType:
        return ContextType.RESEARCH_CONTEXT

    @property
    def supported_module(self) -> str:
        return "research"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        report_id = target_id or "rep_quant_momentum_alpha"

        # Permission check: verify report ownership or tenant entitlement
        allowed_users = params.get("allowed_users", [user_id])
        if user_id not in allowed_users and "ALL_TENANT" not in allowed_users:
            raise AiContextTargetAccessDeniedError("RESEARCH_REPORT", report_id)

        title = params.get(
            "title", "Multi-Factor Momentum & Volatility Decoupling in Large-Cap Equities"
        )
        version = params.get("version", "v1.2")
        review_status = params.get("review_status", "APPROVED")
        published_at = params.get("published_at", "2026-01-20T10:00:00Z")
        as_of = params.get("as_of", "2025-12-31")
        author = params.get("author", "Quantitative Research Desk")
        related = params.get("related_instruments", ["AAPL", "MSFT", "NVDA"])
        summary = params.get(
            "permitted_summary",
            "This empirical report investigates idiosyncratic momentum risk premia after volatility regime shifts. Analysis indicates robust Sharpe ratio expansion when filtering out top-quintile dispersion.",
        )

        payload = {
            "report_id": report_id,
            "title": title,
            "version": version,
            "review_status": review_status,
            "author": author,
            "published_at": published_at,
            "as_of": as_of,
            "related_instruments": related,
            "permitted_summary": summary,
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_res_{report_id}",
            context_type=self.context_type,
            canonical_target_id=report_id,
            source_module="research",
            source_reference=f"atlas://research/reports/{report_id}?rev={version}",
            as_of=as_of,
            source_updated_at=published_at,
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Research Report: '{title}' ({version}, {author})",
            structured_payload=payload,
            estimated_tokens=160,
            relevance_score=3.0,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        rel_str = ", ".join(p.get("related_instruments", []))
        return (
            f"[Authorized Research Report: '{p.get('title')}' ({p.get('version')})]\n"
            f"- Author: {p.get('author')} | Status: {p.get('review_status')} | Published: {p.get('published_at')}\n"
            f"- As-of Analysis Date: {p.get('as_of')} | Target Assets: {rel_str}\n"
            f"- Executive Summary Excerpt: {p.get('permitted_summary')}"
        )
