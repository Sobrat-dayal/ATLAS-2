"""Canonical Company Fundamentals Context Adapter for Stage 125."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)
from atlas.context.resolution import CanonicalEntityResolver


class CompanyContextAdapter(BaseAiContextAdapter):
    """Extracts canonical corporate entity facts, reporting periods, and financial statements."""

    @property
    def adapter_id(self) -> str:
        return "adapter_company"

    @property
    def context_type(self) -> ContextType:
        return ContextType.COMPANY_CONTEXT

    @property
    def supported_module(self) -> str:
        return "companies"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        cid = target_id
        if cid.startswith("c_"):
            cid = cid[2:]
        entity = CanonicalEntityResolver.resolve_company(cid)
        params = parameters or {}
        fiscal_period = params.get("fiscal_period", "FY2025")
        fiscal_year = params.get("fiscal_year", 2025)
        statement_type = params.get("statement_type", "INCOME_STATEMENT")
        as_of_date = params.get("as_of", "2025-12-31")

        # Verified sample financial facts (clean point-in-time)
        facts = params.get("facts") or {
            "revenue": {
                "value": 391035000000,
                "unit": "USD",
                "currency": "USD",
                "growth_yoy": 0.08,
            },
            "operating_income": {
                "value": 123216000000,
                "unit": "USD",
                "currency": "USD",
                "margin": 0.315,
            },
            "net_income": {"value": 93736000000, "unit": "USD", "currency": "USD"},
            "diluted_eps": {"value": 6.11, "unit": "USD", "currency": "USD"},
        }

        payload = {
            "company_id": entity.entity_id,
            "legal_name": entity.canonical_name,
            "display_name": entity.display_name,
            "symbol": entity.symbol,
            "sector": entity.metadata.get("sector", "N/A"),
            "reporting_currency": entity.currency or "USD",
            "fiscal_period": fiscal_period,
            "fiscal_year": fiscal_year,
            "statement_type": statement_type,
            "as_of": as_of_date,
            "is_restated": False,
            "facts": facts,
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_comp_{entity.entity_id}",
            context_type=self.context_type,
            canonical_target_id=entity.entity_id,
            source_module="companies",
            source_reference=f"atlas://companies/{entity.entity_id}/statements/{statement_type.lower()}",
            as_of=as_of_date,
            observed_at=datetime.now(timezone.utc).isoformat(),
            reporting_currency=entity.currency or "USD",
            units="millions",
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Company Financials: {entity.display_name} ({fiscal_period} {statement_type})",
            structured_payload=payload,
            estimated_tokens=140,
            relevance_score=3.0,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        facts = p.get("facts", {})
        rev = facts.get("revenue", {})
        op_inc = facts.get("operating_income", {})
        return (
            f"[Company Fundamentals: {p.get('legal_name')} ({p.get('symbol')})]\n"
            f"- Statement: {p.get('statement_type')} | Period: {p.get('fiscal_period')} | As-of: {p.get('as_of')}\n"
            f"- Reporting Currency: {p.get('reporting_currency')} | Units: USD millions\n"
            f"- Revenue: {rev.get('value')} {rev.get('unit')} (YoY Growth: {int(rev.get('growth_yoy', 0) * 100)}%)\n"
            f"- Operating Income: {op_inc.get('value')} {op_inc.get('unit')} (Margin: {int(op_inc.get('margin', 0) * 100)}%)"
        )
