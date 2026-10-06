import uuid
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from atlas.providers.routing.db_models import (
    ProviderRoutingCandidateModel,
    ProviderRoutingPolicyModel,
)
from atlas.providers.routing.models import (
    ProviderRoutingCandidate,
    ProviderRoutingPolicy,
    ProviderRoutingScope,
)
from atlas.providers.types import ProviderDomain


class ProviderRoutingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_policy(
        self, owner_principal_id: str, domain: ProviderDomain
    ) -> Optional[ProviderRoutingPolicy]:
        stmt = (
            select(ProviderRoutingPolicyModel)
            .options(selectinload(ProviderRoutingPolicyModel.candidates))
            .where(
                ProviderRoutingPolicyModel.owner_principal_id == owner_principal_id,
                ProviderRoutingPolicyModel.domain == domain,
                ProviderRoutingPolicyModel.scope == ProviderRoutingScope.USER,
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        if not model:
            return None
        return self._to_domain_model(model)

    async def get_system_policy(self, domain: ProviderDomain) -> Optional[ProviderRoutingPolicy]:
        stmt = (
            select(ProviderRoutingPolicyModel)
            .options(selectinload(ProviderRoutingPolicyModel.candidates))
            .where(
                ProviderRoutingPolicyModel.scope == ProviderRoutingScope.SYSTEM,
                ProviderRoutingPolicyModel.domain == domain,
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        if not model:
            return None
        return self._to_domain_model(model)

    async def list_user_policies(self, owner_principal_id: str) -> list[ProviderRoutingPolicy]:
        stmt = (
            select(ProviderRoutingPolicyModel)
            .options(selectinload(ProviderRoutingPolicyModel.candidates))
            .where(
                ProviderRoutingPolicyModel.owner_principal_id == owner_principal_id,
                ProviderRoutingPolicyModel.scope == ProviderRoutingScope.USER,
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain_model(m) for m in models]

    async def save_policy(self, policy: ProviderRoutingPolicy) -> ProviderRoutingPolicy:
        # Check if exists
        stmt = select(ProviderRoutingPolicyModel).where(
            ProviderRoutingPolicyModel.policy_id == uuid.UUID(policy.policy_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalars().first()

        if model:
            model.enabled = policy.enabled
            model.fallback_enabled = policy.fallback_enabled
            # update candidates
            # drop old ones and add new ones (cascade logic in SA or manual delete)
            await self.session.execute(
                delete(ProviderRoutingCandidateModel).where(
                    ProviderRoutingCandidateModel.policy_id == model.policy_id
                )
            )
            for cand in policy.candidates:
                model.candidates.append(
                    ProviderRoutingCandidateModel(
                        policy_id=model.policy_id,
                        provider_key=cand.provider_key,
                        position=cand.position,
                    )
                )
        else:
            model = ProviderRoutingPolicyModel(
                policy_id=uuid.UUID(policy.policy_id),
                scope=policy.scope,
                owner_principal_id=policy.owner_principal_id,
                domain=policy.domain.value,
                enabled=policy.enabled,
                fallback_enabled=policy.fallback_enabled,
                schema_version=policy.schema_version,
            )
            for cand in policy.candidates:
                model.candidates.append(
                    ProviderRoutingCandidateModel(
                        policy_id=model.policy_id,
                        provider_key=cand.provider_key,
                        position=cand.position,
                    )
                )
            self.session.add(model)

        await self.session.flush()
        return self._to_domain_model(model)

    async def delete_user_policy(self, owner_principal_id: str, domain: ProviderDomain) -> None:
        stmt = delete(ProviderRoutingPolicyModel).where(
            ProviderRoutingPolicyModel.owner_principal_id == owner_principal_id,
            ProviderRoutingPolicyModel.domain == domain,
            ProviderRoutingPolicyModel.scope == ProviderRoutingScope.USER,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    def _to_domain_model(self, model: ProviderRoutingPolicyModel) -> ProviderRoutingPolicy:
        return ProviderRoutingPolicy(
            policy_id=str(model.policy_id),
            scope=model.scope,
            owner_principal_id=model.owner_principal_id,
            domain=ProviderDomain(model.domain),
            enabled=model.enabled,
            fallback_enabled=model.fallback_enabled,
            schema_version=model.schema_version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            candidates=[
                ProviderRoutingCandidate(provider_key=c.provider_key, position=c.position)
                for c in sorted(model.candidates, key=lambda x: x.position)
            ],
        )
