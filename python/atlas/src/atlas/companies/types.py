from enum import StrEnum

class OrganizationType(StrEnum):
    PUBLIC_COMPANY = "public_company"
    PRIVATE_COMPANY = "private_company"
    STATE_OWNED = "state_owned"
    SUBSIDIARY = "subsidiary"
    JOINT_VENTURE = "joint_venture"
    NONPROFIT = "nonprofit"
    PARTNERSHIP = "partnership"
    COOPERATIVE = "cooperative"
    OTHER = "other"

class CompanyStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISSOLVED = "dissolved"
    ACQUIRED = "acquired"
    BANKRUPT = "bankrupt"
    RESTRUCTURED = "restructured"
    OTHER = "other"
