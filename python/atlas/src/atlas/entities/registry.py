from dataclasses import dataclass
from typing import Optional

from .types import EntityTypeKey


@dataclass(frozen=True)
class EntityTypeDefinition:
    key: EntityTypeKey
    name: str
    description: Optional[str] = None
    parent_key: Optional[EntityTypeKey] = None


CANONICAL_ENTITY_TYPES: list[EntityTypeDefinition] = [
    # Financial / Instruments
    EntityTypeDefinition(
        key=EntityTypeKey.SECURITY, name="Security", description="A tradable financial asset"
    ),
    EntityTypeDefinition(
        key=EntityTypeKey.EQUITY, name="Equity", parent_key=EntityTypeKey.SECURITY
    ),
    EntityTypeDefinition(key=EntityTypeKey.ETF, name="ETF", parent_key=EntityTypeKey.SECURITY),
    EntityTypeDefinition(key=EntityTypeKey.BOND, name="Bond", parent_key=EntityTypeKey.SECURITY),
    EntityTypeDefinition(
        key=EntityTypeKey.OPTION, name="Option", parent_key=EntityTypeKey.SECURITY
    ),
    EntityTypeDefinition(
        key=EntityTypeKey.FUTURE, name="Future", parent_key=EntityTypeKey.SECURITY
    ),
    EntityTypeDefinition(key=EntityTypeKey.FUND, name="Fund", parent_key=EntityTypeKey.SECURITY),
    EntityTypeDefinition(
        key=EntityTypeKey.CRYPTO,
        name="Crypto Asset",
        description="A digital or cryptographic asset",
    ),
    EntityTypeDefinition(
        key=EntityTypeKey.CURRENCY, name="Currency", description="A fiat currency"
    ),
    EntityTypeDefinition(
        key=EntityTypeKey.COMMODITY, name="Commodity", description="A physical commodity"
    ),
    EntityTypeDefinition(key=EntityTypeKey.INDEX, name="Index", description="A financial index"),
    # Organizations / People
    EntityTypeDefinition(
        key=EntityTypeKey.COMPANY, name="Company", description="A business entity or corporation"
    ),
    EntityTypeDefinition(key=EntityTypeKey.PERSON, name="Person", description="An individual"),
    # Geography / Infrastructure
    EntityTypeDefinition(
        key=EntityTypeKey.COUNTRY, name="Country", description="A sovereign state or territory"
    ),
    EntityTypeDefinition(
        key=EntityTypeKey.FACILITY,
        name="Facility",
        description="A physical facility or installation",
    ),
    EntityTypeDefinition(key=EntityTypeKey.PORT, name="Port", parent_key=EntityTypeKey.FACILITY),
    EntityTypeDefinition(
        key=EntityTypeKey.AIRPORT, name="Airport", parent_key=EntityTypeKey.FACILITY
    ),
    EntityTypeDefinition(
        key=EntityTypeKey.EXCHANGE, name="Exchange", description="A trading exchange or venue"
    ),
    # Economics
    EntityTypeDefinition(
        key=EntityTypeKey.ECONOMIC_SERIES,
        name="Economic Series",
        description="A macro-economic data series",
    ),
    # Events / Documents
    EntityTypeDefinition(
        key=EntityTypeKey.NEWS_EVENT, name="News Event", description="An impactful news event"
    ),
    EntityTypeDefinition(
        key=EntityTypeKey.RESEARCH_DOCUMENT,
        name="Research Document",
        description="A published research document",
    ),
]


def get_entity_type_definition(key: str) -> Optional[EntityTypeDefinition]:
    for t in CANONICAL_ENTITY_TYPES:
        if t.key == key:
            return t
    return None
