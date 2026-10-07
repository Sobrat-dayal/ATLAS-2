import re
from typing import Optional

from pydantic import BaseModel, Field, SecretStr, field_validator


class ClickHouseSettings(BaseModel):
    """
    Settings for connecting to ClickHouse infrastructure.
    
    ClickHouse is used for high-volume analytical, time-series, and event data.
    It does NOT replace PostgreSQL for transactional operations.
    """
    
    enabled: bool = Field(
        default=False,
        description="Whether ClickHouse integration is enabled. Disabled by default for standard tests."
    )
    
    host: str = Field(
        default="127.0.0.1",
        description="The host or IP address of the ClickHouse server."
    )
    
    port: int = Field(
        default=8123,
        ge=1,
        le=65535,
        description="The HTTP port used to connect to ClickHouse."
    )
    
    database: str = Field(
        default="atlas",
        description="The name of the ClickHouse database."
    )
    
    username: str = Field(
        default="atlas_app",
        description="The application user name for ClickHouse."
    )
    
    password: Optional[SecretStr] = Field(
        default=None,
        description="The application user password. Must be set if enabled."
    )
    
    secure: bool = Field(
        default=False,
        description="Whether to use a secure (HTTPS/TLS) connection."
    )
    
    verify_tls: bool = Field(
        default=True,
        description="Whether to verify TLS certificates if secure is enabled."
    )
    
    connect_timeout_seconds: int = Field(
        default=10,
        gt=0,
        description="Timeout in seconds for establishing a connection."
    )
    
    query_timeout_seconds: int = Field(
        default=30,
        gt=0,
        description="Timeout in seconds for executing queries."
    )

    @field_validator("database", "username")
    @classmethod
    def _validate_identifiers(cls, v: str) -> str:
        """Ensure database and username are safe identifiers."""
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", v):
            raise ValueError("Must be a valid ClickHouse identifier.")
        return v
