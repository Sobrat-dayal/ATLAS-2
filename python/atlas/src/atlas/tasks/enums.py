"""Enums for ATLAS Personal Tasks (Stage 54)."""

from enum import Enum


class TaskStatus(str, Enum):
    """Lifecycle statuses for a personal task."""

    OPEN = "OPEN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TaskStatusFilter(str, Enum):
    """Query filter options for task listings."""

    OPEN = "OPEN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ALL = "ALL"
