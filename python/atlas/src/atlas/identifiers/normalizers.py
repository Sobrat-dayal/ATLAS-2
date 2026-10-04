import re


def normalize_uppercase_trim(value: str) -> str:
    return value.strip().upper()

def normalize_lowercase_trim(value: str) -> str:
    return value.strip().lower()

def normalize_compact_uppercase(value: str) -> str:
    return re.sub(r"\s+", "", value).upper()

def normalize_digits(value: str) -> str:
    return re.sub(r"\D", "", value)

def normalize_doi(value: str) -> str:
    val = value.strip().lower()
    if val.startswith("https://doi.org/"):
        return val[len("https://doi.org/"):]
    if val.startswith("doi:"):
        return val[4:]
    return val

def normalize_arxiv(value: str) -> str:
    val = value.strip().lower()
    if val.startswith("arxiv:"):
        return val[6:]
    if val.startswith("https://arxiv.org/abs/"):
        return val[len("https://arxiv.org/abs/"):]
    return val

def normalize_openalex(value: str) -> str:
    val = value.strip().upper()
    if val.startswith("HTTPS://OPENALEX.ORG/"):
        return val[len("HTTPS://OPENALEX.ORG/"):]
    return val

def normalize_isbn10(value: str) -> str:
    val = value.strip().upper()
    val = re.sub(r"[\s-]", "", val)
    return val

def normalize_isbn13(value: str) -> str:
    val = value.strip().upper()
    val = re.sub(r"[\s-]", "", val)
    return val

def normalize_preserve_trim(value: str) -> str:
    return value.strip()

def normalize_cik(value: str) -> str:
    val = normalize_digits(value)
    if val:
        return val.zfill(10)
    return ""

def normalize_unlocode(value: str) -> str:
    # UN/LOCODE: 5 characters, usually compact.
    val = value.strip().upper()
    val = re.sub(r"[\s-]", "", val)
    return val
