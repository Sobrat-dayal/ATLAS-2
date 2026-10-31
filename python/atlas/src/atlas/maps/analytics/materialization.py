"""Materialization Job Lifecycle and Preaggregation Registry (Stage 131).

Tracks durable background aggregation jobs for large-scale geospatial datasets.
"""

from __future__ import annotations

import datetime
import uuid
from typing import Dict, List, Optional

from atlas.maps.analytics.domain import MaterializationJob, MaterializationJobStatus
from atlas.maps.analytics.errors import MaterializationJobNotFoundError


class MaterializationJobRegistry:
    """In-memory and durable job tracking registry."""

    def __init__(self):
        self._jobs: Dict[str, MaterializationJob] = {}

    def create_job(
        self,
        dataset_id: str,
        dataset_revision: str,
        metric_id: str,
        h3_resolution: int,
    ) -> MaterializationJob:
        job_id = f"mat-job-{uuid.uuid4().hex[:12]}"
        job = MaterializationJob(
            job_id=job_id,
            dataset_id=dataset_id,
            dataset_revision=dataset_revision,
            metric_id=metric_id,
            h3_resolution=h3_resolution,
            status=MaterializationJobStatus.PENDING,
        )
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> MaterializationJob:
        job = self._jobs.get(job_id)
        if not job:
            raise MaterializationJobNotFoundError(job_id)
        return job

    def update_status(
        self,
        job_id: str,
        status: MaterializationJobStatus,
        records_processed: int = 0,
        cells_generated: int = 0,
        error_message: Optional[str] = None,
    ) -> MaterializationJob:
        job = self.get_job(job_id)
        job.status = status
        job.records_processed = records_processed
        job.cells_generated = cells_generated
        job.error_message = error_message
        if status in (
            MaterializationJobStatus.COMPLETED,
            MaterializationJobStatus.FAILED,
            MaterializationJobStatus.CANCELLED,
        ):
            job.completed_at = datetime.datetime.utcnow()
        return job

    def cancel_job(self, job_id: str) -> MaterializationJob:
        job = self.get_job(job_id)
        if job.status in (MaterializationJobStatus.PENDING, MaterializationJobStatus.RUNNING):
            job.status = MaterializationJobStatus.CANCELLED
            job.completed_at = datetime.datetime.utcnow()
        return job

    def list_jobs(self, dataset_id: Optional[str] = None) -> List[MaterializationJob]:
        if dataset_id:
            return [j for j in self._jobs.values() if j.dataset_id == dataset_id]
        return list(self._jobs.values())
