from enum import StrEnum
from pydantic import BaseModel, Field

class CapabilityPermissionClass(StrEnum):
    READ = "read"
    WRITE = "write"
    ACTION = "action"
    CRITICAL = "critical"

class CapabilityExposure(StrEnum):
    APPLICATION = "application"
    INTERNAL = "internal"

class CapabilityInvocationSource(StrEnum):
    API = "api"
    INTERNAL = "internal"
    AI = "ai"
    AGENT = "agent"
    MCP = "mcp"
    TERMINAL = "terminal"
    WORKFLOW = "workflow"

class CapabilityRef(BaseModel):
    key: str
    version: int = 1
