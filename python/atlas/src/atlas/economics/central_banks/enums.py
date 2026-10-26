"""Enumerations for Institutional Central Bank Intelligence (Stage 91).

Defines controlled taxonomies for central bank institution types, policy rate
representations, instrument categories, decision types, meeting kinds, voting
outcomes, publication types, forward guidance classifications, policy cycles,
and asset purchase/liquidity programs.
"""

from enum import StrEnum


class CentralBankInstitutionKind(StrEnum):
    """Institutional classification of central banking authorities."""
    CENTRAL_BANK = "CENTRAL_BANK"
    FEDERAL_CENTRAL_BANK = "FEDERAL_CENTRAL_BANK"
    SUPRANATIONAL_CENTRAL_BANK = "SUPRANATIONAL_CENTRAL_BANK"
    NATIONAL_CENTRAL_BANK = "NATIONAL_CENTRAL_BANK"
    MONETARY_AUTHORITY = "MONETARY_AUTHORITY"
    CURRENCY_BOARD = "CURRENCY_BOARD"
    REGIONAL_RESERVE_BANK = "REGIONAL_RESERVE_BANK"


class PolicyRateRepresentationKind(StrEnum):
    """Operational rate representation model of monetary policy instruments."""
    SINGLE_RATE = "SINGLE_RATE"                     # Fixed point rate
    SINGLE_TARGET_RATE = "SINGLE_TARGET_RATE"       # Fixed point target (e.g. BOE Bank Rate, RBI Repo)
    TARGET_RANGE = "TARGET_RANGE"                   # Lower and upper bound range (e.g. Fed Funds target range)
    CORRIDOR_FACILITIES = "CORRIDOR_FACILITIES"     # Standing facilities corridor (e.g. ECB MRO / Deposit / MLF)
    ADMINISTERED_BENCHMARK = "ADMINISTERED_BENCHMARK"


class PolicyInstrumentCategory(StrEnum):
    """Functional role of monetary policy instruments."""
    PRIMARY_POLICY_RATE = "PRIMARY_POLICY_RATE"
    TARGET_RANGE = "TARGET_RANGE"
    DEPOSIT_FACILITY = "DEPOSIT_FACILITY"
    DEPOSIT_FACILITY_RATE = "DEPOSIT_FACILITY_RATE"
    LENDING_FACILITY = "LENDING_FACILITY"
    LENDING_FACILITY_RATE = "LENDING_FACILITY_RATE"
    REFINANCING_OPERATION = "REFINANCING_OPERATION"
    REFINANCING_RATE = "REFINANCING_RATE"
    DISCOUNT_WINDOW = "DISCOUNT_WINDOW"
    REPO_RATE = "REPO_RATE"
    REVERSE_REPO_RATE = "REVERSE_REPO_RATE"
    OVERNIGHT_CALL_RATE = "OVERNIGHT_CALL_RATE"
    OVERNIGHT_RATE_TARGET = "OVERNIGHT_RATE_TARGET"
    RESERVE_REMUNERATION_RATE = "RESERVE_REMUNERATION_RATE"
    LOAN_PRIME_RATE = "LOAN_PRIME_RATE"
    OTHER_ADMINISTERED_RATE = "OTHER_ADMINISTERED_RATE"


class PolicyDecisionKind(StrEnum):
    """Action taken on policy interest rates or operating framework."""
    RATE_INCREASE = "RATE_INCREASE"
    RATE_DECREASE = "RATE_DECREASE"
    RATE_HOLD = "RATE_HOLD"
    MULTI_INSTRUMENT_CHANGE = "MULTI_INSTRUMENT_CHANGE"
    ASSET_PURCHASE_CHANGE = "ASSET_PURCHASE_CHANGE"
    FRAMEWORK_CHANGE = "FRAMEWORK_CHANGE"


class MeetingKind(StrEnum):
    """Meeting schedule classification."""
    REGULAR_POLICY_MEETING = "REGULAR_POLICY_MEETING"
    EXTRAORDINARY_MEETING = "EXTRAORDINARY_MEETING"
    EMERGENCY_MEETING = "EMERGENCY_MEETING"
    UNSCHEDULED_INTERMEETING = "UNSCHEDULED_INTERMEETING"


class VotingOutcomeKind(StrEnum):
    """Official recorded vote of policy committee members."""
    FOR = "FOR"
    AGAINST = "AGAINST"
    ABSTAIN = "ABSTAIN"
    ABSENT = "ABSENT"
    NOT_DISCLOSED = "NOT_DISCLOSED"


class PublicationKind(StrEnum):
    """Official communication and document classifications."""
    POLICY_DECISION_STATEMENT = "POLICY_DECISION_STATEMENT"
    MONETARY_POLICY_MINUTES = "MONETARY_POLICY_MINUTES"
    MONETARY_POLICY_REPORT = "MONETARY_POLICY_REPORT"
    ECONOMIC_PROJECTIONS = "ECONOMIC_PROJECTIONS"
    PRESS_RELEASE = "PRESS_RELEASE"
    SPEECH_TRANSCRIPT = "SPEECH_TRANSCRIPT"
    BALANCE_SHEET_RELEASE = "BALANCE_SHEET_RELEASE"


class ForwardGuidanceKind(StrEnum):
    """Official communication stance regarding future policy trajectory."""
    DATE_BASED = "DATE_BASED"                               # Calendar commitment (e.g. through mid-2025)
    STATE_CONTINGENT = "STATE_CONTINGENT"                   # Economic threshold (e.g. until inflation sustainably 2%)
    QUALITATIVE_OUTLOOK = "QUALITATIVE_OUTLOOK"             # Directional inclination without rigid criteria
    REACTION_FUNCTION = "REACTION_FUNCTION"                 # Description of response to incoming data
    POLICY_REACTION_FRAMEWORK = "POLICY_REACTION_FRAMEWORK" # Operational reaction function
    OUTLOOK_STATEMENT = "OUTLOOK_STATEMENT"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class PolicyCycleKind(StrEnum):
    """Monetary policy cycle regime classification."""
    TIGHTENING = "TIGHTENING"
    EASING = "EASING"
    HOLDING = "HOLDING"
    TRANSITIONAL = "TRANSITIONAL"
    MIXED_OR_TRANSITIONAL = "MIXED_OR_TRANSITIONAL"
    UNKNOWN = "UNKNOWN"


class PolicyProgramKind(StrEnum):
    """Categorization of balance sheet and liquidity programs."""
    ASSET_PURCHASE_PROGRAM = "ASSET_PURCHASE_PROGRAM"  # Quantitative Easing (QE)
    BALANCE_SHEET_RUNOFF = "BALANCE_SHEET_RUNOFF"      # Quantitative Tightening (QT)
    REINVESTMENT_POLICY = "REINVESTMENT_POLICY"
    LIQUIDITY_FACILITY = "LIQUIDITY_FACILITY"
    TARGETED_REFINANCING = "TARGETED_REFINANCING"
