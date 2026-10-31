"""Thread-Safe QuantLib Execution Context Manager (Stage 142).

QuantLib relies on global instance settings for evaluation dates.
This context manager serializes calculations and guarantees that:
1. Every evaluation sets its explicit evaluation date.
2. Cross-thread concurrent queries cannot overwrite or leak evaluation dates.
3. Upon exit or exception, the previous evaluation date is safely restored.
"""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Generator
import QuantLib as ql
from atlas.options.quant.quantlib.dates import to_ql_date

_quantlib_global_lock = threading.RLock()


@contextmanager
def isolated_quantlib_context(evaluation_date: ql.Date | str) -> Generator[ql.Date, None, None]:
    """Execute QuantLib pricing logic inside an isolated evaluation-date context."""
    ql_date = to_ql_date(evaluation_date) if isinstance(evaluation_date, str) else evaluation_date

    with _quantlib_global_lock:
        settings = ql.Settings.instance()
        prev_date = settings.evaluationDate
        try:
            settings.evaluationDate = ql_date
            yield ql_date
        finally:
            settings.evaluationDate = prev_date

