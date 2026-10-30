"""Comprehensive pytest suite for Stage 124 AI Assistant V1 and AppShell Overlay.

Covers:
- Conversation lifecycle (create, list, pin, archive, update, delete)
- Message handling & size boundary (16,000 character limit)
- Context windowing & allowlisted route descriptor injection
- Streaming SSE events (RUN_STARTED, DELTA, RUN_COMPLETED, RUN_CANCELLED)
- Financial intelligence (Duration/Convexity, Sharpe ratio calculation, VaR/CVaR, Black-Scholes)
- Stage 124 boundary honesty (No live tick hallucination, no autonomous broker trade execution)
- Canonical 20-module platform navigation guidance
- User isolation & access controls (User A vs User B)
- FastAPI HTTP / SSE API endpoints
"""

from typing import Generator

import pytest
from atlas.ai.domain import (
    GenerationStatus,
    MessageRole,
    MessageStatus,
    StreamEventType,
)
from atlas.ai.errors import (
    AiAccessDeniedError,
    AiConversationNotFoundError,
    AiMessageTooLargeError,
    AiModelNotFoundError,
)
from atlas.ai.prompts.prompt_builder import PromptBuilder
from atlas.ai.providers.mock_provider import MockAiProvider
from atlas.ai.repository import AiRepository
from atlas.ai.service import AiAssistantService
from atlas.auth import AuthPrincipal
from fastapi.testclient import TestClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.main import app

# ---------------- Fixtures ----------------


@pytest.fixture
def ai_service() -> AiAssistantService:
    repo = AiRepository()
    return AiAssistantService(repository=repo)


@pytest.fixture
def user_a() -> str:
    return "usr_portfolio_mgr_101"


@pytest.fixture
def user_b() -> str:
    return "usr_quant_researcher_202"


@pytest.fixture
def client_user_a(user_a: str) -> Generator[TestClient, None, None]:
    principal = AuthPrincipal(
        sub=user_a, email="pm101@atlas.institutional", role="portfolio_manager"
    )
    app.dependency_overrides[get_current_user] = lambda: principal
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_current_user, None)


# ---------------- Unit Tests: Conversations ----------------


def test_conversation_lifecycle(ai_service: AiAssistantService, user_a: str):
    # 1. Create conversation
    conv = ai_service.create_conversation(
        owner_user_id=user_a,
        title="Multi-Asset Risk Assessment",
        model_id="atlas-intelligence-v1",
    )
    assert conv.conversation_id.startswith("conv_")
    assert conv.title == "Multi-Asset Risk Assessment"
    assert conv.model_id == "atlas-intelligence-v1"
    assert conv.is_pinned is False
    assert conv.is_archived is False

    # 2. Get conversation
    fetched = ai_service.get_conversation(conv.conversation_id, user_a)
    assert fetched.conversation_id == conv.conversation_id

    # 3. Pin conversation
    updated = ai_service.update_conversation(conv.conversation_id, user_a, is_pinned=True)
    assert updated.is_pinned is True
    assert updated.pinned_at is not None

    # 4. List conversations
    items, total = ai_service.list_conversations(user_a)
    assert total == 1
    assert items[0].conversation_id == conv.conversation_id

    # 5. Archive conversation
    ai_service.update_conversation(conv.conversation_id, user_a, is_archived=True)
    active_items, active_total = ai_service.list_conversations(user_a, is_archived=False)
    assert active_total == 0

    archived_items, archived_total = ai_service.list_conversations(user_a, is_archived=True)
    assert archived_total == 1
    assert archived_items[0].conversation_id == conv.conversation_id

    # 6. Delete conversation
    assert ai_service.delete_conversation(conv.conversation_id, user_a) is True
    with pytest.raises(AiConversationNotFoundError):
        ai_service.get_conversation(conv.conversation_id, user_a)


def test_invalid_model_rejection(ai_service: AiAssistantService, user_a: str):
    with pytest.raises(AiModelNotFoundError):
        ai_service.create_conversation(owner_user_id=user_a, model_id="nonexistent-model-xyz")


# ---------------- Unit Tests: Message Flow & Windowing ----------------


def test_message_validation_and_size_limits(ai_service: AiAssistantService, user_a: str):
    conv = ai_service.create_conversation(owner_user_id=user_a)

    # Valid message
    msg, run = ai_service.send_message(
        conversation_id=conv.conversation_id,
        owner_user_id=user_a,
        content="What is the difference between Macaulay and Modified Duration?",
    )
    assert msg.role == MessageRole.USER
    assert run.status == GenerationStatus.RUNNING

    # Message exceeding 16,000 characters
    oversized = "A" * 16001
    with pytest.raises(AiMessageTooLargeError):
        ai_service.send_message(
            conversation_id=conv.conversation_id,
            owner_user_id=user_a,
            content=oversized,
        )


def test_prompt_builder_route_injection_and_windowing(ai_service: AiAssistantService, user_a: str):
    conv = ai_service.create_conversation(owner_user_id=user_a)

    route_info = {
        "route": "/risk",
        "module_name": "Risk",
        "summary": "Factor risk models and scenario analysis",
    }

    # Add 5 messages
    for i in range(5):
        ai_service.repository.add_message(
            conversation_id=conv.conversation_id,
            owner_user_id=user_a,
            role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
            content=f"Message turn number {i}",
            route_context=route_info if i == 0 else None,
        )

    history = ai_service.repository.list_messages(conv.conversation_id, user_a)
    turns = PromptBuilder.build_prompt_messages(
        history=history,
        active_route=route_info,
        max_messages=3,
    )

    # First turn is system prompt containing the active route
    assert turns[0]["role"] == "system"
    assert "/risk" in turns[0]["content"]
    assert "Risk" in turns[0]["content"]

    # Turns should respect max_messages window (3 turns + system = 4)
    assert len(turns) == 4
    assert turns[-1]["content"] == "Message turn number 4"


# ---------------- Unit Tests: Streaming & Cancellation ----------------


@pytest.mark.asyncio
async def test_streaming_generation_execution(ai_service: AiAssistantService, user_a: str):
    conv = ai_service.create_conversation(owner_user_id=user_a)
    _, run = ai_service.send_message(
        conversation_id=conv.conversation_id,
        owner_user_id=user_a,
        content="Explain duration and convexity in bond portfolios.",
    )

    events = []
    async for event in ai_service.stream_generation(run.generation_id, user_a):
        events.append(event)

    event_types = [e.event_type for e in events]
    assert StreamEventType.RUN_STARTED in event_types
    assert StreamEventType.DELTA in event_types
    assert StreamEventType.RUN_COMPLETED in event_types

    # Verify run completed in repository
    finished_run = ai_service.get_generation_run(run.generation_id, user_a)
    assert finished_run.status == GenerationStatus.COMPLETED
    assert finished_run.completion_tokens > 0
    assert finished_run.duration_ms is not None

    # Verify assistant message was saved
    messages = ai_service.list_messages(conv.conversation_id, user_a)
    assert len(messages) == 2
    assistant_msg = messages[1]
    assert assistant_msg.role == MessageRole.ASSISTANT
    assert assistant_msg.status == MessageStatus.COMPLETED
    assert "Modified Duration" in assistant_msg.content
    assert "Convexity" in assistant_msg.content


@pytest.mark.asyncio
async def test_streaming_generation_cancellation(ai_service: AiAssistantService, user_a: str):
    conv = ai_service.create_conversation(owner_user_id=user_a)
    _, run = ai_service.send_message(
        conversation_id=conv.conversation_id,
        owner_user_id=user_a,
        content="Explain Black-Scholes option pricing.",
    )

    # Immediately cancel run
    ai_service.cancel_generation(run.generation_id, user_a)

    events = []
    async for event in ai_service.stream_generation(run.generation_id, user_a):
        events.append(event)

    cancelled_event = next(
        (e for e in events if e.event_type == StreamEventType.RUN_CANCELLED), None
    )
    assert cancelled_event is not None

    run_status = ai_service.get_generation_run(run.generation_id, user_a)
    assert run_status.status == GenerationStatus.CANCELLED


# ---------------- Unit Tests: Financial Rigor & Boundary Honesty ----------------


@pytest.mark.asyncio
async def test_numerical_sharpe_ratio_calculation(ai_service: AiAssistantService, user_a: str):
    provider = MockAiProvider()
    response = await provider.generate(
        messages=[
            {
                "role": "user",
                "content": "Calculate Sharpe ratio with return 12%, risk free 3%, volatility 15%",
            }
        ],
        model_id="atlas-intelligence-v1",
    )
    content = response["content"]
    assert "0.60" in content
    assert "12.0%" in content or "12%" in content
    assert "3.0%" in content or "3%" in content
    assert "15.0%" in content or "15%" in content


@pytest.mark.asyncio
async def test_stage124_live_quote_honesty_boundary(ai_service: AiAssistantService, user_a: str):
    provider = MockAiProvider()
    response = await provider.generate(
        messages=[{"role": "user", "content": "What is the live price of AAPL right now?"}],
        model_id="atlas-intelligence-v1",
    )
    content = response["content"]
    assert "Stage 124 Operational Notice" in content
    assert "/markets" in content or "/charts" in content


@pytest.mark.asyncio
async def test_stage124_trade_execution_restriction_boundary(
    ai_service: AiAssistantService, user_a: str
):
    provider = MockAiProvider()
    response = await provider.generate(
        messages=[{"role": "user", "content": "Execute trade: Buy 100 shares of NVDA at market"}],
        model_id="atlas-intelligence-v1",
    )
    content = response["content"]
    assert "Stage 124 Capability Restriction" in content
    assert "/trading" in content


@pytest.mark.asyncio
async def test_navigation_guidance_for_risk_module(ai_service: AiAssistantService, user_a: str):
    provider = MockAiProvider()
    response = await provider.generate(
        messages=[
            {"role": "user", "content": "Where can I find portfolio risk models and stress tests?"}
        ],
        model_id="atlas-intelligence-v1",
    )
    content = response["content"]
    assert "/risk" in content


# ---------------- Unit Tests: User Isolation & Security ----------------


def test_user_tenant_isolation(ai_service: AiAssistantService, user_a: str, user_b: str):
    conv_a = ai_service.create_conversation(owner_user_id=user_a, title="User A Confidential Alpha")

    # User B should be forbidden from accessing User A's conversation
    with pytest.raises(AiAccessDeniedError):
        ai_service.get_conversation(conv_a.conversation_id, user_b)

    with pytest.raises(AiAccessDeniedError):
        ai_service.update_conversation(conv_a.conversation_id, user_b, title="Hacked Title")

    with pytest.raises(AiAccessDeniedError):
        ai_service.delete_conversation(conv_a.conversation_id, user_b)

    # User B's list should not include User A's conversation
    items_b, total_b = ai_service.list_conversations(user_b)
    assert total_b == 0


# ---------------- API Integration Tests (FastAPI / SSE) ----------------


def test_api_conversation_and_messages(client_user_a: TestClient):
    # 1. Create conversation
    create_resp = client_user_a.post(
        "/api/v1/ai/conversations",
        json={"title": "Macro Rate Projections", "model_id": "atlas-intelligence-v1"},
    )
    assert create_resp.status_code == 201
    conv_data = create_resp.json()
    conv_id = conv_data["conversation_id"]
    assert conv_data["title"] == "Macro Rate Projections"

    # 2. Send message
    msg_resp = client_user_a.post(
        f"/api/v1/ai/conversations/{conv_id}/messages",
        json={
            "content": "Explain VaR vs CVaR.",
            "route_context": {
                "route": "/risk",
                "module_name": "Risk",
                "summary": "Risk management",
            },
        },
    )
    assert msg_resp.status_code == 200
    msg_data = msg_resp.json()
    assert msg_data["message"]["role"] == "user"
    gen_id = msg_data["generation_id"]
    assert gen_id.startswith("gen_")

    # 3. Stream SSE generation
    with client_user_a.stream("GET", f"/api/v1/ai/generations/{gen_id}/stream") as stream_resp:
        assert stream_resp.status_code == 200
        assert "text/event-stream" in stream_resp.headers["content-type"]
        body_lines = [line for line in stream_resp.iter_lines() if line]
        assert len(body_lines) > 0

    # 4. Check message list
    list_resp = client_user_a.get(f"/api/v1/ai/conversations/{conv_id}/messages")
    assert list_resp.status_code == 200
    msgs = list_resp.json()["items"]
    assert len(msgs) == 2
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["status"] == "COMPLETED"


def test_api_models_and_preferences(client_user_a: TestClient):
    # Models
    models_resp = client_user_a.get("/api/v1/ai/models")
    assert models_resp.status_code == 200
    models = models_resp.json()["models"]
    assert len(models) >= 3
    model_ids = [m["model_id"] for m in models]
    assert "atlas-intelligence-v1" in model_ids

    # Preferences
    pref_resp = client_user_a.get("/api/v1/ai/preferences")
    assert pref_resp.status_code == 200
    pref_data = pref_resp.json()
    assert pref_data["default_model_id"] == "atlas-intelligence-v1"

    # Update preferences
    update_resp = client_user_a.put(
        "/api/v1/ai/preferences",
        json={"temperature": 0.4, "overlay_width_px": 480, "send_on_enter": False},
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["temperature"] == 0.4
    assert updated_data["overlay_width_px"] == 480
    assert updated_data["send_on_enter"] is False
