"""Domain Exception Hierarchy for Company Peers & Comparable Company Analysis (Stage 87)."""


class PeerError(Exception):
    """Base exception for all company peers domain errors."""

    def __init__(self, message: str, code: str = "PEER_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class PeerCompanyNotFoundError(PeerError):
    def __init__(self, company_id: str):
        super().__init__(
            f"Company '{company_id}' not found in canonical registry.", "PEER_COMPANY_NOT_FOUND"
        )


class PeerGroupNotFoundError(PeerError):
    def __init__(self, group_id: str):
        super().__init__(f"Peer group '{group_id}' not found.", "PEER_GROUP_NOT_FOUND")


class PeerGroupNotAuthorizedError(PeerError):
    def __init__(self, group_id: str):
        super().__init__(
            f"Not authorized to access or modify peer group '{group_id}'.",
            "PEER_GROUP_NOT_AUTHORIZED",
        )


class PeerGroupRevisionConflictError(PeerError):
    def __init__(self, group_id: str, expected_rev: int, current_rev: int):
        super().__init__(
            f"Peer group '{group_id}' revision conflict (expected {expected_rev}, current {current_rev}).",
            "PEER_GROUP_REVISION_CONFLICT",
        )


class PeerGroupSizeExceededError(PeerError):
    def __init__(self, size: int, max_size: int = 25):
        super().__init__(
            f"Peer group size ({size}) exceeds maximum allowed limit of {max_size} companies.",
            "PEER_GROUP_SIZE_EXCEEDED",
        )


class PeerDuplicateCompanyError(PeerError):
    def __init__(self, company_id: str):
        super().__init__(
            f"Company '{company_id}' is already included in this peer group.",
            "PEER_DUPLICATE_COMPANY",
        )


class PeerSelfSelectionNotAllowedError(PeerError):
    def __init__(self, company_id: str):
        super().__init__(
            f"Subject company '{company_id}' cannot be selected as a peer of itself.",
            "PEER_SELF_SELECTION_NOT_ALLOWED",
        )


class PeerClassificationUnavailableError(PeerError):
    def __init__(self, company_id: str):
        super().__init__(
            f"Industry classification unavailable for company '{company_id}'.",
            "PEER_CLASSIFICATION_UNAVAILABLE",
        )


class PeerCandidatesUnavailableError(PeerError):
    def __init__(self, company_id: str):
        super().__init__(
            f"No comparable peer candidates could be resolved for company '{company_id}'.",
            "PEER_CANDIDATES_UNAVAILABLE",
        )


class PeerMetricNotSupportedError(PeerError):
    def __init__(self, metric_id: str):
        super().__init__(
            f"Comparable metric '{metric_id}' is not recognized in registry.",
            "PEER_METRIC_NOT_SUPPORTED",
        )


class PeerMetricIncompatibleError(PeerError):
    def __init__(self, metric_id: str, reason: str):
        super().__init__(
            f"Metric '{metric_id}' cannot be compared across selected companies: {reason}.",
            "PEER_METRIC_INCOMPATIBLE",
        )


class PeerPeriodNotComparableError(PeerError):
    def __init__(self, reason: str):
        super().__init__(
            f"Fiscal periods cannot be compared under selected mode: {reason}.",
            "PEER_PERIOD_NOT_COMPARABLE",
        )


class PeerCurrencyConversionUnavailableError(PeerError):
    def __init__(self, from_curr: str, to_curr: str):
        super().__init__(
            f"Authorized FX rate conversion unavailable between {from_curr} and {to_curr}.",
            "PEER_CURRENCY_CONVERSION_UNAVAILABLE",
        )


class PeerValuationDateUnavailableError(PeerError):
    def __init__(self, company_id: str, date_str: str):
        super().__init__(
            f"Market valuation observation unavailable for '{company_id}' as of {date_str}.",
            "PEER_VALUATION_DATE_UNAVAILABLE",
        )


class PeerInsufficientSampleError(PeerError):
    def __init__(self, metric_id: str, count: int, min_required: int = 2):
        super().__init__(
            f"Insufficient eligible sample size ({count} < {min_required}) to compute peer statistics for '{metric_id}'.",
            "PEER_INSUFFICIENT_SAMPLE",
        )


class PeerRatioNotMeaningfulError(PeerError):
    def __init__(self, metric_id: str, reason: str):
        super().__init__(
            f"Ratio '{metric_id}' is non-meaningful for financial comparison: {reason}.",
            "PEER_RATIO_NOT_MEANINGFUL",
        )
