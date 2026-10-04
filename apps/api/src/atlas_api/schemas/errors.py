from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class AtlasErrorModel(BaseModel):
    code: str = Field(..., description="Machine-readable error code in uppercase")
    message: str = Field(..., description="Human-readable error description")
    request_id: Optional[str] = Field(default=None, description="Request correlation ID")
    details: Optional[Any] = Field(
        default=None, description="Optional detailed error context, such as field errors"
    )


class AtlasErrorEnvelope(BaseModel):
    error: AtlasErrorModel
