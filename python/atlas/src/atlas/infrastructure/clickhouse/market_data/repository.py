from typing import Any
import uuid

from atlas.infrastructure.clickhouse.client import ClickHouseClientFactory
from atlas.infrastructure.clickhouse.errors import ClickHouseUnavailableError


class HistoricalMarketDataRepository:
    def __init__(self, factory: ClickHouseClientFactory):
        self._factory = factory

    def insert_bars(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return

        client = self._factory.get_client()
        if not client:
            raise ClickHouseUnavailableError("ClickHouse client is disabled or unavailable.")

        # Extract column names from the first row
        columns = list(rows[0].keys())
        # clickhouse-connect expects a list of lists or tuples for data
        data = [[row[col] for col in columns] for row in rows]

        try:
            client.insert("historical_market_bars_versions", data, column_names=columns)
        except Exception as e:
            raise ClickHouseUnavailableError(f"Failed to insert historical bars: {e}") from e
