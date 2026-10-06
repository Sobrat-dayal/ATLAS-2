import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .types import (
    BondCouponType,
    CommodityCategory,
    CryptoAssetKind,
    CurrencyKind,
    DistributionPolicy,
    EquityKind,
    ETFReplicationMethod,
    ExerciseStyle,
    FundKind,
    MarketIndexKind,
    OptionRight,
    SettlementType,
)


class BaseInstrumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: str
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class GenericSecurityResponse(BaseInstrumentResponse):
    entity_type: Literal["security"] = "security"


class EquityResponse(BaseInstrumentResponse):
    entity_type: Literal["equity"] = "equity"
    equity_kind: Optional[EquityKind] = None
    share_class_name: Optional[str] = None


class ETFResponse(BaseInstrumentResponse):
    entity_type: Literal["etf"] = "etf"
    base_currency_entity_id: Optional[uuid.UUID] = None
    replication_method: Optional[ETFReplicationMethod] = None
    distribution_policy: Optional[DistributionPolicy] = None


class BondResponse(BaseInstrumentResponse):
    entity_type: Literal["bond"] = "bond"
    denomination_currency_entity_id: Optional[uuid.UUID] = None
    face_value: Optional[Decimal] = None
    coupon_rate: Optional[Decimal] = None
    coupon_type: Optional[BondCouponType] = None
    coupon_frequency: Optional[int] = None
    issue_date: Optional[date] = None
    maturity_date: Optional[date] = None


class OptionResponse(BaseInstrumentResponse):
    entity_type: Literal["option"] = "option"
    underlying_entity_id: uuid.UUID
    option_right: OptionRight
    strike_price: Decimal
    expiration_at: datetime
    exercise_style: Optional[ExerciseStyle] = None
    contract_multiplier: Optional[Decimal] = None
    settlement_type: Optional[SettlementType] = None


class FutureResponse(BaseInstrumentResponse):
    entity_type: Literal["future"] = "future"
    underlying_entity_id: uuid.UUID
    expiration_at: Optional[datetime] = None
    contract_size: Optional[Decimal] = None
    settlement_type: Optional[SettlementType] = None
    settlement_currency_entity_id: Optional[uuid.UUID] = None


class FundResponse(BaseInstrumentResponse):
    entity_type: Literal["fund"] = "fund"
    fund_kind: Optional[FundKind] = None
    base_currency_entity_id: Optional[uuid.UUID] = None
    distribution_policy: Optional[DistributionPolicy] = None


class CryptoAssetResponse(BaseInstrumentResponse):
    entity_type: Literal["crypto"] = "crypto"
    asset_kind: Optional[CryptoAssetKind] = None


class CurrencyResponse(BaseInstrumentResponse):
    entity_type: Literal["currency"] = "currency"
    currency_kind: Optional[CurrencyKind] = None


class CommodityResponse(BaseInstrumentResponse):
    entity_type: Literal["commodity"] = "commodity"
    commodity_category: Optional[CommodityCategory] = None
    unit_of_measure: Optional[str] = None


class MarketIndexResponse(BaseInstrumentResponse):
    entity_type: Literal["index"] = "index"
    index_kind: Optional[MarketIndexKind] = None
    base_currency_entity_id: Optional[uuid.UUID] = None
    weighting_method: Optional[str] = None


InstrumentResponse = Annotated[
    Union[
        EquityResponse,
        ETFResponse,
        BondResponse,
        OptionResponse,
        FutureResponse,
        FundResponse,
        CryptoAssetResponse,
        CurrencyResponse,
        CommodityResponse,
        MarketIndexResponse,
        GenericSecurityResponse,
    ],
    Field(discriminator="entity_type"),
]
