from enum import Enum


class RelationshipCategory(str, Enum):
    CORPORATE = "corporate"
    MARKET = "market"
    OWNERSHIP = "ownership"
    OPERATIONS = "operations"
    COMPETITION = "competition"
    SUPPLY_CHAIN = "supply_chain"
    RESEARCH = "research"


class RelationshipDirection(str, Enum):
    OUTGOING = "outgoing"
    INCOMING = "incoming"
    BOTH = "both"
