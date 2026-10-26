"""Enumerations for Country Economics Intelligence (Stage 90).

Defines controlled taxonomies for accounting scopes, national accounts approaches,
fiscal accounting bases, and trade valuation conventions.
"""

from enum import StrEnum


class GDPApproachKind(StrEnum):
    """National accounts measurement approach."""
    EXPENDITURE = "EXPENDITURE"   # C + I + G + (X - M)
    PRODUCTION = "PRODUCTION"     # Gross Value Added by Sector (Agri, Industry, Services)
    INCOME = "INCOME"             # Compensation of employees + Operating Surplus + Taxes less Subsidies


class GovernmentAccountingScope(StrEnum):
    """Institutional coverage of government fiscal accounts."""
    GENERAL_GOVERNMENT = "GENERAL_GOVERNMENT"  # Central + State/Provincial + Local + Social Security
    CENTRAL_GOVERNMENT = "CENTRAL_GOVERNMENT"  # Federal / National Government only
    PUBLIC_SECTOR = "PUBLIC_SECTOR"            # General Government + Non-financial Public Enterprises
    LOCAL_GOVERNMENT = "LOCAL_GOVERNMENT"      # Municipal / State / Provincial


class FiscalAccountingBasis(StrEnum):
    """Accounting basis for fiscal revenue, spending, and deficits."""
    ACCRUAL = "ACCRUAL"      # Recorded when obligation/liability is incurred (GFSM 2014)
    CASH = "CASH"            # Recorded when cash flows occur
    MODIFIED_CASH = "MODIFIED_CASH"


class TradeValuationKind(StrEnum):
    """Valuation convention for international merchandise trade."""
    FOB = "FOB"              # Free on Board (standard for exports, occasionally imports)
    CIF = "CIF"              # Cost, Insurance, and Freight (standard for customs imports)
    NOT_APPLICABLE = "NOT_APPLICABLE"
