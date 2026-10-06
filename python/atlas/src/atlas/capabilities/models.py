from typing import Any, Generic, Optional, Type, TypeVar

from pydantic import BaseModel, Field


# Represents the input parameters for a capability
class CapabilityInput(BaseModel):
    pass


# Represents the output result from a capability
class CapabilityOutput(BaseModel):
    pass


TInput = TypeVar("TInput", bound=CapabilityInput)
TOutput = TypeVar("TOutput", bound=CapabilityOutput)


class CapabilityContext(BaseModel):
    """
    Context for executing a capability, providing access to:
    - the currently authenticated user ID
    - requested permissions
    - session application context, if any
    """

    user_id: str
    roles: list[str] = Field(default_factory=list)
    session_id: Optional[str] = None
    db_session: Any = None  # To hold AsyncSession or similar

    # Allow for extensible context and arbitrary types
    model_config = {"extra": "allow", "arbitrary_types_allowed": True}


class CapabilityDefinition(Generic[TInput, TOutput]):
    """
    Defines the contract for a capability.
    """

    def __init__(
        self, name: str, description: str, input_type: Type[TInput], output_type: Type[TOutput]
    ):
        self.name = name
        self.description = description
        self.input_type = input_type
        self.output_type = output_type
