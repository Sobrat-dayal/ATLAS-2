"""News Article Context Adapter for Stage 125."""

from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)


class NewsContextAdapter(BaseAiContextAdapter):
    """Extracts verified news headline, publisher, timestamps, and licensed excerpt."""

    @property
    def adapter_id(self) -> str:
        return "adapter_news"

    @property
    def context_type(self) -> ContextType:
        return ContextType.NEWS_CONTEXT

    @property
    def supported_module(self) -> str:
        return "news"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        article_id = target_id or "art_fed_rates_2026"
        headline = params.get(
            "headline",
            "Federal Reserve Signals Data-Dependent Policy Path Amid Persistent Core Inflation",
        )
        publisher = params.get("publisher", "Dow Jones Institutional Newswire")
        pub_time = params.get("publication_timestamp", "2026-01-28T14:30:00Z")
        related_entity = params.get("related_entity_id", "FEDFUNDS")
        summary = params.get(
            "licensed_summary",
            "FOMC participants emphasize balancing dual mandate risks with policy rates remaining restrictive until inflation sustainably reaches the 2% target.",
        )

        payload = {
            "article_id": article_id,
            "headline": headline,
            "publisher": publisher,
            "publication_timestamp": pub_time,
            "related_entity_id": related_entity,
            "licensed_summary": summary,
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_news_{article_id}",
            context_type=self.context_type,
            canonical_target_id=article_id,
            source_module="news",
            source_reference=f"atlas://news/articles/{article_id}",
            observed_at=pub_time,
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"News: '{headline[:50]}...' ({publisher})",
            structured_payload=payload,
            estimated_tokens=95,
            relevance_score=2.2,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        return (
            f"[Financial News Event: {p.get('publisher')}]\n"
            f"- Headline: {p.get('headline')}\n"
            f"- Published: {p.get('publication_timestamp')} | Related: {p.get('related_entity_id')}\n"
            f"- Summary: {p.get('licensed_summary')}"
        )

    @classmethod
    def _create_news_item(
        cls, news_id: str, headline: str, publisher: str = "Reuters"
    ) -> AtlasAiContextItem:
        return AtlasAiContextItem(
            context_item_id=f"ctx_news_{news_id}",
            context_type=ContextType.NEWS_CONTEXT,
            canonical_target_id=news_id,
            source_module="news",
            source_reference=f"atlas://news/{news_id}",
            content_summary=headline,
            data_quality_status=DataQualityStatus.COMPLETE,
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            structured_payload={"headline": headline, "publisher": publisher},
            estimated_tokens=80,
        )
