
from pydantic_core import PydanticCustomError


def concept_not_found_error(key: str) -> PydanticCustomError:
    return PydanticCustomError("concept_not_found", f"Concept '{key}' not found in registry.")

def concept_wrong_unit_error(key: str, expected: str, actual: str) -> PydanticCustomError:
    return PydanticCustomError("concept_wrong_unit", f"Concept '{key}' expects unit kind '{expected}', got '{actual}'.")

def concept_wrong_statement_error(key: str, statement: str) -> PydanticCustomError:
    return PydanticCustomError("concept_wrong_statement", f"Concept '{key}' is not allowed in statement type '{statement}'.")

def concept_wrong_period_nature_error(key: str, expected: str, actual: str) -> PydanticCustomError:
    return PydanticCustomError("concept_wrong_period_nature", f"Concept '{key}' expects period nature '{expected}', got '{actual}'.")
