"""Catalog and registry of supported and authorized AI models."""

from typing import Dict, List

from atlas.ai.domain import ModelCapability
from atlas.ai.errors import AiModelNotFoundError

APPROVED_MODELS: Dict[str, ModelCapability] = {
    "atlas-intelligence-v1": ModelCapability(
        model_id="atlas-intelligence-v1",
        name="ATLAS Intelligence v1",
        provider="atlas",
        description="High-speed institutional financial intelligence model optimized for quantitative research, risk, and platform navigation.",
        context_window=32768,
        supports_streaming=True,
        cost_per_1k_input=0.0015,
        cost_per_1k_output=0.002,
        is_default=True,
    ),
    "atlas-reasoning-v1": ModelCapability(
        model_id="atlas-reasoning-v1",
        name="ATLAS Deep Reasoning v1",
        provider="atlas",
        description="Extended analytical reasoning engine suited for complex financial mathematics, derivatives structuring, and scenario evaluation.",
        context_window=65536,
        supports_streaming=True,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.006,
        is_default=False,
    ),
    "atlas-speed-v1": ModelCapability(
        model_id="atlas-speed-v1",
        name="ATLAS Speed v1",
        provider="atlas",
        description="Ultra-low latency model for immediate platform lookup, navigation queries, and quick terminology definitions.",
        context_window=16384,
        supports_streaming=True,
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.001,
        is_default=False,
    ),
}

DEFAULT_MODEL_ID = "atlas-intelligence-v1"


def get_model_capability(model_id: str) -> ModelCapability:
    """Retrieve capability descriptor for a model ID or raise AiModelNotFoundError."""
    if model_id not in APPROVED_MODELS:
        raise AiModelNotFoundError(model_id)
    return APPROVED_MODELS[model_id]


def list_approved_models() -> List[ModelCapability]:
    """Return all approved models in the registry."""
    return list(APPROVED_MODELS.values())


def is_valid_model(model_id: str) -> bool:
    """Check if model ID is registered."""
    return model_id in APPROVED_MODELS
