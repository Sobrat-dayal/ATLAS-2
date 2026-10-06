from enum import StrEnum


class NewsEventKind(StrEnum):
    CORPORATE = "corporate"
    ECONOMIC = "economic"
    MARKET = "market"
    POLITICAL = "political"
    GEOPOLITICAL = "geopolitical"
    REGULATORY = "regulatory"
    LEGAL = "legal"
    TECHNOLOGY = "technology"
    CYBERSECURITY = "cybersecurity"
    INFRASTRUCTURE = "infrastructure"
    NATURAL_DISASTER = "natural_disaster"
    SECURITY_INCIDENT = "security_incident"
    OTHER = "other"


class NewsEventStatus(StrEnum):
    DEVELOPING = "developing"
    CONFIRMED = "confirmed"
    RESOLVED = "resolved"
    HISTORICAL = "historical"
    OTHER = "other"
