"""Paper Trading Event Store — in-memory event sourcing (Stage 144)."""

from __future__ import annotations

import itertools
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.trading.paper.domain import PaperAccount, PaperPosition


class PaperEventStore:
    """Lightweight in-memory event store for paper trading.

    Events are appended in order and can be replayed from any sequence ID.
    Snapshots are stored as special SNAPSHOT events alongside the main log.
    """

    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []
        self._seq = itertools.count(0)

    # ------------------------------------------------------------------
    # Append
    # ------------------------------------------------------------------

    def append(self, event_type: str, payload: Dict[str, Any]) -> int:
        """Append an event; return the assigned sequence ID."""
        seq_id = next(self._seq)
        self._events.append(
            {
                "seq_id": seq_id,
                "event_type": event_type,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return seq_id

    # ------------------------------------------------------------------
    # Replay
    # ------------------------------------------------------------------

    def replay_from(self, seq_id: int = 0) -> List[Dict[str, Any]]:
        """Return all events with seq_id >= *seq_id*."""
        return [e for e in self._events if e["seq_id"] >= seq_id]

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------

    def snapshot(
        self,
        account_id: str,
        account: PaperAccount,
        positions: List[PaperPosition],
    ) -> None:
        """Persist a full account + position snapshot event."""
        self.append(
            "SNAPSHOT",
            {
                "account_id": account_id,
                "cash": account.cash,
                "equity": account.equity,
                "daily_realized_pnl": account.daily_realized_pnl,
                "kill_switch_active": account.kill_switch_active,
                "positions": [
                    {
                        "symbol": p.symbol,
                        "qty": p.qty,
                        "avg_cost": p.avg_cost,
                        "current_price": p.current_price,
                        "unrealized_pnl": p.unrealized_pnl,
                        "realized_pnl": p.realized_pnl,
                    }
                    for p in positions
                ],
            },
        )

    def get_latest_snapshot(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Return the most recent SNAPSHOT event for *account_id*, or None."""
        snapshot = None
        for event in self._events:
            if (
                event["event_type"] == "SNAPSHOT"
                and event["payload"].get("account_id") == account_id
            ):
                snapshot = event
        return snapshot
