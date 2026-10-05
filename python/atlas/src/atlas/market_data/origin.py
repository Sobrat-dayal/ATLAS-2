from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, constr

from atlas.market_data.enums import MarketDataTimeliness
from atlas.market_data.timestamps import CanonicalDatetime


class MarketDataOrigin(BaseModel):
    """
    Lightweight runtime lineage metadata for Market Data responses.
    This does NOT replace the full Provenance system.
    Must contain no credentials or sensitive data.
    """

    model_config = ConfigDict(frozen=True)

    provider_key: constr(min_length=1, max_length=64, pattern=r"^[a-z0-9_-]+$") = Field(
        ..., description="The key of the Atlas Provider that fulfilled this request."
    )

    upstream_source: Optional[str] = Field(
        default=None,
        max_length=128,
        description="Human/machine-readable source identity (e.g. FRED, CBOE, Polygon) if known.",
    )

    retrieved_at: CanonicalDatetime = Field(
        ..., description="UTC time when Atlas retrieved or received this data."
    )

    timeliness: MarketDataTimeliness = Field(
        ..., description="How fresh the observation is represented to be."
    )

    delay_seconds: Optional[int] = Field(
        default=None,
        ge=0,
        description="The delay in seconds, typically populated when timeliness=delayed.",
    )

    source_timestamp: Optional[CanonicalDatetime] = Field(
        default=None,
        description="The timestamp of the data from the source, if applicable and known.",
    )
