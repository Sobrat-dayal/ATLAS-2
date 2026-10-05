from fastapi import APIRouter, Depends, HTTPException, Query
from atlas.capabilities.gateway import CapabilityGateway
from atlas.providers.types import ProviderDomain
from atlas.providers.errors import ProviderNotRegisteredError

from atlas_api.capabilities_dependencies import get_capability_gateway
from atlas_api.authorization.dependencies import RequirePermission

router = APIRouter(
    prefix="/providers",
    tags=["Providers"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
    }
)


@router.get("", response_model=None, dependencies=[Depends(RequirePermission("atlas.access"))])
async def list_providers(
    domain: ProviderDomain | None = Query(None, description="Optional domain to filter providers"),
    gateway: CapabilityGateway = Depends(get_capability_gateway),
) -> dict:
    """
    Lists registered provider metadata.
    """
    inputs = {}
    if domain:
        inputs["domain"] = domain.value
        
    try:
        response = await gateway.execute_capability(
            capability_key="provider.list",
            inputs=inputs
        )
        return response.result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{provider_key}", response_model=None, dependencies=[Depends(RequirePermission("atlas.access"))])
async def get_provider(
    provider_key: str,
    gateway: CapabilityGateway = Depends(get_capability_gateway),
) -> dict:
    """
    Gets a single provider's metadata by key.
    """
    try:
        response = await gateway.execute_capability(
            capability_key="provider.get",
            inputs={"provider_key": provider_key}
        )
        return response.result
    except ProviderNotRegisteredError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        if "is not registered" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
