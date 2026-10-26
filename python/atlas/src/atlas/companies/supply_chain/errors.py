"""Domain Exceptions for Company Supply Chain Intelligence (Stage 88)."""



class SupplyChainError(Exception):
    """Base exception for all company supply chain domain errors."""

    def __init__(self, message: str, code: str = "SUPPLY_CHAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class SupplyChainCompanyNotFoundError(SupplyChainError):
    """Raised when a requested company entity is unknown in the corporate registry."""

    def __init__(self, company_id: str):
        super().__init__(
            f"Company entity '{company_id}' not found in canonical company registry.",
            "SUPPLY_CHAIN_COMPANY_NOT_FOUND",
        )
        self.company_id = company_id


class SupplyChainRelationshipNotFoundError(SupplyChainError):
    """Raised when an asserted relationship ID cannot be found."""

    def __init__(self, relationship_id: str):
        super().__init__(
            f"Commercial relationship '{relationship_id}' not found.",
            "SUPPLY_CHAIN_RELATIONSHIP_NOT_FOUND",
        )
        self.relationship_id = relationship_id


class SupplyChainTraversalLimitExceededError(SupplyChainError):
    """Raised when network graph query exceeds maximum allowable depth, node, or edge limits."""

    def __init__(self, depth: int, max_depth: int):
        super().__init__(
            f"Requested graph traversal depth {depth} exceeds server budget maximum of {max_depth}.",
            "SUPPLY_CHAIN_TRAVERSAL_LIMIT_EXCEEDED",
        )
        self.depth = depth
        self.max_depth = max_depth


class SupplyChainCycleDetectedError(SupplyChainError):
    """Raised when an unhandled infinite cycle occurs during graph path calculation."""

    def __init__(self, path: list):
        super().__init__(
            f"Graph cycle detected during multi-tier traversal: {' -> '.join(path)}.",
            "SUPPLY_CHAIN_CYCLE_DETECTED",
        )
        self.path = path


class SupplyChainExposureUnavailableError(SupplyChainError):
    """Raised when financial exposure calculation cannot be performed due to incompatible accounting scope or currency."""

    def __init__(self, reason: str):
        super().__init__(
            f"Financial exposure calculation unavailable: {reason}.",
            "SUPPLY_CHAIN_EXPOSURE_UNAVAILABLE",
        )
        self.reason = reason


class SupplyChainInvalidDirectionError(SupplyChainError):
    """Raised when an invalid network direction parameter is provided."""

    def __init__(self, direction: str):
        super().__init__(
            f"Invalid network relationship direction: '{direction}'. Must be UPSTREAM_SUPPLIER, DOWNSTREAM_CUSTOMER, or BOTH.",
            "SUPPLY_CHAIN_DIRECTION_INVALID",
        )
        self.direction = direction


class SupplyChainEvidenceMissingError(SupplyChainError):
    """Raised when an asserted relationship lacks verifiable source evidence."""

    def __init__(self, relationship_id: str):
        super().__init__(
            f"Relationship '{relationship_id}' lacks mandatory verifiable source evidence citations.",
            "SUPPLY_CHAIN_EVIDENCE_MISSING",
        )
        self.relationship_id = relationship_id
