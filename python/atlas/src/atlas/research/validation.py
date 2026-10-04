import re
from typing import Optional

from atlas.research.errors import AbstractTooLargeError, InvalidDocumentLanguageError

# Basic loose validation for language tags
LANG_REGEX = re.compile(r"^[a-zA-Z]{2,3}(-[a-zA-Z0-9]+)*$")

def validate_language_code(language_code: Optional[str]) -> Optional[str]:
    if not language_code:
        return None
    
    language_code = language_code.strip()
    if not language_code:
        return None
        
    if len(language_code) > 35:
        raise InvalidDocumentLanguageError("Language code exceeds maximum length of 35 characters.")
        
    if not LANG_REGEX.match(language_code):
        raise InvalidDocumentLanguageError(f"Invalid language code format: {language_code}")
        
    return language_code

def validate_abstract_text(abstract_text: Optional[str]) -> Optional[str]:
    if not abstract_text:
        return None
        
    abstract_text = abstract_text.strip()
    if not abstract_text:
        return None
        
    # Limit to 64KB approximately
    if len(abstract_text.encode('utf-8')) > 65536:
        raise AbstractTooLargeError("Abstract text exceeds the maximum allowed size of 64KB.")
        
    return abstract_text
