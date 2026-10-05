from typing import Any
import importlib.metadata
import logging

from atlas.providers.openbb.errors import (
    OpenBBRuntimeUnavailableError,
    OpenBBVersionUnsupportedError,
)
from atlas.providers.openbb.inspector import OpenBBCoverageInspector
from atlas.providers.openbb.types import OpenBBCoverageSnapshot

logger = logging.getLogger(__name__)

class OpenBBRuntime:
    """
    Facade for the OpenBB Python runtime.
    Isolates the rest of ATLAS from raw OpenBB objects.
    """
    
    SUPPORTED_MAJOR_VERSION = "2"

    def __init__(self):
        self._obb: Any = None
        self._version: str = ""
        self._coverage_inspector: OpenBBCoverageInspector | None = None

    def initialize(self) -> None:
        """
        Load OpenBB runtime and validate version compatibility.
        """
        try:
            self._version = importlib.metadata.version("openbb-core")
        except importlib.metadata.PackageNotFoundError:
            raise OpenBBRuntimeUnavailableError("openbb-core package is not installed.")

        major_version = self._version.split(".")[0]
        if major_version != self.SUPPORTED_MAJOR_VERSION:
            raise OpenBBVersionUnsupportedError(
                f"Unsupported OpenBB core version: {self._version}. "
                f"Expected major version {self.SUPPORTED_MAJOR_VERSION}."
            )

        try:
            from openbb import obb
            self._obb = obb
            self._coverage_inspector = OpenBBCoverageInspector(self._obb)
        except ImportError as e:
            raise OpenBBRuntimeUnavailableError(f"Failed to import OpenBB runtime: {e}") from e
        except Exception as e:
            raise OpenBBRuntimeUnavailableError(f"OpenBB runtime initialization failed: {e}") from e

    def get_version(self) -> str:
        """Return the installed OpenBB core version."""
        if not self._version:
            self.initialize()
        return self._version

    def get_coverage(self) -> OpenBBCoverageSnapshot:
        """Return local metadata snapshot of OpenBB capabilities."""
        if not self._coverage_inspector:
            self.initialize()
        return self._coverage_inspector.inspect()

    def get_client(self) -> Any:
        """
        Internal access to the raw obb client.
        MUST NOT be exposed to Domain Services or Capability Handlers.
        """
        if not self._obb:
            self.initialize()
        return self._obb
