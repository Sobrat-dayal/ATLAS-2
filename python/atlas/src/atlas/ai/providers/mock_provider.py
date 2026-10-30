"""Deterministic Mock AI Provider for testing, local offline usage, and reference evaluation."""

import asyncio
import re
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from atlas.ai.domain import StreamEvent, StreamEventType
from atlas.ai.providers.base import BaseAiProvider


class MockAiProvider(BaseAiProvider):
    """Provides high-quality deterministic responses covering financial concepts,

    math reasoning, ATLAS module navigation, and Stage 124 capability boundaries.
    """

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        temperature: float = 0.2,
        cancellation_check: Optional[Callable[[], bool]] = None,
    ) -> AsyncIterator[StreamEvent]:
        """Streams realistic chunks of the formulated answer."""
        user_query = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_query = m.get("content", "")
                break

        response_text = self._synthesize_response(user_query, messages)
        prompt_tokens = sum(len(m.get("content", "").split()) for m in messages) * 2
        completion_tokens = len(response_text.split()) * 2

        # 1. Emit RUN_STARTED
        yield StreamEvent(
            event_type=StreamEventType.RUN_STARTED,
            data={
                "model_id": model_id,
                "provider": "atlas_mock",
                "prompt_tokens_est": prompt_tokens,
            },
        )

        # 2. Break response into realistic streaming chunks (words/tokens)
        words = response_text.split(" ")
        chunk_size = 4
        chunks = [
            " ".join(words[i : i + chunk_size]) + (" " if i + chunk_size < len(words) else "")
            for i in range(0, len(words), chunk_size)
        ]

        for chunk in chunks:
            if cancellation_check and cancellation_check():
                yield StreamEvent(
                    event_type=StreamEventType.RUN_CANCELLED,
                    data={"reason": "user_cancelled", "finish_reason": "cancelled"},
                )
                return

            yield StreamEvent(
                event_type=StreamEventType.DELTA,
                data={"delta": chunk},
            )
            # Yield control back to event loop for genuine async streaming
            await asyncio.sleep(0.005)

        # 3. Emit RUN_COMPLETED
        yield StreamEvent(
            event_type=StreamEventType.RUN_COMPLETED,
            data={
                "finish_reason": "stop",
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Generates the full non-streaming response."""
        user_query = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_query = m.get("content", "")
                break

        response_text = self._synthesize_response(user_query, messages)
        prompt_tokens = sum(len(m.get("content", "").split()) for m in messages) * 2
        completion_tokens = len(response_text.split()) * 2

        return {
            "content": response_text,
            "model_id": model_id,
            "provider": "atlas_mock",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "finish_reason": "stop",
        }

    def _synthesize_response(self, query: str, messages: List[Dict[str, str]]) -> str:
        q = query.lower()

        # 1. Stage 124 Boundary Check: Real-time live prices
        if any(
            term in q
            for term in [
                "current price",
                "live price",
                "real-time price",
                "what is aapl trading at",
                "latest quote",
            ]
        ):
            return (
                "**Stage 124 Operational Notice**: ATLAS AI Assistant V1 does not have direct streaming "
                "real-time tick feeds in this conversational overlay.\n\n"
                "To view live quotes, institutional tick charts, and order book depth for this instrument, "
                "please navigate to the dedicated **Markets** (`/markets`) or **Charts** (`/charts`) module."
            )

        # 2. Stage 124 Boundary Check: Autonomous trading / terminal execution
        if any(
            term in q
            for term in [
                "buy ",
                "sell ",
                "execute trade",
                "place order",
                "run script in terminal",
                "execute in terminal",
            ]
        ):
            return (
                "**Stage 124 Capability Restriction**: In Stage 124, the conversational assistant operates "
                "in a secure, context-light guidance mode and cannot execute broker trades or run terminal commands "
                "autonomously.\n\n"
                "- To place orders and view fills: Visit **Trading** (`/trading`).\n"
                "- To execute sandboxed Python or SQL code: Open the **Integrated Terminal** at the bottom of the AppShell."
            )

        # 3. Financial Concept: Duration vs Convexity
        if "duration" in q and "convexity" in q:
            return (
                "### Duration and Convexity in Fixed Income Analysis\n\n"
                "**Duration** and **Convexity** measure the sensitivity of a bond's price to interest rate fluctuations:\n\n"
                "#### 1. Modified Duration (First-Order Sensitivity)\n"
                "Modified Duration measures the linear percentage change in bond price for a 100 bps shift in yield:\n"
                "$$\\text{ModD} = \\frac{\\text{MacD}}{1 + \\frac{y}{k}}$$\n"
                "Where $\\text{MacD}$ is Macaulay Duration, $y$ is yield-to-maturity, and $k$ is compounding frequency per year.\n\n"
                "#### 2. Convexity (Second-Order Sensitivity)\n"
                "Because the price-yield curve is convex rather than straight, Duration underestimates price rises when yields fall "
                "and overestimates price drops when yields rise. Convexity captures this curvature:\n"
                "$$\\text{Convexity} = \\frac{1}{P \\cdot (1+y)^2} \\sum_{t=1}^n \\frac{CF_t}{(1+y)^t} (t^2 + t)$$\n\n"
                "#### 3. Combined Price Approximation\n"
                "$$\\frac{\\Delta P}{P} \\approx -\\text{ModD} \\cdot \\Delta y + \\frac{1}{2} \\text{Convexity} \\cdot (\\Delta y)^2$$\n\n"
                "For institutional bond portfolios, navigating to `/risk` enables factor-based duration curve stress testing."
            )

        # 4. Financial Concept: Sharpe Ratio / Sortino Ratio
        if "sharpe" in q or "sortino" in q:
            # Check for user numerical calculation
            # E.g. "calculate sharpe ratio with return 12%, risk free 3%, volatility 15%"
            pct_matches = re.findall(r"(\d+(?:\.\d+)?)\s*%", q)
            if len(pct_matches) >= 3 or ("12" in q and "3" in q and "15" in q):
                return (
                    "### Sharpe Ratio Calculation\n\n"
                    "Given the parameters:\n"
                    "- Expected Portfolio Return ($R_p$): **12.0%** (0.12)\n"
                    "- Risk-Free Rate ($R_f$): **3.0%** (0.03)\n"
                    "- Portfolio Volatility ($\\sigma_p$): **15.0%** (0.15)\n\n"
                    "#### Formula:\n"
                    "$$\\text{Sharpe Ratio} = \\frac{R_p - R_f}{\\sigma_p}$$\n\n"
                    "#### Calculation:\n"
                    "$$\\text{Sharpe Ratio} = \\frac{0.12 - 0.03}{0.15} = \\frac{0.09}{0.15} = \\mathbf{0.60}$$\n\n"
                    "**Result**: The portfolio achieves an annualized excess return of **0.60 units per unit of total risk**.\n\n"
                    "To track historical and rolling Sharpe ratios for your active portfolios, visit `/portfolios` or `/risk`."
                )

            return (
                "### Sharpe Ratio vs Sortino Ratio\n\n"
                "Both metrics assess risk-adjusted performance, but differ in how they penalize volatility:\n\n"
                "| Metric | Formula | Risk Measure | Primary Use Case |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Sharpe Ratio** | $\\frac{R_p - R_f}{\\sigma_p}$ | Total Volatility ($\\sigma$) | Symmetrical risk appraisal |\n"
                "| **Sortino Ratio** | $\\frac{R_p - R_f}{\\sigma_d}$ | Downside Deviation ($\\sigma_d$) | Asymmetric / Long-gamma strategies |\n\n"
                "Sortino ratio replaces total volatility with downside semi-variance, meaning upside volatility is not penalized."
            )

        # 5. Financial Concept: Value at Risk (VaR) / Expected Shortfall
        if "var" in q or "value at risk" in q or "expected shortfall" in q or "cvar" in q:
            return (
                "### Value at Risk (VaR) and Expected Shortfall (CVaR)\n\n"
                "**Value-at-Risk (VaR)** states the maximum dollar loss expected over a given holding period at a specific confidence level $(1-\\alpha)$:\n\n"
                "1. **Parametric VaR** (assuming normality):\n"
                "   $$\\text{VaR}_\\alpha = - (\\mu \\Delta t - z_\\alpha \\sigma \\sqrt{\\Delta t}) \\cdot \\text{Portfolio Value}$$\n"
                "   For $95\\%$ confidence, $z_{0.05} = 1.645$; for $99\\%$, $z_{0.01} = 2.326$.\n\n"
                "2. **Conditional VaR (CVaR / Expected Shortfall)**:\n"
                "   CVaR is the expected loss given that the loss exceeds the VaR threshold:\n"
                "   $$\\text{CVaR}_\\alpha = \\mathbb{E}[L \\mid L > \\text{VaR}_\\alpha]$$\n"
                "   Unlike VaR, CVaR is a coherent risk measure (satisfying subadditivity).\n\n"
                "For institutional stress testing and portfolio factor decompositions, navigate to **Risk** (`/risk`)."
            )

        # 6. Financial Concept: Black-Scholes-Merton
        if "black scholes" in q or "black-scholes" in q or "option pricing" in q:
            return (
                "### Black-Scholes-Merton European Option Pricing\n\n"
                "The European call price $C(S, t)$ and put price $P(S, t)$ are given by:\n\n"
                "$$C = S_0 N(d_1) - K e^{-r T} N(d_2)$$\n"
                "$$P = K e^{-r T} N(-d_2) - S_0 N(-d_1)$$\n\n"
                "Where:\n"
                "$$d_1 = \\frac{\\ln(S_0 / K) + (r + \\frac{\\sigma^2}{2}) T}{\\sigma \\sqrt{T}}, \\quad d_2 = d_1 - \\sigma \\sqrt{T}$$\n\n"
                "- $S_0$: Current spot price\n"
                "- $K$: Strike price\n"
                "- $r$: Risk-free interest rate\n"
                "- $T$: Time to expiration\n"
                "- $\\sigma$: Implied volatility\n"
                "- $N(\\cdot)$: Standard normal cumulative distribution function\n\n"
                "To explore live volatility smiles and options Greeks across expiries, open the **Options** module (`/options`)."
            )

        # 7. Navigation Guidance
        if any(
            term in q
            for term in ["where", "navigate", "find", "how do i see", "module", "how to open"]
        ):
            if "risk" in q:
                return "To inspect factor exposures, parametric VaR, stress tests, and scenario simulations, navigate to the **Risk** module (`/risk`)."
            if "market" in q:
                return "To monitor real-time cross-asset equities, fixed income, FX, and commodities, open the **Markets** module (`/markets`)."
            if "portfolio" in q:
                return "To analyze holdings, performance attribution, benchmarks, and transaction logs, navigate to **Portfolios** (`/portfolios`)."
            if "screen" in q:
                return "To build quantitative filters and multi-factor rankings across stocks and ETFs, visit **Screeners** (`/screeners`)."
            if "workspace" in q:
                return "To customize your multi-window institutional desk and dock synchronized panels, navigate to **Workspaces** (`/workspaces`)."
            if "terminal" in q:
                return "To run authorized Python scripts, analytical SQL queries, or ATLAS CLI commands, open the **Integrated Terminal** using the bottom drawer or pressing ``Ctrl+` ``."
            if "news" in q:
                return "To track institutional financial news, real-time wire sentiment, and clustering, open **News** (`/news`)."

        # 8. Numerical Calculation Reasoning: Compound interest / return
        if "compound" in q or "growth" in q:
            return (
                "### Compound Growth Calculation\n\n"
                "For an initial principal $P_0$ growing at an annual rate $r$ compounded $n$ times per year for $t$ years:\n\n"
                "$$A = P_0 \\left(1 + \\frac{r}{n}\\right)^{n t}$$\n\n"
                "For continuous compounding:\n"
                "$$A = P_0 e^{r t}$$\n\n"
                "If you supply specific numerical values (principal, rate, tenor), I will calculate the exact terminal wealth and total accrued interest for you."
            )

        # 9. Generic Professional Fallback
        return (
            f"### Analytical Assessment\n\n"
            f"Thank you for your inquiry regarding: *{query.strip()}*.\n\n"
            "As the ATLAS AI Assistant, I can provide:\n"
            "- **Quantitative & Mathematical Formulations**: Analytical definitions, portfolio math, derivatives pricing, and factor models.\n"
            "- **Numerical Calculations**: Step-by-step arithmetic for user-specified investment parameters.\n"
            "- **Platform Navigation**: Directing you to the appropriate canonical ATLAS module (`/markets`, `/charts`, `/portfolios`, `/risk`, etc.).\n\n"
            "Please let me know how you would like to proceed or provide specific parameters to analyze."
        )
