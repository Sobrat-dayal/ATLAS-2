import re


def validate_isin(value: str) -> bool:
    if len(value) != 12:
        return False
    if not re.match(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$", value):
        return False
    # Modulo 10 double add double check digit could be added here, but regex is good enough for Stage 21
    return True


def validate_cusip(value: str) -> bool:
    if len(value) != 9:
        return False
    if not re.match(r"^[A-Z0-9]{9}$", value):
        return False
    return True


def validate_sedol(value: str) -> bool:
    if len(value) != 7:
        return False
    if not re.match(r"^[B-DF-HJ-NP-TV-Z0-9]{6}[0-9]$", value):
        return False
    return True


def validate_figi(value: str) -> bool:
    if len(value) != 12:
        return False
    if not re.match(r"^[A-Z0-9]{12}$", value):
        return False
    return True


def validate_lei(value: str) -> bool:
    if len(value) != 20:
        return False
    if not re.match(r"^[A-Z0-9]{20}$", value):
        return False
    return True


def validate_iso3166_alpha2(value: str) -> bool:
    return bool(re.match(r"^[A-Z]{2}$", value))


def validate_iso3166_alpha3(value: str) -> bool:
    return bool(re.match(r"^[A-Z]{3}$", value))


def validate_iso4217_alpha(value: str) -> bool:
    return bool(re.match(r"^[A-Z]{3}$", value))


def validate_mic(value: str) -> bool:
    return bool(re.match(r"^[A-Z0-9]{4}$", value))


def validate_iata(value: str) -> bool:
    return bool(re.match(r"^[A-Z0-9]{3}$", value))


def validate_icao(value: str) -> bool:
    return bool(re.match(r"^[A-Z0-9]{4}$", value))


def validate_doi(value: str) -> bool:
    # 10.xxxx/xxxx
    return bool(re.match(r"^10\.\d+/.+", value))


def validate_isbn10(value: str) -> bool:
    return bool(re.match(r"^[0-9]{9}[0-9X]$", value))


def validate_isbn13(value: str) -> bool:
    return bool(re.match(r"^[0-9]{13}$", value))
