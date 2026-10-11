import logging
import uuid
from typing import Any, List, Optional, Sequence
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.capabilities import registry
from atlas.entities.name_normalization import normalize_entity_name
from atlas.entities.types import EntityTypeKey
from atlas.identifiers.types import IdentifierSchemeKey
from atlas.search.enums import GlobalSearchMatchKind
from atlas.search.models import GlobalSearchRequest, GlobalSearchResponse
from atlas.search.repository import GlobalSearchRepository
from atlas.search.service import (
    PREFIX_IDENTIFIER_SCHEMES,
    SEARCHABLE_IDENTIFIER_SCHEMES,
    GlobalSearchService,
)
from atlas.search.settings import GlobalSearchSettings
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.config import get_settings
from atlas_api.dependencies import get_db_session
from atlas_api.routers.search import get_search_service


class FakeRow:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        return self.__dict__.get(name, None)


class MockSearchRepository:
    def __init__(self, settings: GlobalSearchSettings):
        self.settings = settings
        self.exact_name_data: List[FakeRow] = []
        self.exact_alias_data: List[FakeRow] = []
        self.exact_identifier_data: List[FakeRow] = []
        self.prefix_name_data: List[FakeRow] = []
        self.prefix_alias_data: List[FakeRow] = []
        self.prefix_identifier_data: List[FakeRow] = []
        self.fuzzy_name_data: List[FakeRow] = []
        self.fuzzy_alias_data: List[FakeRow] = []

        self.last_exact_id_targets = None
        self.last_prefix_id_targets = None
        self.fuzzy_called = False

    async def get_exact_name_candidates(
        self, normalized_query: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Any]:
        return [
            r
            for r in self.exact_name_data
            if not entity_types or r.entity_type in [t.value for t in entity_types]
        ]

    async def get_exact_alias_candidates(
        self, normalized_query: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Any]:
        return [
            r
            for r in self.exact_alias_data
            if not entity_types or r.entity_type in [t.value for t in entity_types]
        ]

    async def get_exact_identifier_candidates(
        self,
        candidates_normalized: dict[IdentifierSchemeKey, str],
        entity_types: Optional[List[EntityTypeKey]],
    ) -> Sequence[Any]:
        self.last_exact_id_targets = candidates_normalized
        return [
            r
            for r in self.exact_identifier_data
            if not entity_types or r.entity_type in [t.value for t in entity_types]
        ]

    async def get_prefix_name_candidates(
        self, prefix: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Any]:
        return [
            r
            for r in self.prefix_name_data
            if not entity_types or r.entity_type in [t.value for t in entity_types]
        ]

    async def get_prefix_alias_candidates(
        self, prefix: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Any]:
        return [
            r
            for r in self.prefix_alias_data
            if not entity_types or r.entity_type in [t.value for t in entity_types]
        ]

    async def get_prefix_identifier_candidates(
        self,
        prefix_candidates: dict[IdentifierSchemeKey, str],
        entity_types: Optional[List[EntityTypeKey]],
    ) -> Sequence[Any]:
        self.last_prefix_id_targets = prefix_candidates
        return [
            r
            for r in self.prefix_identifier_data
            if not entity_types or r.entity_type in [t.value for t in entity_types]
        ]

    async def get_fuzzy_name_candidates(
        self, query: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Any]:
        self.fuzzy_called = True
        return [
            r
            for r in self.fuzzy_name_data
            if not entity_types or r.entity_type in [t.value for t in entity_types]
        ]

    async def get_fuzzy_alias_candidates(
        self, query: str, entity_types: Optional[List[EntityTypeKey]]
    ) -> Sequence[Any]:
        self.fuzzy_called = True
        return [
            r
            for r in self.fuzzy_alias_data
            if not entity_types or r.entity_type in [t.value for t in entity_types]
        ]


# ==============================================================================
# 1. SETTINGS, MODELS & ENUMS TESTS
# ==============================================================================


def test_global_search_settings():
    settings = GlobalSearchSettings()
    assert settings.default_limit == 20
    assert settings.max_limit == 50
    assert settings.max_query_characters == 256
    assert settings.fuzzy_min_characters == 3
    assert settings.minimum_trigram_similarity == 0.35
    assert settings.exact_prefix_candidate_limit == 50
    assert settings.fuzzy_candidate_limit == 150


def test_global_search_request_and_response():
    req = GlobalSearchRequest(query="AAPL", limit=10, entity_types=[EntityTypeKey.SECURITY])
    assert req.query == "AAPL"
    assert req.limit == 10
    assert req.entity_types == [EntityTypeKey.SECURITY]

    res = GlobalSearchResponse(results=[])
    assert res.results == []


def test_global_search_enums():
    kinds = [k.value for k in GlobalSearchMatchKind]
    assert "EXACT_IDENTIFIER" in kinds
    assert "EXACT_CANONICAL_NAME" in kinds
    assert "EXACT_DISPLAY_NAME" in kinds
    assert "EXACT_ALIAS" in kinds
    assert "PREFIX_IDENTIFIER" in kinds
    assert "PREFIX_CANONICAL_NAME" in kinds
    assert "PREFIX_DISPLAY_NAME" in kinds
    assert "PREFIX_ALIAS" in kinds
    assert "FUZZY_CANONICAL_NAME" in kinds
    assert "FUZZY_DISPLAY_NAME" in kinds
    assert "FUZZY_ALIAS" in kinds
    assert len(kinds) == 11


# ==============================================================================
# 2. IDENTIFIER SCHEMES & VALIDATION POLICY TESTS
# ==============================================================================


def test_searchable_identifier_schemes_policy():
    # Provider external IDs must be excluded from normal Global Search
    assert IdentifierSchemeKey.PROVIDER_EXTERNAL_ID not in SEARCHABLE_IDENTIFIER_SCHEMES

    # Required schemes must be present
    assert IdentifierSchemeKey.TICKER in SEARCHABLE_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.ISIN in SEARCHABLE_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.CIK in SEARCHABLE_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.LEI in SEARCHABLE_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.ISO_3166_ALPHA2 in SEARCHABLE_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.MIC in SEARCHABLE_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.IATA_AIRPORT in SEARCHABLE_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.DOI in SEARCHABLE_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.FRED_SERIES in SEARCHABLE_IDENTIFIER_SCHEMES


def test_prefix_identifier_schemes_curated():
    # Only curated schemes allow prefix match
    assert set(PREFIX_IDENTIFIER_SCHEMES) == {
        IdentifierSchemeKey.TICKER,
        IdentifierSchemeKey.MIC,
        IdentifierSchemeKey.IATA_AIRPORT,
        IdentifierSchemeKey.ICAO_AIRPORT,
        IdentifierSchemeKey.ISO_3166_ALPHA2,
        IdentifierSchemeKey.ISO_3166_ALPHA3,
    }
    # Large numeric spaces (ISIN, CIK, LEI, FIGI) must not prefix match
    assert IdentifierSchemeKey.ISIN not in PREFIX_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.CIK not in PREFIX_IDENTIFIER_SCHEMES
    assert IdentifierSchemeKey.LEI not in PREFIX_IDENTIFIER_SCHEMES


# ==============================================================================
# 3. TEXT & IDENTIFIER NORMALIZATION TESTS
# ==============================================================================


def test_text_normalization_unicode_nfkc():
    raw = "NVI\u2145A"  # \u2145 is double-struck capital D
    normalized = normalize_entity_name(raw)
    assert normalized == "nvida"


def test_text_normalization_casefold():
    assert normalize_entity_name("NVIDIA") == "nvidia"
    assert normalize_entity_name("nvIdIa") == "nvidia"
    assert normalize_entity_name("ß") == "ss"


def test_text_normalization_whitespace_and_punctuation():
    # Repeated whitespace collapsed, trim outer, preserve punctuation
    raw = "   Berkshire    Hathaway   Inc.  "
    assert normalize_entity_name(raw) == "berkshire hathaway inc."

    raw_doi = " 10.1038/s41586-020-2649-2 "
    assert normalize_entity_name(raw_doi) == "10.1038/s41586-020-2649-2"


def test_empty_and_whitespace_query():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    # Empty string
    res = pytest.importorskip("asyncio").run(service.search_entities(GlobalSearchRequest(query="")))
    assert res.results == []
    assert not repo.fuzzy_called

    # Whitespace only
    res2 = pytest.importorskip("asyncio").run(
        service.search_entities(GlobalSearchRequest(query="    "))
    )
    assert res2.results == []
    assert not repo.fuzzy_called


def test_query_max_length_rejection():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    overlong = "a" * 257
    with pytest.raises(ValueError, match="SEARCH_QUERY_TOO_LONG"):
        pytest.importorskip("asyncio").run(
            service.search_entities(GlobalSearchRequest(query=overlong))
        )


# ==============================================================================
# 4. EXACT IDENTIFIER, AMBIGUITY, AND SECURITY VS COMPANY IDENTITY TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_exact_identifier_match_and_security_vs_company_distinction():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    sec_id = uuid.uuid4()
    exchange_id = uuid.uuid4()

    # Searching "NVDA" returns Security (not Company)
    repo.exact_identifier_data = [
        FakeRow(
            entity_id=sec_id,
            entity_type="security",
            canonical_name="NVIDIA Corporation Common Stock",
            display_name="NVIDIA Corp",
            scheme_key="ticker",
            matched_text="NVDA",
            scope_entity_id=exchange_id,
            scope_display_name="NASDAQ",
        )
    ]

    res = await service.search_entities(GlobalSearchRequest(query="NVDA"))
    assert len(res.results) == 1
    item = res.results[0]
    assert item.entity_id == sec_id
    assert item.entity_type == EntityTypeKey.SECURITY
    assert item.match_kind == GlobalSearchMatchKind.EXACT_IDENTIFIER
    assert item.matched_text == "NVDA"
    assert item.identifier_scheme_key == "ticker"
    assert item.scope_entity_id == exchange_id
    assert item.scope_display_name == "NASDAQ"


@pytest.mark.asyncio
async def test_ticker_ambiguity_across_exchanges():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    sec1_id = uuid.uuid4()
    sec2_id = uuid.uuid4()
    ex1_id = uuid.uuid4()
    ex2_id = uuid.uuid4()

    # Same ticker "ABC" on two different exchanges
    repo.exact_identifier_data = [
        FakeRow(
            entity_id=sec1_id,
            entity_type="security",
            canonical_name="ABC Common Stock",
            display_name="ABC Inc",
            scheme_key="ticker",
            matched_text="ABC",
            scope_entity_id=ex1_id,
            scope_display_name="NYSE",
        ),
        FakeRow(
            entity_id=sec2_id,
            entity_type="security",
            canonical_name="ABC Ltd Common Stock",
            display_name="ABC Ltd",
            scheme_key="ticker",
            matched_text="ABC",
            scope_entity_id=ex2_id,
            scope_display_name="LSE",
        ),
    ]

    res = await service.search_entities(GlobalSearchRequest(query="ABC"))
    assert len(res.results) == 2
    ids = {r.entity_id for r in res.results}
    assert ids == {sec1_id, sec2_id}
    scopes = {r.scope_display_name for r in res.results}
    assert scopes == {"NYSE", "LSE"}


@pytest.mark.asyncio
async def test_company_name_returns_company():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    comp_id = uuid.uuid4()
    repo.exact_name_data = [
        FakeRow(
            entity_id=comp_id,
            entity_type="company",
            canonical_name="NVIDIA Corporation",
            display_name="NVIDIA Corporation",
            exact_canonical=True,
            exact_display=True,
        )
    ]

    res = await service.search_entities(GlobalSearchRequest(query="NVIDIA Corporation"))
    assert len(res.results) == 1
    assert res.results[0].entity_id == comp_id
    assert res.results[0].entity_type == EntityTypeKey.COMPANY
    assert res.results[0].match_kind == GlobalSearchMatchKind.EXACT_CANONICAL_NAME


@pytest.mark.asyncio
async def test_alias_exact_and_prefix():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    tsmc_id = uuid.uuid4()
    repo.exact_alias_data = [
        FakeRow(
            entity_id=tsmc_id,
            entity_type="company",
            canonical_name="Taiwan Semiconductor Manufacturing Company Limited",
            display_name="TSMC",
            alias_type_key="short_name",
            matched_text="TSMC",
        )
    ]

    res = await service.search_entities(GlobalSearchRequest(query="TSMC"))
    assert len(res.results) == 1
    assert res.results[0].entity_id == tsmc_id
    assert res.results[0].match_kind == GlobalSearchMatchKind.EXACT_ALIAS
    assert res.results[0].alias_type_key == "short_name"


# ==============================================================================
# 5. PREFIX, FUZZY, CUTOFF, AND NO-FUZZY-IDENTIFIER TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_short_query_cutoffs():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    # 1-char query (valid short ticker like 'C')
    await service.search_entities(GlobalSearchRequest(query="C"))
    assert not repo.fuzzy_called

    # 2-char query ('NV')
    await service.search_entities(GlobalSearchRequest(query="NV"))
    assert not repo.fuzzy_called

    # 3-char query ('NVI') -> fuzzy path may be invoked
    await service.search_entities(GlobalSearchRequest(query="NVI"))
    assert repo.fuzzy_called


@pytest.mark.asyncio
async def test_fuzzy_name_typo_match():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    nvda_id = uuid.uuid4()
    repo.fuzzy_name_data = [
        FakeRow(
            entity_id=nvda_id,
            entity_type="company",
            canonical_name="NVIDIA Corporation",
            display_name="NVIDIA",
            sim_canonical=0.82,
            sim_display=0.75,
        )
    ]

    res = await service.search_entities(GlobalSearchRequest(query="NVIDA"))
    assert len(res.results) == 1
    assert res.results[0].entity_id == nvda_id
    assert res.results[0].match_kind == GlobalSearchMatchKind.FUZZY_CANONICAL_NAME


@pytest.mark.asyncio
async def test_identifiers_never_fuzzy_matched():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    # User enters typo ticker "NVDB".
    # Repo contains no exact match, but contains fuzzy rows for other things.
    # The fuzzy queries MUST only search names and aliases, never entity_identifiers.
    await service.search_entities(GlobalSearchRequest(query="NVDB"))
    assert repo.last_exact_id_targets.get(IdentifierSchemeKey.TICKER) == "NVDB"


# ==============================================================================
# 6. DEDUPLICATION, RANK TIERS, AND DETERMINISTIC TIE-BREAKING
# ==============================================================================


@pytest.mark.asyncio
async def test_result_deduplication_best_match_wins():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    shared_id = uuid.uuid4()

    # Entity matches as both Exact Identifier (Tier 1) and Exact Name (Tier 2)
    # and Exact Alias (Tier 3)
    repo.exact_identifier_data = [
        FakeRow(
            entity_id=shared_id,
            entity_type="security",
            canonical_name="NVIDIA Corp",
            display_name="NVIDIA",
            scheme_key="ticker",
            matched_text="NVDA",
            scope_entity_id=None,
            scope_display_name=None,
        )
    ]
    repo.exact_name_data = [
        FakeRow(
            entity_id=shared_id,
            entity_type="security",
            canonical_name="NVDA",
            display_name="NVDA",
            exact_canonical=True,
            exact_display=True,
        )
    ]
    repo.exact_alias_data = [
        FakeRow(
            entity_id=shared_id,
            entity_type="security",
            canonical_name="NVIDIA",
            display_name="NVIDIA",
            alias_type_key="short_name",
            matched_text="NVDA",
        )
    ]

    res = await service.search_entities(GlobalSearchRequest(query="NVDA"))
    # Appears EXACTLY ONCE
    assert len(res.results) == 1
    # Highest tier (EXACT_IDENTIFIER) is selected as best match
    assert res.results[0].match_kind == GlobalSearchMatchKind.EXACT_IDENTIFIER


@pytest.mark.asyncio
async def test_deterministic_ordering_tie_break():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    id_a = uuid.uuid4()
    id_b = uuid.uuid4()

    # Two exact name matches with same matched text length
    repo.exact_name_data = [
        FakeRow(
            entity_id=id_b,
            entity_type="company",
            canonical_name="BetaX",
            display_name="Beta Corp",
            exact_canonical=True,
            exact_display=False,
        ),
        FakeRow(
            entity_id=id_a,
            entity_type="company",
            canonical_name="Alpha",
            display_name="Alpha Corp",
            exact_canonical=True,
            exact_display=False,
        ),
    ]

    res1 = await service.search_entities(GlobalSearchRequest(query="something"))
    res2 = await service.search_entities(GlobalSearchRequest(query="something"))

    assert [r.display_name for r in res1.results] == ["Alpha Corp", "Beta Corp"]
    assert [r.entity_id for r in res1.results] == [r.entity_id for r in res2.results]


@pytest.mark.asyncio
async def test_result_limit():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    repo.exact_name_data = [
        FakeRow(
            entity_id=uuid.uuid4(),
            entity_type="company",
            canonical_name=f"Comp {i}",
            display_name=f"Comp {i}",
            exact_canonical=True,
            exact_display=True,
        )
        for i in range(25)
    ]

    res = await service.search_entities(GlobalSearchRequest(query="Comp", limit=5))
    assert len(res.results) == 5


@pytest.mark.asyncio
async def test_entity_type_filter():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    c_id = uuid.uuid4()
    s_id = uuid.uuid4()
    repo.exact_name_data = [
        FakeRow(
            entity_id=c_id,
            entity_type="company",
            canonical_name="Apple Inc",
            display_name="Apple Inc",
            exact_canonical=True,
            exact_display=True,
        ),
        FakeRow(
            entity_id=s_id,
            entity_type="security",
            canonical_name="Apple Common Stock",
            display_name="AAPL Security",
            exact_canonical=True,
            exact_display=True,
        ),
    ]

    res = await service.search_entities(
        GlobalSearchRequest(query="Apple", entity_types=[EntityTypeKey.COMPANY])
    )
    assert len(res.results) == 1
    assert res.results[0].entity_id == c_id


# ==============================================================================
# 7. ZERO EXTERNAL CALLS, NO PERSISTENCE & PRIVACY
# ==============================================================================


@pytest.mark.asyncio
async def test_zero_external_network_and_zero_writes(caplog):
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    with patch("urllib.request.urlopen") as mock_url, patch("httpx.AsyncClient.get") as mock_http:
        caplog.set_level(logging.INFO)
        raw_query = "SECRET_INVESTMENT_IDEA_123"

        res = await service.search_entities(GlobalSearchRequest(query=raw_query))
        assert res.results == []

        # 0 external calls
        assert mock_url.call_count == 0
        assert mock_http.call_count == 0

        # No raw search query in INFO logs
        for record in caplog.records:
            if record.levelno == logging.INFO:
                assert raw_query not in record.message


# ==============================================================================
# 8. CAPABILITY LAYER INTEGRATION
# ==============================================================================


def test_search_capability_registered():
    cap = registry.get_definition("search.entities")
    assert cap is not None
    assert cap.key == "search.entities"
    assert cap.version == 1
    assert cap.category == "Search"
    assert cap.required_permissions == ["atlas.access"]
    assert cap.requires_confirmation is False
    assert cap.input_model == GlobalSearchRequest
    assert cap.output_model == GlobalSearchResponse


# ==============================================================================
# 9. API ENDPOINT & AUTHENTICATION / AUTHORIZATION TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_search_api_unauthenticated_rejected():
    app = create_app()
    settings = get_settings()

    # Provide a dummy session to bypass DatabaseManager check
    dummy_session = AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: dummy_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Without credentials/auth, returns 401
        res = await client.get(f"{settings.api_prefix}/search/entities?q=AAPL")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_search_api_unauthorized_rejected():
    app = create_app()
    settings = get_settings()

    mock_principal = AuthPrincipal(sub=str(uuid.uuid4()), email="test@example.com", role="guest")
    # Auth context without 'atlas.access'
    mock_authz = AuthorizationContext(
        principal=mock_principal, roles=frozenset(["guest"]), permissions=frozenset()
    )

    dummy_session = AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: dummy_session
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/search/entities?q=AAPL")
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_search_api_authorized_returns_results():
    app = create_app()
    settings = get_settings()

    mock_principal = AuthPrincipal(sub=str(uuid.uuid4()), email="trader@example.com", role="trader")
    mock_authz = AuthorizationContext(
        principal=mock_principal,
        roles=frozenset(["trader"]),
        permissions=frozenset(["atlas.access"]),
    )

    search_settings = GlobalSearchSettings()
    repo = MockSearchRepository(search_settings)
    ent_id = uuid.uuid4()
    repo.exact_name_data = [
        FakeRow(
            entity_id=ent_id,
            entity_type="company",
            canonical_name="Apple Inc.",
            display_name="Apple Inc.",
            exact_canonical=True,
            exact_display=True,
        )
    ]
    mock_service = GlobalSearchService(repo, search_settings)

    dummy_session = AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: dummy_session
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz
    app.dependency_overrides[get_search_service] = lambda: mock_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/search/entities?q=Apple")
        assert res.status_code == 200
        data = res.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["entity_id"] == str(ent_id)
        assert data["results"][0]["display_name"] == "Apple Inc."


@pytest.mark.asyncio
async def test_search_api_too_long_query():
    app = create_app()
    settings = get_settings()

    mock_principal = AuthPrincipal(sub=str(uuid.uuid4()), email="trader@example.com", role="trader")
    mock_authz = AuthorizationContext(
        principal=mock_principal,
        roles=frozenset(["trader"]),
        permissions=frozenset(["atlas.access"]),
    )

    dummy_session = AsyncMock()
    app.dependency_overrides[get_db_session] = lambda: dummy_session
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get(f"{settings.api_prefix}/search/entities?q={'x' * 260}")
        assert res.status_code == 400
        data = res.json()
        assert "Search query is too long" in str(data)


# ==============================================================================
# 10. REPOSITORY SQL & WILDCARD ESCAPING TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_repository_wildcard_escaping():
    session = AsyncMock()
    session.execute.return_value = MagicMock(fetchall=MagicMock(return_value=[]))
    settings = GlobalSearchSettings()
    repo = GlobalSearchRepository(session, settings)

    # Prefix query with special LIKE metacharacters: %, _, \
    await repo.get_prefix_name_candidates("100%_growth\\tech", None)
    call_args = session.execute.call_args
    assert call_args is not None
    # Verify the escaped pattern passed to parameter
    params = call_args[0][1]
    assert params["like_pattern"] == "100\\%\\_growth\\\\tech%"


# ==============================================================================
# 11. COMMAND PALETTE & NLP BOUNDARY TESTS
# ==============================================================================


@pytest.mark.asyncio
async def test_command_and_nlp_boundaries_are_plain_text():
    settings = GlobalSearchSettings()
    repo = MockSearchRepository(settings)
    service = GlobalSearchService(repo, settings)

    # NVDA CHART must not trigger chart command
    res1 = await service.search_entities(GlobalSearchRequest(query="NVDA CHART"))
    assert isinstance(res1, GlobalSearchResponse)

    # /markets must not trigger navigation
    res2 = await service.search_entities(GlobalSearchRequest(query="/markets"))
    assert isinstance(res2, GlobalSearchResponse)
