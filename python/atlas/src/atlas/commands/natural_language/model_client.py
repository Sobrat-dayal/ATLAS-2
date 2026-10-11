"""Model client abstractions for ATLAS Natural-Language Command Interpretation (Stage 48)."""

import json
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from pydantic import ValidationError

from .errors import (
    InterpreterTimeoutError,
    InterpreterUnavailableError,
    InvalidModelOutputError,
)
from .models import RawModelCommandOutput
from .prompt import NaturalLanguageCommandPromptBuilder
from .settings import NaturalLanguageCommandSettings


class CommandInterpretationModelClient(ABC):
    """Abstract interface for command interpretation model adapters."""

    @abstractmethod
    async def interpret(
        self,
        user_text: str,
        prompt_builder: NaturalLanguageCommandPromptBuilder,
    ) -> RawModelCommandOutput:
        """Sends user text for structured classification and returns validated output."""
        pass


class OpenAICompatibleModelClient(CommandInterpretationModelClient):
    """Client for OpenAI-compatible structured JSON chat completions endpoints."""

    def __init__(
        self,
        settings: NaturalLanguageCommandSettings,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.settings = settings
        self._external_client = http_client

    async def interpret(
        self,
        user_text: str,
        prompt_builder: NaturalLanguageCommandPromptBuilder,
    ) -> RawModelCommandOutput:
        base_url = (self.settings.model_base_url or "").rstrip("/")
        if not base_url:
            raise InterpreterUnavailableError(
                "Model base URL is not configured for command interpretation."
            )

        url = f"{base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.settings.model_api_key:
            headers["Authorization"] = f"Bearer {self.settings.model_api_key}"

        body = {
            "model": self.settings.model_name,
            "messages": [
                {"role": "system", "content": prompt_builder.build_system_prompt()},
                {"role": "user", "content": prompt_builder.build_user_message(user_text)},
            ],
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_output_tokens,
            "response_format": {"type": "json_object"},
        }

        try:
            if self._external_client:
                response = await self._external_client.post(
                    url,
                    json=body,
                    headers=headers,
                    timeout=self.settings.timeout_seconds,
                )
            else:
                async with httpx.AsyncClient(timeout=self.settings.timeout_seconds) as client:
                    response = await client.post(url, json=body, headers=headers)

            if response.status_code >= 400:
                raise InterpreterUnavailableError(
                    f"Model endpoint returned error status {response.status_code}."
                )

            data = response.json()
            choices = data.get("choices")
            if not choices or not isinstance(choices, list):
                raise InvalidModelOutputError("Model response contained no choices.")

            message_content = choices[0].get("message", {}).get("content", "")
            if not message_content:
                raise InvalidModelOutputError("Model response message content was empty.")

            parsed_json = json.loads(message_content)
            return RawModelCommandOutput.model_validate(parsed_json)

        except httpx.TimeoutException as err:
            raise InterpreterTimeoutError(
                f"Model endpoint timed out after {self.settings.timeout_seconds}s."
            ) from err
        except httpx.RequestError as err:
            raise InterpreterUnavailableError(
                f"Failed to communicate with model endpoint: {err}"
            ) from err
        except json.JSONDecodeError as err:
            raise InvalidModelOutputError("Model response was not valid JSON.") from err
        except ValidationError as err:
            raise InvalidModelOutputError(f"Model output violated strict schema: {err}") from err


class MockCommandInterpretationModelClient(CommandInterpretationModelClient):
    """Deterministic mock client for offline testing and development environments."""

    def __init__(
        self,
        settings: Optional[NaturalLanguageCommandSettings] = None,
        override_output: Optional[RawModelCommandOutput] = None,
    ):
        self.settings = settings
        self.override_output = override_output
        self.call_count = 0
        self.last_user_text: Optional[str] = None
        self.injected_error: Optional[Exception] = None

    async def interpret(
        self,
        user_text: str,
        prompt_builder: NaturalLanguageCommandPromptBuilder,
    ) -> RawModelCommandOutput:
        self.call_count += 1
        self.last_user_text = user_text

        if self.injected_error:
            raise self.injected_error

        if self.override_output:
            return self.override_output

        # Default heuristic parsing for standard test fixtures
        lower = user_text.lower().strip()

        # Prompt injection / adversarial checks
        if "ignore" in lower and ("instruction" in lower or "system" in lower or "rule" in lower):
            if "buy" in lower or "trade" in lower:
                return RawModelCommandOutput(
                    intent="UNSUPPORTED_ACTION",
                    unsupported_reason="TRADING_ACTION",
                )
            return RawModelCommandOutput(intent="NOT_COMMAND")

        # Unsupported actions
        if any(w in lower for w in ["buy", "sell", "order", "purchase", "shares of"]):
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="TRADING_ACTION",
            )
        risk_words = ["calculate", "run", "compute", "portfolio risk"]
        if "risk" in lower and any(w in lower for w in risk_words):
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="RISK_ACTION",
            )
        if any(w in lower for w in ["rebalance", "optimize", "holdings"]):
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="PORTFOLIO_ACTION",
            )
        agent_words = ["create an agent", "run my agent", "new agent", "research agent"]
        if any(w in lower for w in agent_words):
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="AGENT_ACTION",
            )
        if any(w in lower for w in ["build a workflow", "run workflow"]):
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="WORKFLOW_ACTION",
            )
        if any(w in lower for w in ["run python", "execute ls", "open shell"]):
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="TERMINAL_ACTION",
            )
        if any(w in lower for w in ["rm -rf", "delete system"]):
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="SYSTEM_ACTION",
            )
        if "http://" in lower or "https://" in lower:
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="EXTERNAL_ACTION",
            )
        if any(w in lower for w in ["send email", "message someone", "post online"]):
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="EXTERNAL_ACTION",
            )
        if " and then " in lower or " then " in lower:
            return RawModelCommandOutput(
                intent="UNSUPPORTED_ACTION",
                unsupported_reason="MULTI_COMMAND",
            )

        # Informational questions
        info_prefixes = (
            "what is",
            "why is",
            "why did",
            "how are",
            "tell me about",
            "what happened",
        )
        if any(lower.startswith(q) for q in info_prefixes):
            return RawModelCommandOutput(intent="NOT_COMMAND")
        if "what should i buy" in lower:
            return RawModelCommandOutput(intent="NOT_COMMAND")

        # Shell utilities
        if any(w in lower for w in ["settings", "preferences", "config"]):
            return RawModelCommandOutput(intent="OPEN_GLOBAL_SETTINGS")
        if any(w in lower for w in ["search entities", "open entity search", "find entities"]):
            return RawModelCommandOutput(intent="FOCUS_ENTITY_SEARCH")
        clear_phrases = ["clear selected entity", "remove current entity selection", "clear entity"]
        if any(w in lower for w in clear_phrases):
            return RawModelCommandOutput(intent="CLEAR_SELECTED_ENTITY")

        def entity_or_nav(mod: str, target: str) -> RawModelCommandOutput:
            if target:
                return RawModelCommandOutput(
                    intent="OPEN_ENTITY_IN_MODULE",
                    module=mod,
                    target_text=target,
                )
            return RawModelCommandOutput(
                intent="NAVIGATE_MODULE",
                module=mod,
            )

        # Entity in module navigation
        if "chart" in lower:
            target = self._extract_target(
                user_text, ["chart", "charts", "show me", "open", "the", "view", "for", "'s", "in"]
            )
            return entity_or_nav("charts", target)
        if "news" in lower:
            target = self._extract_target(
                user_text, ["news", "show", "open", "the", "view", "for", "'s", "in"]
            )
            return entity_or_nav("news", target)
        if "research" in lower:
            target = self._extract_target(
                user_text, ["research", "show", "open", "the", "view", "for", "'s", "in"]
            )
            return entity_or_nav("research", target)
        if "map" in lower or "maps" in lower:
            target = self._extract_target(
                user_text,
                ["map", "maps", "show", "open", "on", "the", "view", "for", "'s", "in"],
            )
            return entity_or_nav("maps", target)
        if "option" in lower or "options" in lower:
            target = self._extract_target(
                user_text,
                ["option", "options", "show", "open", "the", "view", "for", "'s", "in"],
            )
            return entity_or_nav("options", target)
        if "companies" in lower or "company" in lower:
            target = self._extract_target(
                user_text,
                ["companies", "company", "show", "open", "the", "view", "for", "'s", "in"],
            )
            return entity_or_nav("companies", target)
        if "intelligence" in lower or "intel" in lower:
            target = self._extract_target(
                user_text,
                ["intelligence", "intel", "show", "open", "the", "view", "for", "'s", "in"],
            )
            return entity_or_nav("intelligence", target)

        # Module navigation: "take me to markets", "go to maps", etc.
        nav_modules = prompt_builder.get_allowed_navigation_modules()
        for mod in nav_modules:
            if mod in lower or (mod == "ai" and ("assistant" in lower or "ai" in lower)):
                return RawModelCommandOutput(
                    intent="NAVIGATE_MODULE",
                    module=mod,
                )

        # Ambiguous action without destination
        if any(lower.startswith(w) for w in ["open ", "show ", "view "]):
            target = user_text.split(maxsplit=1)[-1].strip()
            return RawModelCommandOutput(
                intent="AMBIGUOUS",
                clarification_question=f"Which ATLAS module should open '{target}'?",
            )

        return RawModelCommandOutput(intent="NOT_COMMAND")

    def _extract_target(self, text: str, stop_words: list[str]) -> str:
        single_stop_words = set(
            w.lower().strip("'\":,.-") for item in stop_words for w in item.split()
        ) | {"show", "me", "the", "open", "on", "in", "view", "for", "to", "take", "go"}
        words = text.split()
        cleaned = []
        for w in words:
            cw = w.strip("'\":,.-")
            if cw.lower().endswith("'s"):
                cw = cw[:-2]
            if cw.lower() not in single_stop_words and cw:
                cleaned.append(cw)
        return " ".join(cleaned) if cleaned else ""
