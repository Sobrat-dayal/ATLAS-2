import uuid
from datetime import date
from typing import Optional

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class ResearchDocument(Base):
    __tablename__ = "research_documents"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.entity_id", ondelete="RESTRICT"), primary_key=True
    )
    document_kind: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(35), nullable=True)
    abstract_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "document_kind IN ('journal_article', 'conference_paper', 'preprint', 'working_paper', 'research_report', 'technical_report', 'white_paper', 'thesis', 'dissertation', 'book_chapter', 'dataset_documentation', 'other')",
            name="ck_research_doc_kind",
        ),
    )
