import uuid
from typing import Any, Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import ProviderConfiguration, ProviderCredentialBinding
from .secrets import SecretStore


class ProviderConfigurationService:
    """
    Domain service for managing provider configurations and credential bindings.
    """

    def __init__(self, session: AsyncSession, secret_store: SecretStore):
        self.session = session
        self.secret_store = secret_store

    async def get_configuration(
        self, user_id: uuid.UUID, provider_id: str
    ) -> Optional[ProviderConfiguration]:
        """
        Retrieves a user's configuration for a specific provider.
        """
        stmt = (
            select(ProviderConfiguration)
            .where(
                ProviderConfiguration.user_id == user_id,
                ProviderConfiguration.provider_id == provider_id,
            )
            .options(selectinload(ProviderConfiguration.bindings))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_configurations(self, user_id: uuid.UUID) -> List[ProviderConfiguration]:
        """
        Retrieves all provider configurations for a user.
        """
        stmt = (
            select(ProviderConfiguration)
            .where(ProviderConfiguration.user_id == user_id)
            .options(selectinload(ProviderConfiguration.bindings))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_configuration(
        self, user_id: uuid.UUID, provider_id: str, enabled: bool, settings: dict[str, Any]
    ) -> ProviderConfiguration:
        """
        Creates or updates a provider configuration.
        """
        config = await self.get_configuration(user_id, provider_id)
        if config:
            config.enabled = enabled
            config.settings = settings
        else:
            config = ProviderConfiguration(
                user_id=user_id,
                provider_id=provider_id,
                enabled=enabled,
                settings=settings,
            )
            self.session.add(config)
        
        await self.session.flush()
        return config

    async def set_credential(
        self, user_id: uuid.UUID, provider_id: str, credential_key: str, secret_value: str, description: str = ""
    ) -> ProviderCredentialBinding:
        """
        Stores a secret in the vault and creates/updates the credential binding.
        """
        # Ensure configuration exists
        config = await self.get_configuration(user_id, provider_id)
        if not config:
            config = await self.upsert_configuration(user_id, provider_id, enabled=False, settings={})

        # Store in vault
        secret_id = await self.secret_store.store_secret(
            name=f"{provider_id}_{credential_key}_{user_id}",
            description=description or f"Credential {credential_key} for provider {provider_id}",
            secret=secret_value
        )

        # Check existing binding
        existing_binding = next((b for b in config.bindings if b.credential_key == credential_key), None)
        if existing_binding:
            # Delete old secret from vault
            await self.secret_store.delete_secret(existing_binding.vault_secret_id)
            existing_binding.vault_secret_id = secret_id
            binding = existing_binding
        else:
            binding = ProviderCredentialBinding(
                configuration_id=config.id,
                credential_key=credential_key,
                vault_secret_id=secret_id
            )
            self.session.add(binding)
            config.bindings.append(binding)

        await self.session.flush()
        return binding

    async def delete_credential(self, user_id: uuid.UUID, provider_id: str, credential_key: str) -> bool:
        """
        Deletes a credential binding and its associated secret in the vault.
        """
        config = await self.get_configuration(user_id, provider_id)
        if not config:
            return False

        existing_binding = next((b for b in config.bindings if b.credential_key == credential_key), None)
        if not existing_binding:
            return False

        # Delete from vault
        await self.secret_store.delete_secret(existing_binding.vault_secret_id)
        
        # Delete binding
        await self.session.delete(existing_binding)
        config.bindings.remove(existing_binding)
        
        await self.session.flush()
        return True

    async def resolve_credentials(self, user_id: uuid.UUID, provider_id: str) -> dict[str, str]:
        """
        Retrieves all plaintext credentials for a provider.
        (Used by the backend to inject credentials into provider instances).
        """
        config = await self.get_configuration(user_id, provider_id)
        if not config or not config.enabled:
            return {}

        credentials = {}
        for binding in config.bindings:
            try:
                secret_value = await self.secret_store.get_secret(binding.vault_secret_id)
                credentials[binding.credential_key] = secret_value
            except Exception:
                # Log error or handle missing secret
                pass
        return credentials
