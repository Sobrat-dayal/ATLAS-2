from typing import TYPE_CHECKING

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from atlas.realtime.websocket.errors import WebSocketProtocolError
from atlas.realtime.websocket.models import ClientMessage

if TYPE_CHECKING:
    from atlas.realtime.websocket.models import ServerMessage


async def receive_message(websocket: WebSocket) -> ClientMessage:
    try:
        data = await websocket.receive_text()
    except WebSocketDisconnect:
        raise

    try:
        return ClientMessage.model_validate_json(data)
    except ValidationError as e:
        raise WebSocketProtocolError(f"Invalid message format: {e}")


async def send_message(websocket: WebSocket, message: "ServerMessage"):
    await websocket.send_text(message.model_dump_json(exclude_none=True))
