class IdentifierDomainError(Exception):
    """Base class for all identifier errors."""
    pass

class IdentifierNotFoundError(IdentifierDomainError):
    pass

class UnknownIdentifierSchemeError(IdentifierDomainError):
    pass

class InvalidIdentifierValueError(IdentifierDomainError):
    pass

class IdentifierSubjectTypeInvalidError(IdentifierDomainError):
    pass

class IdentifierScopeRequiredError(IdentifierDomainError):
    pass

class IdentifierScopeForbiddenError(IdentifierDomainError):
    pass

class IdentifierScopeTypeInvalidError(IdentifierDomainError):
    pass

class IdentifierNamespaceRequiredError(IdentifierDomainError):
    pass

class IdentifierNamespaceForbiddenError(IdentifierDomainError):
    pass

class InvalidIdentifierNamespaceError(IdentifierDomainError):
    pass

class IdentifierConflictError(IdentifierDomainError):
    pass

class IdentifierHistoryConflictError(IdentifierDomainError):
    pass

class IdentifierAlreadyRetiredError(IdentifierDomainError):
    pass

class InvalidIdentifierValidityError(IdentifierDomainError):
    pass
