from pydantic import BaseModel, ConfigDict, Field

from atlas.economics.enums import EconomicDataOperation, EconomicRevisionPolicy

class EconomicProviderCapabilities(BaseModel):
    operations: frozenset[EconomicDataOperation] = Field(default_factory=frozenset)
    revision_policies: frozenset[EconomicRevisionPolicy] = Field(default_factory=frozenset)

    model_config = ConfigDict(frozen=True)
