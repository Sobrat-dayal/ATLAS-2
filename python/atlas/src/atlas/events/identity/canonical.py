"""Canonical Event Identity Key Generation (Stage 135).

Generates stable, deterministic canonical identity keys from domain-specific
identity tuples (issuer, fiscal period, central bank, authority, or seismic ID)
preventing title-based collision or false deduplication.
"""

import hashlib
import re
from typing import Any, Dict, Optional


def normalize_token(text: Any) -> str:
    """Normalize text token for identity key generation."""
    if text is None:
        return "UNKNOWN"
    if hasattr(text, "isoformat"):
        text = text.isoformat()
    elif not isinstance(text, str):
        text = str(text)
    if not text.strip():
        return "UNKNOWN"
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", text.strip().upper())
    return re.sub(r"_+", "_", cleaned).strip("_")


def generate_canonical_event_key(
    event_type: str,
    payload: Dict[str, Any],
    source_event_id: Optional[str] = None,
    country_or_jurisdiction: Optional[str] = None,
    occurred_or_scheduled_date: Optional[str] = None,
) -> str:
    """Generate a deterministic canonical event key based on type-specific identity rules."""
    norm_type = normalize_token(event_type)

    # 1. Earnings Releases
    if "EARNINGS" in norm_type:
        issuer = normalize_token(payload.get("issuer_reference", payload.get("ticker", "UNKNOWN")))
        fy = str(payload.get("fiscal_year", "YYYY"))
        fq = str(payload.get("fiscal_quarter", "Q"))
        return f"FINANCIAL.EARNINGS:{issuer}:{fy}:{fq}"

    # 2. Economic Releases
    if norm_type.startswith("ECONOMIC"):
        indicator = normalize_token(payload.get("indicator_id", payload.get("indicator_name", "INDICATOR")))
        country = normalize_token(country_or_jurisdiction or payload.get("country_region", "GLOBAL"))
        period = normalize_token(payload.get("reporting_period", payload.get("reference_period", occurred_or_scheduled_date or "PERIOD")))
        vintage = normalize_token(payload.get("revision_vintage", "INITIAL"))
        return f"ECONOMIC:{indicator}:{country}:{period}:{vintage}"

    # 3. Monetary Policy Decisions
    if "RATE_DECISION" in norm_type or norm_type.startswith("MONETARY_POLICY"):
        cb = normalize_token(payload.get("central_bank_reference", country_or_jurisdiction or "CB"))
        date_str = normalize_token(occurred_or_scheduled_date or payload.get("decision_time", "DATE"))[0:10]
        instrument = normalize_token(payload.get("policy_instrument", "POLICY_RATE"))
        return f"MONETARY_POLICY:{cb}:{instrument}:{date_str}"

    # 4. Sanctions Designations
    if norm_type.startswith("SANCTIONS"):
        authority = normalize_token(payload.get("authority_id", "AUTHORITY"))
        subject = normalize_token(payload.get("designated_subject_reference", payload.get("official_action_id", "SUBJECT")))
        action = normalize_token(payload.get("action_type", "DESIGNATION"))
        date_str = normalize_token(occurred_or_scheduled_date or payload.get("publication_date", "DATE"))[0:10]
        return f"SANCTIONS:{authority}:{action}:{subject}:{date_str}"

    # 5. Corporate Actions (Mergers, Acquisitions, Dividends)
    if norm_type.startswith("CORPORATE"):
        issuer = normalize_token(payload.get("issuer_reference", "ISSUER"))
        action = normalize_token(payload.get("action_type", norm_type))
        target = normalize_token(payload.get("target_reference", "NONE"))
        date_str = normalize_token(occurred_or_scheduled_date or payload.get("declaration_date", "DATE"))[0:10]
        return f"CORPORATE:{issuer}:{action}:{target}:{date_str}"

    # 6. Earthquakes & Natural Disasters
    if "EARTHQUAKE" in norm_type:
        src_id = normalize_token(source_event_id or payload.get("source_event_id", "USGS_UNKNOWN"))
        return f"NATURAL_DISASTER.EARTHQUAKE:{src_id}"

    if norm_type.startswith("NATURAL_DISASTER"):
        disaster = normalize_token(payload.get("disaster_type", norm_type))
        src_id = normalize_token(source_event_id or payload.get("source_event_id", "DISASTER"))
        date_str = normalize_token(occurred_or_scheduled_date or "DATE")[0:10]
        return f"NATURAL_DISASTER:{disaster}:{src_id}:{date_str}"

    # 7. Regulatory Actions
    if norm_type.startswith("REGULATORY"):
        agency = normalize_token(payload.get("agency", "AGENCY"))
        action = normalize_token(payload.get("action_type", "ACTION"))
        matter = normalize_token(payload.get("rule_or_matter_reference", "MATTER"))
        date_str = normalize_token(occurred_or_scheduled_date or payload.get("publication_date", "DATE"))[0:10]
        return f"REGULATORY:{agency}:{action}:{matter}:{date_str}"

    # Default fallback using cryptographic hash of core parameters
    seed_str = f"{norm_type}:{source_event_id or ''}:{occurred_or_scheduled_date or ''}:{country_or_jurisdiction or ''}"
    hash_digest = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()[0:16]
    return f"{norm_type}:{hash_digest}"
