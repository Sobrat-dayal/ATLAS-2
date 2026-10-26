"""Domain enums for Company Ownership Intelligence (Stage 85).

Defines canonical taxonomies for holder classifications, ownership forms,
security position types, regulatory disclosure kinds, jurisdictions, and
position change statuses.
"""

from enum import Enum


class HolderCategory(str, Enum):
    """Classification of the security holder or reporting person."""
    INSTITUTIONAL_MANAGER = "INSTITUTIONAL_MANAGER"  # 13F investment manager / adviser
    INVESTMENT_FUND = "INVESTMENT_FUND"              # Specific mutual fund, ETF, or trust
    INSIDER_PERSON = "INSIDER_PERSON"                # Officers, directors, or executive insiders
    BENEFICIAL_OWNER = "BENEFICIAL_OWNER"            # 13D/13G >=5% beneficial owners
    CORPORATION = "CORPORATION"                      # Corporate parent or strategic cross-holder
    GOVERNMENT_SOVEREIGN = "GOVERNMENT_SOVEREIGN"    # Sovereign wealth funds / state institutions
    PROMOTER = "PROMOTER"                            # Founders / promoter group (e.g. SEBI taxonomy)
    PROMOTER_GROUP = "PROMOTER_GROUP"                # Promoter group entities
    NOMINEE_CUSTODIAN = "NOMINEE_CUSTODIAN"          # Legal nominee / clearing custodian
    OTHER_DISCLOSED = "OTHER_DISCLOSED"              # Other public disclosed holders


class OwnershipForm(str, Enum):
    """Legal nature of the ownership or holding."""
    DIRECT = "DIRECT"                              # Directly owned and registered
    INDIRECT = "INDIRECT"                          # Owned via trust, family, or holding vehicle
    BENEFICIAL = "BENEFICIAL"                      # Beneficial ownership under regulatory definition
    MANAGED_DISCRETIONARY = "MANAGED_DISCRETIONARY"# Investment discretion without direct economic title
    NOMINEE = "NOMINEE"                            # Street name / nominee holding for underlying owner
    VOTING_ONLY = "VOTING_ONLY"                    # Dispositive/voting power without economic claim


class PositionType(str, Enum):
    """Type of instrument or share class in which the position is held."""
    COMMON_SHARES = "COMMON_SHARES"                # Ordinary common equity
    PREFERRED_SHARES = "PREFERRED_SHARES"          # Preferred equity
    DEPOSITARY_RECEIPT = "DEPOSITARY_RECEIPT"      # ADR / GDR units
    RESTRICTED_STOCK_UNITS = "RESTRICTED_STOCK_UNITS" # Unvested or vested restricted share units
    OPTIONS_CALL = "OPTIONS_CALL"                  # Call options (never merged with common equity)
    OPTIONS_PUT = "OPTIONS_PUT"                    # Put options (never merged with common equity)
    WARRANTS = "WARRANTS"                          # Warrants
    CONVERTIBLE_DEBT = "CONVERTIBLE_DEBT"          # Convertible debt instruments


class DisclosureType(str, Enum):
    """Regulatory or authoritative disclosure origin."""
    FORM_13F = "FORM_13F"                          # US SEC Form 13F-HR institutional report
    SCHEDULE_13D = "SCHEDULE_13D"                  # US SEC Schedule 13D active beneficial filing
    SCHEDULE_13G = "SCHEDULE_13G"                  # US SEC Schedule 13G passive beneficial filing
    FORM_3 = "FORM_3"                              # US SEC Form 3 initial insider disclosure
    FORM_4 = "FORM_4"                              # US SEC Form 4 insider transaction report
    FORM_5 = "FORM_5"                              # US SEC Form 5 annual insider statement
    SHAREHOLDING_PATTERN_SEBI = "SHAREHOLDING_PATTERN_SEBI" # Indian SEBI Reg 31 shareholding pattern
    ANNUAL_REPORT_DISCLOSURE = "ANNUAL_REPORT_DISCLOSURE"   # Corporate annual report shareholder notes
    EXCHANGE_FILING = "EXCHANGE_FILING"            # Exchange notification or major holder disclosure


class PositionChangeStatus(str, Enum):
    """Classification of position evolution between consecutive reporting snapshots."""
    NEW_POSITION = "NEW_POSITION"                  # First appearance in disclosure coverage
    INCREASED = "INCREASED"                        # Shares increased vs prior period
    DECREASED = "DECREASED"                        # Shares decreased vs prior period
    UNCHANGED = "UNCHANGED"                        # Identical shares held
    SOLD_OUT = "SOLD_OUT"                          # Explicitly reported exit (0 shares)


class Jurisdiction(str, Enum):
    """Regulatory framework governing the disclosure."""
    US_SEC = "US_SEC"
    INDIA_SEBI = "INDIA_SEBI"
    UK_FCA = "UK_FCA"
    EU_ESMA = "EU_ESMA"
    GLOBAL_OTHER = "GLOBAL_OTHER"
