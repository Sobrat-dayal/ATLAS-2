from fastapi import APIRouter, Depends, Query, WebSocket, Request, status
from pydantic import BaseModel
from redis.asyncio import Redis

from atlas_api.auth.dependencies import get_current_user
from atlas.auth.principal import AuthPrincipal
from atlas.realtime.websocket.ticket import WebSocketTicketStore

router = APIRouter(
    prefix="/realtime",
    tags=["Realtime"]
)

class TicketResponse(BaseModel):
    ticket: str
    expires_in: int = 30

@router.post("/websocket-ticket", response_model=TicketResponse)
async def get_websocket_ticket(
    request: Request,
    principal: AuthPrincipal = Depends(get_current_user)
):
    redis: Redis = request.app.state.redis
    store = WebSocketTicketStore(redis)
    ticket = await store.issue_ticket(principal)
    return TicketResponse(ticket=ticket)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket: str = Query(..., description="Short-lived authentication ticket")
):
    redis: Redis = websocket.app.state.redis
    store = WebSocketTicketStore(redis)
    principal = await store.redeem_ticket(ticket)
    
    if not principal:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired ticket")
        return
        
    gateway = websocket.app.state.realtime_gateway
    await gateway.handle_websocket(websocket, principal)
