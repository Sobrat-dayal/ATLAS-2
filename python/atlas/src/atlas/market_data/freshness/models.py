from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, model_validator

from atlas.market_data.freshness.enums import (
    MarketDataFreshnessAgeBasis,
    MarketDataSourceTimestampFallback,
    MarketDataFreshnessStatus,
    MarketDataFreshnessReason,
)
from atlas.realtime.websocket.models import QuoteSubscriptionKey


class MarketDataFreshnessPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    fresh_until_seconds: int = Field(ge=0, le=604800)  # max 7 days
    stale_after_seconds: int = Field(ge=0, le=604800)
    
    age_basis: MarketDataFreshnessAgeBasis = MarketDataFreshnessAgeBasis.SOURCE_TIME_PREFERRED
    source_timestamp_fallback: MarketDataSourceTimestampFallback = MarketDataSourceTimestampFallback.USE_RECEIVED_AT

    @model_validator(mode="after")
    def validate_thresholds(self) -> "MarketDataFreshnessPolicy":
        if self.fresh_until_seconds >= self.stale_after_seconds:
            raise ValueError("fresh_until_seconds must be strictly less than stale_after_seconds")
        return self


class MarketDataFreshnessState(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: int = 1
    
    series_key: QuoteSubscriptionKey
    provider_key: str
    
    status: MarketDataFreshnessStatus
    reason: MarketDataFreshnessReason
    
    effective_age_seconds: int = Field(ge=0)
    age_basis_used: MarketDataFreshnessAgeBasis
    
    provider_delayed: bool = False
    provider_delay_seconds: Optional[int] = None
    
    quote_source_timestamp: Optional[datetime] = None
    quote_received_at: Optional[datetime] = None
    
    evaluated_at: datetime
    status_changed_at: datetime
    previous_status: Optional[MarketDataFreshnessStatus] = None
    
    # Policy summary
    fresh_until_seconds: int
    stale_after_seconds: int


class MarketDataFreshnessEvaluation(BaseModel):
    state: MarketDataFreshnessState
    next_evaluation_at: Optional[datetime] = None
