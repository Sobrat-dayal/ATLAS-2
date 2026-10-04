import uuid
from datetime import date
from typing import Optional

from sqlalchemy import UUID, Date, ForeignKey, String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base

class Company(Base):
    __tablename__ = "companies"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    legal_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    short_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    organization_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    founded_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    primary_country_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("countries.entity_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    __table_args__ = (
        CheckConstraint(
            "organization_type IN ('public_company', 'private_company', 'state_owned', 'subsidiary', 'joint_venture', 'nonprofit', 'partnership', 'cooperative', 'other')",
            name="chk_companies_organization_type"
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'dissolved', 'acquired', 'bankrupt', 'restructured', 'other')",
            name="chk_companies_status"
        ),
    )
