"""Research Authorization and Access Control for Stage 127.

Enforces least-privilege document access, multi-tenant boundaries,
and user-private isolation rules (Part LXVII & Part LXVIII).
"""

from __future__ import annotations

from typing import Optional

from atlas.ai.research.domain import LicensingClass, ResearchDocument, ResearchSource
from atlas.ai.research.errors import (
    ResearchCitationAccessDeniedError,
    ResearchDocumentAccessDeniedError,
    ResearchSourceAccessDeniedError,
)


class ResearchAccessController:
    """Verifies that requests adhere to tenant and user access control boundaries."""

    @staticmethod
    def verify_source_access(
        source: ResearchSource,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Verifies access to a research source."""
        if not source.is_active:
            raise ResearchSourceAccessDeniedError(source.source_id, "Source has been deactivated.")

        if source.tenant_id and tenant_id and source.tenant_id != tenant_id:
            raise ResearchSourceAccessDeniedError(
                source.source_id,
                f"Cross-tenant access prohibited ({source.tenant_id} != {tenant_id}).",
            )

        if source.licensing_class == LicensingClass.USER_PRIVATE:
            if not user_id or source.owner_user_id != user_id:
                raise ResearchSourceAccessDeniedError(
                    source.source_id, "Private source access denied for user."
                )

    @staticmethod
    def verify_document_access(
        document: ResearchDocument,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Verifies that caller has access to read the document."""
        if document.is_revoked:
            raise ResearchDocumentAccessDeniedError(document.document_id, user_id or "anonymous")

        if document.tenant_id and tenant_id and document.tenant_id != tenant_id:
            raise ResearchDocumentAccessDeniedError(document.document_id, user_id or "anonymous")

        if document.access_tier == "USER_PRIVATE":
            if not user_id or document.owner_user_id != user_id:
                raise ResearchDocumentAccessDeniedError(
                    document.document_id, user_id or "anonymous"
                )

    @staticmethod
    def verify_citation_access(
        citation_id: str,
        document: ResearchDocument,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Re-authorizes citation resolution so revoked or private docs cannot leak."""
        try:
            ResearchAccessController.verify_document_access(document, user_id, tenant_id)
        except ResearchDocumentAccessDeniedError:
            raise ResearchCitationAccessDeniedError(citation_id, document.document_id)
