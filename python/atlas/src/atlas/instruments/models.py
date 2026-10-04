import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    UUID,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base

PRICE_NUMERIC = Numeric(38, 18)
RATE_NUMERIC = Numeric(20, 10)
MULTIPLIER_NUMERIC = Numeric(38, 18)

class FinancialInstrument(Base):
    __tablename__ = "financial_instruments"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )

class Security(Base):
    __tablename__ = "securities"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )

class Currency(Base):
    __tablename__ = "currencies"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    currency_kind: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

class CryptoAsset(Base):
    __tablename__ = "crypto_assets"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    asset_kind: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

class Commodity(Base):
    __tablename__ = "commodities"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    commodity_category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    unit_of_measure: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

class MarketIndex(Base):
    __tablename__ = "market_indexes"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    index_kind: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    base_currency_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("currencies.entity_id", ondelete="RESTRICT"),
        nullable=True,
    )
    weighting_method: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

class Equity(Base):
    __tablename__ = "equities"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("securities.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    equity_kind: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    share_class_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

class ETF(Base):
    __tablename__ = "etfs"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("securities.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    base_currency_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("currencies.entity_id", ondelete="RESTRICT"),
        nullable=True,
    )
    replication_method: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    distribution_policy: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

class Bond(Base):
    __tablename__ = "bonds"
    __table_args__ = (
        CheckConstraint("face_value >= 0", name="bonds_face_value_check"),
        CheckConstraint("coupon_frequency > 0", name="bonds_coupon_frequency_check"),
        CheckConstraint("maturity_date >= issue_date", name="bonds_maturity_date_check"),
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("securities.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    denomination_currency_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("currencies.entity_id", ondelete="RESTRICT"),
        nullable=True,
    )
    face_value: Mapped[Optional[Decimal]] = mapped_column(PRICE_NUMERIC, nullable=True)
    coupon_rate: Mapped[Optional[Decimal]] = mapped_column(RATE_NUMERIC, nullable=True)
    coupon_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    coupon_frequency: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    maturity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

class Option(Base):
    __tablename__ = "options"
    __table_args__ = (
        CheckConstraint("strike_price >= 0", name="options_strike_price_check"),
        CheckConstraint("contract_multiplier > 0", name="options_multiplier_check"),
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("securities.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    underlying_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    option_right: Mapped[str] = mapped_column(String(16), nullable=False)
    strike_price: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    expiration_at: Mapped[date] = mapped_column(DateTime(timezone=True), nullable=False)
    exercise_style: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    contract_multiplier: Mapped[Optional[Decimal]] = mapped_column(MULTIPLIER_NUMERIC, nullable=True)
    settlement_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

class Future(Base):
    __tablename__ = "futures"
    __table_args__ = (
        CheckConstraint("contract_size > 0", name="futures_contract_size_check"),
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("securities.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    underlying_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    expiration_at: Mapped[Optional[date]] = mapped_column(DateTime(timezone=True), nullable=True)
    contract_size: Mapped[Optional[Decimal]] = mapped_column(MULTIPLIER_NUMERIC, nullable=True)
    settlement_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    settlement_currency_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("currencies.entity_id", ondelete="RESTRICT"),
        nullable=True,
    )

class Fund(Base):
    __tablename__ = "funds"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("securities.entity_id", ondelete="RESTRICT"),
        primary_key=True,
    )
    fund_kind: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    base_currency_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("currencies.entity_id", ondelete="RESTRICT"),
        nullable=True,
    )
    distribution_policy: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
