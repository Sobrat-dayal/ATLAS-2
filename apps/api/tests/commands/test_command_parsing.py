import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.commands.enums import (
    AtlasCommandErrorCode,
    AtlasCommandParseStatus,
    AtlasCommandSourceKind,
)
from atlas.commands.errors import AtlasCommandLexerError, AtlasCommandParserError
from atlas.commands.lexer import AtlasCommandLexer
from atlas.commands.parser import AtlasCommandParser
from atlas.commands.service import AtlasCommandParsingService
from atlas.commands.specs import (
    CANONICAL_MODULE_SPECS,
    AtlasCommandModuleSpec,
    AtlasCommandSpecRegistry,
)
from atlas.resolution.schemas import EntityResolutionResponse, ResolutionCandidate
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session


# -----------------------------------------------------------------------------
# 1. Lexer Tests
# -----------------------------------------------------------------------------
class TestAtlasCommandLexer:
    def setup_method(self):
        self.lexer = AtlasCommandLexer()

    def test_tokenize_basic_slash_command(self):
        tokens = self.lexer.tokenize("/markets")
        # Slash, word(markets), EOF
        assert len(tokens) == 3
        assert tokens[0].value == "/"
        assert tokens[1].value == "markets"

    def test_tokenize_slash_with_target(self):
        tokens = self.lexer.tokenize("/charts NVDA")
        assert len(tokens) == 4
        assert tokens[0].value == "/"
        assert tokens[1].value == "charts"
        assert tokens[2].value == "NVDA"

    def test_tokenize_quoted_string_double_and_single(self):
        tokens1 = self.lexer.tokenize('/research "NVIDIA Corporation"')
        assert len(tokens1) == 4
        assert tokens1[2].value == "NVIDIA Corporation"

        tokens2 = self.lexer.tokenize("/companies 'Apple Inc'")
        assert len(tokens2) == 4
        assert tokens2[2].value == "Apple Inc"

    def test_tokenize_escaped_quotes(self):
        tokens = self.lexer.tokenize(r'/news "NVIDIA \"Special\" Corp"')
        assert len(tokens) == 4
        assert tokens[2].value == 'NVIDIA "Special" Corp'

    def test_unterminated_quote_raises(self):
        with pytest.raises(AtlasCommandLexerError) as exc_info:
            self.lexer.tokenize('/companies "Unterminated string')
        assert exc_info.value.error_code == AtlasCommandErrorCode.UNTERMINATED_QUOTE

    def test_control_characters_rejected(self):
        with pytest.raises(AtlasCommandLexerError) as exc_info:
            self.lexer.tokenize("/charts NVDA\x00malicious")
        assert exc_info.value.error_code == AtlasCommandErrorCode.CONTROL_CHARACTERS

        with pytest.raises(AtlasCommandLexerError) as exc_info:
            self.lexer.tokenize("/charts NVDA\x1bmalicious")
        assert exc_info.value.error_code == AtlasCommandErrorCode.CONTROL_CHARACTERS

    def test_max_command_length_enforced(self):
        long_command = "/charts " + ("A" * 510)
        with pytest.raises(AtlasCommandLexerError) as exc_info:
            self.lexer.tokenize(long_command)
        assert exc_info.value.error_code == AtlasCommandErrorCode.COMMAND_TOO_LONG

    def test_max_token_length_enforced(self):
        long_token = "/charts " + ("A" * 260)
        # Length under 512, but token length > 256
        with pytest.raises(AtlasCommandLexerError) as exc_info:
            self.lexer.tokenize(long_token)
        assert exc_info.value.error_code == AtlasCommandErrorCode.TOKEN_TOO_LONG

    def test_max_tokens_enforced(self):
        many_tokens = "/charts " + " ".join([f"t{i}" for i in range(35)])
        with pytest.raises(AtlasCommandLexerError) as exc_info:
            self.lexer.tokenize(many_tokens)
        assert exc_info.value.error_code == AtlasCommandErrorCode.TOO_MANY_TOKENS

    @pytest.mark.parametrize(
        "forbidden_op",
        ["|", "||", "&", "&&", ";", ">", ">>", "<", "<<", "`", "$()", "${}"],
    )
    def test_forbidden_shell_syntax_rejected(self, forbidden_op):
        bad_input = f"/charts NVDA {forbidden_op} echo hello"
        with pytest.raises(AtlasCommandLexerError) as exc_info:
            self.lexer.tokenize(bad_input)
        assert exc_info.value.error_code == AtlasCommandErrorCode.FORBIDDEN_SYNTAX


# -----------------------------------------------------------------------------
# 2. Syntactic Parser Tests
# -----------------------------------------------------------------------------
class TestAtlasCommandParser:
    def setup_method(self):
        self.lexer = AtlasCommandLexer()
        self.parser = AtlasCommandParser()

    def parse_str(self, text: str):
        tokens = self.lexer.tokenize(text)
        return self.parser.parse(tokens, text)

    def test_parse_all_20_canonical_modules(self):
        modules = [
            "home",
            "markets",
            "charts",
            "watchlists",
            "screeners",
            "companies",
            "economics",
            "news",
            "research",
            "maps",
            "intelligence",
            "options",
            "trading",
            "portfolios",
            "risk",
            "ai",
            "data",
            "saved",
            "workspaces",
            "agents",
        ]
        for mod in modules:
            ast = self.parse_str(f"/{mod}")
            assert ast.source_kind == AtlasCommandSourceKind.SLASH
            assert ast.command_name == mod
            assert ast.target is None

    def test_parse_module_aliases(self):
        aliases = [
            ("market", "market"),
            ("mkt", "mkt"),
            ("chart", "chart"),
            ("ch", "ch"),
            ("company", "company"),
            ("econ", "econ"),
            ("macro", "macro"),
            ("nw", "nw"),
            ("rsch", "rsch"),
            ("map", "map"),
            ("intel", "intel"),
            ("opt", "opt"),
            ("trade", "trade"),
            ("port", "port"),
            ("assistant", "assistant"),
            ("workspace", "workspace"),
            ("agent", "agent"),
        ]
        for alias, expected in aliases:
            ast = self.parse_str(f"/{alias}")
            assert ast.command_name == expected

    def test_parse_slash_with_default_action_and_explicit_action(self):
        ast1 = self.parse_str("/charts NVDA")
        assert ast1.command_name == "charts"
        assert ast1.target == "NVDA"

        ast2 = self.parse_str("/charts open NVDA")
        assert ast2.command_name == "charts"
        assert ast2.action == "open"
        assert ast2.target == "NVDA"

    def test_parse_utilities(self):
        ast_settings = self.parse_str("/settings")
        assert ast_settings.command_name == "settings"

        ast_search = self.parse_str("/search")
        assert ast_search.command_name == "search"

        ast_clear = self.parse_str("/clear entity")
        assert ast_clear.command_name == "clear_entity"
        assert ast_clear.action == "clear"

    def test_parse_shorthand_syntax(self):
        ast_chart = self.parse_str("NVDA CHART")
        assert ast_chart.source_kind == AtlasCommandSourceKind.SHORTHAND
        assert ast_chart.target == "NVDA"
        assert ast_chart.action == "open"

        ast_news = self.parse_str("NVDA NEWS")
        assert ast_news.target == "NVDA"

        ast_res = self.parse_str("NVDA RESEARCH")
        assert ast_res.target == "NVDA"

        ast_map = self.parse_str("MAP TSMC")
        assert ast_map.target == "TSMC"

        ast_opt = self.parse_str("OPTIONS NVDA")
        assert ast_opt.target == "NVDA"

        ast_quoted = self.parse_str('"NVIDIA Corporation" NEWS')
        assert ast_quoted.target == "NVIDIA Corporation"

        ast_fa = self.parse_str("NVDA FA")
        assert ast_fa.action == "fundamentals"

        ast_port = self.parse_str("PORT RISK")
        assert ast_port.action == "analyze"

        ast_buy = self.parse_str("BUY NVDA")
        assert ast_buy.action == "buy"

        ast_sell = self.parse_str("SELL NVDA")
        assert ast_sell.action == "sell"

    def test_parse_parameters(self):
        ast = self.parse_str("/charts NVDA --timeframe 1D")
        assert ast.parameters == {"timeframe": "1D"}

        ast_eq = self.parse_str("/charts NVDA --timeframe=1D")
        assert ast_eq.parameters == {"timeframe": "1D"}

    def test_duplicate_parameter_raises(self):
        with pytest.raises(AtlasCommandParserError) as exc_info:
            self.parse_str("/charts NVDA --timeframe 1D --timeframe 1W")
        assert exc_info.value.error_code == AtlasCommandErrorCode.DUPLICATE_PARAMETER

    def test_empty_or_natural_language_not_structured(self):
        with pytest.raises(AtlasCommandParserError) as exc_info:
            self.parse_str("show me Nvidia chart")
        assert exc_info.value.error_code == AtlasCommandErrorCode.NOT_STRUCTURED_COMMAND

        with pytest.raises(AtlasCommandParserError) as exc_info:
            self.parse_str("what happened to Apple")
        assert exc_info.value.error_code == AtlasCommandErrorCode.NOT_STRUCTURED_COMMAND

        with pytest.raises(AtlasCommandParserError) as exc_info:
            self.parse_str("find me stocks")
        assert exc_info.value.error_code == AtlasCommandErrorCode.NOT_STRUCTURED_COMMAND


# -----------------------------------------------------------------------------
# 3. Spec Registry & Collision Tests
# -----------------------------------------------------------------------------
class TestSpecRegistry:
    def test_registry_has_no_alias_collisions(self):
        reg = AtlasCommandSpecRegistry()
        assert len(reg.modules_by_id) == 20
        assert len(reg.utilities_by_id) == 3

    def test_duplicate_alias_triggers_value_error(self):
        dup_mod = AtlasCommandModuleSpec(
            module_id="dup_test",
            canonical_slash_name="dup_test",
            command_id="test.dup",
            entity_command_id=None,
            route="/dup_test",
            required_permission="test.dup",
            aliases=["markets"],  # collision with canonical "markets"
        )
        with pytest.raises(ValueError, match="Collision detected"):
            AtlasCommandSpecRegistry(module_specs=[*CANONICAL_MODULE_SPECS, dup_mod])


# -----------------------------------------------------------------------------
# 4. Service & Target Resolution Tests (Async Mocking)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
class TestAtlasCommandParsingService:
    def setup_method(self):
        self.mock_session = AsyncMock()
        self.service = AtlasCommandParsingService(self.mock_session)

    async def test_parse_module_navigation_ready(self):
        res = await self.service.parse_command("/markets")
        assert res.status == AtlasCommandParseStatus.READY
        assert res.command_id == "navigation.markets"
        assert res.module == "markets"
        assert res.execution_summary == "Navigate to Markets"

    async def test_parse_utility_settings_ready(self):
        res = await self.service.parse_command("/settings")
        assert res.status == AtlasCommandParseStatus.READY
        assert res.command_id == "settings.global.open"
        assert res.execution_summary == "Open Global Settings"

    async def test_parse_utility_search_ready(self):
        res = await self.service.parse_command("/search")
        assert res.status == AtlasCommandParseStatus.READY
        assert res.command_id == "search.focus"

    async def test_parse_utility_clear_entity_ready(self):
        res = await self.service.parse_command("/clear entity")
        assert res.status == AtlasCommandParseStatus.READY
        assert res.command_id == "entity.selection.clear"

    async def test_parse_incomplete_action_missing_target(self):
        res = await self.service.parse_command("/charts open")
        assert res.status == AtlasCommandParseStatus.INCOMPLETE
        assert res.error_code == AtlasCommandErrorCode.MISSING_TARGET

    async def test_parse_unknown_action(self):
        res = await self.service.parse_command("/charts delete NVDA")
        assert res.status == AtlasCommandParseStatus.INVALID
        assert res.error_code == AtlasCommandErrorCode.UNKNOWN_ACTION

    async def test_parse_unknown_module(self):
        res = await self.service.parse_command("/foo NVDA")
        assert res.status == AtlasCommandParseStatus.INVALID
        assert res.error_code == AtlasCommandErrorCode.UNKNOWN_MODULE

    async def test_target_resolution_unique_security_ready(self):
        security_id = uuid.uuid4()
        candidate = ResolutionCandidate(
            entity_id=security_id,
            entity_type="security",
            canonical_name="NVIDIA Corp Ordinary Shares",
            display_name="NVIDIA Corp",
            match_kind="unscoped_ticker",
            matched_value="NVDA",
        )

        mock_resolution = EntityResolutionResponse(
            status="resolved",
            query="NVDA",
            resolved_entity_id=security_id,
            candidates=[candidate],
        )

        self.service.resolver.resolution_service.resolve_entity = AsyncMock(
            return_value=mock_resolution
        )

        res = await self.service.parse_command("NVDA CHART")
        assert res.status == AtlasCommandParseStatus.READY
        assert res.command_id == "navigation.charts.entity"
        assert res.resolved_target is not None
        assert res.resolved_target.entity_id == security_id
        assert res.arguments == {"entityId": str(security_id)}
        assert "NVIDIA Corp → Charts" in (res.execution_summary or "")

    async def test_target_resolution_target_not_found(self):
        mock_resolution = EntityResolutionResponse(
            status="not_found",
            query="NVIDA",
            candidates=[],
        )
        self.service.resolver.resolution_service.resolve_entity = AsyncMock(
            return_value=mock_resolution
        )

        # Misspelled entity is NOT fuzzy corrected
        res = await self.service.parse_command("NVIDA CHART")
        assert res.status == AtlasCommandParseStatus.INVALID
        assert res.error_code == AtlasCommandErrorCode.TARGET_NOT_FOUND

    async def test_target_resolution_ambiguous(self):
        cand1 = ResolutionCandidate(
            entity_id=uuid.uuid4(),
            entity_type="security",
            canonical_name="ABC US",
            display_name="ABC Holdings",
            match_kind="unscoped_ticker",
            matched_value="ABC",
        )
        cand2 = ResolutionCandidate(
            entity_id=uuid.uuid4(),
            entity_type="security",
            canonical_name="ABC LN",
            display_name="ABC London",
            match_kind="unscoped_ticker",
            matched_value="ABC",
        )
        mock_resolution = EntityResolutionResponse(
            status="ambiguous",
            query="ABC",
            candidates=[cand1, cand2],
        )
        self.service.resolver.resolution_service.resolve_entity = AsyncMock(
            return_value=mock_resolution
        )

        res = await self.service.parse_command("ABC CHART")
        assert res.status == AtlasCommandParseStatus.AMBIGUOUS
        assert res.error_code == AtlasCommandErrorCode.TARGET_AMBIGUOUS
        assert len(res.ambiguity_candidates or []) == 2

    async def test_target_type_mismatch_security_for_company(self):
        cand = ResolutionCandidate(
            entity_id=uuid.uuid4(),
            entity_type="security",
            canonical_name="NVIDIA Security",
            display_name="NVDA",
            match_kind="unscoped_ticker",
            matched_value="NVDA",
        )
        mock_resolution = EntityResolutionResponse(
            status="resolved",
            query="NVDA",
            candidates=[cand],
        )
        self.service.resolver.resolution_service.resolve_entity = AsyncMock(
            return_value=mock_resolution
        )

        res = await self.service.parse_command("/companies NVDA")
        assert res.status == AtlasCommandParseStatus.INVALID
        assert res.error_code == AtlasCommandErrorCode.TARGET_TYPE_MISMATCH

    async def test_company_resolution_succeeds_for_company_target(self):
        company_id = uuid.uuid4()
        cand = ResolutionCandidate(
            entity_id=company_id,
            entity_type="company",
            canonical_name="NVIDIA Corporation",
            display_name="NVIDIA Corporation",
            match_kind="canonical_name",
            matched_value="NVIDIA Corporation",
        )
        mock_resolution = EntityResolutionResponse(
            status="resolved",
            query="NVIDIA Corporation",
            candidates=[cand],
        )
        self.service.resolver.resolution_service.resolve_entity = AsyncMock(
            return_value=mock_resolution
        )

        res = await self.service.parse_command('/companies "NVIDIA Corporation"')
        assert res.status == AtlasCommandParseStatus.READY
        assert res.command_id == "navigation.companies.entity"
        assert res.resolved_target.entity_id == company_id

    async def test_reserved_unavailable_shorthand(self):
        res_fa = await self.service.parse_command("NVDA FA")
        assert res_fa.status == AtlasCommandParseStatus.UNAVAILABLE
        assert res_fa.error_code == AtlasCommandErrorCode.COMMAND_UNAVAILABLE
        assert "Fundamental analysis is not available" in (res_fa.error_message or "")

        res_risk = await self.service.parse_command("PORT RISK")
        assert res_risk.status == AtlasCommandParseStatus.UNAVAILABLE
        assert res_risk.error_code == AtlasCommandErrorCode.COMMAND_UNAVAILABLE

    async def test_forbidden_buy_sell_commands(self):
        res_buy = await self.service.parse_command("BUY NVDA")
        assert res_buy.status == AtlasCommandParseStatus.UNAVAILABLE
        assert "Trading execution and order placement are not supported" in (
            res_buy.error_message or ""
        )

        res_sell = await self.service.parse_command("SELL AAPL")
        assert res_sell.status == AtlasCommandParseStatus.UNAVAILABLE

    async def test_module_authorization_enforced(self):
        authz_context = MagicMock(spec=AuthorizationContext)
        authz_context.has_permission = MagicMock(return_value=False)

        res = await self.service.parse_command("/markets", authz_context=authz_context)
        assert res.status == AtlasCommandParseStatus.INVALID
        assert res.error_code == AtlasCommandErrorCode.COMMAND_FORBIDDEN


# -----------------------------------------------------------------------------
# 5. FastAPI Endpoint Integration Tests
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
class TestFastApiCommandsEndpoint:
    async def test_parse_endpoint_success(self):
        app = create_app()

        fake_user = AuthPrincipal(
            sub=str(uuid.uuid4()),
            email="test@atlas.local",
        )

        mock_authz = AuthorizationContext(
            principal=fake_user,
            roles=frozenset(["trader"]),
            permissions=frozenset(["atlas.access", "module.markets.view"]),
        )

        dummy_session = AsyncMock()

        app.dependency_overrides[get_db_session] = lambda: dummy_session
        app.dependency_overrides[get_current_user] = lambda: fake_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_authz

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/commands/parse",
                json={"text": "/markets"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "READY"
            assert data["command_id"] == "navigation.markets"
            assert data["command_language_version"] == 1

    async def test_parse_endpoint_unauthorized_without_auth(self):
        app = create_app()
        dummy_session = AsyncMock()
        app.dependency_overrides[get_db_session] = lambda: dummy_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/commands/parse",
                json={"text": "/markets"},
            )
            assert resp.status_code == 401
