from typing import Tuple

from atlas.realtime.errors import LiveEventCursorInvalid


class LiveEventCursor:
    """
    Utilities for managing and validating Redis Stream cursors.
    A Redis Stream ID is typically of the format "millisecondsTime-sequenceNumber" (e.g. "1526919030474-55").
    """
    
    EMPTY_CURSOR = "0-0"

    @classmethod
    def parse(cls, cursor: str) -> Tuple[int, int]:
        """
        Parses a stream ID into its numeric components (milliseconds, sequence).
        Raises LiveEventCursorInvalid if the format is invalid.
        """
        try:
            parts = cursor.split("-")
            if len(parts) != 2:
                raise ValueError("Cursor must contain exactly one hyphen.")
            ms = int(parts[0])
            seq = int(parts[1])
            return ms, seq
        except Exception as e:
            raise LiveEventCursorInvalid(f"Invalid cursor format '{cursor}': {e}") from e

    @classmethod
    def compare(cls, cursor1: str, cursor2: str) -> int:
        """
        Numerically compares two cursors.
        Returns:
            -1 if cursor1 < cursor2
             0 if cursor1 == cursor2
             1 if cursor1 > cursor2
        """
        ms1, seq1 = cls.parse(cursor1)
        ms2, seq2 = cls.parse(cursor2)

        if ms1 < ms2:
            return -1
        if ms1 > ms2:
            return 1
        
        if seq1 < seq2:
            return -1
        if seq1 > seq2:
            return 1
            
        return 0
