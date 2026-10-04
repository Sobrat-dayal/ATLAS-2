"""
ATLAS Authentication Core.

Provides the AuthPrincipal identity model and Supabase JWT verification
for the ATLAS platform. This module answers: "Who is making this request?"

Architecture:
    Supabase Auth (credential authority)
        → JWT access token
        → JWKS local verification (PyJWT + cryptography)
        → AuthPrincipal dataclass
"""

from .principal import AuthPrincipal
from .verifier import SupabaseTokenVerifier

__all__ = ["AuthPrincipal", "SupabaseTokenVerifier"]
