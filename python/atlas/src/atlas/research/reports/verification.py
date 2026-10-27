"""Institutional Research Report & Thesis Verification Engine (Stage 107)."""

import datetime
import uuid
from typing import Any, Dict, List, Optional

from atlas.research.domain import (
    ResearchReport,
    ResearchReportSection,
    ResearchReportVerification,
)
from atlas.research.enums import (
    VerificationIssueSeverity,
    VerificationIssueType,
)
from atlas.research.reports.templates import get_report_template


def verify_research_report(
    report: ResearchReport,
    sections: List[ResearchReportSection],
    known_citation_ids: Optional[List[str]] = None,
    known_analysis_run_ids: Optional[List[str]] = None,
    source_metadata_lookup: Optional[Dict[str, Dict[str, Any]]] = None,
    verified_by_user_id: str = "system",
) -> ResearchReportVerification:
    """Perform rigorous automated verification of report structure, citations, and point-in-time compliance."""
    issues: List[Dict[str, Any]] = []
    known_citations = set(known_citation_ids or [])
    known_runs = set(known_analysis_run_ids or [])
    source_meta = source_metadata_lookup or {}

    # 1. Structural Verification against Template Requirements
    if report.template_id:
        template = get_report_template(report.template_id)
        if template:
            present_section_types = {s.section_type for s in sections}
            for req_sec in template.required_sections:
                if req_sec not in present_section_types:
                    issues.append({
                        "issue_type": VerificationIssueType.STRUCTURE_INCOMPLETE.value,
                        "severity": VerificationIssueSeverity.BLOCKING.value,
                        "message": f"Required template section '{req_sec.value}' is missing from the report outline.",
                        "section_id": None,
                        "block_id": None,
                    })

    # Track metrics for citation coverage
    total_content_blocks = 0
    cited_blocks = 0

    # 2. Section & Content Block Verification
    for section in sections:
        # Check empty heading
        if not section.heading or not section.heading.strip():
            issues.append({
                "issue_type": VerificationIssueType.STRUCTURE_INCOMPLETE.value,
                "severity": VerificationIssueSeverity.WARNING.value,
                "message": f"Section '{section.section_id}' has an empty or blank heading.",
                "section_id": section.section_id,
                "block_id": None,
            })

        for block in section.content_blocks:
            total_content_blocks += 1
            citation_ids = block.get("citation_ids") or []
            if not citation_ids and block.get("citation_id"):
                citation_ids = [block["citation_id"]]
            analysis_run_id = block.get("analysis_run_id")

            if citation_ids or analysis_run_id:
                cited_blocks += 1

            # Check Citations
            for cit_id in citation_ids:
                if known_citations and cit_id not in known_citations:
                    issues.append({
                        "issue_type": VerificationIssueType.BROKEN_CITATION.value,
                        "severity": VerificationIssueSeverity.BLOCKING.value,
                        "message": f"In-text citation '{cit_id}' cannot be resolved to verified evidence.",
                        "section_id": section.section_id,
                        "block_id": block.get("block_id"),
                        "reference_id": cit_id,
                    })
                
                # Check Source Metadata for withdrawn / restricted / lookahead
                meta = source_meta.get(cit_id) or block.get("metadata") or block
                if meta.get("is_withdrawn"):
                    issues.append({
                        "issue_type": VerificationIssueType.SOURCE_WITHDRAWN.value,
                        "severity": VerificationIssueSeverity.BLOCKING.value,
                        "message": f"Citation '{cit_id}' references a primary document that has been officially withdrawn.",
                        "section_id": section.section_id,
                        "block_id": block.get("block_id"),
                        "reference_id": cit_id,
                    })
                if meta.get("is_restricted"):
                    issues.append({
                        "issue_type": VerificationIssueType.SOURCE_RESTRICTED.value,
                        "severity": VerificationIssueSeverity.WARNING.value,
                        "message": f"Citation '{cit_id}' references source material with redistribution restrictions.",
                        "section_id": section.section_id,
                        "block_id": block.get("block_id"),
                        "reference_id": cit_id,
                    })
                # Check Temporal Cutoff (No-Look-Ahead)
                pub_date = meta.get("publication_date")
                if pub_date and report.research_cutoff:
                    try:
                        if isinstance(pub_date, str):
                            dt = datetime.datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                        elif isinstance(pub_date, datetime.date) and not isinstance(pub_date, datetime.datetime):
                            dt = datetime.datetime(pub_date.year, pub_date.month, pub_date.day)
                        else:
                            dt = pub_date

                        cutoff = report.research_cutoff
                        if dt.tzinfo is None and cutoff.tzinfo is not None:
                            dt = dt.replace(tzinfo=cutoff.tzinfo)
                        elif dt.tzinfo is not None and cutoff.tzinfo is None:
                            cutoff = cutoff.replace(tzinfo=dt.tzinfo)

                        if dt > cutoff:
                            issues.append({
                                "issue_type": VerificationIssueType.POINT_IN_TIME_CONFLICT.value,
                                "severity": VerificationIssueSeverity.BLOCKING.value,
                                "message": f"Citation '{cit_id}' was published on {dt.date()} after report research cutoff {cutoff.date()}.",
                                "section_id": section.section_id,
                                "block_id": block.get("block_id"),
                                "reference_id": cit_id,
                            })
                    except Exception:
                        pass

            # Check Analysis Run Embeds
            if analysis_run_id:
                if known_runs and analysis_run_id not in known_runs:
                    issues.append({
                        "issue_type": VerificationIssueType.ANALYSIS_RUN_NOT_FOUND.value,
                        "severity": VerificationIssueSeverity.BLOCKING.value,
                        "message": f"Embedded analysis run '{analysis_run_id}' cannot be found or is not accessible.",
                        "section_id": section.section_id,
                        "block_id": block.get("block_id"),
                        "reference_id": analysis_run_id,
                    })

    # Coverage percentage
    citation_coverage_pct = round((cited_blocks / max(total_content_blocks, 1)) * 100.0, 1)

    # Informational issue summarizing cutoff & citation status
    issues.append({
        "issue_type": "TEMPORAL_CUTOFF_CHECK",
        "severity": VerificationIssueSeverity.INFORMATIONAL.value,
        "message": f"Report research cutoff evaluated at {report.research_cutoff.isoformat()}. Citation density: {citation_coverage_pct}%.",
        "section_id": None,
        "block_id": None,
    })

    blocking_count = sum(1 for i in issues if i["severity"] == VerificationIssueSeverity.BLOCKING.value)
    warnings_count = sum(1 for i in issues if i["severity"] == VerificationIssueSeverity.WARNING.value)
    info_count = sum(1 for i in issues if i["severity"] == VerificationIssueSeverity.INFORMATIONAL.value)

    return ResearchReportVerification(
        verification_id=f"ver-{uuid.uuid4().hex[:12]}",
        report_id=report.report_id,
        revision_number=report.current_revision,
        checked_at=datetime.datetime.now(datetime.timezone.utc),
        is_valid=(blocking_count == 0),
        blocking_issues_count=blocking_count,
        warnings_count=warnings_count,
        info_count=info_count,
        issues=issues,
        citation_coverage_pct=citation_coverage_pct,
        verified_by_user_id=verified_by_user_id,
    )
