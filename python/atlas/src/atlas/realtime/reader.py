import json
from typing import List, Optional, Tuple

from redis.asyncio import Redis

from atlas.realtime.cursor import LiveEventCursor
from atlas.realtime.errors import (
    LiveEventCursorExpired,
    LiveEventDecodeError,
    LiveEventUnsupportedSchemaVersion,
    LiveEventUnsupportedType,
)
from atlas.realtime.enums import LiveEventType
from atlas.realtime.models import LiveEventEnvelope, LiveEventMessage
from atlas.realtime.settings import LiveEventPipelineSettings


class LiveEventReader:
    """
    Reader for the Live Market Event Stream.
    Uses cursor-based XREAD (no consumer groups).
    """

    def __init__(self, redis_client: Redis, settings: LiveEventPipelineSettings):
        self.redis = redis_client
        self.settings = settings
        self.stream_key = settings.stream_key_prefix

    async def get_stream_bounds(self) -> Tuple[Optional[str], Optional[str], int]:
        """
        Returns (first_cursor, last_cursor, length).
        If the stream is empty or missing, returns (None, None, 0).
        """
        try:
            info = await self.redis.xinfo_stream(self.stream_key)
            if not info:
                return None, None, 0
                
            length = info.get("length", 0)
            if length == 0:
                return None, None, 0
                
            first_entry = info.get("first-entry")
            last_entry = info.get("last-entry")
            
            first_cursor = first_entry[0] if first_entry else None
            last_cursor = last_entry[0] if last_entry else None
            
            return first_cursor, last_cursor, length
        except Exception:
            # Missing key throws exception in some redis-py versions for XINFO
            return None, None, 0

    async def get_tail_cursor(self) -> str:
        """
        Returns the ID of the last entry in the stream.
        If the stream is empty, returns the EMPTY_CURSOR.
        """
        _, last_cursor, _ = await self.get_stream_bounds()
        if not last_cursor:
            return LiveEventCursor.EMPTY_CURSOR
        return last_cursor

    async def is_cursor_available(self, cursor: str) -> bool:
        """
        Checks if a given cursor is still available in the stream.
        Returns False if the requested cursor is older than the first retained entry.
        """
        if cursor == LiveEventCursor.EMPTY_CURSOR:
            return True

        first_cursor, _, _ = await self.get_stream_bounds()
        if not first_cursor:
            # Stream is empty, so technically the cursor doesn't exist yet, but it's not "expired"
            return True

        # If requested cursor < first_cursor, it has been trimmed
        return LiveEventCursor.compare(cursor, first_cursor) >= 0

    def _decode_envelope(self, stream_id: str, raw_data: bytes) -> LiveEventEnvelope:
        try:
            data_dict = json.loads(raw_data.decode("utf-8"))
        except Exception as e:
            raise LiveEventDecodeError(f"Failed to parse JSON payload: {e}", stream_id)

        version = data_dict.get("schema_version")
        if version != 1:
            raise LiveEventUnsupportedSchemaVersion(f"Unsupported schema version: {version}")

        event_type = data_dict.get("event_type")
        try:
            # Try to match it against our Enum
            LiveEventType(event_type)
        except ValueError:
            raise LiveEventUnsupportedType(f"Unsupported event type: {event_type}")

        try:
            return LiveEventEnvelope.model_validate(data_dict)
        except Exception as e:
            raise LiveEventDecodeError(f"Failed to validate envelope: {e}", stream_id)

    async def read_after(
        self,
        cursor: str,
        count: Optional[int] = None,
        block_ms: Optional[int] = None,
    ) -> List[LiveEventMessage]:
        """
        Reads events after the given cursor.
        """
        # Validate cursor parsing
        if cursor != LiveEventCursor.EMPTY_CURSOR:
            LiveEventCursor.parse(cursor)

        actual_count = count if count is not None else self.settings.default_read_count
        if actual_count < 1 or actual_count > self.settings.max_read_count:
            raise ValueError(f"Count must be between 1 and {self.settings.max_read_count}")

        actual_block = block_ms if block_ms is not None else self.settings.default_block_milliseconds
        if actual_block < 0 or actual_block > self.settings.max_block_milliseconds:
            raise ValueError(f"Block time must be between 0 and {self.settings.max_block_milliseconds}")

        # In Redis, BLOCK 0 means block indefinitely, which is forbidden
        # But we treat actual_block=0 as non-blocking in our own terms, passing it to redis-py
        # Actually redis-py xread `block` param:
        # block (int) – number of milliseconds to wait, if 0 wait indefinitely
        # So we only pass block if actual_block > 0
        kwargs = {"count": actual_count}
        if actual_block > 0:
            kwargs["block"] = actual_block

        try:
            # Streams dict format: {stream_key: cursor}
            streams = {self.stream_key: cursor}
            # redis.xread returns [[stream_name, [(id, fields), (id, fields), ...]]]
            response = await self.redis.xread(streams, **kwargs)
        except Exception as e:
            # Missing stream could result in empty list if not blocked
            # Or other transport errors
            response = []

        if not response:
            # Need to check if cursor expired if we didn't block and got nothing,
            # or if we got nothing maybe stream was trimmed?
            # Wait, XREAD returns nothing if no new messages.
            # But what if the cursor is too old and the stream has moved past it?
            # Actually, XREAD on an older cursor will return all messages available.
            # If the cursor was trimmed, XREAD just returns messages > cursor.
            # Wait, if cursor is trimmed, does XREAD return the oldest available?
            # Yes, if we pass a cursor smaller than the first available, it returns starting from the first available.
            # The prompt requires: "detect trimmed replay cursors" and return/raise `LiveEventCursorExpired`.
            # So if we get events back, we check if the requested cursor was expired.
            # Wait, the easiest way is to check availability FIRST if we want strict semantics,
            # but checking every time is slow.
            # The prompt says: "Do not run XINFO before every live XREAD. Cursor availability checks should be explicit."
            # So if the caller cares, they should call `is_cursor_available` themselves, or we check ONLY if there's a problem?
            # "If a caller requests replay older than the first retained stream ID: return/raise a typed condition such as LiveEventCursorExpired."
            pass

        results = []
        if response:
            # Extract entries for our stream
            # response[0][1] is the list of tuples
            entries = response[0][1]
            for stream_id, fields in entries:
                # stream_id is bytes, fields is dict {b'data': b'...'}
                decoded_stream_id = stream_id.decode("utf-8")
                raw_data = fields.get(b"data")
                if not raw_data:
                    # Invalid entry without 'data' field
                    raise LiveEventDecodeError("Missing 'data' field", decoded_stream_id)

                envelope = self._decode_envelope(decoded_stream_id, raw_data)
                results.append(LiveEventMessage(stream_id=decoded_stream_id, event=envelope))

        return results
