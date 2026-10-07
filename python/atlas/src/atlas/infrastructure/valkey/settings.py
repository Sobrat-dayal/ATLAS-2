import re
from typing import Optional
from pydantic import BaseModel, Field, SecretStr, field_validator


class ValkeySettings(BaseModel):
    """
    Settings for connecting to Valkey infrastructure.
    
    Valkey provides low-latency, ephemeral state, coordination, and caching.
    It does NOT replace PostgreSQL for durable, authoritative data.
    """
    
    enabled: bool = Field(
        default=False,
        description="Whether Valkey integration is enabled. Disabled by default for standard tests."
    )
    
    host: str = Field(
        default="127.0.0.1",
        description="The host or IP address of the Valkey server."
    )
    
    port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="The TCP port used to connect to Valkey."
    )
    
    database: int = Field(
        default=0,
        description="The logical database index (0 is strictly preferred for ATLAS)."
    )
    
    username: str = Field(
        default="atlas_app",
        description="The application user name for Valkey."
    )
    
    password: Optional[SecretStr] = Field(
        default=None,
        description="The application user password. Must be set if enabled."
    )
    
    secure: bool = Field(
        default=False,
        description="Whether to use a secure (TLS) connection."
    )
    
    verify_tls: bool = Field(
        default=True,
        description="Whether to verify TLS certificates if secure is enabled."
    )
    
    connect_timeout_seconds: int = Field(
        default=5,
        gt=0,
        description="Timeout in seconds for establishing a connection."
    )
    
    socket_timeout_seconds: int = Field(
        default=5,
        gt=0,
        description="Timeout in seconds for socket operations."
    )
    
    health_check_interval_seconds: int = Field(
        default=30,
        ge=0,
        description="Interval in seconds for idle connection health checks."
    )
    
    max_connections: int = Field(
        default=100,
        gt=0,
        description="Maximum number of connections in the pool."
    )
    
    key_prefix: str = Field(
        default="atlas:dev:",
        description="The top-level key namespace prefix."
    )

    @field_validator("database")
    @classmethod
    def _validate_database(cls, v: int) -> int:
        """Enforce DB 0 policy."""
        if v != 0:
            raise ValueError("ATLAS enforces logical database 0 only.")
        return v
        
    @field_validator("key_prefix")
    @classmethod
    def _validate_key_prefix(cls, v: str) -> str:
        """Enforce safe namespace format."""
        if not re.match(r"^[a-z0-9_-]+:[a-z0-9_-]+:$", v):
            raise ValueError("Must be a valid namespaced prefix (e.g. 'atlas:dev:').")
        return v
