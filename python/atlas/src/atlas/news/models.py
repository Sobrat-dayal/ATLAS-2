import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class NewsEvent(Base):
    __tablename__ = "news_events"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.entity_id", ondelete="RESTRICT"), primary_key=True
    )
    event_kind: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    event_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    event_status: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "event_kind IN ('corporate', 'economic', 'market', 'political', 'geopolitical', 'regulatory', 'legal', 'technology', 'cybersecurity', 'infrastructure', 'natural_disaster', 'security_incident', 'other')",
            name="ck_news_event_kind",
        ),
        CheckConstraint(
            "event_status IN ('developing', 'confirmed', 'resolved', 'historical', 'other')",
            name="ck_news_event_status",
        ),
    )
