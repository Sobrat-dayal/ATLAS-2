"""Source Manifest Builder for Stage 127 AI Research (Part XXXVIII)."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

from atlas.ai.research.domain import ResearchEvidence, ResearchSourceManifest


def build_source_manifest(
    run_id: str,
    evidence_units: List[ResearchEvidence],
    total_evaluated: int,
    excluded_count: int,
    has_conflicting_sources: bool = False,
    conflict_notes: str = "",
) -> ResearchSourceManifest:
    """Builds a structured manifest of sources utilized in research generation."""
    sources_used: List[Dict[str, Any]] = []
    seen_docs = set()

    for ev in evidence_units:
        if ev.document_id not in seen_docs:
            seen_docs.add(ev.document_id)
            sources_used.append(
                {
                    "document_id": ev.document_id,
                    "title": ev.title,
                    "symbol": ev.symbol,
                    "page_number": ev.page_number,
                    "section_title": ev.section_title,
                    "publication_date": ev.publication_date,
                    "publisher": ev.publisher,
                }
            )

    coverage_summary = (
        f"Grounded in {len(sources_used)} primary document(s) across {len(evidence_units)} evidence unit(s)."
        if sources_used
        else "No matching evidence sources were utilized."
    )

    return ResearchSourceManifest(
        manifest_id=f"man_{uuid.uuid4().hex[:12]}",
        run_id=run_id,
        sources_used=sources_used,
        total_sources_evaluated=total_evaluated,
        excluded_sources_count=excluded_count,
        coverage_summary=coverage_summary,
        has_conflicting_sources=has_conflicting_sources,
        conflict_notes=conflict_notes if has_conflicting_sources else None,
    )

