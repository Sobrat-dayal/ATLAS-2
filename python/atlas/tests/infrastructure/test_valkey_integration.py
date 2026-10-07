import pytest
import pytest_asyncio
import valkey.asyncio as valkey
from valkey.exceptions import ResponseError, AuthenticationError
from pydantic import SecretStr
from atlas.infrastructure.valkey import (
    ValkeySettings,
    ValkeyClientFactory,
    ValkeyHealthService,
    ValkeyAuthenticationError,
)

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

@pytest.fixture
def valkey_settings():
    return ValkeySettings(
        enabled=True,
        host="127.0.0.1",
        port=6379,
        database=0,
        username="atlas_app",
        password=SecretStr("test_valkey_password") # Used in dev config
    )

@pytest_asyncio.fixture
async def valkey_factory(valkey_settings):
    factory = ValkeyClientFactory(valkey_settings)
    yield factory
    await factory.close()

async def test_integration_valkey_connection_and_ping(valkey_factory):
    """Test actual connection to Valkey (PING)."""
    client = valkey_factory.get_client()
    assert client is not None
    result = await client.ping()
    assert result is True

async def test_integration_valkey_wrong_password(valkey_settings):
    """Test wrong password raises Authentication Error."""
    wrong_settings = valkey_settings.model_copy(update={"password": SecretStr("wrong")})
    factory = ValkeyClientFactory(wrong_settings)
    
    with pytest.raises(ValkeyAuthenticationError):
        await factory.execute_safe_health_ping()
        
    await factory.close()

async def test_integration_valkey_namespace_key(valkey_factory):
    """Test SET/GET/TTL/UNLINK on a namespaced smoke key."""
    client = valkey_factory.get_client()
    key = "atlas:test:stage38:smoke"
    
    # Clean up first if needed
    await client.unlink(key)
    
    # SET with EX 30
    await client.set(key, "ok", ex=30)
    
    # GET
    val = await client.get(key)
    assert val == b"ok"  # No decode_responses by default
    
    # TTL
    ttl = await client.ttl(key)
    assert 0 < ttl <= 30
    
    # UNLINK
    await client.unlink(key)
    val = await client.get(key)
    assert val is None

async def test_integration_valkey_forbidden_admin_commands(valkey_factory):
    """Test that application user is denied dangerous commands."""
    client = valkey_factory.get_client()
    
    dangerous_commands = [
        ("FLUSHALL",),
        ("FLUSHDB",),
        ("CONFIG", "GET", "*"),
        ("ACL", "LIST"),
        ("MODULE", "LIST"),
    ]
    
    for cmd in dangerous_commands:
        with pytest.raises(ResponseError) as exc_info:
            await client.execute_command(*cmd)
        # NOPERM or equivalent expected
        assert "NOPERM" in str(exc_info.value) or "No permissions" in str(exc_info.value)

async def test_integration_valkey_namespace_acl(valkey_factory):
    """Test that application user cannot write outside atlas:* namespace."""
    client = valkey_factory.get_client()
    
    with pytest.raises(ResponseError) as exc_info:
        await client.set("outside:test", "value")
    
    assert "NOPERM" in str(exc_info.value) or "No permissions" in str(exc_info.value)

async def test_integration_valkey_health_service(valkey_factory):
    """Test real health check against Valkey."""
    health_service = ValkeyHealthService(valkey_factory)
    status = await health_service.check_health()
    assert status.status == "available"
    assert status.database == 0
    assert status.server_version is not None
    assert status.latency_ms is not None

async def test_integration_no_business_keys_remain(valkey_factory):
    """Verify no production-style ATLAS keys exist."""
    client = valkey_factory.get_client()
    
    # SCAN using pattern '*' is safe enough for tests, though application shouldn't use KEYS.
    cursor = b'0'
    keys_found = []
    while cursor:
        cursor, keys = await client.scan(cursor=cursor, match="*")
        keys_found.extend(keys)
        if cursor == 0 or cursor == b'0':
            break
            
    # There should be no keys, or at most a few from other concurrent tests (all test namespaces)
    for key in keys_found:
        decoded_key = key.decode("utf-8")
        assert decoded_key.startswith("atlas:test:"), f"Found non-test key in Valkey: {decoded_key}"
