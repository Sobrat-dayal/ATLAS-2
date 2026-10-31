"""Universal Event Ingestion Adapters (Stage 135)."""

from .base import BaseEventAdapter
from .central_bank import CentralBankAdapter
from .corporate_action import CorporateActionAdapter
from .earnings import EarningsAdapter
from .economic_release import EconomicReleaseAdapter
from .geopolitical import GeopoliticalAdapter
from .news import NewsEventAdapter
from .physical_world import PhysicalWorldAdapter
from .sanctions import SanctionsAdapter

__all__ = [
    "BaseEventAdapter",
    "CentralBankAdapter",
    "CorporateActionAdapter",
    "EarningsAdapter",
    "EconomicReleaseAdapter",
    "GeopoliticalAdapter",
    "NewsEventAdapter",
    "PhysicalWorldAdapter",
    "SanctionsAdapter",
]

