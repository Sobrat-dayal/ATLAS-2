"""Risk Policy Engine — validates orders against risk limits (Stage 144)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from atlas.trading.paper.domain import (
    KillSwitchEvent,
    PaperAccount,
    PaperOrder,
    PaperOrderSide,
    PaperPosition,
    RiskPolicy,
)
from atlas.trading.paper.errors import (
    KillSwitchActiveError,
    RiskPolicyViolationError,
)


class RiskPolicyEngine:
    """Validates paper trading orders against configurable risk policies."""

    DEFAULT_POLICY: RiskPolicy = RiskPolicy(
        max_order_value=50_000.0,
        max_position_value=100_000.0,
        max_daily_loss=5_000.0,
        max_drawdown_pct=0.20,
        max_open_orders=50,
        max_notional_per_symbol=25_000.0,
        leverage_limit=2.0,
    )

    # ------------------------------------------------------------------
    # Kill switch
    # ------------------------------------------------------------------

    def check_kill_switch(self, account: PaperAccount) -> None:
        """Raise KillSwitchActiveError if the account kill switch is on."""
        if account.kill_switch_active:
            raise KillSwitchActiveError(
                f"Kill switch is active for account '{account.account_id}'. "
                "All new orders are blocked until the switch is manually cleared."
            )

    def activate_kill_switch(
        self,
        account: PaperAccount,
        reason: str,
        triggered_by: str,
    ) -> KillSwitchEvent:
        """Set kill_switch_active=True and return a KillSwitchEvent."""
        account.kill_switch_active = True
        account.updated_at = datetime.now(timezone.utc)
        return KillSwitchEvent(
            account_id=account.account_id,
            triggered_at=datetime.now(timezone.utc),
            reason=reason,
            triggered_by=triggered_by,
        )

    # ------------------------------------------------------------------
    # Daily loss
    # ------------------------------------------------------------------

    def check_daily_loss(self, account: PaperAccount, policy: RiskPolicy) -> None:
        """Activate kill switch if daily loss exceeds the configured limit."""
        loss = -account.daily_realized_pnl  # loss is positive when pnl is negative
        if loss >= policy.max_daily_loss:
            self.activate_kill_switch(
                account,
                reason=f"Daily loss limit reached: loss={loss:.2f} >= limit={policy.max_daily_loss:.2f}",
                triggered_by="risk_engine_auto",
            )
            raise KillSwitchActiveError(
                f"Daily loss limit of {policy.max_daily_loss:.2f} breached "
                f"(realized_pnl={account.daily_realized_pnl:.2f}). Kill switch activated."
            )

    # ------------------------------------------------------------------
    # Order validation
    # ------------------------------------------------------------------

    def validate_order(
        self,
        account: PaperAccount,
        order: PaperOrder,
        open_orders: List[PaperOrder],
        positions: List[PaperPosition],
        policy: RiskPolicy,
        reference_price: float | None = None,
    ) -> None:
        """Check all applicable risk rules; raise RiskPolicyViolationError on any breach."""

        # --- Kill switch ---
        self.check_kill_switch(account)

        # --- Estimate notional value ---
        # Use a rough estimate: for MARKET orders use buying_power / open_orders heuristic
        # For LIMIT orders use limit_price; otherwise we use a safe default
        est_price = reference_price or order.limit_price or order.stop_price
        if est_price is None:
            raise RiskPolicyViolationError(
                "A valid market-data price is required to validate a market order."
            )
        notional = order.qty * est_price

        # --- Max order value ---
        if notional > policy.max_order_value:
            raise RiskPolicyViolationError(
                f"Order notional {notional:.2f} exceeds max_order_value={policy.max_order_value:.2f}."
            )

        # --- Max open orders ---
        if len(open_orders) >= policy.max_open_orders:
            raise RiskPolicyViolationError(
                f"Open order count {len(open_orders)} has reached max_open_orders={policy.max_open_orders}."
            )

        # --- Max notional per symbol ---
        symbol_positions_value = sum(
            p.qty * p.current_price
            for p in positions
            if p.symbol == order.symbol and p.current_price
        )
        projected_notional = symbol_positions_value + (
            notional if order.side == PaperOrderSide.BUY else 0
        )
        if projected_notional > policy.max_notional_per_symbol:
            raise RiskPolicyViolationError(
                f"Projected symbol notional {projected_notional:.2f} for '{order.symbol}' "
                f"exceeds max_notional_per_symbol={policy.max_notional_per_symbol:.2f}."
            )

        # --- Buying power check ---
        if order.side == PaperOrderSide.BUY:
            required = notional
            if required > account.buying_power:
                raise RiskPolicyViolationError(
                    f"Insufficient buying power: required={required:.2f}, "
                    f"available={account.buying_power:.2f}."
                )

        # --- Max position value ---
        total_positions_value = sum(p.qty * p.current_price for p in positions if p.current_price)
        projected_total = total_positions_value + (
            notional if order.side == PaperOrderSide.BUY else 0
        )
        if projected_total > policy.max_position_value:
            raise RiskPolicyViolationError(
                f"Projected total position value {projected_total:.2f} "
                f"exceeds max_position_value={policy.max_position_value:.2f}."
            )

        # --- Daily loss check ---
        self.check_daily_loss(account, policy)
