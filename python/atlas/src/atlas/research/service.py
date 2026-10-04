import uuid
from datetime import date
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from atlas.entities.repository import EntityRepository
from atlas.entities.service import EntityService
from atlas.entities.types import EntityTypeKey
from atlas.research.errors import (
    InvalidResearchDocumentKindError,
    ResearchDocumentDataInconsistentError,
    ResearchDocumentNotFoundError,
)
from atlas.research.repository import ResearchDocumentRepository
from atlas.research.schemas import ResearchDocumentResponse
from atlas.research.types import ResearchDocumentKind
from atlas.research.validation import validate_abstract_text, validate_language_code


class ResearchDocumentService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ResearchDocumentRepository(session)
        self.entity_service = EntityService(session)
        self.entity_repository = EntityRepository(session)

    def create_research_document(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        document_kind: Optional[str] = None,
        publication_date: Optional[date] = None,
        language_code: Optional[str] = None,
        abstract_text: Optional[str] = None,
    ) -> ResearchDocumentResponse:
        
        if document_kind is not None:
            try:
                ResearchDocumentKind(document_kind)
            except ValueError:
                raise InvalidResearchDocumentKindError(
                    f"Invalid document_kind: {document_kind}"
                )

        language_code = validate_language_code(language_code)
        abstract_text = validate_abstract_text(abstract_text)

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.RESEARCH_DOCUMENT,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            doc = self.repository.create_research_document_specialization(
                entity_id=entity.entity_id,
                document_kind=document_kind,
                publication_date=publication_date,
                language_code=language_code,
                abstract_text=abstract_text,
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return ResearchDocumentResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            document_kind=doc.document_kind,
            publication_date=doc.publication_date,
            language_code=doc.language_code,
            abstract_text=doc.abstract_text,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def get_research_document(self, entity_id: uuid.UUID) -> ResearchDocumentResponse:
        entity = self.entity_repository.get_entity(entity_id)
        if not entity:
            raise ResearchDocumentNotFoundError(f"Research Document {entity_id} not found.")

        if entity.entity_type != EntityTypeKey.RESEARCH_DOCUMENT:
            raise ResearchDocumentNotFoundError(
                f"Entity {entity_id} is not a Research Document."
            )

        doc_tuple = self.repository.get_research_document(entity_id)
        if not doc_tuple:
            raise ResearchDocumentDataInconsistentError(
                f"Research Document {entity_id} missing specialization row."
            )

        _, doc = doc_tuple

        return ResearchDocumentResponse.model_validate(
            {
                **entity.__dict__,
                "document_kind": doc.document_kind,
                "publication_date": doc.publication_date,
                "language_code": doc.language_code,
                "abstract_text": doc.abstract_text,
            }
        )
