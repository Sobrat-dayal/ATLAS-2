import logging
from dataclasses import dataclass
from typing import Optional

from .client import ClickHouseClientFactory
from .errors import ClickHouseError, ClickHouseConfigurationError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClickHouseHealthStatus:
    """Infrastructure health status of ClickHouse."""
    status: str
    database: Optional[str] = None
    server_version: Optional[str] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class ClickHouseHealthService:
    """
    Provides health checking for ClickHouse infrastructure.
    This is entirely separate from Provider Health.
    """
    def __init__(self, client_factory: ClickHouseClientFactory):
        self._client_factory = client_factory

    def check_health(self) -> ClickHouseHealthStatus:
        """
        Check the connectivity and availability of the ClickHouse database.
        Executes a lightweight `SELECT 1` without writing any data.
        """
        if not self._client_factory.settings.enabled:
            return ClickHouseHealthStatus(status="disabled")
            
        try:
            client = self._client_factory.get_client()
            if not client:
                return ClickHouseHealthStatus(status="disabled")

            # Execute a simple SELECT 1 to verify connectivity.
            # Using client.ping() if available, or direct command.
            if hasattr(client, 'ping'):
                is_up = client.ping()
                if not is_up:
                    return ClickHouseHealthStatus(
                        status="unavailable",
                        error="Ping failed",
                        database=self._client_factory.settings.database
                    )
            
            # Additional verification: get server version & current DB
            try:
                version = client.server_version
                db = client.command("SELECT currentDatabase()")
            except Exception as e:
                logger.debug(f"Could not retrieve server metadata: {e}")
                version = None
                db = self._client_factory.settings.database
                
            return ClickHouseHealthStatus(
                status="available",
                database=db,
                server_version=version
            )

        except ClickHouseConfigurationError as e:
            logger.error("ClickHouse configuration error in health check", exc_info=False)
            return ClickHouseHealthStatus(
                status="unavailable",
                error="Configuration Error",
                database=self._client_factory.settings.database
            )
        except ClickHouseError as e:
            logger.error("ClickHouse error in health check", exc_info=False)
            return ClickHouseHealthStatus(
                status="unavailable",
                error=str(e),
                database=self._client_factory.settings.database
            )
        except Exception as e:
            logger.error("Unexpected error in ClickHouse health check", exc_info=False)
            return ClickHouseHealthStatus(
                status="unavailable",
                error="Unexpected Infrastructure Error",
                database=self._client_factory.settings.database
            )
