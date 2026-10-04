"""
Supabase JWT Verifier — local cryptographic verification using JWKS.

This module fetches the Supabase project's JWKS (JSON Web Key Set) and
verifies access tokens locally. It does NOT call the Supabase user endpoint
on every request — only the JWKS endpoint is hit, and keys are cached.

The JWKS URL is derived from the Supabase project URL:
    https://<project-ref>.supabase.co/.well-known/jwks.json
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional
from urllib.request import Request, urlopen

import jwt
from jwt import PyJWKSet

from .principal import AuthPrincipal

logger = logging.getLogger("atlas.auth.verifier")

# Cache JWKS for 1 hour by default
_JWKS_CACHE_TTL_SECONDS = 3600


class TokenVerificationError(Exception):
    """Raised when a JWT cannot be verified."""


class SupabaseTokenVerifier:
    """
    Verifies Supabase access tokens locally via JWKS.

    Usage::

        verifier = SupabaseTokenVerifier(
            supabase_url="https://xyz.supabase.co",
            supabase_jwt_secret="your-jwt-secret",  # optional fallback
        )
        principal = verifier.verify(token)

    The verifier supports two modes:
    1. **JWKS mode** (preferred): Fetches public keys from the Supabase JWKS
       endpoint and verifies using RS256.
    2. **JWT secret mode** (fallback): Uses the Supabase JWT secret for HS256
       verification. This is simpler but less secure for production.

    In development, the JWT secret is typically used. In production, JWKS is
    strongly recommended.
    """

    def __init__(
        self,
        supabase_url: str,
        supabase_jwt_secret: Optional[str] = None,
        audience: str = "authenticated",
        jwks_cache_ttl: int = _JWKS_CACHE_TTL_SECONDS,
    ):
        self._supabase_url = supabase_url.rstrip("/")
        self._jwt_secret = supabase_jwt_secret
        self._audience = audience
        self._jwks_cache_ttl = jwks_cache_ttl

        # JWKS cache
        self._jwks: Optional[PyJWKSet] = None
        self._jwks_fetched_at: float = 0.0

        # Derive JWKS URL
        self._jwks_url = f"{self._supabase_url}/auth/v1/.well-known/jwks.json"

    def _fetch_jwks(self) -> Optional[PyJWKSet]:
        """Fetch and cache the JWKS from Supabase."""
        now = time.time()
        if self._jwks and (now - self._jwks_fetched_at) < self._jwks_cache_ttl:
            return self._jwks

        try:
            req = Request(self._jwks_url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=10) as resp:
                jwks_data = json.loads(resp.read())
            self._jwks = PyJWKSet.from_dict(jwks_data)
            self._jwks_fetched_at = now
            logger.info("Refreshed JWKS from %s", self._jwks_url)
            return self._jwks
        except Exception as exc:
            logger.warning("Failed to fetch JWKS from %s: %s", self._jwks_url, exc)
            return self._jwks  # Return stale cache if available

    def _get_signing_key(self, token: str) -> Any:
        """Get the signing key for the token from JWKS."""
        jwks = self._fetch_jwks()
        if jwks is None:
            return None

        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            if kid:
                for key in jwks.keys:
                    if key.key_id == kid:
                        return key.key
            # If no kid match, try first key
            if jwks.keys:
                return jwks.keys[0].key
        except Exception as exc:
            logger.warning("Failed to extract signing key: %s", exc)
        return None

    def verify(self, token: str) -> AuthPrincipal:
        """
        Verify a Supabase access token and return an AuthPrincipal.

        Args:
            token: The raw JWT string from the Authorization header.

        Returns:
            An AuthPrincipal with the verified identity.

        Raises:
            TokenVerificationError: If the token is invalid, expired, or
                cannot be verified.
        """
        if not token:
            raise TokenVerificationError("Empty token")

        # Strip 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[7:]

        # Try JWKS verification first (RS256)
        signing_key = self._get_signing_key(token)
        if signing_key:
            try:
                claims = jwt.decode(
                    token,
                    signing_key,
                    algorithms=["RS256"],
                    audience=self._audience,
                    options={"verify_exp": True},
                )
                return AuthPrincipal.from_claims(claims)
            except jwt.ExpiredSignatureError:
                raise TokenVerificationError("Token has expired")
            except jwt.InvalidAudienceError:
                raise TokenVerificationError("Invalid token audience")
            except jwt.InvalidTokenError as exc:
                logger.debug("JWKS verification failed, trying secret: %s", exc)

        # Fallback to JWT secret (HS256) — common in development
        if self._jwt_secret:
            try:
                claims = jwt.decode(
                    token,
                    self._jwt_secret,
                    algorithms=["HS256"],
                    audience=self._audience,
                    options={"verify_exp": True},
                )
                return AuthPrincipal.from_claims(claims)
            except jwt.ExpiredSignatureError:
                raise TokenVerificationError("Token has expired")
            except jwt.InvalidAudienceError:
                raise TokenVerificationError("Invalid token audience")
            except jwt.InvalidTokenError as exc:
                raise TokenVerificationError(f"Token verification failed: {exc}")

        raise TokenVerificationError(
            "No verification method available. "
            "Configure SUPABASE_JWT_SECRET or ensure JWKS endpoint is reachable."
        )
