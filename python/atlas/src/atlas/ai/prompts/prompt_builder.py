"""Prompt assembly, route descriptor injection, and context windowing for ATLAS AI."""

from typing import Any, Dict, List, Optional

from atlas.ai.domain import AiMessage, MessageRole
from atlas.ai.prompts.system_instructions import ATLAS_AI_V1_SYSTEM_PROMPT


class PromptBuilder:
    """Builds well-structured prompt message lists for LLM invocation."""

    DEFAULT_MAX_MESSAGES = 20
    DEFAULT_MAX_CHARS = 32000

    @classmethod
    def build_prompt_messages(
        cls,
        history: List[AiMessage],
        system_override: Optional[str] = None,
        active_route: Optional[Dict[str, Any]] = None,
        context_block: Optional[str] = None,
        max_messages: int = DEFAULT_MAX_MESSAGES,
    ) -> List[Dict[str, str]]:
        """Assembles the system message, contextual route indicator, verified context block, and recent message turns."""
        messages: List[Dict[str, str]] = []

        # 1. System Prompt
        system_content = system_override.strip() if system_override else ATLAS_AI_V1_SYSTEM_PROMPT

        # 2. Minimal Allowlisted Route Descriptor (Stage 124 Context-Light Boundary)
        if active_route:
            route = active_route.get("route", "") or active_route.get("current_route", "")
            module_name = active_route.get("module_name", "") or active_route.get(
                "active_module", ""
            )
            summary = active_route.get("summary", "")
            if route or module_name:
                system_content += (
                    f"\n\n[Active Platform Context: Route '{route}' ({module_name}) - {summary}]"
                )

        # 3. Verified Financial Context Block (Stage 125 Context Awareness Engine)
        if context_block:
            system_content += f"\n\n{context_block}"

        messages.append({"role": "system", "content": system_content})

        # 3. Message turns with windowing
        # Filter completed or user messages, sort by created_at ascending
        valid_turns = [
            m for m in history if m.role in (MessageRole.USER, MessageRole.ASSISTANT) and m.content
        ]

        # Take the most recent N messages
        recent_turns = (
            valid_turns[-max_messages:] if len(valid_turns) > max_messages else valid_turns
        )

        # Ensure budget
        total_chars = 0
        budgeted_turns: List[AiMessage] = []
        for turn in reversed(recent_turns):
            if total_chars + len(turn.content) > cls.DEFAULT_MAX_CHARS:
                break
            budgeted_turns.append(turn)
            total_chars += len(turn.content)

        budgeted_turns.reverse()

        for turn in budgeted_turns:
            messages.append(
                {
                    "role": turn.role.value if hasattr(turn.role, "value") else str(turn.role),
                    "content": turn.content,
                }
            )

        return messages
