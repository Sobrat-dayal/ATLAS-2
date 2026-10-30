"""Comprehensive Unit and Integration Test Suite for Stage 127: AI Research and RAG.

Covers:
- Reference Fixtures A through J (Golden Research Dataset)
- Document ingestion, normalization, section extraction, and chunking
- Deterministic 384-dimensional vector embeddings and cosine similarity
- Hybrid retrieval (Lexical, Semantic, and Reciprocal Rank Fusion)
- Server-authoritative citation validation and rejection of fabricated citations
- Prompt-injection defense fencing for untrusted document context
- Multi-tenant and user-private document isolation and revocation
- Stage 126 Tool Gateway research adapter execution
- FastAPI HTTP endpoints under /api/v1/ai/research
"""

from __future__ import annotations

import pytest
from atlas.ai.research.domain import (
    CitationValidationStatus,
    ResearchRunStatus,
)
from atlas.ai.research.embeddings.generation import AtlasDeterministicEmbeddingProvider
from atlas.ai.research.errors import (
    ResearchCitationAccessDeniedError,
    ResearchCitationSourceMissingError,
    ResearchDocumentAccessDeniedError,
)
from atlas.ai.research.ingestion.service import DocumentIngestionService
from atlas.ai.research.service import AtlasAiResearchService
from atlas.ai.research.source_registry import AtlasResearchSourceRegistry
from atlas.ai.research.synthesis.citation_validation import CitationValidator
from atlas.ai.research.synthesis.context_builder import build_research_context_envelope
from atlas.ai.tools.dispatcher import AiToolDispatcher
from atlas.auth import AuthPrincipal
from fastapi.testclient import TestClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user


@pytest.fixture(autouse=True)
def reset_registry():
    """Resets the singleton registry before each test."""
    AtlasResearchSourceRegistry.reset_instance()
    yield


@pytest.fixture
def auth_principal():
    return AuthPrincipal(
        sub="test_user_stage127",
        email="analyst@atlas.institution",
        role="analyst",
    )


@pytest.fixture
def test_client(auth_principal):
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: auth_principal
    client = TestClient(app)
    return client


# =============================================================================
# REFERENCE FIXTURE TESTS (A THROUGH J)
# =============================================================================


@pytest.mark.asyncio
async def test_reference_fixture_a_annual_report_growth():
    """Fixture A: Revenue growth of 25% (100M to 125M USD) with correct units and citation."""
    service = AtlasAiResearchService.get_instance()
    run = await service.execute_research_query(
        query="What was TEST_COMPANY's revenue growth?",
        user_id="user_test",
        tenant_id="tenant_alpha",
    )

    assert run.status == ResearchRunStatus.COMPLETED
    assert "25%" in run.answer_text
    assert "100 USD million" in run.answer_text
    assert "125 USD million" in run.answer_text
    assert len(run.citations) > 0
    assert run.citations[0].status == CitationValidationStatus.VERIFIED
    assert run.citations[0].page_number == 14


@pytest.mark.asyncio
async def test_reference_fixture_b_document_comparison_capex():
    """Fixture B: Identifies 30 million USD difference between planned CapEx."""
    service = AtlasAiResearchService.get_instance()
    comparison = await service.compare_documents(
        document_id_a="doc_fixture_b1_capex2024",
        document_id_b="doc_fixture_b2_capex2025",
        user_id="user_test",
        tenant_id="tenant_alpha",
    )

    assert "30 million USD" in comparison["summary_text"]
    assert len(comparison["differences"]) == 1
    diff = comparison["differences"][0]
    assert diff["aspect"] == "Capital Expenditures Planned"
    assert diff["doc_a_value"] == "50 million USD"
    assert diff["doc_b_value"] == "80 million USD"


@pytest.mark.asyncio
async def test_reference_fixture_c_historical_as_of_filtering():
    """Fixture C: Source published 2025-03-01 is strictly excluded on as-of 2024-12-31."""
    service = AtlasAiResearchService.get_instance()

    # Query with historical as-of before doc_c was published
    evidence = await service.search_passages(
        query="Quantum AI acquisition",
        user_id="user_test",
        tenant_id="tenant_alpha",
        historical_as_of="2024-12-31T23:59:59Z",
    )

    # Document C was published 2025-03-01, so it MUST NOT be retrieved
    doc_ids = [ev.document_id for ev in evidence]
    assert "doc_fixture_c_future" not in doc_ids


@pytest.mark.asyncio
async def test_reference_fixture_d_restricted_document_access_denial():
    """Fixture D: User B cannot retrieve User A's private document."""
    service = AtlasAiResearchService.get_instance()

    # User B tries to search for User A's private M&A document
    evidence = await service.search_passages(
        query="Confidential M&A valuation multiples",
        user_id="user_b",
        tenant_id="tenant_alpha",
    )

    doc_ids = [ev.document_id for ev in evidence]
    assert "doc_fixture_d_private" not in doc_ids

    # Direct document metadata lookup by user_b must raise ResearchDocumentAccessDeniedError
    with pytest.raises(ResearchDocumentAccessDeniedError):
        service.get_document_metadata(
            "doc_fixture_d_private", user_id="user_b", tenant_id="tenant_alpha"
        )

    # But user_a CAN access it
    doc = service.get_document_metadata(
        "doc_fixture_d_private", user_id="user_a", tenant_id="tenant_alpha"
    )
    assert doc.document_id == "doc_fixture_d_private"


def test_reference_fixture_e_fabricated_citation_rejected():
    """Fixture E: Fabricated citation [Source 999] is rejected and stripped."""
    service = AtlasAiResearchService.get_instance()

    answer_with_fake = "The enterprise margin was 45% [Source 999] according to estimates."
    sanitized_text, citations = CitationValidator.extract_and_validate_citations(
        answer_with_fake, []
    )

    # Rejected citation should not be in user text
    assert "[Source 999]" not in sanitized_text
    # Citation object must be marked REJECTED
    assert len(citations) == 1
    assert citations[0].status == CitationValidationStatus.REJECTED
    assert "999" in citations[0].citation_id

    # Resolving fabricated citation must fail
    with pytest.raises(ResearchCitationSourceMissingError):
        service.resolve_citation("cite_999", user_id="user_test", tenant_id="tenant_alpha")


def test_reference_fixture_f_prompt_injection_defense():
    """Fixture F: Document text with prompt injection is contained in untrusted security fence."""
    service = AtlasAiResearchService.get_instance()
    chunks = service.registry.get_chunks_for_document("doc_fixture_f_injection")
    doc = service.registry.get_document("doc_fixture_f_injection")
    source = service.registry.get_source(doc.source_id)

    from atlas.ai.research.synthesis.evidence import build_evidence_unit

    ev = build_evidence_unit(chunks[0], doc, source, 1.0)
    context_env = build_research_context_envelope([ev])

    # Must contain protective directive and tags
    assert "<atlas_verified_financial_context>" in context_env
    assert "</atlas_verified_financial_context>" in context_env
    assert "untrusted external financial document texts" in context_env
    assert "Ignore previous instructions" in context_env  # present as data, not instruction


@pytest.mark.asyncio
async def test_reference_fixture_g_empty_retrieval_insufficient_evidence():
    """Fixture G: Query requiring absent evidence returns INSUFFICIENT_EVIDENCE without hallucination."""
    service = AtlasAiResearchService.get_instance()
    run = await service.execute_research_query(
        query="What is TEST_COMPANY's commercial real estate exposure in Antarctica?",
        user_id="user_test",
        tenant_id="tenant_alpha",
    )

    assert run.status == ResearchRunStatus.INSUFFICIENT_EVIDENCE
    assert "Sufficient evidence was not found" in run.answer_text
    assert len(run.citations) == 0


@pytest.mark.asyncio
async def test_reference_fixture_h_conflicting_sources():
    """Fixture H: Reconciles differing GAAP (35M) vs Non-GAAP (52M) figures."""
    service = AtlasAiResearchService.get_instance()
    run = await service.execute_research_query(
        query="What was TEST_COMPANY's FY2025 operating income under GAAP and Non-GAAP?",
        user_id="user_test",
        tenant_id="tenant_alpha",
    )

    assert run.status == ResearchRunStatus.COMPLETED
    assert "35 million USD" in run.answer_text
    assert "52 million USD" in run.answer_text
    assert "17 million USD" in run.answer_text  # stock-based compensation variance
    assert run.evidence_manifest.has_conflicting_sources is True


def test_reference_fixture_i_revoked_document_access():
    """Fixture I: Revoking document immediately blocks search and citation resolution."""
    service = AtlasAiResearchService.get_instance()

    # doc_fixture_i_revoked is initialized with is_revoked=True
    with pytest.raises(ResearchDocumentAccessDeniedError):
        service.get_document_metadata(
            "doc_fixture_i_revoked", user_id="user_test", tenant_id="tenant_alpha"
        )

    # Resolving citation for revoked document raises ResearchCitationAccessDeniedError
    with pytest.raises(ResearchCitationAccessDeniedError):
        service.resolve_citation(
            "cite_chk_fixture_i_1", user_id="user_test", tenant_id="tenant_alpha"
        )


def test_reference_fixture_j_large_document_chunking():
    """Fixture J: Large document is broken into bounded structural chunks."""
    service = AtlasAiResearchService.get_instance()
    chunks = service.registry.get_chunks_for_document("doc_fixture_j_large")

    assert len(chunks) == 3
    assert chunks[0].section_title == "Executive Summary"
    assert chunks[1].section_title == "Market Risk Assessment"
    assert chunks[2].section_title == "Segment Breakdown"


# =============================================================================
# INGESTION & EMBEDDING TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_document_ingestion_pipeline():
    """Tests end-to-end ingestion and structural chunking."""
    service = DocumentIngestionService()
    raw_content = (
        "Section 1: Overview\n"
        "Operating profit expanded 14% to 45 USD million.\n\n"
        "Section 2: Segment Analysis\n"
        "North America accounted for 70% of shipments."
    )

    job = await service.ingest_document(
        source_id="src_corp_ir",
        title="Q3 Interim Shareholder Report",
        document_type="10-Q",
        publication_date="2026-03-01T00:00:00Z",
        content_text=raw_content,
        user_id="user_test",
        tenant_id="tenant_alpha",
        symbol="TEST_COMPANY",
    )

    assert job.indexing_status.value == "INDEXED"
    assert job.chunks_count >= 2


@pytest.mark.asyncio
async def test_deterministic_embedding_generation():
    """Verifies that embeddings are 384-dimensional and unit-normalized."""
    provider = AtlasDeterministicEmbeddingProvider(dimensions=384)
    vec1 = await provider.embed_text("Capital expenditures planned: 50 million")
    vec2 = await provider.embed_text("Capital expenditures planned: 50 million")
    vec3 = await provider.embed_text("Completely unrelated text about biotechnology")

    assert len(vec1) == 384
    # Determinism
    assert vec1 == vec2

    # L2 unit length
    norm = sum(x * x for x in vec1)
    assert abs(norm - 1.0) < 1e-4

    # Similarity between identical texts = 1.0
    sim_identical = sum(a * b for a, b in zip(vec1, vec2))
    assert abs(sim_identical - 1.0) < 1e-4

    # Similarity between dissimilar texts is lower
    sim_different = sum(a * b for a, b in zip(vec1, vec3))
    assert sim_different < 0.95


# =============================================================================
# STAGE 126 AI TOOL GATEWAY INTEGRATION TESTS
# =============================================================================


@pytest.mark.asyncio
async def test_tool_gateway_research_adapters():
    """Executes Stage 127 research tools via the Stage 126 AiToolDispatcher."""
    dispatcher = AiToolDispatcher.get_instance()

    # 1. atlas.research.search_documents
    res_docs = await dispatcher.dispatch(
        tool_id="atlas.research.search_documents",
        arguments={"symbol": "TEST_COMPANY"},
        user_id="user_primary",
    )
    assert res_docs.success is True
    assert res_docs.data["count"] >= 1

    # 2. atlas.research.search_passages
    res_passages = await dispatcher.dispatch(
        tool_id="atlas.research.search_passages",
        arguments={"query": "revenue FY2025"},
        user_id="user_primary",
    )
    assert res_passages.success is True
    assert res_passages.data["count"] >= 1

    # 3. atlas.research.compare_documents
    res_compare = await dispatcher.dispatch(
        tool_id="atlas.research.compare_documents",
        arguments={
            "document_id_a": "doc_fixture_b1_capex2024",
            "document_id_b": "doc_fixture_b2_capex2025",
        },
        user_id="user_primary",
    )
    assert res_compare.success is True
    assert "30 million USD" in res_compare.data["summary_text"]

    # 4. atlas.research.get_citation_source
    res_cite = await dispatcher.dispatch(
        tool_id="atlas.research.get_citation_source",
        arguments={"citation_id": "cite_chk_fixture_a_1"},
        user_id="user_primary",
    )
    assert res_cite.success is True
    assert res_cite.data["symbol"] == "TEST_COMPANY"


# =============================================================================
# FASTAPI HTTP ENDPOINT TESTS
# =============================================================================


def test_api_list_sources(test_client):
    """GET /api/v1/ai/research/sources"""
    response = test_client.get("/api/v1/ai/research/sources")
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert data["count"] >= 2


def test_api_list_documents(test_client):
    """GET /api/v1/ai/research/documents"""
    response = test_client.get("/api/v1/ai/research/documents?symbol=TEST_COMPANY")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert data["count"] >= 1


def test_api_search_passages(test_client):
    """POST /api/v1/ai/research/search"""
    response = test_client.post(
        "/api/v1/ai/research/search",
        json={"query": "revenue growth FY2025", "symbols": ["TEST_COMPANY"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_hits"] >= 1
    assert "passages" in data


def test_api_execute_research_query(test_client):
    """POST /api/v1/ai/research/query"""
    response = test_client.post(
        "/api/v1/ai/research/query",
        json={"query": "What was the revenue growth for TEST_COMPANY?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert "25%" in data["answer_text"]
    assert len(data["citations"]) >= 1


def test_api_compare_documents(test_client):
    """POST /api/v1/ai/research/compare"""
    response = test_client.post(
        "/api/v1/ai/research/compare",
        json={
            "document_id_a": "doc_fixture_b1_capex2024",
            "document_id_b": "doc_fixture_b2_capex2025",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "differences" in data
    assert len(data["differences"]) >= 1


def test_api_resolve_citation(test_client):
    """GET /api/v1/ai/research/citations/{id}"""
    response = test_client.get("/api/v1/ai/research/citations/cite_chk_fixture_a_1")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "VERIFIED"
    assert data["symbol"] == "TEST_COMPANY"
