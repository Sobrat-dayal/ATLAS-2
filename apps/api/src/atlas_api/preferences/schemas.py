from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    preference_key: str
    schema_version: int
    revision: int
    payload: dict[str, Any]
    updated_at: datetime

class PreferenceListResponse(BaseModel):
    preferences: list[PreferenceResponse]

class PreferenceUpdateRequest(BaseModel):
    schema_version: int
    expected_revision: Optional[int] = None
    payload: dict[str, Any]
