"""Document Revisions and Indexing Job Tracking for Ingestion."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from atlas.ai.research.domain import DocumentIndexingStatus, DocumentParsingStatus


@dataclass
class ResearchIngestionJob:
    """Async ingestion pipeline job descriptor."""

    job_id: str
    document_id: str
    revision_id: str
    user_id: str
    tenant_id: str
    parsing_status: DocumentParsingStatus = DocumentParsingStatus.PENDING
    indexing_status: DocumentIndexingStatus = DocumentIndexingStatus.PENDING
    chunks_count: int = 0
    error_message: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


class IngestionJobManager:
    """In-memory manager for tracking ingestion jobs."""

    _jobs: Dict[str, ResearchIngestionJob] = {}

    @classmethod
    def create_job(
        cls,
        job_id: str,
        document_id: str,
        revision_id: str,
        user_id: str,
        tenant_id: str,
    ) -> ResearchIngestionJob:
        job = ResearchIngestionJob(
            job_id=job_id,
            document_id=document_id,
            revision_id=revision_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )
        cls._jobs[job_id] = job
        return job

    @classmethod
    def get_job(cls, job_id: str) -> Optional[ResearchIngestionJob]:
        return cls._jobs.get(job_id)

    @classmethod
    def update_job(
        cls,
        job_id: str,
        parsing_status: Optional[DocumentParsingStatus] = None,
        indexing_status: Optional[DocumentIndexingStatus] = None,
        chunks_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        job = cls._jobs.get(job_id)
        if job:
            if parsing_status:
                job.parsing_status = parsing_status
            if indexing_status:
                job.indexing_status = indexing_status
            if chunks_count is not None:
                job.chunks_count = chunks_count
            if error_message:
                job.error_message = error_message
            if indexing_status in (DocumentIndexingStatus.INDEXED, DocumentIndexingStatus.FAILED):
                job.completed_at = datetime.now(timezone.utc).isoformat()
