"""Research Tool Adapters for Stage 126 and Stage 127 AI Tool Gateway.

Implements approved, permission-aware research adapters:
- atlas.research.list_metadata
- atlas.research.search_documents
- atlas.research.search_passages
- atlas.research.get_document_metadata
- atlas.research.get_authorized_excerpt
- atlas.research.compare_documents
- atlas.research.get_citation_source
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from atlas.ai.research.service import AtlasAiResearchService
from atlas.ai.tools.adapters.base import BaseAiToolAdapter, ToolExecutionContext
from atlas.ai.tools.domain import AtlasAiToolResult

CANONICAL_REPORTS = [
    {
        "report_id": "rep_2026_cloud_infra",
        "symbol": "MSFT",
        "title": "Hyperscale Cloud Infrastructure: Enterprise AI Unit Economics & Capex Trajectory",
        "author": "Victoria Chen, CFA",
        "published_at": "2026-10-15T09:00:00Z",
        "rating": "OUTPERFORM",
        "price_target": 480.0,
        "access_tier": "INSTITUTIONAL",
        "summary": "Deep-dive analysis of server cluster depreciation cycles and generative AI operating margins.",
    },
    {
        "report_id": "rep_2026_semi_foundry",
        "symbol": "NVDA",
        "title": "Silicon Packaging Architecture and High-Bandwidth Memory Supply Constraints",
        "author": "Marcus Sterling, PhD",
        "published_at": "2026-10-18T11:30:00Z",
        "rating": "OVERWEIGHT",
        "price_target": 165.0,
        "access_tier": "INSTITUTIONAL",
        "summary": "Assessment of next-generation packaging capacity and wafer-level interconnect yields.",
    },
]


class ResearchListMetadataAdapter(BaseAiToolAdapter):
    """Adapter for atlas.research.list_metadata."""

    tool_id = "atlas.research.list_metadata"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        query = str(arguments.get("query", "")).lower()
        symbol = str(arguments.get("symbol", "")).upper()
        limit = min(int(arguments.get("limit", 5)), 20)

        results: List[Dict[str, Any]] = []
        for rep in CANONICAL_REPORTS:
            if symbol and rep["symbol"] != symbol:
                continue
            if query and (
                query not in rep["title"].lower() and query not in rep["summary"].lower()
            ):
                continue
            results.append(rep)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"reports": results[:limit], "count": len(results[:limit])},
            data_source="ATLAS Equity Research Repository",
            attribution="ATLAS Global Institutional Research",
            record_count=len(results[:limit]),
            execution_time_ms=elapsed_ms,
        )


class ResearchSearchDocumentsAdapter(BaseAiToolAdapter):
    """Adapter for atlas.research.search_documents."""

    tool_id = "atlas.research.search_documents"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        service = AtlasAiResearchService.get_instance()
        symbol = arguments.get("symbol")
        doc_type = arguments.get("document_type")
        hist_as_of = arguments.get("historical_as_of")

        docs = service.list_authorized_documents(
            user_id=context.user_id,
            tenant_id=getattr(context, "tenant_id", "default_tenant"),
            symbol=symbol,
            document_type=doc_type,
            historical_as_of=hist_as_of,
        )
        data = [
            {
                "document_id": d.document_id,
                "title": d.title,
                "symbol": d.symbol,
                "document_type": d.document_type,
                "publication_date": d.publication_date,
                "access_tier": d.access_tier,
            }
            for d in docs
        ]
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"documents": data, "count": len(data)},
            data_source="ATLAS Research Document Registry",
            attribution="ATLAS Institutional Document Governance",
            record_count=len(data),
            execution_time_ms=elapsed_ms,
        )


class ResearchSearchPassagesAdapter(BaseAiToolAdapter):
    """Adapter for atlas.research.search_passages."""

    tool_id = "atlas.research.search_passages"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        service = AtlasAiResearchService.get_instance()
        query = str(arguments.get("query", ""))
        symbols = arguments.get("symbols")
        hist_as_of = arguments.get("historical_as_of")
        limit = min(int(arguments.get("limit", 5)), 15)

        evidence = await service.search_passages(
            query=query,
            user_id=context.user_id,
            tenant_id=getattr(context, "tenant_id", "default_tenant"),
            symbols=symbols,
            historical_as_of=hist_as_of,
            limit=limit,
        )
        data = [
            {
                "evidence_id": ev.evidence_id,
                "chunk_id": ev.chunk_id,
                "document_id": ev.document_id,
                "title": ev.title,
                "symbol": ev.symbol,
                "section_title": ev.section_title,
                "page_number": ev.page_number,
                "publication_date": ev.publication_date,
                "snippet": ev.context_snippet,
                "relevance_score": ev.relevance_score,
            }
            for ev in evidence
        ]
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"evidence": data, "count": len(data)},
            data_source="ATLAS Hybrid Evidence Index",
            attribution="ATLAS Institutional Research Intelligence",
            record_count=len(data),
            execution_time_ms=elapsed_ms,
        )


class ResearchGetDocumentMetadataAdapter(BaseAiToolAdapter):
    """Adapter for atlas.research.get_document_metadata."""

    tool_id = "atlas.research.get_document_metadata"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        service = AtlasAiResearchService.get_instance()
        doc_id = str(arguments.get("document_id", ""))

        doc = service.get_document_metadata(
            document_id=doc_id,
            user_id=context.user_id,
            tenant_id=getattr(context, "tenant_id", "default_tenant"),
        )
        data = {
            "document_id": doc.document_id,
            "title": doc.title,
            "source_id": doc.source_id,
            "document_type": doc.document_type,
            "publication_date": doc.publication_date,
            "symbol": doc.symbol,
            "company_id": doc.company_id,
            "access_tier": doc.access_tier,
            "content_hash": doc.content_hash,
        }
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data=data,
            data_source="ATLAS Document Metadata Registry",
            attribution="ATLAS Research Registry",
            record_count=1,
            execution_time_ms=elapsed_ms,
        )


class ResearchGetAuthorizedExcerptAdapter(BaseAiToolAdapter):
    """Adapter for atlas.research.get_authorized_excerpt."""

    tool_id = "atlas.research.get_authorized_excerpt"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        service = AtlasAiResearchService.get_instance()
        doc_id = str(arguments.get("document_id", ""))
        page_num = arguments.get("page_number")

        chunks = service.registry.get_chunks_for_document(
            document_id=doc_id,
            user_id=context.user_id,
            tenant_id=getattr(context, "tenant_id", "default_tenant"),
        )
        matched_chunks = [c for c in chunks if page_num is None or c.page_number == int(page_num)]
        excerpt = "\n\n".join(c.clean_text for c in matched_chunks)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data={"document_id": doc_id, "page_number": page_num, "excerpt": excerpt},
            data_source="ATLAS Document Passage Store",
            attribution="ATLAS Authorized Document Vault",
            record_count=len(matched_chunks),
            execution_time_ms=elapsed_ms,
        )


class ResearchCompareDocumentsAdapter(BaseAiToolAdapter):
    """Adapter for atlas.research.compare_documents."""

    tool_id = "atlas.research.compare_documents"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        service = AtlasAiResearchService.get_instance()
        doc_a = str(arguments.get("document_id_a", ""))
        doc_b = str(arguments.get("document_id_b", ""))

        comparison = await service.compare_documents(
            document_id_a=doc_a,
            document_id_b=doc_b,
            user_id=context.user_id,
            tenant_id=getattr(context, "tenant_id", "default_tenant"),
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data=comparison,
            data_source="ATLAS Multi-Document Comparative Synthesis",
            attribution="ATLAS Research Analysis",
            record_count=len(comparison.get("differences", [])),
            execution_time_ms=elapsed_ms,
        )


class ResearchGetCitationSourceAdapter(BaseAiToolAdapter):
    """Adapter for atlas.research.get_citation_source."""

    tool_id = "atlas.research.get_citation_source"

    async def execute(
        self,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
    ) -> AtlasAiToolResult:
        start_time = time.perf_counter()
        service = AtlasAiResearchService.get_instance()
        citation_id = str(arguments.get("citation_id", ""))

        resolved = service.resolve_citation(
            citation_id=citation_id,
            user_id=context.user_id,
            tenant_id=getattr(context, "tenant_id", "default_tenant"),
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self.build_result(
            context=context,
            data=resolved,
            data_source="ATLAS Verified Citation Registry",
            attribution="ATLAS Grounded Claim Validation",
            record_count=1,
            execution_time_ms=elapsed_ms,
        )
