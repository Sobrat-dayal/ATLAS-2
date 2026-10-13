"""Domain exceptions for ATLAS User Activity."""


class ActivityError(Exception):
    """Base exception for activity domain."""


class ActivityHistoryDisabledError(ActivityError):
    """Raised when recording is attempted while activity history is disabled."""

    def __init__(self, message: str = "Activity history recording is disabled for this user."):
        super().__init__(message)


class InvalidModuleIdError(ActivityError):
    """Raised when an unknown module ID is supplied."""

    def __init__(self, module_id: str):
        super().__init__(f"Unknown canonical module ID: {module_id}")
        self.module_id = module_id


class InvalidEntityError(ActivityError):
    """Raised when an entity UUID is invalid or does not exist."""

    def __init__(self, entity_id: str):
        super().__init__(f"Canonical entity not found: {entity_id}")
        self.entity_id = entity_id


class EntityAccessDeniedError(ActivityError):
    """Raised when the user lacks permission to access the entity."""

    def __init__(self, entity_id: str):
        super().__init__(f"Access denied to entity: {entity_id}")
        self.entity_id = entity_id


class ModuleAccessDeniedError(ActivityError):
    """Raised when the user lacks permission to access the module."""

    def __init__(self, module_id: str):
        super().__init__(f"Access denied to module: {module_id}")
        self.module_id = module_id


class IdempotencyConflictError(ActivityError):
    """Raised when a client_event_id is re-submitted with conflicting payload."""

    def __init__(self, client_event_id: str):
        super().__init__(
            f"Event with client_event_id {client_event_id} already exists with different payload."
        )
        self.client_event_id = client_event_id


class InvalidCursorError(ActivityError):
    """Raised when an invalid keyset pagination cursor is provided."""

    def __init__(self, message: str = "Invalid activity pagination cursor."):
        super().__init__(message)
