"""
Authentication API router.

Provides the ``/auth/me`` endpoint that returns the current user's identity.
This is the only authenticated endpoint created in Stage 13.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from atlas.auth import AuthPrincipal

from .dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me")
async def get_me(
    principal: AuthPrincipal = Depends(get_current_user),
) -> dict:
    """
    Return the authenticated user's identity.

    Requires a valid Bearer token in the Authorization header.
    """
    return {
        "user_id": principal.user_id,
        "email": principal.email,
        "email_verified": principal.email_verified,
        "role": principal.role,
    }
