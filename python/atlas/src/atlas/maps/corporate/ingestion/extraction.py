"""Facility evidence claim extraction with exact source citations (Stage 132)."""

from __future__ import annotations

import datetime
import uuid

from atlas.maps.corporate.domain import FacilityEvidenceClaim, VerificationStatus


def create_evidence_claim(
    facility_id: str,
    subject_entity_id: str,
    predicate: str,
    source_title: str,
    source_document_id: str,
    publisher: str,
    publication_date: datetime.datetime,
    exact_evidence_span: str,
    document_url: str | None = None,
    licensing_policy: str = "authorized_disclosure",
    verification_status: VerificationStatus = VerificationStatus.VERIFIED,
) -> FacilityEvidenceClaim:
    """Create a grounded, verifiable facility claim linked to exact document text."""
    claim_id = f"clm_{uuid.uuid4().hex[:12]}"
    return FacilityEvidenceClaim(
        claim_id=claim_id,
        facility_id=facility_id,
        subject_entity_id=subject_entity_id,
        predicate=predicate,
        source_title=source_title,
        source_document_id=source_document_id,
        publisher=publisher,
        publication_date=publication_date,
        exact_evidence_span=exact_evidence_span.strip(),
        document_url=document_url,
        licensing_policy=licensing_policy,
        verification_status=verification_status,
    )

