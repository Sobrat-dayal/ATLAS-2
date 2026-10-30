"""View Configuration Validation, Versioning, Sanitization, and Migration for Stage 119."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, List, Tuple

from atlas.saved.enums import ViewConfigurationType
from atlas.saved.errors import (
    SavedConfigurationInvalidError,
    SavedConfigurationMigrationFailedError,
    SavedConfigurationTooLargeError,
    SavedConfigurationUnsupportedVersionError,
)

logger = logging.getLogger(__name__)

MAX_CONFIGURATION_PAYLOAD_BYTES = 262144  # 256 KB
SUPPORTED_SCHEMA_VERSIONS: Dict[ViewConfigurationType, List[int]] = {
    ViewConfigurationType.CHART: [1, 2],
    ViewConfigurationType.SCREENER: [1, 2],
    ViewConfigurationType.ECONOMICS: [1],
    ViewConfigurationType.PORTFOLIO: [1],
    ViewConfigurationType.RISK: [1],
    ViewConfigurationType.MAP: [1],
    ViewConfigurationType.DATA_QUERY: [1],
}

LATEST_SCHEMA_VERSIONS: Dict[ViewConfigurationType, int] = {
    ViewConfigurationType.CHART: 2,
    ViewConfigurationType.SCREENER: 2,
    ViewConfigurationType.ECONOMICS: 1,
    ViewConfigurationType.PORTFOLIO: 1,
    ViewConfigurationType.RISK: 1,
    ViewConfigurationType.MAP: 1,
    ViewConfigurationType.DATA_QUERY: 1,
}

SENSITIVE_KEY_SUBSTRINGS = (
    "secret",
    "token",
    "password",
    "api_key",
    "apikey",
    "auth",
    "bearer",
    "credential",
    "private_key",
)


def compute_payload_hash(payload: Dict[str, Any]) -> str:
    """Computes deterministic SHA-256 hash of normalized JSON payload."""
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def redact_sensitive_values(data: Any) -> Any:
    """Recursively redacts secrets, tokens, credentials, and API keys."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            key_lower = str(k).lower()
            if any(s in key_lower for s in SENSITIVE_KEY_SUBSTRINGS):
                sanitized[k] = "[REDACTED_SECRET]"
            else:
                sanitized[k] = redact_sensitive_values(v)
        return sanitized
    elif isinstance(data, list):
        return [redact_sensitive_values(item) for item in data]
    return data


def validate_and_sanitize_configuration_payload(
    config_type: ViewConfigurationType,
    schema_version: int,
    payload: Dict[str, Any],
) -> Tuple[Dict[str, Any], str]:
    """
    Validates configuration payload against schema rules, redacts secrets,
    and returns (sanitized_payload, payload_hash).
    """
    if not isinstance(payload, dict):
        raise SavedConfigurationInvalidError(
            "Configuration payload must be a JSON object dictionary."
        )

    # Size check
    raw_bytes = len(json.dumps(payload).encode("utf-8"))
    if raw_bytes > MAX_CONFIGURATION_PAYLOAD_BYTES:
        raise SavedConfigurationTooLargeError(raw_bytes, MAX_CONFIGURATION_PAYLOAD_BYTES)

    # Version check
    supported = SUPPORTED_SCHEMA_VERSIONS.get(config_type, [1])
    if schema_version not in supported:
        raise SavedConfigurationUnsupportedVersionError(schema_version, supported)

    # Sanitize secrets
    sanitized = redact_sensitive_values(payload)

    # Type-specific validation
    if config_type == ViewConfigurationType.CHART:
        _validate_chart_config(sanitized, schema_version)
    elif config_type == ViewConfigurationType.SCREENER:
        _validate_screener_config(sanitized, schema_version)
    elif config_type == ViewConfigurationType.ECONOMICS:
        _validate_economics_config(sanitized, schema_version)
    elif config_type == ViewConfigurationType.PORTFOLIO:
        _validate_portfolio_config(sanitized, schema_version)
    elif config_type == ViewConfigurationType.RISK:
        _validate_risk_config(sanitized, schema_version)
    elif config_type == ViewConfigurationType.MAP:
        _validate_map_config(sanitized, schema_version)
    elif config_type == ViewConfigurationType.DATA_QUERY:
        _validate_data_query_config(sanitized, schema_version)

    payload_hash = compute_payload_hash(sanitized)
    return sanitized, payload_hash


def _validate_chart_config(payload: Dict[str, Any], schema_version: int) -> None:
    if "timeframe" in payload and not isinstance(payload["timeframe"], str):
        raise SavedConfigurationInvalidError("'timeframe' must be a string (e.g. '1D', '1W').")
    if "chart_type" in payload and not isinstance(payload["chart_type"], str):
        raise SavedConfigurationInvalidError(
            "'chart_type' must be a string (e.g. 'CANDLESTICK', 'LINE')."
        )
    if "indicators" in payload and not isinstance(payload["indicators"], list):
        raise SavedConfigurationInvalidError(
            "'indicators' must be a list of indicator specifications."
        )
    if schema_version >= 2:
        if "timezone" in payload and not isinstance(payload["timezone"], str):
            raise SavedConfigurationInvalidError("'timezone' must be a string in schema v2.")


def _validate_screener_config(payload: Dict[str, Any], schema_version: int) -> None:
    if "universe" in payload and not isinstance(payload["universe"], str):
        raise SavedConfigurationInvalidError("'universe' must be a string identifier.")
    if "filters" in payload:
        if not isinstance(payload["filters"], list):
            raise SavedConfigurationInvalidError("'filters' must be a list of filter criteria.")
        for flt in payload["filters"]:
            if not isinstance(flt, dict) or "field" not in flt:
                raise SavedConfigurationInvalidError(
                    "Each filter must contain at least a 'field' attribute."
                )


def _validate_economics_config(payload: Dict[str, Any], schema_version: int) -> None:
    if "indicator_id" in payload and not isinstance(payload["indicator_id"], str):
        raise SavedConfigurationInvalidError("'indicator_id' must be a string identifier.")


def _validate_portfolio_config(payload: Dict[str, Any], schema_version: int) -> None:
    if "portfolio_id" in payload and not isinstance(payload["portfolio_id"], str):
        raise SavedConfigurationInvalidError("'portfolio_id' must be a string.")


def _validate_risk_config(payload: Dict[str, Any], schema_version: int) -> None:
    if "lookback_days" in payload and not isinstance(payload["lookback_days"], (int, float)):
        raise SavedConfigurationInvalidError("'lookback_days' must be numeric.")


def _validate_map_config(payload: Dict[str, Any], schema_version: int) -> None:
    if "geo_scope" in payload and not isinstance(payload["geo_scope"], str):
        raise SavedConfigurationInvalidError("'geo_scope' must be a string.")


def _validate_data_query_config(payload: Dict[str, Any], schema_version: int) -> None:
    if "query_name" in payload and not isinstance(payload["query_name"], str):
        raise SavedConfigurationInvalidError("'query_name' must be a string.")
    # Forbid raw executable SQL expressions in client payloads
    if "raw_sql" in payload or "executable_code" in payload:
        raise SavedConfigurationInvalidError(
            "Arbitrary executable code and raw SQL expressions are strictly prohibited."
        )


def migrate_configuration(
    config_type: ViewConfigurationType,
    from_version: int,
    to_version: int,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Deterministically migrates a configuration payload from from_version to to_version.
    Preserves all original user settings without data loss.
    """
    if from_version == to_version:
        return payload

    migrated = dict(payload)

    if config_type == ViewConfigurationType.CHART:
        if from_version == 1 and to_version == 2:
            # Upgrade ChartConfig from v1 to v2: default timezone to UTC and ensure indicators array
            if "timezone" not in migrated:
                migrated["timezone"] = "UTC"
            if "indicators" not in migrated:
                migrated["indicators"] = []
            return migrated
        raise SavedConfigurationMigrationFailedError(
            from_version,
            to_version,
            f"Unsupported chart migration path from {from_version} to {to_version}",
        )

    if config_type == ViewConfigurationType.SCREENER:
        if from_version == 1 and to_version == 2:
            # Upgrade ScreenerConfig from v1 to v2: ensure sort direction and columns
            if "sort_direction" not in migrated:
                migrated["sort_direction"] = "DESC"
            if "columns" not in migrated:
                migrated["columns"] = []
            return migrated
        raise SavedConfigurationMigrationFailedError(
            from_version,
            to_version,
            f"Unsupported screener migration path from {from_version} to {to_version}",
        )

    # For other types without multi-version specs yet
    if from_version < to_version:
        raise SavedConfigurationMigrationFailedError(
            from_version,
            to_version,
            f"No migration pipeline defined for {config_type} from {from_version} to {to_version}",
        )

    return migrated
