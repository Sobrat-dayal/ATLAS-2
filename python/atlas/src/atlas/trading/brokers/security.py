"""Sandbox egress and secret-handling controls."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from cryptography.fernet import Fernet, InvalidToken

from atlas.trading.brokers.errors import (
    CredentialEncryptionError,
    SandboxFirewallError,
    SSRFProtectionError,
)


def validate_sandbox_url(url: str, allowed_hosts: frozenset[str]) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise SSRFProtectionError("Broker URLs must use HTTPS and include a hostname.")
    host = parsed.hostname.lower().rstrip(".")
    if host not in allowed_hosts:
        raise SandboxFirewallError(f"Host '{host}' is not an allowed sandbox host.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and (address.is_private or address.is_loopback or address.is_link_local):
        raise SSRFProtectionError("Private and link-local destinations are forbidden.")
    if parsed.username or parsed.password or parsed.fragment:
        raise SSRFProtectionError("Credentials and fragments are forbidden in broker URLs.")
    return parsed.geturl()


class SecretVault:
    """Encrypts credentials in memory; callers must persist ciphertext only."""

    def __init__(self, key: bytes) -> None:
        try:
            self._fernet = Fernet(key)
        except (TypeError, ValueError) as exc:
            raise CredentialEncryptionError("Invalid secret-vault key.") from exc

    def encrypt(self, secret: str) -> bytes:
        if not secret:
            raise CredentialEncryptionError("Cannot encrypt an empty secret.")
        return self._fernet.encrypt(secret.encode("utf-8"))

    def decrypt(self, ciphertext: bytes) -> str:
        try:
            return self._fernet.decrypt(ciphertext).decode("utf-8")
        except (InvalidToken, UnicodeDecodeError) as exc:
            raise CredentialEncryptionError("Credential decryption failed.") from exc
