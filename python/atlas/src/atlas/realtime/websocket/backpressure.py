import asyncio
from typing import Dict, List

from atlas.realtime.websocket.models import LiveEventMessageOut, QuoteSubscriptionKey, ServerMessage


class OutboundBuffer:
    def __init__(self, max_control_messages: int = 256):
        self.control_queue: asyncio.Queue[ServerMessage] = asyncio.Queue(maxsize=max_control_messages)
        self.pending_quotes: Dict[QuoteSubscriptionKey, LiveEventMessageOut] = {}
        self.event = asyncio.Event()
        self.closed = False

    def enqueue_control(self, message: ServerMessage) -> None:
        if self.closed:
            return
        try:
            self.control_queue.put_nowait(message)
            self.event.set()
        except asyncio.QueueFull:
            raise BufferError("Control queue overflow")

    def enqueue_quote(self, series: QuoteSubscriptionKey, message: LiveEventMessageOut) -> None:
        if self.closed:
            return
        self.pending_quotes[series] = message
        self.event.set()

    async def wait_for_messages(self) -> List[ServerMessage]:
        if self.closed:
            return []

        if self.control_queue.empty() and not self.pending_quotes:
            await self.event.wait()
            
        if self.closed:
            return []
            
        self.event.clear()
        
        messages: List[ServerMessage] = []
        
        # Drain control messages first
        while not self.control_queue.empty():
            messages.append(self.control_queue.get_nowait())
        
        # Drain quotes
        if self.pending_quotes:
            messages.extend(self.pending_quotes.values())
            self.pending_quotes.clear()
        
        # If queue got new items while draining quotes, ensure event is set
        if not self.control_queue.empty() or self.pending_quotes:
            self.event.set()
            
        return messages
            
    def close(self):
        self.closed = True
        self.event.set()
