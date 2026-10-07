from enum import StrEnum

class EconomicObservationAvailability(StrEnum):
    AVAILABLE = "available"
    MISSING = "missing"

class EconomicRevisionStatus(StrEnum):
    PRELIMINARY = "preliminary"
    REVISED = "revised"
    FINAL = "final"
    UNKNOWN = "unknown"

class EconomicRevisionPolicy(StrEnum):
    LATEST_AVAILABLE = "latest_available"
    AS_OF = "as_of"
    ALL_VINTAGES = "all_vintages"

class EconomicDataOperation(StrEnum):
    OBSERVATIONS = "observations"
    LATEST_OBSERVATIONS = "latest_observations"
