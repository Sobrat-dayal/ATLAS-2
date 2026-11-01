"""Paper Order Book — in-memory order management (Stage 144)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from atlas.trading.paper.domain import (
    PaperFill,
    PaperOrder,
    PaperOrderStatus,
)
from atlas.trading.paper.errors import (
    CrossTenantAccessError,
    DuplicateOrderError,
    OrderNotFoundError,
)


class PaperOrderBook:
    """Manages the lifecycle of paper trading orders."""

    def __init__(self) -> None:
        self._orders: Dict[str, PaperOrder] = {}
        self._account_orders: Dict[str, List[str]] = {}
        self._client_order_index: Dict[str, str] = {}  # client_order_id -> order_id

    # ------------------------------------------------------------------
    # Submission
    # ------------------------------------------------------------------

    def submit(self, order: PaperOrder) -> None:
        """Accept and store a new order."""
        if order.client_order_id and order.client_order_id in self._client_order_index:
            raise DuplicateOrderError(
                f"An order with client_order_id='{order.client_order_id}' already exists."
            )
        self._orders[order.order_id] = order
        self._account_orders.setdefault(order.account_id, []).append(order.order_id)
        if order.client_order_id:
            self._client_order_index[order.client_order_id] = order.order_id

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get(self, order_id: str) -> PaperOrder:
        """Return a single order by ID."""
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order '{order_id}' not found.")
        return order

    def get_by_client_order_id(self, client_order_id: str) -> Optional[PaperOrder]:
        order_id = self._client_order_index.get(client_order_id)
        return self._orders.get(order_id) if order_id else None

    def list_open(self, account_id: str) -> List[PaperOrder]:
        """Return all OPEN, PARTIAL, or PENDING orders for an account."""
        open_statuses = {
            PaperOrderStatus.OPEN,
            PaperOrderStatus.PARTIAL,
            PaperOrderStatus.PENDING,
        }
        return [
            self._orders[oid]
            for oid in self._account_orders.get(account_id, [])
            if oid in self._orders and self._orders[oid].status in open_statuses
        ]

    def list_all(self, account_id: str) -> List[PaperOrder]:
        """Return all orders for an account."""
        return [
            self._orders[oid]
            for oid in self._account_orders.get(account_id, [])
            if oid in self._orders
        ]

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def update(self, order: PaperOrder) -> None:
        """Replace an existing order record."""
        if order.order_id not in self._orders:
            raise OrderNotFoundError(f"Order '{order.order_id}' not found for update.")
        self._orders[order.order_id] = order

    def clear_account(self, account_id: str) -> None:
        order_ids = self._account_orders.pop(account_id, [])
        for order_id in order_ids:
            order = self._orders.pop(order_id, None)
            if order and order.client_order_id:
                self._client_order_index.pop(order.client_order_id, None)

    def cancel(self, order_id: str, account_id: str, tenant_id: str) -> PaperOrder:
        """Cancel an open order; validate ownership first."""
        order = self.get(order_id)
        if order.account_id != account_id:
            raise CrossTenantAccessError(
                f"Order '{order_id}' does not belong to account '{account_id}'."
            )
        if order.status in (
            PaperOrderStatus.FILLED,
            PaperOrderStatus.CANCELLED,
            PaperOrderStatus.REJECTED,
            PaperOrderStatus.EXPIRED,
        ):
            # Already in a terminal state; return as-is without error
            return order
        order.status = PaperOrderStatus.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        self._orders[order_id] = order
        return order

    def apply_fill(self, order_id: str, fill: PaperFill) -> PaperOrder:
        """Apply a fill to an order; update filled_qty and status."""
        order = self.get(order_id)
        order.fills.append(fill)
        order.filled_qty += fill.qty
        order.updated_at = datetime.now(timezone.utc)

        if order.filled_qty >= order.qty:
            order.status = PaperOrderStatus.FILLED
        elif order.filled_qty > 0:
            order.status = PaperOrderStatus.PARTIAL

        self._orders[order_id] = order
        return order
