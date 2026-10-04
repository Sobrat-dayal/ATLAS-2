"""
ATLAS API Authentication layer.

Provides FastAPI dependencies for extracting and verifying the current user
from Supabase JWTs, plus the auth API router for ``/auth/me``.
"""

from .dependencies import get_current_user, get_optional_user
from .router import router as auth_router

__all__ = ["get_current_user", "get_optional_user", "auth_router"]
