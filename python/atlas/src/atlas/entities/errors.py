from atlas.core.exceptions import AtlasError


class EntityError(AtlasError):
    pass


class EntityNotFoundError(EntityError):
    def __init__(self, entity_id: str):
        super().__init__(code="ENTITY_NOT_FOUND", message=f"Entity '{entity_id}' not found.")


class UnknownEntityTypeError(EntityError):
    def __init__(self, entity_type: str):
        super().__init__(
            code="UNKNOWN_ENTITY_TYPE", message=f"Unknown entity type: '{entity_type}'."
        )


class InvalidEntityNameError(EntityError):
    def __init__(self, message: str = "Invalid entity name"):
        super().__init__(code="INVALID_ENTITY_NAME", message=message)


class InvalidEntityDescriptionError(EntityError):
    def __init__(self, message: str = "Invalid entity description"):
        super().__init__(code="INVALID_ENTITY_DESCRIPTION", message=message)
