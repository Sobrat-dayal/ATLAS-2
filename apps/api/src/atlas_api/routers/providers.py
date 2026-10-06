from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
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

@router.post("/{provider_key}/health", response_model=None, dependencies=[Depends(RequirePermission("atlas.access"))])
async def check_provider_health(
    provider_key: str,
    target_type: str = Query("integration", description="Target type (e.g., integration, configuration)"),
    gateway: CapabilityGateway = Depends(get_capability_gateway),
) -> dict:
    """
    Manually checks the health of a provider.
    """
    try:
        response = await gateway.execute_capability(
            capability_key="provider.health.check",
            inputs={"provider_key": provider_key, "target_type": target_type}
        )
        return response.result.model_dump() # ProviderHealthCheckResult
    except ProviderNotRegisteredError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        if "Cooldown" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{provider_key}/health/history", response_model=None, dependencies=[Depends(RequirePermission("atlas.access"))])
async def get_provider_health_history(
    provider_key: str,
    target_type: str = Query("integration", description="Target type"),
    limit: int = Query(25, ge=1, le=100),
    gateway: CapabilityGateway = Depends(get_capability_gateway),
) -> dict:
    """
    Gets the health history of a provider.
    """
    try:
        response = await gateway.execute_capability(
            capability_key="provider.health.history",
            inputs={"provider_key": provider_key, "target_type": target_type, "limit": limit}
        )
        return response.result.model_dump()
    except ProviderNotRegisteredError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routing", response_model=None, dependencies=[Depends(RequirePermission("atlas.access"))])
async def list_provider_routing_policies(
    gateway: CapabilityGateway = Depends(get_capability_gateway),
) -> dict:
    try:
        response = await gateway.execute_capability(
            capability_key="provider.routing.list",
            inputs={}
        )
        return response.result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routing/{domain}", response_model=None, dependencies=[Depends(RequirePermission("atlas.access"))])
async def get_provider_routing_policy(
    domain: str,
    gateway: CapabilityGateway = Depends(get_capability_gateway),
) -> dict:
    try:
        response = await gateway.execute_capability(
            capability_key="provider.routing.get",
            inputs={"domain": domain}
        )
        return response.result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProviderRoutingUpdatePayload(BaseModel):
    enabled: bool
    fallback_enabled: bool
    provider_keys: list[str]

@router.put("/routing/{domain}", response_model=None, dependencies=[Depends(RequirePermission("atlas.access"))])
async def update_provider_routing_policy(
    domain: str,
    payload: ProviderRoutingUpdatePayload,
    gateway: CapabilityGateway = Depends(get_capability_gateway),
) -> dict:
    try:
        response = await gateway.execute_capability(
            capability_key="provider.routing.update",
            inputs={
                "domain": domain,
                "enabled": payload.enabled,
                "fallback_enabled": payload.fallback_enabled,
                "provider_keys": payload.provider_keys
            }
        )
        return response.result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/routing/{domain}/reset", response_model=None, dependencies=[Depends(RequirePermission("atlas.access"))])
async def reset_provider_routing_policy(
    domain: str,
    gateway: CapabilityGateway = Depends(get_capability_gateway),
) -> dict:
    try:
        await gateway.execute_capability(
            capability_key="provider.routing.reset",
            inputs={"domain": domain}
        )
        return {"status": "reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routing/{domain}/plan", response_model=None, dependencies=[Depends(RequirePermission("atlas.access"))])
async def get_provider_routing_plan(
    domain: str,
    gateway: CapabilityGateway = Depends(get_capability_gateway),
) -> dict:
    try:
        response = await gateway.execute_capability(
            capability_key="provider.routing.plan",
            inputs={"domain": domain}
        )
        return response.result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
