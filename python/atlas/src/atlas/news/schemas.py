import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict

from atlas.news.types import NewsEventKind, NewsEventStatus


class NewsEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    event_kind: Optional[NewsEventKind] = None
    event_time: Optional[datetime.datetime] = None
    event_status: Optional[NewsEventStatus] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
