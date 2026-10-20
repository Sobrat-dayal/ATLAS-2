import json
import secrets
from datetime import timedelta
from typing import TYPE_CHECKING, Optional

from redis.asyncio import Redis

if TYPE_CHECKING:
    from atlas.auth.principal import AuthPrincipal


class WebSocketTicketStore:
    """
    Issues and redeems short-lived, single-use tickets for WebSocket authentication.
    Since browsers cannot easily send headers during WS handshake, we use this ticket mechanism.
    """

    def __init__(self, redis_client: Redis, ttl_seconds: int = 30):
        self.redis = redis_client
        self.ttl = timedelta(seconds=ttl_seconds)

    def _key(self, ticket: str) -> str:
        return f"atlas:ws:ticket:{ticket}"

    async def issue_ticket(self, principal: "AuthPrincipal") -> str:
        """
        Creates a single-use ticket for the given user ID.
        """
        # Using a cryptographically secure random string for the ticket
        ticket = secrets.token_urlsafe(32)
        key = self._key(ticket)

        # Store full AuthPrincipal claims
        payload = json.dumps({"claims": principal.raw_claims})

        await self.redis.setex(key, self.ttl, payload)
        return ticket

    async def redeem_ticket(self, ticket: str) -> Optional["AuthPrincipal"]:
        """
        Validates and consumes the ticket.
        Returns the AuthPrincipal if valid, None if invalid or expired.
        """
        from atlas.auth.principal import AuthPrincipal

        key = self._key(ticket)

        # Atomically GET and DELETE the ticket
        raw = await self.redis.getdel(key)

        if not raw:
            return None

        data = json.loads(raw)
        return AuthPrincipal.from_claims(data["claims"])
