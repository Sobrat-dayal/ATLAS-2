import uuid
from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationService, AuthorizationContext
from atlas.authorization.repository import AuthorizationRepository
from atlas.capabilities import (
    registry, CapabilityGateway, CapabilityExecutionContext, CapabilityInvocationSource
)
from atlas_api.dependencies import get_db_session
from atlas_api.auth.dependencies import get_current_user

async def get_authorization_context(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> AuthorizationContext:
    repo = AuthorizationRepository(session)
    service = AuthorizationService(repo)
    return await service.get_authorization_context(principal)

def get_capability_gateway(
    authz_context: Annotated[AuthorizationContext, Depends(get_authorization_context)],
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> CapabilityGateway:
    return CapabilityGateway(
        registry=registry,
        authz_context=authz_context,
        session=session
    )

def get_capability_execution_context(
    request: Request,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)]
) -> CapabilityExecutionContext:
    return CapabilityExecutionContext(
        principal=principal,
        invocation_source=CapabilityInvocationSource.API,
        request_id=request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
    )
