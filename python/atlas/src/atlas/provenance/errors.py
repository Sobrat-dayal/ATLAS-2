class ProvenanceError(Exception):
    """Base exception for provenance errors."""
    pass


class ProvenanceSourceNotFoundError(ProvenanceError):
    pass


class ProvenanceSourceConflictError(ProvenanceError):
    pass


class InvalidProvenanceSourceKeyError(ProvenanceError):
    pass


class InvalidProvenanceSourceKindError(ProvenanceError):
    pass


class InvalidProvenanceRecordKindError(ProvenanceError):
    pass


class InvalidProvenanceURLError(ProvenanceError):
    pass


class InvalidProvenanceHashError(ProvenanceError):
    pass


class ProvenanceNotFoundError(ProvenanceError):
    pass


class InvalidEvidenceRoleError(ProvenanceError):
    pass


class InvalidProvenanceConfidenceError(ProvenanceError):
    pass


class ProvenanceTargetNotFoundError(ProvenanceError):
    pass


class ProvenanceLinkConflictError(ProvenanceError):
    pass
