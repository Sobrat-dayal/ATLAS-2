from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field


def current_utc() -> datetime:
    return datetime.now(timezone.utc)


class OpenBBCoverageSnapshot(BaseModel):
    """Local metadata snapshot of installed OpenBB capabilities."""

    runtime_version: str = Field(..., description="The OpenBB runtime version")
    provider_names: List[str] = Field(
        default_factory=list, description="Installed OpenBB provider extensions"
    )
    commands_by_provider: Dict[str, int] = Field(
        default_factory=dict, description="Command count by provider"
    )
    generated_at: datetime = Field(
        default_factory=current_utc, description="When this coverage snapshot was generated"
    )
