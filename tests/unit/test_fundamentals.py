import uuid
import pytest
from datetime import date, datetime, timezone
from decimal import Decimal

from pydantic import ValidationError

from atlas.fundamentals.enums import (
    FinancialStatementType,
    FinancialPeriodNature,
    FinancialUnitKind,
    FiscalPeriod,
    AccountingStandard,
)
from atlas.fundamentals.numeric import CanonicalDecimal
from atlas.fundamentals.units import FinancialUnit
from atlas.fundamentals.origin import FundamentalDataOrigin
from atlas.fundamentals.periods import FinancialPeriod
from atlas.fundamentals.line_items import StatementLineItem
from atlas.fundamentals.statements import IncomeStatement, BalanceSheet, CashFlowStatement
from atlas.fundamentals.facts import FinancialFact
from atlas.fundamentals.concept_registry import registry
from atlas.fundamentals.concepts import FundamentalConceptDefinition

COMPANY_ID = uuid.uuid4()
ORIGIN = FundamentalDataOrigin(
    provider_key="openbb",
    retrieved_at=datetime.now(timezone.utc)
)

def test_statement_line_item_validation():
    # Valid
    item = StatementLineItem(
        concept="revenue",
        value=CanonicalDecimal("100.5"),
        unit=FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD", scale=0)
    )
    assert str(item.value) == "100.5"

    # Invalid concept
    with pytest.raises(ValidationError, match="Concept 'nonexistent' not found in registry"):
        StatementLineItem(
            concept="nonexistent",
            value=CanonicalDecimal("10"),
            unit=FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD", scale=0)
        )
        
    # Invalid unit for concept
    with pytest.raises(ValidationError, match="Concept 'revenue' expects unit kind"):
        StatementLineItem(
            concept="revenue",
            value=CanonicalDecimal("10"),
            unit=FinancialUnit(kind=FinancialUnitKind.SHARES, scale=0)
        )

def test_income_statement_validation():
    period = FinancialPeriod(
        nature=FinancialPeriodNature.DURATION,
        period_start=date(2023, 1, 1),
        period_end=date(2023, 12, 31),
        fiscal_year=2023,
        fiscal_period=FiscalPeriod.FY,
    )
    
    # Valid
    stmt = IncomeStatement(
        company_id=COMPANY_ID,
        period=period,
        origin=ORIGIN,
        line_items=(
            StatementLineItem(
                concept="revenue",
                value=CanonicalDecimal("100"),
                unit=FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD", scale=0)
            ),
        )
    )
    assert stmt.line_items[0].concept == "revenue"

    # Wrong statement type for concept (revenue on balance sheet)
    with pytest.raises(ValidationError, match="Concept 'cash_and_cash_equivalents' is not allowed in statement type 'income_statement'"):
        IncomeStatement(
            company_id=COMPANY_ID,
            period=period,
            origin=ORIGIN,
            line_items=(
                StatementLineItem(
                    concept="cash_and_cash_equivalents",
                    value=CanonicalDecimal("100"),
                    unit=FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD", scale=0)
                ),
            )
        )

    # Wrong period nature
    bad_period = FinancialPeriod(
        nature=FinancialPeriodNature.INSTANT,
        period_end=date(2023, 12, 31),
        fiscal_year=2023,
        fiscal_period=FiscalPeriod.FY,
    )
    with pytest.raises(ValidationError, match="Concept 'revenue' expects period nature 'duration', got 'instant'"):
        IncomeStatement(
            company_id=COMPANY_ID,
            period=bad_period,
            origin=ORIGIN,
            line_items=(
                StatementLineItem(
                    concept="revenue",
                    value=CanonicalDecimal("100"),
                    unit=FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD", scale=0)
                ),
            )
        )
        
    # Duplicate concepts
    with pytest.raises(ValidationError, match="Duplicate canonical concept found in statement: revenue"):
        IncomeStatement(
            company_id=COMPANY_ID,
            period=period,
            origin=ORIGIN,
            line_items=(
                StatementLineItem(
                    concept="revenue",
                    value=CanonicalDecimal("100"),
                    unit=FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD", scale=0)
                ),
                StatementLineItem(
                    concept="revenue",
                    value=CanonicalDecimal("200"),
                    unit=FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD", scale=0)
                ),
            )
        )

def test_balance_sheet_validation():
    period = FinancialPeriod(
        nature=FinancialPeriodNature.INSTANT,
        period_end=date(2023, 12, 31),
        fiscal_year=2023,
        fiscal_period=FiscalPeriod.FY,
    )
    
    # Valid
    stmt = BalanceSheet(
        company_id=COMPANY_ID,
        period=period,
        origin=ORIGIN,
        line_items=(
            StatementLineItem(
                concept="cash_and_cash_equivalents",
                value=CanonicalDecimal("500"),
                unit=FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD", scale=0)
            ),
        )
    )
    assert stmt.statement_type == FinancialStatementType.BALANCE_SHEET

def test_financial_fact_validation():
    fact = FinancialFact(
        company_id=COMPANY_ID,
        concept="revenue",
        value=CanonicalDecimal("100"),
        unit=FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD", scale=0),
        period=FinancialPeriod(
            nature=FinancialPeriodNature.DURATION,
            period_start=date(2023, 1, 1),
            period_end=date(2023, 12, 31),
        ),
        origin=ORIGIN
    )
    assert fact.concept == "revenue"
