import pytest
from pydantic import ValidationError, SecretStr
from atlas.infrastructure.clickhouse import (
    ClickHouseSettings,
    ClickHouseClientFactory,
    ClickHouseHealthService,
    ClickHouseConfigurationError,
)


def test_clickhouse_settings_disabled_by_default():
    settings = ClickHouseSettings()
    assert settings.enabled is False
    assert settings.host == "127.0.0.1"


def test_clickhouse_settings_valid():
    settings = ClickHouseSettings(
        enabled=True,
        password=SecretStr("supersecret")
    )
    assert settings.enabled is True
    assert settings.password.get_secret_value() == "supersecret"


def test_clickhouse_settings_invalid_port():
    with pytest.raises(ValidationError):
        ClickHouseSettings(port=-1)

    with pytest.raises(ValidationError):
        ClickHouseSettings(port=70000)


def test_clickhouse_settings_invalid_database():
    with pytest.raises(ValidationError):
        ClickHouseSettings(database="invalid name!")

    with pytest.raises(ValidationError):
        ClickHouseSettings(database="123database")


def test_clickhouse_settings_secret_redaction():
    settings = ClickHouseSettings(password=SecretStr("secret_password"))
    repr_str = repr(settings)
    str_str = str(settings)
    assert "secret_password" not in repr_str
    assert "secret_password" not in str_str


def test_client_factory_no_import_time_connection():
    # Importing and instantiating factory should not connect
    settings = ClickHouseSettings(enabled=True, password=SecretStr("test"))
    factory = ClickHouseClientFactory(settings)
    assert factory._client is None


def test_client_factory_disabled_no_network():
    settings = ClickHouseSettings(enabled=False)
    factory = ClickHouseClientFactory(settings)
    client = factory.get_client()
    assert client is None


def test_client_factory_missing_password_error():
    settings = ClickHouseSettings(enabled=True)
    factory = ClickHouseClientFactory(settings)
    with pytest.raises(ClickHouseConfigurationError):
        factory.get_client()


def test_health_service_disabled():
    settings = ClickHouseSettings(enabled=False)
    factory = ClickHouseClientFactory(settings)
    health = ClickHouseHealthService(factory)
    
    status = health.check_health()
    assert status.status == "disabled"
