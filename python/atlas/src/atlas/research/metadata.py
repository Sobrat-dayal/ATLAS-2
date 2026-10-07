import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from atlas.research.origin import ResearchDataOrigin
from atlas.research.types import ResearchDocumentKind


class ResearchMetadata(BaseModel):
    """
    A canonical, immutable representation of a Research Document's metadata as reported by a provider.
    Aligns with the Universal Entity system's Research Document structure.
    """
    research_document_id: Optional[uuid.UUID] = Field(default=None, description="The resolved UUID in ATLAS if known.")
    title: str = Field(..., description="The title of the research document.")
    abstract_text: Optional[str] = Field(default=None, description="The abstract or summary of the research.")
    document_kind: Optional[ResearchDocumentKind] = Field(default=None, description="The kind of research document.")
    publication_date: Optional[datetime.date] = Field(default=None, description="The date the research was published.")
    language_code: Optional[str] = Field(default=None, description="ISO language code of the document (e.g., 'en').")
    authors: tuple[str, ...] = Field(default_factory=tuple, description="List of author names.")
    url: Optional[HttpUrl] = Field(default=None, description="The URL to the document or provider's page.")
    origin: ResearchDataOrigin = Field(..., description="The provenance information of the research metadata.")

    model_config = ConfigDict(frozen=True)
