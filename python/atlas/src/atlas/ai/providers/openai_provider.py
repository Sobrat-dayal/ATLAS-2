"""OpenAI-compatible inference provider supporting streaming SSE responses."""

import json
import logging
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

import httpx

from atlas.ai.domain import StreamEvent, StreamEventType
from atlas.ai.errors import AiProviderError
from atlas.ai.providers.base import BaseAiProvider

logger = logging.getLogger(__name__)


class OpenAiCompatibleProvider(BaseAiProvider):
    """Integrates with OpenAI-compatible inference APIs (OpenAI, Groq, NVIDIA NIM)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 60.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        temperature: float = 0.2,
        cancellation_check: Optional[Callable[[], bool]] = None,
    ) -> AsyncIterator[StreamEvent]:
        """Streams tokens from OpenAI-compatible /chat/completions endpoint."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }

        yield StreamEvent(
            event_type=StreamEventType.RUN_STARTED,
            data={"model_id": model_id, "provider": "openai_compatible"},
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        raise AiProviderError(
                            "openai_compatible",
                            f"HTTP {response.status_code}: {error_body.decode('utf-8')}",
                        )

                    total_chunks = 0
                    async for line in response.aiter_lines():
                        if cancellation_check and cancellation_check():
                            yield StreamEvent(
                                event_type=StreamEventType.RUN_CANCELLED,
                                data={"reason": "user_cancelled", "finish_reason": "cancelled"},
                            )
                            return

                        line_str = line.strip()
                        if not line_str or line_str.startswith(":"):
                            continue

                        if line_str == "data: [DONE]":
                            break

                        if line_str.startswith("data: "):
                            data_json = line_str[6:]
                            try:
                                chunk_data = json.loads(data_json)
                                choices = chunk_data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content_delta = delta.get("content")
                                    if content_delta:
                                        total_chunks += 1
                                        yield StreamEvent(
                                            event_type=StreamEventType.DELTA,
                                            data={"delta": content_delta},
                                        )
                            except json.JSONDecodeError:
                                continue

                    yield StreamEvent(
                        event_type=StreamEventType.RUN_COMPLETED,
                        data={"finish_reason": "stop", "chunks": total_chunks},
                    )

        except Exception as exc:
            logger.error("Error during OpenAI compatible streaming: %s", exc)
            yield StreamEvent(
                event_type=StreamEventType.ERROR,
                data={"error_code": "AI_PROVIDER_ERROR", "message": str(exc)},
            )

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Non-streaming completion."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code != 200:
                    raise AiProviderError(
                        "openai_compatible", f"HTTP {resp.status_code}: {resp.text}"
                    )
                data = resp.json()
                choice = data["choices"][0]
                return {
                    "content": choice["message"]["content"],
                    "model_id": model_id,
                    "provider": "openai_compatible",
                    "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": data.get("usage", {}).get("total_tokens", 0),
                    "finish_reason": choice.get("finish_reason", "stop"),
                }
        except Exception as exc:
            raise AiProviderError("openai_compatible", str(exc)) from exc
