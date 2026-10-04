class GeographicDomainError(Exception):
    pass


class GeographicEntityNotFoundError(GeographicDomainError):
    pass


class GeographicEntityDataInconsistentError(GeographicDomainError):
    pass


class CountryNotFoundError(GeographicDomainError):
    pass


class InvalidCountryKindError(GeographicDomainError):
    pass


class InvalidPortKindError(GeographicDomainError):
    pass


class InvalidAirportKindError(GeographicDomainError):
    pass


class InvalidExchangeKindError(GeographicDomainError):
    pass


class InvalidCoordinatesError(GeographicDomainError):
    pass


class InvalidTimezoneError(GeographicDomainError):
    pass
