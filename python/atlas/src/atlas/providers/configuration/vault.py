import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .secrets import SecretStore


class SupabaseVaultSecretStore(SecretStore):
    """
    Implementation of SecretStore using Supabase Vault (PostgreSQL extension).
    Requires the `supabase_vault` extension to be enabled in the database.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def store_secret(self, name: str, description: str, secret: str) -> uuid.UUID:
        """
        Stores a secret using the vault.create_secret function.
        """
        stmt = text("SELECT vault.create_secret(:secret, :name, :description) AS secret_id;")
        result = await self.session.execute(
            stmt, {"secret": secret, "name": name, "description": description}
        )
        row = result.fetchone()
        if not row or not row.secret_id:
            raise Exception("Failed to store secret in Vault")

        # Ensure it's a UUID
        if isinstance(row.secret_id, str):
            return uuid.UUID(row.secret_id)
        return row.secret_id

    async def get_secret(self, secret_id: uuid.UUID) -> str:
        """
        Retrieves the decrypted secret from the vault.decrypted_secrets view.
        """
        stmt = text("SELECT decrypted_secret FROM vault.decrypted_secrets WHERE id = :id")
        result = await self.session.execute(stmt, {"id": secret_id})
        row = result.fetchone()
        if not row:
            raise Exception(f"Secret {secret_id} not found in Vault")

        return row.decrypted_secret

    async def delete_secret(self, secret_id: uuid.UUID) -> None:
        """
        Deletes a secret from the vault.secrets table.
        """
        stmt = text("DELETE FROM vault.secrets WHERE id = :id")
        await self.session.execute(stmt, {"id": secret_id})
