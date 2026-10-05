import datetime
import uuid
from typing import Any

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas.database import Base


class ProviderConfiguration(Base):
    __tablename__ = "provider_configurations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    provider_id: Mapped[str] = mapped_column(String(128), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    bindings: Mapped[list["ProviderCredentialBinding"]] = relationship(
        "ProviderCredentialBinding", back_populates="configuration", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "provider_id", name="uq_provider_config_user_provider"),
    )


class ProviderCredentialBinding(Base):
    __tablename__ = "provider_credential_bindings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("provider_configurations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    credential_key: Mapped[str] = mapped_column(String(128), nullable=False)
    vault_secret_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    configuration: Mapped["ProviderConfiguration"] = relationship(
        "ProviderConfiguration", back_populates="bindings"
    )

    __table_args__ = (
        UniqueConstraint("configuration_id", "credential_key", name="uq_provider_credential_config_key"),
    )
