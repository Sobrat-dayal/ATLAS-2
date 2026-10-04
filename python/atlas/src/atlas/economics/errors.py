class EconomicDomainError(Exception):
    pass


class EconomicSeriesNotFoundError(EconomicDomainError):
    pass


class EconomicSeriesDataInconsistentError(EconomicDomainError):
    pass


class InvalidEconomicSeriesKindError(EconomicDomainError):
    pass


class InvalidEconomicFrequencyError(EconomicDomainError):
    pass


class InvalidValueRepresentationError(EconomicDomainError):
    pass


class InvalidSeasonalAdjustmentError(EconomicDomainError):
    pass


class InvalidEconomicScopeError(EconomicDomainError):
    pass
