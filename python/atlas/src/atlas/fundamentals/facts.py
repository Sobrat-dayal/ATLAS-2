import uuid

from pydantic import BaseModel, Field, model_validator

from atlas.fundamentals.concept_registry import registry
from atlas.fundamentals.concepts import FundamentalConceptKey
from atlas.fundamentals.errors import (
    concept_not_found_error,
    concept_wrong_period_nature_error,
    concept_wrong_unit_error,
)
from atlas.fundamentals.numeric import CanonicalDecimal
from atlas.fundamentals.origin import FundamentalDataOrigin
from atlas.fundamentals.periods import FinancialPeriod
from atlas.fundamentals.statements import FinancialReportMetadata
from atlas.fundamentals.units import FinancialUnit


class FinancialFact(BaseModel):
    company_id: uuid.UUID = Field(...)
    concept: FundamentalConceptKey = Field(...)
    period: FinancialPeriod = Field(...)
    value: CanonicalDecimal = Field(...)
    unit: FinancialUnit = Field(...)
    metadata: FinancialReportMetadata = Field(default_factory=FinancialReportMetadata)
    origin: FundamentalDataOrigin = Field(...)

    @model_validator(mode="after")
    def validate_fact(self) -> "FinancialFact":
        concept_def = registry.get(self.concept)
        if not concept_def:
            raise concept_not_found_error(self.concept)
            
        if self.unit.kind not in concept_def.unit_kinds:
            raise concept_wrong_unit_error(self.concept, str([k.value for k in concept_def.unit_kinds]), self.unit.kind.value)
            
        if self.period.nature != concept_def.period_nature:
            raise concept_wrong_period_nature_error(self.concept, concept_def.period_nature.value, self.period.nature.value)
            
        return self

    model_config = {"frozen": True}
