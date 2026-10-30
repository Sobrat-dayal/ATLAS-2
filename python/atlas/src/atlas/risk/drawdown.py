"""ATLAS Financial Risk Foundation — Drawdown Analytics Engine (Stage 115).

Calculates cumulative wealth indices, running historical peaks, drawdown series,
maximum historical drawdown, and discrete drawdown episodes.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from .enums import DrawdownEpisodeStatus
from .errors import RiskDrawdownIndexInvalidError
from .models import DrawdownEpisode


class DrawdownEngine:
    """Calculates cash-flow-neutral drawdown series and historical recovery episodes."""

    @staticmethod
    def build_wealth_index(returns: List[float], base_value: float = 100.0) -> List[float]:
        """Constructs compounded wealth index from time-weighted return series.

        Formula:
            W_0 = base_value
            W_t = W_{t-1} * (1 + r_t)
        """
        if base_value <= 0:
            raise RiskDrawdownIndexInvalidError("Wealth index base value must be strictly positive.")

        wealth = [base_value]
        current = base_value
        for r in returns:
            # Handle total loss domain boundary (1 + r <= 0)
            factor = max(0.0, 1.0 + r)
            current = current * factor
            wealth.append(current)

        return wealth

    @staticmethod
    def compute_drawdown_series(wealth_index: List[float]) -> Tuple[List[float], List[float]]:
        """Computes running historical peaks and percentage drawdown relative to peak.

        Formula:
            P_t = max_{0 <= s <= t} W_s
            D_t = (W_t / P_t) - 1.0
        """
        if not wealth_index:
            return [], []

        peaks: List[float] = []
        drawdowns: List[float] = []
        running_peak = -float("inf")

        for w in wealth_index:
            if w > running_peak:
                running_peak = w
            peaks.append(running_peak)

            if running_peak > 0:
                dd = (w / running_peak) - 1.0
            else:
                dd = -1.0  # Total loss
            drawdowns.append(dd)

        return peaks, drawdowns

    @staticmethod
    def compute_maximum_drawdown(drawdowns: List[float]) -> float:
        """Computes maximum historical drawdown (minimum peak-to-trough decline)."""
        if not drawdowns:
            return 0.0
        return min(0.0, min(drawdowns))

    @staticmethod
    def extract_drawdown_episodes(
        timestamps: List[datetime],
        wealth_index: List[float],
    ) -> List[DrawdownEpisode]:
        """Identifies historical drawdown episodes with peak, trough, and observed recovery.

        Never assigns an invented future recovery date to an ongoing unrecovered drawdown.
        """
        n = len(wealth_index)
        if n < 2 or len(timestamps) != n:
            return []

        episodes: List[DrawdownEpisode] = []
        in_drawdown = False
        peak_idx = 0
        peak_val = wealth_index[0]
        trough_idx = 0
        trough_val = wealth_index[0]
        episode_counter = 1

        for i in range(1, n):
            w = wealth_index[i]
            if not in_drawdown:
                if w < peak_val:
                    # Drawdown starts
                    in_drawdown = True
                    trough_idx = i
                    trough_val = w
                else:
                    peak_idx = i
                    peak_val = w
            else:
                # In drawdown
                if w < trough_val:
                    trough_idx = i
                    trough_val = w

                if w >= peak_val:
                    # Recovery achieved
                    mdd = (trough_val / peak_val) - 1.0
                    peak_dt = timestamps[peak_idx]
                    trough_dt = timestamps[trough_idx]
                    rec_dt = timestamps[i]

                    time_to_trough = (trough_dt - peak_dt).days
                    rec_dur = (rec_dt - trough_dt).days

                    episodes.append(
                        DrawdownEpisode(
                            episode_id=f"DD-EP-{episode_counter:03d}",
                            peak_date=peak_dt,
                            peak_value=peak_val,
                            trough_date=trough_dt,
                            trough_value=trough_val,
                            max_drawdown=mdd,
                            recovery_date=rec_dt,
                            time_to_trough_days=max(0, time_to_trough),
                            recovery_duration_days=max(0, rec_dur),
                            status=DrawdownEpisodeStatus.RECOVERED,
                        )
                    )
                    episode_counter += 1
                    in_drawdown = False
                    peak_idx = i
                    peak_val = w

        # Check for unrecovered ongoing episode at the end of the history
        if in_drawdown:
            mdd = (trough_val / peak_val) - 1.0
            peak_dt = timestamps[peak_idx]
            trough_dt = timestamps[trough_idx]
            time_to_trough = (trough_dt - peak_dt).days

            episodes.append(
                DrawdownEpisode(
                    episode_id=f"DD-EP-{episode_counter:03d}",
                    peak_date=peak_dt,
                    peak_value=peak_val,
                    trough_date=trough_dt,
                    trough_value=trough_val,
                    max_drawdown=mdd,
                    recovery_date=None,  # Not recovered
                    time_to_trough_days=max(0, time_to_trough),
                    recovery_duration_days=None,
                    status=DrawdownEpisodeStatus.ONGOING,
                )
            )

        return episodes

