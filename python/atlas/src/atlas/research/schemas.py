import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from atlas.research.types import ResearchDocumentKind


class ResearchDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    document_kind: Optional[ResearchDocumentKind] = None
    publication_date: Optional[datetime.date] = None
    language_code: Optional[str] = None
    abstract_text: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
