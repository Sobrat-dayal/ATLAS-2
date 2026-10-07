import uuid
from datetime import date, datetime, timezone
import pytest
from pydantic import ValidationError

from atlas.fundamentals.enums import (
    FinancialStatementType,
    FinancialPeriodNature,
    FiscalPeriod,
    ReportingPeriodType,
    FinancialUnitKind,
)
from atlas.fundamentals.units import FinancialUnit
from atlas.fundamentals.periods import FinancialPeriod
from atlas.fundamentals.origin import FundamentalDataOrigin
from atlas.fundamentals.line_items import StatementLineItem
from atlas.fundamentals.statements import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialReportMetadata,
)
from atlas.fundamentals.facts import FinancialFact
from atlas.fundamentals.concept_registry import registry
from atlas.fundamentals.numeric import CanonicalDecimal

def test_financial_unit_validation():
    # Valid
    unit = FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD")
    assert unit.currency_code == "USD"

    # Invalid currency code
    with pytest.raises(ValidationError):
        FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="usd")

    with pytest.raises(ValidationError):
        FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="US")

    # Missing currency code
    with pytest.raises(ValidationError):
        FinancialUnit(kind=FinancialUnitKind.CURRENCY)

    # Extra currency code
    with pytest.raises(ValidationError):
        FinancialUnit(kind=FinancialUnitKind.SHARES, currency_code="USD")


def test_financial_period_validation():
    # Valid DURATION
    p = FinancialPeriod(
        nature=FinancialPeriodNature.DURATION,
        period_start=date(2023, 1, 1),
        period_end=date(2023, 12, 31),
        fiscal_year=2023,
        fiscal_period=FiscalPeriod.FY,
        reporting_period_type=ReportingPeriodType.ANNUAL
    )

    # Valid INSTANT
    p2 = FinancialPeriod(
        nature=FinancialPeriodNature.INSTANT,
        period_end=date(2023, 12, 31),
    )

    # Invalid INSTANT with start date
    with pytest.raises(ValidationError):
        FinancialPeriod(
            nature=FinancialPeriodNature.INSTANT,
            period_start=date(2023, 1, 1),
            period_end=date(2023, 12, 31)
        )

    # Incompatible period
    with pytest.raises(ValidationError):
        FinancialPeriod(
            nature=FinancialPeriodNature.DURATION,
            period_start=date(2023, 1, 1),
            period_end=date(2023, 12, 31),
            fiscal_period=FiscalPeriod.Q1,
            reporting_period_type=ReportingPeriodType.ANNUAL
        )

def test_statement_line_item():
    unit = FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD")
    item = StatementLineItem(concept="revenue", value="100.5", unit=unit)
    assert item.value == CanonicalDecimal("100.5")

    # Invalid concept
    with pytest.raises(ValidationError):
        StatementLineItem(concept="unknown_concept_xyz", value="100.5", unit=unit)

    # Invalid unit for concept
    shares_unit = FinancialUnit(kind=FinancialUnitKind.SHARES)
    with pytest.raises(ValidationError):
        StatementLineItem(concept="revenue", value="100.5", unit=shares_unit)

def test_financial_statements():
    company_id = uuid.uuid4()
    origin = FundamentalDataOrigin(provider_key="test", retrieved_at=datetime.now(timezone.utc))
    period = FinancialPeriod(
        nature=FinancialPeriodNature.DURATION,
        period_start=date(2023, 1, 1),
        period_end=date(2023, 12, 31)
    )
    unit = FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD")
    
    # Valid Income Statement
    item = StatementLineItem(concept="revenue", value="1000", unit=unit)
    stmt = IncomeStatement(
        company_id=company_id,
        period=period,
        origin=origin,
        line_items=(item,)
    )

    # Invalid statement type concept
    with pytest.raises(ValidationError):
        bad_item = StatementLineItem(concept="total_assets", value="1000", unit=unit)
        IncomeStatement(
            company_id=company_id,
            period=period,
            origin=origin,
            line_items=(bad_item,)
        )

    # Duplicate concept
    with pytest.raises(ValidationError):
        IncomeStatement(
            company_id=company_id,
            period=period,
            origin=origin,
            line_items=(item, item)
        )

def test_financial_facts():
    company_id = uuid.uuid4()
    origin = FundamentalDataOrigin(provider_key="test", retrieved_at=datetime.now(timezone.utc))
    period = FinancialPeriod(
        nature=FinancialPeriodNature.DURATION,
        period_start=date(2023, 1, 1),
        period_end=date(2023, 12, 31)
    )
    unit = FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD")

    fact = FinancialFact(
        company_id=company_id,
        concept="revenue",
        period=period,
        value="500",
        unit=unit,
        origin=origin
    )
    assert fact.value == CanonicalDecimal("500")

