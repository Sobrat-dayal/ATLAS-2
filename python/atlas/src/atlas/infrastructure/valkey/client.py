import logging
from typing import Optional
import valkey.asyncio as valkey
from valkey.exceptions import AuthenticationError, ConnectionError as ValkeyConnectionError, TimeoutError as ValkeyTimeoutError

from .settings import ValkeySettings
from .errors import (
    ValkeyConfigurationError,
    ValkeyUnavailableError,
    ValkeyAuthenticationError,
)

logger = logging.getLogger(__name__)


class ValkeyClientFactory:
    """
    Factory for managing Valkey client lifecycle.
    
    Creates a Valkey async client with a connection pool from configuration.
    The client is NOT created at import time.
    """
    def __init__(self, settings: ValkeySettings):
        self.settings = settings
        self._pool: Optional[valkey.ConnectionPool] = None
        self._client: Optional[valkey.Valkey] = None
        
    def get_client(self) -> Optional[valkey.Valkey]:
        """
        Returns the active Valkey client if enabled, otherwise None.
        Creates it on the first call if enabled and not already created.
        """
        if not self.settings.enabled:
            return None
            
        if self._client is not None:
            return self._client
            
        if not self.settings.password:
            raise ValkeyConfigurationError(
                "Valkey is enabled but password is not set."
            )
            
        try:
            password = self.settings.password.get_secret_value()
            
            # Connection kwargs mapping
            kwargs = {
                "host": self.settings.host,
                "port": self.settings.port,
                "db": self.settings.database,
                "username": self.settings.username,
                "password": password,
                "socket_connect_timeout": self.settings.connect_timeout_seconds,
                "socket_timeout": self.settings.socket_timeout_seconds,
                "max_connections": self.settings.max_connections,
                "health_check_interval": self.settings.health_check_interval_seconds,
                "decode_responses": False,  # Keep transport boundary as bytes
            }
            
            if self.settings.secure:
                kwargs["ssl"] = True
                if not self.settings.verify_tls:
                    import ssl
                    kwargs["ssl_cert_reqs"] = ssl.CERT_NONE
            
            self._pool = valkey.ConnectionPool(**kwargs)
            self._client = valkey.Valkey(connection_pool=self._pool)
            return self._client
            
        except Exception as e:
            # Mask unknown exceptions to avoid leaking credentials via unhandled errors
            raise ValkeyConfigurationError("An unexpected error occurred while initializing Valkey.") from e

    async def close(self) -> None:
        """Close the Valkey connection pool cleanly."""
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception as e:
                logger.warning("Error closing Valkey client", exc_info=e)
            finally:
                self._client = None
                
        if self._pool is not None:
            try:
                await self._pool.disconnect()
            except Exception as e:
                logger.warning("Error disconnecting Valkey pool", exc_info=e)
            finally:
                self._pool = None

    async def execute_safe_health_ping(self) -> bool:
        """Execute a safe PING command translating exceptions."""
        client = self.get_client()
        if not client:
            return False
            
        try:
            return await client.ping()
        except AuthenticationError as e:
            raise ValkeyAuthenticationError("Valkey authentication failed") from e
        except (ValkeyConnectionError, ValkeyTimeoutError) as e:
            raise ValkeyUnavailableError("Valkey is temporarily unavailable") from e
        except Exception as e:
            raise ValkeyUnavailableError("An unexpected Valkey error occurred.") from e
