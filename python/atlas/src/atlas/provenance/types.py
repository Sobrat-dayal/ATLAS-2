from enum import Enum


class ProvenanceSourceKind(str, Enum):
    OFFICIAL = "official"
    REGULATORY = "regulatory"
    EXCHANGE = "exchange"
    ACADEMIC = "academic"
    NEWS = "news"
    DATASET = "dataset"
    PROVIDER = "provider"
    WEBSITE = "website"
    USER_INPUT = "user_input"
    INTERNAL_SYSTEM = "internal_system"
    IMPORT = "import"
    OTHER = "other"


class ProvenanceRecordKind(str, Enum):
    API_RESPONSE = "api_response"
    DOCUMENT = "document"
    WEB_PAGE = "web_page"
    DATASET_RECORD = "dataset_record"
    MANUAL_ASSERTION = "manual_assertion"
    DERIVED_ASSERTION = "derived_assertion"
    IMPORTED_RECORD = "imported_record"
    SYSTEM_OBSERVATION = "system_observation"
    OTHER = "other"


class EvidenceRole(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVED_FROM = "derived_from"
    CONTEXT = "context"
