class LiveEventPipelineError(Exception):
    """Base class for all Live Event Pipeline errors."""
    pass


class LiveEventPipelineUnavailable(LiveEventPipelineError):
    """Raised when the Event Pipeline infrastructure is unavailable."""
    pass


class LiveEventSerializationError(LiveEventPipelineError):
    """Raised when an event fails serialization."""
    pass


class LiveEventTooLarge(LiveEventPipelineError):
    """Raised when an event payload exceeds the configured maximum size."""
    pass


class LiveEventDecodeError(LiveEventPipelineError):
    """Raised when a stream entry cannot be decoded into a valid event."""
    def __init__(self, message: str, stream_id: str):
        super().__init__(f"{message} (stream_id: {stream_id})")
        self.stream_id = stream_id


class LiveEventCursorInvalid(LiveEventPipelineError):
    """Raised when a given cursor format is invalid."""
    pass


class LiveEventCursorExpired(LiveEventPipelineError):
    """Raised when a requested cursor is older than the oldest retained stream entry."""
    def __init__(self, message: str, first_available_cursor: str = None, latest_cursor: str = None):
        super().__init__(message)
        self.first_available_cursor = first_available_cursor
        self.latest_cursor = latest_cursor


class LiveEventUnsupportedSchemaVersion(LiveEventPipelineError):
    """Raised when encountering an unsupported event schema version."""
    pass


class LiveEventUnsupportedType(LiveEventPipelineError):
    """Raised when encountering an unsupported live event type."""
    pass
