class ResearchDomainError(Exception):
    pass


class ResearchDocumentNotFoundError(ResearchDomainError):
    pass


class ResearchDocumentDataInconsistentError(ResearchDomainError):
    pass


class InvalidResearchDocumentKindError(ResearchDomainError):
    pass


class InvalidDocumentLanguageError(ResearchDomainError):
    pass


class AbstractTooLargeError(ResearchDomainError):
    pass
