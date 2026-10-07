import re
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator

from atlas.fundamentals.enums import (
    FinancialPeriodNature,
    FinancialStatementType,
    FinancialUnitKind,
)

CONCEPT_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,127}$")

def validate_concept_key(key: str) -> str:
    if not CONCEPT_KEY_PATTERN.match(key):
        raise ValueError(f"Invalid canonical concept key: {key}")
    return key

FundamentalConceptKey = Annotated[str, AfterValidator(validate_concept_key)]

class FundamentalConceptDefinition(BaseModel):
    """
    Defines a canonical accounting concept in ATLAS.
    """

    key: FundamentalConceptKey = Field(...)
    display_name: str = Field(...)
    statement_types: frozenset[FinancialStatementType] = Field(...)
    period_nature: FinancialPeriodNature = Field(...)
    unit_kinds: frozenset[FinancialUnitKind] = Field(...)
    description: str = Field(default="")
    normal_sign: str = Field(default="signed")

    model_config = {"frozen": True}
