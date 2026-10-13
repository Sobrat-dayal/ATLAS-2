"""Enums for ATLAS Approval Inbox and Decision Architecture (Stage 54)."""

from enum import Enum


class ApprovalStatus(str, Enum):
    """Persisted lifecycle statuses for an approval request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ApprovalDecisionType(str, Enum):
    """Decision options for an authorized human actor."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"


class ApprovalStatusFilter(str, Enum):
    """Filter options for querying approval requests."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    ALL = "ALL"
