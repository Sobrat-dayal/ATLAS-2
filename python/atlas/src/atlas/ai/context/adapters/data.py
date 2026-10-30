"""Data Catalog & Dataset Context Adapter for Stage 125."""

from typing import Any, Dict, Optional

from atlas.ai.context.adapters.base import BaseAiContextAdapter
from atlas.ai.context.domain import (
    AtlasAiContextItem,
    ContextType,
    DataQualityStatus,
    ProviderDisclosureStatus,
)


class DataContextAdapter(BaseAiContextAdapter):
    """Extracts master data catalog dataset schemas, column definitions, and quality metrics."""

    @property
    def adapter_id(self) -> str:
        return "adapter_data"

    @property
    def context_type(self) -> ContextType:
        return ContextType.DATA_CONTEXT

    @property
    def supported_module(self) -> str:
        return "data"

    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        params = parameters or {}
        dataset_id = target_id or "ds_crsp_daily_stock"
        name = params.get("dataset_name", "CRSP Daily Stock US")
        columns = params.get("columns", ["permno", "date", "ticker", "prc", "vol", "ret", "shrout"])
        row_count = params.get("row_count", 45000000)

        payload = {
            "dataset_id": dataset_id,
            "dataset_name": name,
            "schema_name": params.get("schema_name", "market_microstructure"),
            "columns": columns,
            "row_count": row_count,
            "data_frequency": params.get("data_frequency", "DAILY"),
            "source_provenance": params.get(
                "provenance", "Wharton Research Data Services (WRDS) / CRSP"
            ),
            "updated_at": params.get("updated_at", "2026-01-28T02:00:00Z"),
        }

        item = AtlasAiContextItem(
            context_item_id=f"ctx_data_{dataset_id}",
            context_type=self.context_type,
            canonical_target_id=dataset_id,
            source_module="data",
            source_reference=f"atlas://data/catalog/{dataset_id}",
            source_updated_at=payload["updated_at"],
            data_quality_status=DataQualityStatus.COMPLETE,
            permission_status="AUTHORIZED",
            model_disclosure_status=ProviderDisclosureStatus.ALLOWED,
            content_summary=f"Dataset: {name} ({row_count:,} records, {len(columns)} columns)",
            structured_payload=payload,
            estimated_tokens=85,
            relevance_score=2.0,
        )
        item.compute_content_hash()
        return item

    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        p = item.structured_payload
        cols_str = ", ".join(p.get("columns", []))
        return (
            f"[Data Platform Catalog: {p.get('dataset_name')} ({p.get('dataset_id')})]\n"
            f"- Schema: {p.get('schema_name')} | Frequency: {p.get('data_frequency')} | Row Count: {p.get('row_count'):,}\n"
            f"- Columns: {cols_str}\n"
            f"- Vendor Provenance: {p.get('source_provenance')}"
        )
