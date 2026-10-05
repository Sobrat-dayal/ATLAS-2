import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from atlas.providers.models import Base
from atlas.providers.routing.models import ProviderRoutingScope

class ProviderRoutingPolicyModel(Base):
    __tablename__ = "provider_routing_policies"

    policy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope: Mapped[ProviderRoutingScope] = mapped_column(SQLEnum(ProviderRoutingScope, name="provider_routing_scope", create_type=False), nullable=False)
    owner_principal_id: Mapped[str | None] = mapped_column(String, nullable=True)
    domain: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fallback_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    candidates: Mapped[list["ProviderRoutingCandidateModel"]] = relationship(
        "ProviderRoutingCandidateModel",
        back_populates="policy",
        cascade="all, delete-orphan",
        order_by="ProviderRoutingCandidateModel.position"
    )

    __table_args__ = (
        UniqueConstraint('owner_principal_id', 'domain', name='uq_provider_routing_user_domain'),
        UniqueConstraint('scope', 'domain', name='uq_provider_routing_system_domain'), # Partial constraint in PG ideally, but simplified here
    )

class ProviderRoutingCandidateModel(Base):
    __tablename__ = "provider_routing_candidates"

    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("provider_routing_policies.policy_id", ondelete="CASCADE"), nullable=False)
    provider_key: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    policy: Mapped[ProviderRoutingPolicyModel] = relationship("ProviderRoutingPolicyModel", back_populates="candidates")

    __table_args__ = (
        UniqueConstraint('policy_id', 'provider_key', name='uq_provider_routing_candidate_provider'),
        UniqueConstraint('policy_id', 'position', name='uq_provider_routing_candidate_position'),
    )
