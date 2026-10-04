"""
FastAPI authentication dependencies.

These are injected into route handlers via ``Depends()``:

- ``get_current_user``: Returns AuthPrincipal or raises 401.
- ``get_optional_user``: Returns AuthPrincipal or None (for mixed endpoints).
"""

from __future__ import annotations

import logging
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from atlas.auth import AuthPrincipal, SupabaseTokenVerifier
from atlas.auth.verifier import TokenVerificationError

from ..config import Settings, get_settings

logger = logging.getLogger("atlas.api.auth")

# Bearer token extraction — auto_error=False lets us handle missing tokens
# gracefully in the optional variant.
_bearer_scheme = HTTPBearer(auto_error=False)

# Singleton verifier — created lazily on first use.
_verifier: Optional[SupabaseTokenVerifier] = None


def _get_verifier(settings: Settings = Depends(get_settings)) -> SupabaseTokenVerifier:
    """Return (or create) the singleton Supabase token verifier."""
    global _verifier
    if _verifier is None:
        _verifier = SupabaseTokenVerifier(
            supabase_url=settings.supabase_url,
            supabase_jwt_secret=settings.supabase_jwt_secret,
        )
    return _verifier


async def get_current_user(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Depends(_bearer_scheme)
    ] = None,
    verifier: SupabaseTokenVerifier = Depends(_get_verifier),
) -> AuthPrincipal:
    """
    Require a valid Supabase access token. Returns the verified AuthPrincipal.

    Raises HTTP 401 if the token is missing, invalid, or expired.
    Error messages never leak provider internals.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        principal = verifier.verify(credentials.credentials)
        return principal
    except TokenVerificationError as exc:
        logger.debug("Token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Depends(_bearer_scheme)
    ] = None,
    verifier: SupabaseTokenVerifier = Depends(_get_verifier),
) -> Optional[AuthPrincipal]:
    """
    Optionally extract user identity. Returns AuthPrincipal or None.

    Use this for endpoints that work for both anonymous and authenticated users.
    """
    if credentials is None:
        return None

    try:
        return verifier.verify(credentials.credentials)
    except TokenVerificationError:
        return None
