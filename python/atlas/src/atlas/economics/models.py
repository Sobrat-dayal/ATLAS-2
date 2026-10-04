import uuid
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class EconomicSeries(Base):
    __tablename__ = "economic_series"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.entity_id", ondelete="RESTRICT"), primary_key=True
    )
    series_kind: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    frequency: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    unit_label: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    value_representation: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    seasonal_adjustment: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    scope_geographic_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("geographic_entities.entity_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        CheckConstraint(
            "series_kind IN ('output', 'prices', 'labor', 'interest_rate', 'monetary', 'fiscal', 'trade', 'housing', 'consumption', 'business', 'demographic', 'financial_conditions', 'sentiment', 'other')",
            name="ck_econ_series_kind",
        ),
        CheckConstraint(
            "frequency IN ('intraday', 'daily', 'weekly', 'monthly', 'quarterly', 'semiannual', 'annual', 'irregular', 'other')",
            name="ck_econ_frequency",
        ),
        CheckConstraint(
            "value_representation IN ('level', 'percent', 'rate', 'index', 'currency', 'count', 'ratio', 'change', 'growth_rate', 'other')",
            name="ck_econ_val_rep",
        ),
        CheckConstraint(
            "seasonal_adjustment IN ('not_adjusted', 'seasonally_adjusted', 'seasonally_adjusted_annual_rate', 'other')",
            name="ck_econ_seas_adj",
        ),
    )
