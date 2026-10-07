from typing import Optional

from pydantic import BaseModel, Field, model_validator

from atlas.fundamentals.enums import FinancialUnitKind


class FinancialUnit(BaseModel):
    """
    Represents a financial unit.
    """

    kind: FinancialUnitKind = Field(...)
    currency_code: Optional[str] = Field(
        default=None,
        description="Must be exactly 3 uppercase letters (e.g. USD) if kind is currency or currency_per_share",
    )

    @model_validator(mode="after")
    def validate_currency_code(self) -> "FinancialUnit":
        if self.kind in (
            FinancialUnitKind.CURRENCY,
            FinancialUnitKind.CURRENCY_PER_SHARE,
        ):
            if not self.currency_code:
                raise ValueError(
                    "currency_code is required for currency and currency_per_share units."
                )
            if len(self.currency_code) != 3 or not self.currency_code.isupper() or not self.currency_code.isalpha():
                raise ValueError("currency_code must be exactly 3 uppercase letters.")
        else:
            if self.currency_code is not None:
                raise ValueError(f"currency_code must be None for {self.kind.value} units.")
        return self

    model_config = {"frozen": True}
