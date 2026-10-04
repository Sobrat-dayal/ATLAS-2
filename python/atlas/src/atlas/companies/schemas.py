import uuid
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

from .types import CompanyStatus, OrganizationType


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: uuid.UUID
    entity_type: Literal["company"] = "company"
    canonical_name: str
    display_name: str
    description: Optional[str] = None
    legal_name: Optional[str] = None
    short_name: Optional[str] = None
    organization_type: Optional[OrganizationType] = None
    status: Optional[CompanyStatus] = None
    founded_date: Optional[date] = None
    website_url: Optional[str] = None
    primary_country_entity_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
