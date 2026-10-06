import uuid
from typing import Protocol


class SecretStore(Protocol):
    """
    Abstraction for a secure vault backend (e.g., Supabase Vault, AWS Secrets Manager).
    Atlas uses this to store and retrieve provider credentials.
    """

    async def store_secret(self, name: str, description: str, secret: str) -> uuid.UUID:
        """
        Stores a secret securely.

        Args:
            name: A human-readable name for the secret.
            description: A description of what the secret is used for.
            secret: The plaintext secret value to encrypt and store.

        Returns:
            The unique identifier (UUID) of the stored secret in the vault.
        """
        ...

    async def get_secret(self, secret_id: uuid.UUID) -> str:
        """
        Retrieves the plaintext value of a secret.

        Args:
            secret_id: The unique identifier of the secret in the vault.

        Returns:
            The plaintext secret value.

        Raises:
            Exception: If the secret is not found or cannot be accessed.
        """
        ...

    async def delete_secret(self, secret_id: uuid.UUID) -> None:
        """
        Deletes a secret from the vault.

        Args:
            secret_id: The unique identifier of the secret in the vault.
        """
        ...
