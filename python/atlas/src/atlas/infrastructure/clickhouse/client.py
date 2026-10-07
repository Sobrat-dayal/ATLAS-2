import logging
import clickhouse_connect
from clickhouse_connect.driver.client import Client as ClickHouseClient
from clickhouse_connect.driver.exceptions import ProgrammingError, OperationalError, DatabaseError

from .settings import ClickHouseSettings
from .errors import (
    ClickHouseConfigurationError,
    ClickHouseUnavailableError,
    ClickHouseAuthenticationError,
)

logger = logging.getLogger(__name__)


class ClickHouseClientFactory:
    """
    Factory for managing ClickHouse client lifecycle.
    
    Creates a ClickHouse client from configuration.
    The client is NOT created at import time.
    """
    def __init__(self, settings: ClickHouseSettings):
        self.settings = settings
        self._client: ClickHouseClient | None = None
        
    def get_client(self) -> ClickHouseClient | None:
        """
        Returns the active ClickHouse client if enabled, otherwise None.
        Creates it on the first call if enabled and not already created.
        """
        if not self.settings.enabled:
            return None
            
        if self._client is not None:
            return self._client
            
        if not self.settings.password:
            raise ClickHouseConfigurationError(
                "ClickHouse is enabled but password is not set."
            )
            
        try:
            password = self.settings.password.get_secret_value()
            self._client = clickhouse_connect.get_client(
                host=self.settings.host,
                port=self.settings.port,
                username=self.settings.username,
                password=password,
                database=self.settings.database,
                secure=self.settings.secure,
                verify=self.settings.verify_tls,
                connect_timeout=self.settings.connect_timeout_seconds,
                send_receive_timeout=self.settings.query_timeout_seconds,
            )
            return self._client
        except ProgrammingError as e:
            if "Authentication failed" in str(e):
                raise ClickHouseAuthenticationError("ClickHouse authentication failed") from e
            raise ClickHouseUnavailableError(f"Database error: {e}") from e
        except OperationalError as e:
            raise ClickHouseUnavailableError("ClickHouse is temporarily unavailable") from e
        except DatabaseError as e:
            raise ClickHouseUnavailableError(f"ClickHouse connection failed: {e}") from e
        except Exception as e:
            # Mask unknown exceptions to avoid leaking credentials via unhandled errors
            raise ClickHouseUnavailableError("An unexpected ClickHouse error occurred.") from e

    def close(self) -> None:
        """Close the ClickHouse client connection if it exists."""
        if self._client is not None:
            try:
                # Assuming the client handles its own resources or session
                # If there's an explicit close(), we'd call it. 
                # clickhouse-connect uses keep-alive by default, closing sessions manually isn't strictly required,
                # but let's clear the reference.
                if hasattr(self._client, 'close'):
                    self._client.close()
            except Exception as e:
                logger.warning(f"Error closing ClickHouse client: {e}")
            finally:
                self._client = None
