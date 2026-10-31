"""Canonical Options Strategy Templates (Stage 141).

Registers 20 institutional strategy templates with directional bias and risk profiles.
"""

from __future__ import annotations

from typing import Dict, List
from pydantic import BaseModel


class StrategyTemplateDefinition(BaseModel):
    template_id: str
    name: str
    description: str
    directional_bias: str  # "BULLISH", "BEARISH", "NEUTRAL", "VOLATILITY"
    max_risk_profile: str  # "DEFINED", "UNDEFINED"
    typical_legs_count: int


CANONICAL_TEMPLATES: List[StrategyTemplateDefinition] = [
    StrategyTemplateDefinition(template_id="LONG_CALL", name="Long Call", description="Bullish directional call purchase with defined risk capped at premium paid.", directional_bias="BULLISH", max_risk_profile="DEFINED", typical_legs_count=1),
    StrategyTemplateDefinition(template_id="LONG_PUT", name="Long Put", description="Bearish directional put purchase with defined risk capped at premium paid.", directional_bias="BEARISH", max_risk_profile="DEFINED", typical_legs_count=1),
    StrategyTemplateDefinition(template_id="SHORT_CALL", name="Short Call (Naked)", description="Bearish to neutral call sale receiving upfront credit with unbounded upside risk.", directional_bias="BEARISH", max_risk_profile="UNDEFINED", typical_legs_count=1),
    StrategyTemplateDefinition(template_id="SHORT_PUT", name="Short Put", description="Bullish to neutral put sale receiving upfront credit with substantial downside risk.", directional_bias="BULLISH", max_risk_profile="DEFINED", typical_legs_count=1),
    StrategyTemplateDefinition(template_id="BULL_CALL_SPREAD", name="Bull Call Spread", description="Debit spread buying a lower strike call and selling a higher strike call.", directional_bias="BULLISH", max_risk_profile="DEFINED", typical_legs_count=2),
    StrategyTemplateDefinition(template_id="BEAR_PUT_SPREAD", name="Bear Put Spread", description="Debit spread buying a higher strike put and selling a lower strike put.", directional_bias="BEARISH", max_risk_profile="DEFINED", typical_legs_count=2),
    StrategyTemplateDefinition(template_id="BULL_PUT_SPREAD", name="Bull Put Spread", description="Credit spread selling a higher strike put and buying a lower strike put.", directional_bias="BULLISH", max_risk_profile="DEFINED", typical_legs_count=2),
    StrategyTemplateDefinition(template_id="BEAR_CALL_SPREAD", name="Bear Call Spread", description="Credit spread selling a lower strike call and buying a higher strike call.", directional_bias="BEARISH", max_risk_profile="DEFINED", typical_legs_count=2),
    StrategyTemplateDefinition(template_id="LONG_STRADDLE", name="Long Straddle", description="Non-directional volatility strategy buying ATM call and put at the same strike.", directional_bias="VOLATILITY", max_risk_profile="DEFINED", typical_legs_count=2),
    StrategyTemplateDefinition(template_id="SHORT_STRADDLE", name="Short Straddle", description="Neutral short volatility strategy selling ATM call and put at the same strike.", directional_bias="NEUTRAL", max_risk_profile="UNDEFINED", typical_legs_count=2),
    StrategyTemplateDefinition(template_id="LONG_STRANGLE", name="Long Strangle", description="Volatility strategy buying OTM call and OTM put at different strikes.", directional_bias="VOLATILITY", max_risk_profile="DEFINED", typical_legs_count=2),
    StrategyTemplateDefinition(template_id="SHORT_STRANGLE", name="Short Strangle", description="Neutral strategy selling OTM call and OTM put at different strikes.", directional_bias="NEUTRAL", max_risk_profile="UNDEFINED", typical_legs_count=2),
    StrategyTemplateDefinition(template_id="LONG_BUTTERFLY", name="Long Butterfly", description="Low-cost neutral spread combining three strikes with defined risk and reward.", directional_bias="NEUTRAL", max_risk_profile="DEFINED", typical_legs_count=3),
    StrategyTemplateDefinition(template_id="SHORT_BUTTERFLY", name="Short Butterfly", description="Credit spread profiting from breakout moves away from the middle strike.", directional_bias="VOLATILITY", max_risk_profile="DEFINED", typical_legs_count=3),
    StrategyTemplateDefinition(template_id="IRON_CONDOR", name="Iron Condor", description="Four-leg neutral credit spread combining a bull put spread and a bear call spread.", directional_bias="NEUTRAL", max_risk_profile="DEFINED", typical_legs_count=4),
    StrategyTemplateDefinition(template_id="IRON_BUTTERFLY", name="Iron Butterfly", description="Four-leg neutral credit spread selling ATM straddle and buying OTM wings.", directional_bias="NEUTRAL", max_risk_profile="DEFINED", typical_legs_count=4),
    StrategyTemplateDefinition(template_id="COVERED_CALL", name="Covered Call", description="Income strategy selling calls against an owned underlying equity position.", directional_bias="BULLISH", max_risk_profile="DEFINED", typical_legs_count=1),
    StrategyTemplateDefinition(template_id="PROTECTIVE_PUT", name="Protective Put", description="Hedging strategy holding long equity combined with a long put option.", directional_bias="BULLISH", max_risk_profile="DEFINED", typical_legs_count=1),
    StrategyTemplateDefinition(template_id="COLLAR", name="Collar", description="Capital preservation strategy combining long stock, long put, and short call.", directional_bias="NEUTRAL", max_risk_profile="DEFINED", typical_legs_count=2),
    StrategyTemplateDefinition(template_id="CUSTOM_MULTI_LEG", name="Custom Multi-Leg", description="User-configured multi-leg options strategy configuration.", directional_bias="NEUTRAL", max_risk_profile="DEFINED", typical_legs_count=1),
]
