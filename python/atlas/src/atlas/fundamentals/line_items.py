
from pydantic import BaseModel, Field, model_validator

from atlas.fundamentals.concept_registry import registry
from atlas.fundamentals.concepts import FundamentalConceptKey
from atlas.fundamentals.errors import concept_not_found_error, concept_wrong_unit_error
from atlas.fundamentals.numeric import CanonicalDecimal
from atlas.fundamentals.units import FinancialUnit


class StatementLineItem(BaseModel):
    """
    Represents a line item in a financial statement.
    """

    concept: FundamentalConceptKey = Field(...)
    value: CanonicalDecimal = Field(...)
    unit: FinancialUnit = Field(...)

    @model_validator(mode="after")
    def validate_concept_and_unit(self) -> "StatementLineItem":
        concept_def = registry.get(self.concept)
        if not concept_def:
            raise concept_not_found_error(self.concept)
        if self.unit.kind not in concept_def.unit_kinds:
            raise concept_wrong_unit_error(self.concept, str([k.value for k in concept_def.unit_kinds]), self.unit.kind.value)
        return self

    model_config = {"frozen": True}
