import pytest
from pydantic import ValidationError, SecretStr
from atlas.infrastructure.valkey import (
    ValkeySettings,
    ValkeyClientFactory,
    ValkeyHealthService,
    ValkeyConfigurationError,
)

pytestmark = pytest.mark.asyncio

def test_valkey_settings_disabled_by_default():
    settings = ValkeySettings()
    assert settings.enabled is False
    assert settings.host == "127.0.0.1"


def test_valkey_settings_valid():
    settings = ValkeySettings(
        enabled=True,
        password=SecretStr("supersecret")
    )
    assert settings.enabled is True
    assert settings.password.get_secret_value() == "supersecret"


def test_valkey_settings_invalid_port():
    with pytest.raises(ValidationError):
        ValkeySettings(port=-1)

    with pytest.raises(ValidationError):
        ValkeySettings(port=70000)


def test_valkey_settings_enforces_db_0():
    with pytest.raises(ValidationError):
        ValkeySettings(database=1)

def test_valkey_settings_invalid_prefix():
    with pytest.raises(ValidationError):
        ValkeySettings(key_prefix="invalid name!")

    with pytest.raises(ValidationError):
        ValkeySettings(key_prefix="missing_colon")


def test_valkey_settings_secret_redaction():
    settings = ValkeySettings(password=SecretStr("secret_password"))
    repr_str = repr(settings)
    str_str = str(settings)
    assert "secret_password" not in repr_str
    assert "secret_password" not in str_str


def test_client_factory_no_import_time_connection():
    settings = ValkeySettings(enabled=True, password=SecretStr("test"))
    factory = ValkeyClientFactory(settings)
    assert factory._client is None
    assert factory._pool is None


def test_client_factory_disabled_no_network():
    settings = ValkeySettings(enabled=False)
    factory = ValkeyClientFactory(settings)
    client = factory.get_client()
    assert client is None


def test_client_factory_missing_password_error():
    settings = ValkeySettings(enabled=True)
    factory = ValkeyClientFactory(settings)
    with pytest.raises(ValkeyConfigurationError):
        factory.get_client()


async def test_health_service_disabled():
    settings = ValkeySettings(enabled=False)
    factory = ValkeyClientFactory(settings)
    health = ValkeyHealthService(factory)
    
    status = await health.check_health()
    assert status.status == "disabled"
