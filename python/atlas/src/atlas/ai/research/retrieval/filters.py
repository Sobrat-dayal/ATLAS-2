"""Hard Retrieval Filters for Point-in-Time and Security Compliance (Part XXXI & XXXIII)."""

from __future__ import annotations

from typing import List, Optional

from atlas.ai.research.domain import ResearchDocument


class ResearchRetrievalFilter:
    """Applies non-negotiable security, point-in-time, and scope constraints."""

    @staticmethod
    def is_document_eligible(
        doc: ResearchDocument,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        historical_as_of: Optional[str] = None,
        allowed_symbols: Optional[List[str]] = None,
        allowed_document_types: Optional[List[str]] = None,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
    ) -> bool:
        """Evaluates whether a document passes all security and temporal gates."""
        # 1. Revocation check (Fixture I)
        if doc.is_revoked:
            return False

        # 2. Tenant isolation
        if doc.tenant_id and tenant_id and doc.tenant_id != tenant_id:
            return False

        # 3. User privacy (Fixture D)
        if doc.access_tier == "USER_PRIVATE":
            if not user_id or doc.owner_user_id != user_id:
                return False

        # 4. Point-in-Time Historical Cutoff (Fixture C)
        # Prevents look-ahead bias by rejecting any source published after the historical date
        if historical_as_of and doc.publication_date > historical_as_of:
            return False

        # 5. Date range bounds
        if date_start and doc.publication_date < date_start:
            return False
        if date_end and doc.publication_date > date_end:
            return False

        # 6. Symbol match (if targeted)
        if allowed_symbols and doc.symbol:
            target_upper = [s.upper() for s in allowed_symbols]
            if doc.symbol.upper() not in target_upper:
                return False

        # 7. Document type match
        if allowed_document_types and doc.document_type:
            if doc.document_type not in allowed_document_types:
                return False

        return True
