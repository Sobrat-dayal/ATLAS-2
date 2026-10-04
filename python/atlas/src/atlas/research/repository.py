import uuid
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas.entities.models import Entity
from atlas.research.models import ResearchDocument


class ResearchDocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_research_document(self, entity_id: uuid.UUID) -> Optional[tuple[Entity, ResearchDocument]]:
        stmt = (
            select(Entity, ResearchDocument)
            .join(ResearchDocument, Entity.entity_id == ResearchDocument.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def create_research_document_specialization(
        self,
        entity_id: uuid.UUID,
        document_kind: Optional[str] = None,
        publication_date: Optional[date] = None,
        language_code: Optional[str] = None,
        abstract_text: Optional[str] = None,
    ) -> ResearchDocument:
        doc = ResearchDocument(
            entity_id=entity_id,
            document_kind=document_kind,
            publication_date=publication_date,
            language_code=language_code,
            abstract_text=abstract_text,
        )
        self.session.add(doc)
        return doc
