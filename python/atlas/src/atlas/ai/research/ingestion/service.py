"""Document Ingestion Service for Stage 127 AI Research (Part IX)."""

from __future__ import annotations

import hashlib
import uuid
from typing import Optional

from atlas.ai.research.domain import (
    DocumentIndexingStatus,
    DocumentParsingStatus,
    ResearchDocument,
    ResearchDocumentRevision,
)
from atlas.ai.research.ingestion.chunking import chunk_document_text
from atlas.ai.research.ingestion.indexing_jobs import IngestionJobManager, ResearchIngestionJob
from atlas.ai.research.source_registry import AtlasResearchSourceRegistry


class DocumentIngestionService:
    """Orchestrates document ingestion, chunking, and registration."""

    def __init__(
        self,
        registry: Optional[AtlasResearchSourceRegistry] = None,
    ) -> None:
        self.registry = registry or AtlasResearchSourceRegistry.get_instance()

    async def ingest_document(
        self,
        source_id: str,
        title: str,
        document_type: str,
        publication_date: str,
        content_text: str,
        user_id: str,
        tenant_id: str,
        symbol: Optional[str] = None,
        company_id: Optional[str] = None,
        filing_date: Optional[str] = None,
        access_tier: str = "PUBLIC",
    ) -> ResearchIngestionJob:
        """Executes full document ingestion pipeline."""
        job_id = f"job_ingest_{uuid.uuid4().hex[:12]}"
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        rev_id = f"rev_{doc_id}_1"

        job = IngestionJobManager.create_job(
            job_id=job_id,
            document_id=doc_id,
            revision_id=rev_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )

        try:
            # 1. Update parsing status
            IngestionJobManager.update_job(job_id, parsing_status=DocumentParsingStatus.PARSING)

            content_hash = hashlib.sha256(content_text.encode()).hexdigest()

            # 2. Extract and Chunk
            IngestionJobManager.update_job(
                job_id,
                parsing_status=DocumentParsingStatus.EXTRACTED,
                indexing_status=DocumentIndexingStatus.CHUNKING,
            )
            chunks = chunk_document_text(
                document_id=doc_id,
                revision_id=rev_id,
                raw_text=content_text,
            )

            # 3. Create Document and Revision
            doc = ResearchDocument(
                document_id=doc_id,
                source_id=source_id,
                title=title,
                document_type=document_type,
                publication_date=publication_date,
                company_id=company_id,
                symbol=symbol,
                filing_date=filing_date or publication_date,
                access_tier=access_tier,
                owner_user_id=user_id if access_tier == "USER_PRIVATE" else None,
                tenant_id=tenant_id,
                content_hash=content_hash,
            )
            rev = ResearchDocumentRevision(
                revision_id=rev_id,
                document_id=doc_id,
                revision_number=1,
                effective_date=publication_date,
                as_of_date=publication_date,
                content_hash=content_hash,
            )

            # 4. Register with Source Registry
            self.registry.register_document(
                document=doc,
                revisions=[rev],
                chunks_by_revision={rev_id: chunks},
            )

            IngestionJobManager.update_job(
                job_id,
                indexing_status=DocumentIndexingStatus.INDEXED,
                chunks_count=len(chunks),
            )
            return job

        except Exception as exc:
            IngestionJobManager.update_job(
                job_id,
                indexing_status=DocumentIndexingStatus.FAILED,
                error_message=str(exc),
            )
            raise
