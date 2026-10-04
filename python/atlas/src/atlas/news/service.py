import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from atlas.entities.repository import EntityRepository
from atlas.entities.service import EntityService
from atlas.entities.types import EntityTypeKey
from atlas.news.errors import (
    InvalidNewsEventKindError,
    InvalidNewsEventStatusError,
    NewsEventDataInconsistentError,
    NewsEventNotFoundError,
)
from atlas.news.repository import NewsEventRepository
from atlas.news.schemas import NewsEventResponse
from atlas.news.types import NewsEventKind, NewsEventStatus


class NewsEventService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = NewsEventRepository(session)
        self.entity_service = EntityService(session)
        self.entity_repository = EntityRepository(session)

    def create_news_event(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        event_kind: Optional[str] = None,
        event_time: Optional[datetime] = None,
        event_status: Optional[str] = None,
    ) -> NewsEventResponse:
        
        if event_kind is not None:
            try:
                NewsEventKind(event_kind)
            except ValueError:
                raise InvalidNewsEventKindError(f"Invalid event_kind: {event_kind}")

        if event_status is not None:
            try:
                NewsEventStatus(event_status)
            except ValueError:
                raise InvalidNewsEventStatusError(f"Invalid event_status: {event_status}")

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.NEWS_EVENT,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            event = self.repository.create_news_event_specialization(
                entity_id=entity.entity_id,
                event_kind=event_kind,
                event_time=event_time,
                event_status=event_status,
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return NewsEventResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            event_kind=event.event_kind,
            event_time=event.event_time,
            event_status=event.event_status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def get_news_event(self, entity_id: uuid.UUID) -> NewsEventResponse:
        entity = self.entity_repository.get_entity(entity_id)
        if not entity:
            raise NewsEventNotFoundError(f"News Event {entity_id} not found.")

        if entity.entity_type != EntityTypeKey.NEWS_EVENT:
            raise NewsEventNotFoundError(f"Entity {entity_id} is not a News Event.")

        event_tuple = self.repository.get_news_event(entity_id)
        if not event_tuple:
            raise NewsEventDataInconsistentError(
                f"News Event {entity_id} missing specialization row."
            )

        _, event = event_tuple

        return NewsEventResponse.model_validate(
            {
                **entity.__dict__,
                "event_kind": event.event_kind,
                "event_time": event.event_time,
                "event_status": event.event_status,
            }
        )
