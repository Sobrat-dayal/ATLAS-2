from atlas.search.enums import GlobalSearchMatchKind
from atlas.search.models import GlobalSearchRequest
from atlas.search.settings import GlobalSearchSettings
from atlas.entities.types import EntityTypeKey

def test_global_search_settings():
    settings = GlobalSearchSettings()
    assert settings.default_limit == 20
    assert settings.fuzzy_min_characters == 3

def test_global_search_request():
    req = GlobalSearchRequest(query="AAPL")
    assert req.query == "AAPL"
    assert req.limit is None

def test_global_search_enums():
    assert GlobalSearchMatchKind.EXACT_CANONICAL_NAME.value == "EXACT_CANONICAL_NAME"
