import logging
import sys
from contextvars import ContextVar

from .config import get_settings

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def setup_logging():
    """Initialize structured logging foundation."""
    settings = get_settings()
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | [%(request_id)s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
        stream=sys.stdout,
    )
    
    # Add request ID filter to root logger handlers
    request_filter = RequestIdFilter()
    for handler in logging.getLogger().handlers:
        handler.addFilter(request_filter)

    # Uvicorn loggers setup
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            handler.addFilter(request_filter)
