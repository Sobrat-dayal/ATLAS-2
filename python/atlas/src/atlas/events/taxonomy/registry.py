"""Event Taxonomy Registry and Validation Engine (Stage 135)."""

from typing import Dict, List, Optional, Set
from ..domain import EventCategory
from ..errors import EventTypeInvalidError
from .classifications import CANONICAL_TAXONOMY


class EventTaxonomyRegistry:
    """Registry maintaining authorized categories, subtypes, and schema validation."""

    def __init__(self) -> None:
        self._taxonomy: Dict[EventCategory, List[str]] = dict(CANONICAL_TAXONOMY)
        self._all_subtypes: Set[str] = {
            subtype for subtypes in self._taxonomy.values() for subtype in subtypes
        }

    def list_categories(self) -> List[str]:
        """List all primary event categories."""
        return [c.value for c in self._taxonomy.keys()]

    def list_categories_with_subtypes(self) -> Dict[str, List[str]]:
        """List all primary categories mapped to their supported subtypes."""
        return {c.value: list(subtypes) for c, subtypes in self._taxonomy.items()}

    def list_subtypes(self, category: Optional[EventCategory] = None) -> List[str]:
        """List all subtypes, optionally filtered by category."""
        if category:
            return list(self._taxonomy.get(category, []))
        return sorted(list(self._all_subtypes))

    def validate_subtype(self, event_type: str) -> bool:
        """Validate whether a subtype string is registered without raising an exception."""
        return event_type in self._all_subtypes

    def validate_type(self, event_type: str) -> bool:
        """Validate whether an event type string is recognized."""
        if event_type not in self._all_subtypes:
            raise EventTypeInvalidError(event_type)
        return True

    def resolve_category(self, event_type: str) -> EventCategory:
        """Resolve primary category from a subtype string."""
        self.validate_type(event_type)
        for cat, subtypes in self._taxonomy.items():
            if event_type in subtypes:
                return cat
        raise EventTypeInvalidError(event_type)

    def register_custom_subtype(self, category: EventCategory, subtype: str) -> None:
        """Register a valid custom subtype under an existing category."""
        if category not in self._taxonomy:
            self._taxonomy[category] = []
        if subtype not in self._taxonomy[category]:
            self._taxonomy[category].append(subtype)
            self._all_subtypes.add(subtype)


# Global singleton registry
event_taxonomy_registry = EventTaxonomyRegistry()
