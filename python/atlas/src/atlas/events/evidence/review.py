"""Event Review Queue and Disputed Claim Management (Stage 135).

Holds ambiguous candidate deduplications, disputed claims, and provisional events
requiring institutional operator verification.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReviewItem(BaseModel):
    """Entry in the operator event review queue."""
    review_id: str
    item_type: str  # "AMBIGUOUS_MATCH", "CLAIM_CONFLICT", "UNVERIFIED_CANDIDATE"
    event_id: str
    candidate_key: str
    title: str
    competing_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    conflicting_claims: List[Dict[str, Any]] = Field(default_factory=list)
    reason: str
    status: str = "PENDING"  # "PENDING", "APPROVED", "REJECTED"
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer: Optional[str] = None


class EventReviewQueue:
    """Queue maintaining items requiring human or privileged service review."""

    def __init__(self) -> None:
        self._items: Dict[str, ReviewItem] = {}

    def enqueue(self, item: ReviewItem) -> None:
        """Enqueue an event issue for review."""
        self._items[item.review_id] = item

    def list_pending(self) -> List[ReviewItem]:
        """List all pending review items."""
        return [i for i in self._items.values() if i.status == "PENDING"]

    def resolve(self, review_id: str, approved: bool, reviewer: str = "OPERATOR") -> Optional[ReviewItem]:
        """Resolve a review item."""
        item = self._items.get(review_id)
        if not item:
            return None
        item.status = "APPROVED" if approved else "REJECTED"
        item.reviewed_at = datetime.now(timezone.utc)
        item.reviewer = reviewer
        return item
