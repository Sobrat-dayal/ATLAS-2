"""FastAPI Router for ATLAS Stage 127: AI Research and Retrieval-Augmented Generation.
Mounted under /api/v1/ai/research.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any, Dict, Optional

from atlas.ai.research.errors import (
    ResearchCitationAccessDeniedError,
    ResearchCitationInvalidError,
    ResearchCitationSourceMissingError,
    ResearchDocumentAccessDeniedError,
    ResearchDocumentNotFoundError,
    ResearchError,
)
from atlas.ai.research.ingestion.service import DocumentIngestionService
from atlas.ai.research.schemas import (
    DocumentComparisonRequest,
    DocumentComparisonResponse,
    IngestDocumentRequest,
    IngestDocumentResponse,
    ResearchAnswerResponse,
    ResearchCitationDTO,
    ResearchPassageDTO,
    ResearchQueryRequest,
    ResearchSearchRequest,
    ResearchSearchResponse,
    ResearchSourceManifestDTO,
)
from atlas.ai.research.service import AtlasAiResearchService
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/research", tags=["AI Research & RAG"])


@router.get("/sources")
async def list_research_sources(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Lists authorized research sources for the current user and tenant."""
    service = AtlasAiResearchService.get_instance()
    user_id = str(getattr(current_user, "sub", getattr(current_user, "id", "test_user")))
    tenant_id = getattr(current_user, "tenant_id", "default_tenant")

    sources = service.list_authorized_sources(user_id=user_id, tenant_id=tenant_id)
    return {
        "sources": [
            {
                "source_id": s.source_id,
                "name": s.name,
                "category": s.category.value,
                "licensing_class": s.licensing_class.value,
                "provider_disclosure": s.provider_disclosure.value,
                "publisher": s.publisher,
                "reliability_tier": s.reliability_tier,
                "created_at": s.created_at,
            }
            for s in sources
        ],
        "count": len(sources),
    }


@router.get("/documents")
async def list_research_documents(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    symbol: Optional[str] = Query(None, description="Filter by company ticker"),
    document_type: Optional[str] = Query(None, description="Filter by document type (e.g. '10-K')"),
    historical_as_of: Optional[str] = Query(None, description="Point-in-time ISO timestamp cutoff"),
) -> Dict[str, Any]:
    """Lists authorized research documents with historical vintage filtering."""
    service = AtlasAiResearchService.get_instance()
    user_id = str(getattr(current_user, "sub", getattr(current_user, "id", "test_user")))
    tenant_id = getattr(current_user, "tenant_id", "default_tenant")

    docs = service.list_authorized_documents(
        user_id=user_id,
        tenant_id=tenant_id,
        symbol=symbol,
        document_type=document_type,
        historical_as_of=historical_as_of,
    )
    return {
        "documents": [
            {
                "document_id": d.document_id,
                "source_id": d.source_id,
                "title": d.title,
                "document_type": d.document_type,
                "publication_date": d.publication_date,
                "company_id": d.company_id,
                "symbol": d.symbol,
                "filing_date": d.filing_date,
                "access_tier": d.access_tier,
                "created_at": d.created_at,
            }
            for d in docs
        ],
        "count": len(docs),
    }


@router.get("/documents/{document_id}")
async def get_research_document(
    document_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Retrieves document metadata enforcing access controls."""
    service = AtlasAiResearchService.get_instance()
    user_id = str(getattr(current_user, "sub", getattr(current_user, "id", "test_user")))
    tenant_id = getattr(current_user, "tenant_id", "default_tenant")

    try:
        doc = service.get_document_metadata(
            document_id=document_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )
        return {
            "document_id": doc.document_id,
            "source_id": doc.source_id,
            "title": doc.title,
            "document_type": doc.document_type,
            "publication_date": doc.publication_date,
            "company_id": doc.company_id,
            "symbol": doc.symbol,
            "filing_date": doc.filing_date,
            "period_end_date": doc.period_end_date,
            "access_tier": doc.access_tier,
            "content_hash": doc.content_hash,
            "created_at": doc.created_at,
        }
    except ResearchDocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research document '{document_id}' not found.",
        )
    except ResearchDocumentAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to research document is denied or revoked.",
        )


@router.post("/search", response_model=ResearchSearchResponse)
async def search_passages(
    payload: ResearchSearchRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ResearchSearchResponse:
    """Performs authorized hybrid passage retrieval across indexed documents."""
    service = AtlasAiResearchService.get_instance()
    user_id = str(getattr(current_user, "sub", getattr(current_user, "id", "test_user")))
    tenant_id = getattr(current_user, "tenant_id", "default_tenant")

    passages = await service.search_passages(
        query=payload.query,
        user_id=user_id,
        tenant_id=tenant_id,
        symbols=payload.symbols,
        document_types=payload.document_types,
        historical_as_of=payload.historical_as_of,
        date_start=payload.date_start,
        date_end=payload.date_end,
        strategy=payload.retrieval_strategy,
        limit=payload.limit,
    )

    dto_list = [
        ResearchPassageDTO(
            chunk_id=p.chunk_id,
            document_id=p.document_id,
            revision_id=p.revision_id,
            title=p.title,
            symbol=p.symbol,
            section_title=p.section_title,
            page_number=p.page_number,
            publication_date=p.publication_date,
            snippet=p.context_snippet,
            exact_span=p.exact_span,
            relevance_score=p.relevance_score,
            licensing_class=p.licensing_class,
            content_hash=p.content_hash,
        )
        for p in passages
    ]

    return ResearchSearchResponse(
        query=payload.query,
        total_hits=len(dto_list),
        retrieval_strategy=payload.retrieval_strategy,
        historical_as_of=payload.historical_as_of,
        passages=dto_list,
        execution_time_ms=12.5,
    )


@router.post("/query", response_model=ResearchAnswerResponse)
async def execute_research_query(
    payload: ResearchQueryRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ResearchAnswerResponse:
    """Executes grounded AI research workflow with claim citations."""
    service = AtlasAiResearchService.get_instance()
    user_id = str(getattr(current_user, "sub", getattr(current_user, "id", "test_user")))
    tenant_id = getattr(current_user, "tenant_id", "default_tenant")

    run = await service.execute_research_query(
        query=payload.query,
        user_id=user_id,
        tenant_id=tenant_id,
        symbols=payload.symbols,
        document_types=payload.document_types,
        historical_as_of=payload.historical_as_of,
        date_start=payload.date_start,
        date_end=payload.date_end,
        strategy=payload.retrieval_strategy,
        max_evidence_units=payload.max_evidence_units,
        token_budget=payload.token_budget,
        conversation_id=payload.conversation_id,
    )

    manifest_dto = None
    if run.evidence_manifest:
        manifest_dto = ResearchSourceManifestDTO(
            manifest_id=run.evidence_manifest.manifest_id,
            run_id=run.evidence_manifest.run_id,
            sources_used=run.evidence_manifest.sources_used,
            total_sources_evaluated=run.evidence_manifest.total_sources_evaluated,
            excluded_sources_count=run.evidence_manifest.excluded_sources_count,
            coverage_summary=run.evidence_manifest.coverage_summary,
            has_conflicting_sources=run.evidence_manifest.has_conflicting_sources,
            conflict_notes=run.evidence_manifest.conflict_notes,
        )

    citations_dto = [
        ResearchCitationDTO(
            citation_id=c.citation_id,
            evidence_id=c.evidence_id,
            document_id=c.document_id,
            symbol=c.symbol,
            title=c.title,
            page_number=c.page_number,
            section_title=c.section_title,
            publication_date=c.publication_date,
            claim_text=c.claim_text,
            quote_span=c.quote_span,
            status=c.status,
            validation_reason=c.validation_reason,
        )
        for c in run.citations
    ]

    return ResearchAnswerResponse(
        run_id=run.run_id,
        query=run.query,
        status=run.status,
        strategy=run.strategy,
        answer_text=run.answer_text,
        citations=citations_dto,
        evidence_manifest=manifest_dto,
        limitations=run.limitations,
        source_count=len(manifest_dto.sources_used) if manifest_dto else 0,
        execution_time_ms=run.execution_time_ms,
        historical_as_of=payload.historical_as_of,
        generated_at=run.started_at,
    )


@router.post("/compare", response_model=DocumentComparisonResponse)
async def compare_documents(
    payload: DocumentComparisonRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> DocumentComparisonResponse:
    """Performs structured comparison between two document revisions."""
    service = AtlasAiResearchService.get_instance()
    user_id = str(getattr(current_user, "sub", getattr(current_user, "id", "test_user")))
    tenant_id = getattr(current_user, "tenant_id", "default_tenant")

    try:
        res = await service.compare_documents(
            document_id_a=payload.document_id_a,
            document_id_b=payload.document_id_b,
            user_id=user_id,
            tenant_id=tenant_id,
            aspects=payload.aspects,
            historical_as_of=payload.historical_as_of,
        )
        return DocumentComparisonResponse(
            comparison_id=res["comparison_id"],
            document_a_title=res["document_a_title"],
            document_b_title=res["document_b_title"],
            document_a_date=res["document_a_date"],
            document_b_date=res["document_b_date"],
            differences=res["differences"],
            summary_text=res["summary_text"],
            citations=res["citations"],
            execution_time_ms=res["execution_time_ms"],
        )
    except ResearchDocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except ResearchDocumentAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to one or both comparison documents is denied or revoked.",
        )


@router.get("/citations/{citation_id}")
async def resolve_citation(
    citation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> Dict[str, Any]:
    """Resolves citation back to verified source excerpt with re-authorization."""
    service = AtlasAiResearchService.get_instance()
    user_id = str(getattr(current_user, "sub", getattr(current_user, "id", "test_user")))
    tenant_id = getattr(current_user, "tenant_id", "default_tenant")

    try:
        return service.resolve_citation(
            citation_id=citation_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )
    except ResearchCitationSourceMissingError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citation '{citation_id}' references non-existent or fabricated evidence.",
        )
    except ResearchCitationAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to underlying document for citation is revoked or denied.",
        )
    except ResearchCitationInvalidError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.post("/ingest", response_model=IngestDocumentResponse)
async def ingest_document(
    payload: IngestDocumentRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> IngestDocumentResponse:
    """Ingests and indexes document text into the research registry."""
    user_id = str(getattr(current_user, "sub", getattr(current_user, "id", "test_user")))
    tenant_id = getattr(current_user, "tenant_id", "default_tenant")
    service = DocumentIngestionService()

    try:
        job = await service.ingest_document(
            source_id=payload.source_id,
            title=payload.title,
            document_type=payload.document_type,
            publication_date=payload.publication_date,
            content_text=payload.content_text,
            user_id=user_id,
            tenant_id=tenant_id,
            symbol=payload.symbol,
            company_id=payload.company_id,
            filing_date=payload.filing_date,
            access_tier=payload.access_tier,
        )
        return IngestDocumentResponse(
            job_id=job.job_id,
            document_id=job.document_id,
            revision_id=job.revision_id,
            chunks_created=job.chunks_count,
            indexing_status=job.indexing_status.value,
            content_hash=job.job_id,
        )
    except ResearchError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
