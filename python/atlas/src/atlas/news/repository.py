import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from atlas.entities.models import Entity
from atlas.news.models import NewsEvent


class NewsEventRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_news_event(self, entity_id: uuid.UUID) -> Optional[tuple[Entity, NewsEvent]]:
        stmt = (
            select(Entity, NewsEvent)
            .join(NewsEvent, Entity.entity_id == NewsEvent.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def create_news_event_specialization(
        self,
        entity_id: uuid.UUID,
        event_kind: Optional[str] = None,
        event_time: Optional[datetime] = None,
        event_status: Optional[str] = None,
    ) -> NewsEvent:
        event = NewsEvent(
            entity_id=entity_id,
            event_kind=event_kind,
            event_time=event_time,
            event_status=event_status,
        )
        self.session.add(event)
        return event
