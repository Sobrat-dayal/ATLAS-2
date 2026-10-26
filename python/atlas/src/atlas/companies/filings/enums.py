"""Enums for Regulatory Company Filings Intelligence (Stage 86)."""

from enum import Enum


class Regulator(str, Enum):
    """Regulatory agency or filing authority."""

    SEC_EDGAR = "SEC_EDGAR"
    SEBI = "SEBI"
    NSE = "NSE"
    BSE = "BSE"
    MCA = "MCA"
    COMPANIES_HOUSE = "COMPANIES_HOUSE"
    OTHER_REGULATOR = "OTHER_REGULATOR"


class FilingCategory(str, Enum):
    """High-level regulatory filing category."""

    ANNUAL_REPORTS = "ANNUAL_REPORTS"
    QUARTERLY_REPORTS = "QUARTERLY_REPORTS"
    CURRENT_REPORTS = "CURRENT_REPORTS"
    OWNERSHIP_INSIDER = "OWNERSHIP_INSIDER"
    PROXY_STATEMENTS = "PROXY_STATEMENTS"
    REGISTRATION_STATEMENTS = "REGISTRATION_STATEMENTS"
    OTHER_REGULATORY = "OTHER_REGULATORY"


class FilingForm(str, Enum):
    """Canonical regulatory filing form identifiers."""

    # Annual
    FORM_10K = "10-K"
    FORM_10K_A = "10-K/A"
    FORM_20F = "20-F"
    FORM_40F = "40-F"

    # Quarterly
    FORM_10Q = "10-Q"
    FORM_10Q_A = "10-Q/A"

    # Current & Material Events
    FORM_8K = "8-K"
    FORM_8K_A = "8-K/A"
    FORM_6K = "6-K"

    # Proxy
    DEF_14A = "DEF 14A"
    DEFA_14A = "DEFA14A"

    # Registration & Offering
    FORM_S1 = "S-1"
    FORM_S1_A = "S-1/A"
    FORM_S3 = "S-3"
    FORM_F1 = "F-1"

    # Institutional & Beneficial Ownership
    FORM_13F_HR = "13F-HR"
    FORM_13F_HR_A = "13F-HR/A"
    SCHEDULE_13D = "SC 13D"
    SCHEDULE_13D_A = "SC 13D/A"
    SCHEDULE_13G = "SC 13G"
    SCHEDULE_13G_A = "SC 13G/A"

    # Insider Disclosures
    FORM_3 = "3"
    FORM_3_A = "3/A"
    FORM_4 = "4"
    FORM_4_A = "4/A"
    FORM_5 = "5"
    FORM_5_A = "5/A"

    OTHER = "OTHER"


class DocumentMediaType(str, Enum):
    """Media types for filing attachments and document bodies."""

    HTML = "HTML"
    XML_XBRL = "XML_XBRL"
    PDF = "PDF"
    PLAIN_TEXT = "PLAIN_TEXT"
    JSON = "JSON"


class IngestionStatus(str, Enum):
    """Filing ingestion lifecycle status."""

    DISCOVERED = "DISCOVERED"
    DOWNLOADED = "DOWNLOADED"
    PARSED = "PARSED"
    INDEXED = "INDEXED"
    FAILED = "FAILED"
    RESTRICTED = "RESTRICTED"


class XBRLContextPeriodType(str, Enum):
    """XBRL temporal context nature."""

    INSTANT = "INSTANT"
    DURATION = "DURATION"


class XBRLUnitType(str, Enum):
    """XBRL measurement unit."""

    USD = "USD"
    SHARES = "SHARES"
    USD_PER_SHARE = "USD_PER_SHARE"
    PERCENT = "PERCENT"
    PURE = "PURE"


class AmendmentStatus(str, Enum):
    """Filing revision status."""

    ORIGINAL = "ORIGINAL"
    AMENDMENT = "AMENDMENT"
    SUPERSEDED = "SUPERSEDED"
