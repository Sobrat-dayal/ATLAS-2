import datetime
import uuid
from typing import Any

from sqlalchemy import UUID, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class ProviderHealthState(Base):
    __tablename__ = "provider_health_states"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_key: Mapped[str] = mapped_column(String(128), nullable=False)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    configuration_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("provider_configurations.id", ondelete="CASCADE"),
        nullable=True,
    )
    owner_principal_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False)
    coverage: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    components: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)

    checked_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_success_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_failure_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    consecutive_successes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    probe_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_provider_health_states_integration",
            "provider_key",
            "target_type",
            unique=True,
            postgresql_where=(target_type == "integration"),
        ),
        Index(
            "ix_provider_health_states_configuration",
            "configuration_id",
            unique=True,
            postgresql_where=(target_type == "configuration"),
        ),
        CheckConstraint(
            "(target_type = 'integration' AND configuration_id IS NULL AND owner_principal_id IS NULL) OR "
            "(target_type = 'configuration' AND configuration_id IS NOT NULL AND owner_principal_id IS NOT NULL)",
            name="ck_provider_health_target_type_constraints",
        ),
    )


class ProviderHealthCheck(Base):
    __tablename__ = "provider_health_checks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_key: Mapped[str] = mapped_column(String(128), nullable=False)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    configuration_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("provider_configurations.id", ondelete="CASCADE"),
        nullable=True,
    )
    owner_principal_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    trigger: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    coverage: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    components: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)

    probe_version: Mapped[int] = mapped_column(Integer, nullable=False)

    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_provider_health_checks_provider", "provider_key", "started_at"),
        Index("ix_provider_health_checks_configuration", "configuration_id", "started_at"),
        Index("ix_provider_health_checks_owner", "owner_principal_id", "started_at"),
    )
