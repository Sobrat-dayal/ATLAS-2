"""ATLAS Trading Domain.

Backtesting dependencies are optional for consumers that only use paper
trading, so the backtesting package is loaded lazily.
"""

from importlib import import_module
from typing import Any

__all__ = ["backtesting", "AtlasBacktestingService", "backtesting_router"]


def __getattr__(name: str) -> Any:
    if name == "backtesting":
        return import_module(".backtesting", __name__)
    if name in {"AtlasBacktestingService", "backtesting_router"}:
        module = import_module(".backtesting", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
