"""
AuthPrincipal — the identity of the authenticated user.

This is a read-only data transfer object derived from a verified Supabase JWT.
It contains no authorization information (roles/permissions come in Stage 14).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True, slots=True)
class AuthPrincipal:
    """
    Represents a verified user identity extracted from a Supabase access token.

    Attributes:
        sub: The Supabase user UUID (``auth.users.id``).
        email: The user's email address, if present in the token.
        email_verified: Whether the email has been verified.
        phone: The user's phone number, if present.
        aud: The JWT audience claim.
        role: The Supabase role claim (e.g. ``"authenticated"``).
        iat: Issued-at timestamp (epoch seconds).
        exp: Expiration timestamp (epoch seconds).
        raw_claims: The full decoded JWT payload for downstream inspection.
    """

    sub: str
    email: Optional[str] = None
    email_verified: bool = False
    phone: Optional[str] = None
    aud: str = "authenticated"
    role: str = "authenticated"
    iat: Optional[int] = None
    exp: Optional[int] = None
    raw_claims: dict = field(default_factory=dict, repr=False)

    @property
    def user_id(self) -> str:
        """Alias for ``sub`` — the Supabase user UUID."""
        return self.sub

    @classmethod
    def from_claims(cls, claims: dict) -> AuthPrincipal:
        """
        Construct an AuthPrincipal from a decoded JWT claims dict.

        Args:
            claims: The decoded JWT payload.

        Returns:
            An AuthPrincipal populated from the claims.
        """
        user_metadata = claims.get("user_metadata", {})
        return cls(
            sub=claims["sub"],
            email=claims.get("email"),
            email_verified=user_metadata.get("email_verified", False)
            or claims.get("email_confirmed_at") is not None,
            phone=claims.get("phone"),
            aud=claims.get("aud", "authenticated"),
            role=claims.get("role", "authenticated"),
            iat=claims.get("iat"),
            exp=claims.get("exp"),
            raw_claims=claims,
        )
