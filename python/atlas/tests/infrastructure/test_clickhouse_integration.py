import pytest
from pydantic import SecretStr
from atlas.infrastructure.clickhouse import (
    ClickHouseSettings,
    ClickHouseClientFactory,
    ClickHouseHealthService,
    ClickHouseAuthenticationError,
)

pytestmark = pytest.mark.integration

@pytest.fixture
def clickhouse_settings():
    return ClickHouseSettings(
        enabled=True,
        host="127.0.0.1",
        port=8123,
        database="atlas",
        username="atlas_app",
        password=SecretStr("test_clickhouse_password") # We will use this password in dev
    )

@pytest.fixture
def clickhouse_factory(clickhouse_settings):
    factory = ClickHouseClientFactory(clickhouse_settings)
    yield factory
    factory.close()

def test_integration_clickhouse_connection(clickhouse_factory):
    """Test actual connection to ClickHouse (SELECT 1)."""
    client = clickhouse_factory.get_client()
    assert client is not None
    result = client.command("SELECT 1")
    assert result == 1

def test_integration_clickhouse_database(clickhouse_factory, clickhouse_settings):
    """Test configured database is correct."""
    client = clickhouse_factory.get_client()
    result = client.command("SELECT currentDatabase()")
    assert result == clickhouse_settings.database

def test_integration_clickhouse_application_user(clickhouse_factory, clickhouse_settings):
    """Test connection is using the expected application user, not default."""
    client = clickhouse_factory.get_client()
    result = client.command("SELECT currentUser()")
    assert result == clickhouse_settings.username
    assert result != "default"

def test_integration_clickhouse_wrong_password(clickhouse_settings):
    """Test wrong password raises Authentication Error."""
    wrong_settings = clickhouse_settings.model_copy(update={"password": SecretStr("wrong")})
    factory = ClickHouseClientFactory(wrong_settings)
    with pytest.raises(ClickHouseAuthenticationError):
        factory.get_client()

def test_integration_clickhouse_utc_timezone(clickhouse_factory):
    """Test server/session timezone is UTC."""
    client = clickhouse_factory.get_client()
    result = client.command("SELECT timezone()")
    assert result == "UTC"

def test_integration_clickhouse_health_service(clickhouse_factory):
    """Test real health check against ClickHouse."""
    health_service = ClickHouseHealthService(clickhouse_factory)
    status = health_service.check_health()
    assert status.status == "available"
    assert status.database == "atlas"
    assert status.server_version is not None

def test_integration_no_business_tables(clickhouse_factory, clickhouse_settings):
    """Verify that Stage 37 did not create any Market Data business tables."""
    client = clickhouse_factory.get_client()
    tables = client.command("SHOW TABLES")
    
    # We may get a single string or a list/tuple depending on driver behavior,
    # let's normalize to a list of lowercased strings.
    if isinstance(tables, str):
        tables = [t.strip().lower() for t in tables.split("\n") if t.strip()]
    elif hasattr(tables, '__iter__'):
        tables = [str(t).lower() for t in tables]
    else:
        tables = []
        
    forbidden_tables = [
        "quotes", "trades", "ohlcv", "bars", "order_books", "market_snapshots",
        "economic_observations", "news_articles", "research_results",
        "users", "entities", "identifiers", "provider_credentials"
    ]
    
    for forbidden in forbidden_tables:
        assert forbidden not in tables, f"Table {forbidden} should not exist in Stage 37!"
