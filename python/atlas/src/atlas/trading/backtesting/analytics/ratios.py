"""Institutional Risk-Adjusted Return Metrics & Ratios (Stage 143)."""

from __future__ import annotations

import math
from typing import List, Optional
import numpy as np

from atlas.trading.backtesting.domain import DrawdownMetrics, PerformanceMetrics, TradeRecord


class FinancialMetricsEngine:
    """Calculates mathematically rigorous, documented risk-adjusted performance ratios."""

    @staticmethod
    def calculate_performance_metrics(
        initial_cash: float,
        final_equity: float,
        daily_returns: List[float],
        trades: List[TradeRecord],
        drawdown_metrics: DrawdownMetrics,
        total_commissions: float = 0.0,
        total_slippage: float = 0.0,
        risk_free_rate_annual: float = 0.02,
    ) -> PerformanceMetrics:
        """
        Compute institutional performance metrics.
        Enforces Test W (Zero Trades) and Test X (Zero Volatility exception safety).
        """
        total_return_dollar = round(final_equity - initial_cash, 2)
        total_return_pct = round((total_return_dollar / initial_cash) * 100.0, 2) if initial_cash > 0 else 0.0

        n_days = max(1, len(daily_returns))
        # Annualized CAGR
        years = n_days / 252.0
        if years > 0 and final_equity > 0 and initial_cash > 0:
            cagr_pct = round(((final_equity / initial_cash) ** (1.0 / years) - 1.0) * 100.0, 2)
        else:
            cagr_pct = total_return_pct

        # Daily Returns Volatility & Sharpe
        ann_vol_pct = 0.0
        sharpe_ratio: Optional[float] = None
        sortino_ratio: Optional[float] = None

        if len(daily_returns) >= 2:
            returns_arr = np.array(daily_returns, dtype=float)
            std_dev = float(np.std(returns_arr))
            mean_ret = float(np.mean(returns_arr))

            # Annualized volatility
            ann_vol_pct = round(std_dev * math.sqrt(252.0) * 100.0, 2)

            # Test X: If volatility is zero or negligible, Sharpe is undefined (None)
            if std_dev > 1e-7:
                daily_rf = (1.0 + risk_free_rate_annual) ** (1.0 / 252.0) - 1.0
                excess_ret = mean_ret - daily_rf
                sharpe_val = (excess_ret / std_dev) * math.sqrt(252.0)
                sharpe_ratio = round(float(sharpe_val), 2)

            # Downside deviation for Sortino
            downside_returns = returns_arr[returns_arr < 0]
            if len(downside_returns) > 0:
                downside_std = float(np.std(downside_returns))
                if downside_std > 1e-7:
                    sortino_val = (mean_ret / downside_std) * math.sqrt(252.0)
                    sortino_ratio = round(float(sortino_val), 2)

        # Calmar Ratio
        calmar_ratio: Optional[float] = None
        if drawdown_metrics.max_drawdown_pct > 0.01:
            calmar_ratio = round(cagr_pct / drawdown_metrics.max_drawdown_pct, 2)

        # Trade-by-trade analytics (Test W: zero trades)
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.net_pnl > 0]
        losing_trades = [t for t in trades if t.net_pnl < 0]

        gross_profits = sum(t.gross_pnl for t in winning_trades)
        gross_losses = abs(sum(t.gross_pnl for t in losing_trades))

        # Profit Factor: gross profits / gross losses (None if zero losses)
        profit_factor: Optional[float] = None
        if gross_losses > 1e-4:
            profit_factor = round(gross_profits / gross_losses, 2)
        elif gross_profits > 0:
            profit_factor = None  # Undefined / infinite

        win_rate_pct = round((len(winning_trades) / total_trades * 100.0), 2) if total_trades > 0 else 0.0
        avg_winner = round(sum(t.net_pnl for t in winning_trades) / len(winning_trades), 2) if winning_trades else 0.0
        avg_loser = round(sum(t.net_pnl for t in losing_trades) / len(losing_trades), 2) if losing_trades else 0.0

        expectancy_dollar = 0.0
        if total_trades > 0:
            win_prob = len(winning_trades) / total_trades
            loss_prob = len(losing_trades) / total_trades
            expectancy_dollar = round((win_prob * avg_winner) + (loss_prob * avg_loser), 2)

        # Max consecutive losses
        max_cons_losses = 0
        cur_cons_losses = 0
        for t in trades:
            if t.net_pnl < 0:
                cur_cons_losses += 1
                if cur_cons_losses > max_cons_losses:
                    max_cons_losses = cur_cons_losses
            else:
                cur_cons_losses = 0

        return PerformanceMetrics(
            total_return_dollar=total_return_dollar,
            total_return_pct=total_return_pct,
            cagr_pct=cagr_pct,
            annualized_volatility_pct=ann_vol_pct,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            profit_factor=profit_factor,
            win_rate_pct=win_rate_pct,
            expectancy_dollar=expectancy_dollar,
            total_trades_count=total_trades,
            winning_trades_count=len(winning_trades),
            losing_trades_count=len(losing_trades),
            avg_winning_trade=avg_winner,
            avg_losing_trade=avg_loser,
            max_consecutive_losses=max_cons_losses,
            total_commissions_paid=round(total_commissions, 2),
            total_slippage_cost=round(total_slippage, 2),
            turnover_ratio=round((total_trades * 100.0) / max(1, n_days), 2),
            drawdown=drawdown_metrics,
        )
