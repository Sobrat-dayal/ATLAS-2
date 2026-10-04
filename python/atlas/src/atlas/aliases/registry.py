from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AliasTypeDef:
    key: str
    name: str
    category: str
    normalization_strategy: str
    description: Optional[str] = None
    is_system: bool = True

_ALIAS_TYPES: Dict[str, AliasTypeDef] = {}

def register_alias_type(
    key: str, name: str, category: str, normalization_strategy: str, description: Optional[str] = None, is_system: bool = True
) -> None:
    _ALIAS_TYPES[key] = AliasTypeDef(
        key=key, name=name, category=category, normalization_strategy=normalization_strategy, description=description, is_system=is_system
    )

def get_alias_type_definition(key: str) -> Optional[AliasTypeDef]:
    return _ALIAS_TYPES.get(key)

def get_all_alias_type_definitions() -> List[AliasTypeDef]:
    return list(_ALIAS_TYPES.values())


# Register core alias types
register_alias_type("common_name", "Common Name", "name", "standard", "The primary common name of the entity")
register_alias_type("short_name", "Short Name", "name", "standard", "A shortened name or common acronym")
register_alias_type("acronym", "Acronym", "abbreviation", "standard", "Common acronym used to refer to the entity")
register_alias_type("abbreviation", "Abbreviation", "abbreviation", "standard", "Common abbreviation")
register_alias_type("brand_name", "Brand Name", "brand", "standard", "Brand name used by the entity")
register_alias_type("localized_name", "Localized Name", "localized", "standard", "Name translated or localized")
register_alias_type("informal_name", "Informal Name", "informal", "standard", "Informal or slang name")
register_alias_type("former_name", "Former Name", "historical", "standard", "A previously held name")
