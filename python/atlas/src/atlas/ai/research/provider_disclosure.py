"""Third-Party Model Provider Disclosure Enforcement for Stage 127.

Enforces provider disclosure policies (Part XXXV) so sensitive or proprietary
research documents are never disclosed to external model providers without rights.
"""

from __future__ import annotations

from typing import List

from atlas.ai.research.domain import ProviderDisclosurePolicy, ResearchEvidence, ResearchSource
from atlas.ai.research.errors import ResearchSourceDisclosureDeniedError


class ProviderDisclosureChecker:
    """Verifies evidence against model provider disclosure permissions."""

    @staticmethod
    def verify_source_disclosure(
        source: ResearchSource,
        is_external_provider: bool = True,
    ) -> None:
        """Verifies if source content can be transmitted to an external model provider."""
        if not is_external_provider:
            return

        if source.provider_disclosure == ProviderDisclosurePolicy.PROHIBITED:
            raise ResearchSourceDisclosureDeniedError(
                source.source_id, source.provider_disclosure.value
            )

    @staticmethod
    def filter_disclosable_evidence(
        evidence_list: List[ResearchEvidence],
        source_registry_lookup,
        is_external_provider: bool = True,
    ) -> List[ResearchEvidence]:
        """Filters out evidence units whose underlying sources prohibit external disclosure."""
        if not is_external_provider:
            return evidence_list

        filtered: List[ResearchEvidence] = []
        for ev in evidence_list:
            try:
                # Look up document and source
                doc = source_registry_lookup.get_document(ev.document_id)
                source = source_registry_lookup.get_source(doc.source_id)
                ProviderDisclosureChecker.verify_source_disclosure(source, is_external_provider)
                filtered.append(ev)
            except Exception:
                # Omit non-disclosable evidence from external model context
                continue
        return filtered
