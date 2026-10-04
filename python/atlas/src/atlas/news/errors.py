class NewsDomainError(Exception):
    pass


class NewsEventNotFoundError(NewsDomainError):
    pass


class NewsEventDataInconsistentError(NewsDomainError):
    pass


class InvalidNewsEventKindError(NewsDomainError):
    pass


class InvalidNewsEventStatusError(NewsDomainError):
    pass
