from typing import Protocol

from atlas.economics.requests import EconomicObservationsRequest, LatestEconomicObservationsRequest
from atlas.economics.responses import EconomicObservationsResponse, LatestEconomicObservationsResponse

class EconomicObservationsProvider(Protocol):
    async def get_economic_observations(
        self, request: EconomicObservationsRequest
    ) -> EconomicObservationsResponse:
        ...

class LatestEconomicObservationsProvider(Protocol):
    async def get_latest_economic_observations(
        self, request: LatestEconomicObservationsRequest
    ) -> LatestEconomicObservationsResponse:
        ...
