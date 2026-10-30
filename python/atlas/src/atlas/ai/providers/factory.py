"""Provider factory resolving configured AI model providers."""

import os
from typing import Optional

from atlas.ai.providers.base import BaseAiProvider
from atlas.ai.providers.mock_provider import MockAiProvider
from atlas.ai.providers.openai_provider import OpenAiCompatibleProvider


def get_ai_provider(provider_name: Optional[str] = None) -> BaseAiProvider:
    """Resolves and returns the configured AI provider.

    Defaults to MockAiProvider for offline, tests, or when credentials are not configured.
    """
    # In test mode or when mock explicitly requested
    if (
        os.getenv("ATLAS_TEST_ENV") == "1"
        or provider_name == "mock"
        or provider_name == "atlas_mock"
    ):
        return MockAiProvider()

    # Check for OpenAI-compatible endpoint configurations
    openai_key = os.getenv("ATLAS_AI_API_KEY") or os.getenv("OPENAI_API_KEY")
    openai_base = os.getenv("ATLAS_AI_BASE_URL", "https://api.openai.com/v1")

    if openai_key and (provider_name in ("openai", "groq", "nvidia") or not provider_name):
        return OpenAiCompatibleProvider(api_key=openai_key, base_url=openai_base)

    # Clean deterministic fallback
    return MockAiProvider()
