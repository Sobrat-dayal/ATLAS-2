"""Event Identity and Deduplication Module (Stage 135)."""

from .canonical import generate_canonical_event_key, normalize_token
from .deduplication import DeduplicationEngine, MatchConfidence
from .merge_split import MergeAuditRecord, MergeSplitManager

__all__ = [
    "generate_canonical_event_key",
    "normalize_token",
    "DeduplicationEngine",
    "MatchConfidence",
    "MergeAuditRecord",
    "MergeSplitManager",
]

