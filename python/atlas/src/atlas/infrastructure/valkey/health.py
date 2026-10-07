import logging
import time
from dataclasses import dataclass
from typing import Optional

from .client import ValkeyClientFactory
from .errors import ValkeyError, ValkeyConfigurationError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ValkeyHealthStatus:
    """Infrastructure health status of Valkey."""
    status: str
    database: Optional[int] = None
    server_version: Optional[str] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class ValkeyHealthService:
    """
    Provides health checking for Valkey infrastructure.
    This is entirely separate from Provider Health.
    """
    def __init__(self, client_factory: ValkeyClientFactory):
        self._client_factory = client_factory

    async def check_health(self) -> ValkeyHealthStatus:
        """
        Check the connectivity and availability of the Valkey server.
        Executes a lightweight `PING` without writing any data.
        """
        if not self._client_factory.settings.enabled:
            return ValkeyHealthStatus(status="disabled")
            
        start_time = time.perf_counter()
        
        try:
            client = self._client_factory.get_client()
            if not client:
                return ValkeyHealthStatus(status="disabled")

            # Execute a safe ping translating exceptions
            is_up = await self._client_factory.execute_safe_health_ping()
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            if not is_up:
                return ValkeyHealthStatus(
                    status="unavailable",
                    error="Ping returned False",
                    database=self._client_factory.settings.database,
                    latency_ms=latency_ms
                )
            
            # Additional verification: get server info safely (subset)
            try:
                # We specifically only fetch 'server' section to avoid huge payloads
                info = await client.info(section="server")
                version = info.get("redis_version") or info.get("valkey_version")
            except Exception as e:
                logger.debug(f"Could not retrieve server metadata: {e}")
                version = None
                
            return ValkeyHealthStatus(
                status="available",
                database=self._client_factory.settings.database,
                server_version=version,
                latency_ms=latency_ms
            )

        except ValkeyConfigurationError:
            logger.error("Valkey configuration error in health check", exc_info=False)
            return ValkeyHealthStatus(
                status="unavailable",
                error="Configuration Error",
                database=self._client_factory.settings.database,
                latency_ms=(time.perf_counter() - start_time) * 1000
            )
        except ValkeyError as e:
            logger.error("Valkey error in health check", exc_info=False)
            return ValkeyHealthStatus(
                status="unavailable",
                error=str(e),
                database=self._client_factory.settings.database,
                latency_ms=(time.perf_counter() - start_time) * 1000
            )
        except Exception:
            logger.error("Unexpected error in Valkey health check", exc_info=False)
            return ValkeyHealthStatus(
                status="unavailable",
                error="Unexpected Infrastructure Error",
                database=self._client_factory.settings.database,
                latency_ms=(time.perf_counter() - start_time) * 1000
            )
