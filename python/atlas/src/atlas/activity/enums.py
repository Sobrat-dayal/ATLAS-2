from enum import Enum


class ActivityEventType(str, Enum):
    MODULE_OPENED = "MODULE_OPENED"
    ENTITY_SELECTED = "ENTITY_SELECTED"
