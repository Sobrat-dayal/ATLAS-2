"""Enums and Controlled Vocabularies for Company Supply Chain Intelligence (Stage 88)."""

from enum import Enum


class SupplyChainRelationshipType(str, Enum):
    """Canonical commercial relationship categories."""

    # Component & Material Supply
    SUPPLIES_COMPONENTS_TO = "SUPPLIES_COMPONENTS_TO"
    SUPPLIES_RAW_MATERIALS_TO = "SUPPLIES_RAW_MATERIALS_TO"
    SUPPLIES_PRODUCTS_TO = "SUPPLIES_PRODUCTS_TO"
    PROVIDES_SERVICES_TO = "PROVIDES_SERVICES_TO"

    # Manufacturing & Fabrication
    CONTRACT_MANUFACTURES_FOR = "CONTRACT_MANUFACTURES_FOR"
    OEM_SUPPLIES_TO = "OEM_SUPPLIES_TO"
    ODM_MANUFACTURES_FOR = "ODM_MANUFACTURES_FOR"

    # Distribution & Logistics
    DISTRIBUTES_PRODUCTS_FOR = "DISTRIBUTES_PRODUCTS_FOR"
    PROVIDES_LOGISTICS_TO = "PROVIDES_LOGISTICS_TO"
    SELLS_GOODS_TO = "SELLS_GOODS_TO"

    # Intellectual Property & Technology
    LICENSES_TECHNOLOGY_TO = "LICENSES_TECHNOLOGY_TO"

    # Other
    OTHER_COMMERCIAL_RELATIONSHIP = "OTHER_COMMERCIAL_RELATIONSHIP"


class RelationshipDirection(str, Enum):
    """Directionality relative to the subject company."""

    UPSTREAM_SUPPLIER = "UPSTREAM_SUPPLIER"    # Supplier -> Subject Company
    DOWNSTREAM_CUSTOMER = "DOWNSTREAM_CUSTOMER"  # Subject Company -> Customer


class VerificationStatus(str, Enum):
    """Data evidence verification state."""

    VERIFIED = "VERIFIED"                      # Formally verified in official regulatory filings (Form 10-K/20-F)
    SOURCE_REPORTED = "SOURCE_REPORTED"        # Reported by single verified provider or official announcement
    CORROBORATED = "CORROBORATED"              # Corroborated across multiple independent disclosures
    CANDIDATE_UNVERIFIED = "CANDIDATE_UNVERIFIED"  # Preliminary unverified candidate (excluded from confirmed tables)
    DISPUTED = "DISPUTED"                      # Conflicting disclosures observed
    OBSOLETE = "OBSOLETE"                      # Stale disclosure superseded by newer evidence


class RelationshipLifecycleStatus(str, Enum):
    """Temporal commercial lifecycle state."""

    ACTIVE_CONFIRMED = "ACTIVE_CONFIRMED"            # Currently confirmed active commercial relationship
    HISTORICALLY_REPORTED = "HISTORICALLY_REPORTED"  # Historically confirmed, no recent disclosure
    PLANNED = "PLANNED"                              # Announced contract, supply not yet commenced
    TERMINATED_CONFIRMED = "TERMINATED_CONFIRMED"    # Formally verified termination / phase-out
    STATUS_UNKNOWN = "STATUS_UNKNOWN"                # Status cannot be determined from evidence


class ConcentrationScope(str, Enum):
    """Scope of financial revenue or procurement dependency."""

    CONSOLIDATED_REVENUE = "CONSOLIDATED_REVENUE"      # Percentage of consolidated net revenue
    SEGMENT_REVENUE = "SEGMENT_REVENUE"                # Percentage of specific business segment revenue
    PROCUREMENT_SPEND = "PROCUREMENT_SPEND"            # Percentage of total procurement / cost of sales spend
    CRITICAL_INPUT_DEPENDENCY = "CRITICAL_INPUT_DEPENDENCY"  # Qualitative single-source critical dependency


class EntityKind(str, Enum):
    """Counterparty legal and listing classification."""

    PUBLIC_COMPANY = "PUBLIC_COMPANY"      # Exchange-listed corporate issuer
    PRIVATE_COMPANY = "PRIVATE_COMPANY"    # Privately held commercial entity
    SUBSIDIARY = "SUBSIDIARY"              # Operating subsidiary of corporate group
    ANONYMOUS_MAJOR = "ANONYMOUS_MAJOR"    # Unnamed disclosed counterparty (e.g. 'Customer A')
