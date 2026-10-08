from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class RealtimeWebSocketSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ATLAS_WS_", env_file=".env", extra="ignore")

    enabled: bool = True
    path: str = "/api/v1/realtime/ws"
    allowed_origins: List[str] = ["*"]  # Should be overridden in production
    max_inbound_message_bytes: int = 65536
    max_series_per_message: int = 100
    max_series_per_connection: int = 500
    subscription_buffer_max_events: int = 2048
    outbound_control_queue_max_messages: int = 256
    heartbeat_interval_seconds: int = 25
    heartbeat_timeout_seconds: int = 15
    event_backend_grace_seconds: int = 10
    shutdown_grace_seconds: int = 15
    max_resync_attempts: int = 3
