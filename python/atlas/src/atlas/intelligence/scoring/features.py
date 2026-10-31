"""Feature Definitions and Point-in-Time Extraction for Intelligence Scoring (Stage 139)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from .domain import FactorTransformationMethod
from .errors import ScoringLookAheadViolationError


class FeatureDefinition(BaseModel):
    """Institutional definition of a scoring feature and its availability policy."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    feature_id: str
    display_name: str
    source_domain: str  # EVENTS, GRAPH, EXPOSURE, PROVENANCE, GEOGRAPHY, ECONOMICS
    feature_type: str   # FLOAT, INTEGER, BOOLEAN, CATEGORY
    units: Optional[str] = None
    default_transformation: FactorTransformationMethod
    is_essential: bool = False


CANONICAL_FEATURES: Dict[str, FeatureDefinition] = {
    "FEAT_DIRECT_ISSUER_MATCH": FeatureDefinition(
        feature_id="FEAT_DIRECT_ISSUER_MATCH",
        display_name="Direct Canonical Issuer Match",
        source_domain="GRAPH",
        feature_type="BOOLEAN",
        default_transformation=FactorTransformationMethod.BINARY_ELIGIBILITY,
        is_essential=False,
    ),
    "FEAT_PORTFOLIO_WEIGHT": FeatureDefinition(
        feature_id="FEAT_PORTFOLIO_WEIGHT",
        display_name="Portfolio NAV Holding Weight",
        source_domain="EXPOSURE",
        feature_type="FLOAT",
        units="PERCENTAGE",
        default_transformation=FactorTransformationMethod.BOUNDED_PROPORTION,
        is_essential=False,
    ),
    "FEAT_INDEPENDENT_SOURCE_COUNT": FeatureDefinition(
        feature_id="FEAT_INDEPENDENT_SOURCE_COUNT",
        display_name="Deduplicated Independent Sources",
        source_domain="PROVENANCE",
        feature_type="INTEGER",
        units="COUNT",
        default_transformation=FactorTransformationMethod.ORDINAL_MAPPING,
        is_essential=False,
    ),
    "FEAT_PRIMARY_OFFICIAL_FILING": FeatureDefinition(
        feature_id="FEAT_PRIMARY_OFFICIAL_FILING",
        display_name="Official Regulatory/Central Bank Filing Present",
        source_domain="PROVENANCE",
        feature_type="BOOLEAN",
        default_transformation=FactorTransformationMethod.BINARY_ELIGIBILITY,
        is_essential=False,
    ),
    "FEAT_SOURCE_CONFLICT_FLAG": FeatureDefinition(
        feature_id="FEAT_SOURCE_CONFLICT_FLAG",
        display_name="Conflicting Source Statements Present",
        source_domain="PROVENANCE",
        feature_type="BOOLEAN",
        default_transformation=FactorTransformationMethod.BINARY_ELIGIBILITY,
        is_essential=False,
    ),
    "FEAT_RECENCY_ELAPSED_HOURS": FeatureDefinition(
        feature_id="FEAT_RECENCY_ELAPSED_HOURS",
        display_name="Elapsed Hours Since Publication",
        source_domain="EVENTS",
        feature_type="FLOAT",
        units="HOURS",
        default_transformation=FactorTransformationMethod.EXPONENTIAL_DECAY,
        is_essential=False,
    ),
    "FEAT_PROXIMITY_KM": FeatureDefinition(
        feature_id="FEAT_PROXIMITY_KM",
        display_name="Distance to Monitored Asset",
        source_domain="GEOGRAPHY",
        feature_type="FLOAT",
        units="KILOMETERS",
        default_transformation=FactorTransformationMethod.DISTANCE_STEP_FUNCTION,
        is_essential=False,
    ),
    "FEAT_NOVELTY_IS_NEW_EVENT": FeatureDefinition(
        feature_id="FEAT_NOVELTY_IS_NEW_EVENT",
        display_name="New Material Information Disclosed",
        source_domain="EVENTS",
        feature_type="BOOLEAN",
        default_transformation=FactorTransformationMethod.BINARY_ELIGIBILITY,
        is_essential=False,
    ),
}


class IntelligenceFeatureSnapshot(BaseModel):
    """Immutable point-in-time snapshot of extracted features."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    snapshot_id: str
    subject_id: str
    context_id: Optional[str] = None
    feature_values: Dict[str, Any]
    feature_available_at: Dict[str, str]
    missing_features: List[str] = Field(default_factory=list)
    known_as_of: str
    generated_at: str


class FeatureExtractor:
    """Extracts features point-in-time while strictly guarding against look-ahead leakage."""

    @classmethod
    def extract_event_features(
        cls,
        event_data: Dict[str, Any],
        known_as_of: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> IntelligenceFeatureSnapshot:
        snapshot_id = f"snap_{event_data.get('event_id', 'unknown')}_{int(datetime.now(timezone.utc).timestamp())}"
        values: Dict[str, Any] = {}
        avail_map: Dict[str, str] = {}
        missing: List[str] = []

        now_asof = datetime.fromisoformat(known_as_of.replace("Z", "+00:00"))

        # Event publication time
        pub_str = event_data.get("published_at") or event_data.get("occurrence_time") or known_as_of
        pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))

        # 1. Look-ahead check on event itself
        if pub_dt > now_asof:
            raise ScoringLookAheadViolationError(
                known_as_of=known_as_of,
                feature_available_at=pub_str,
                feature_id="EVENT_PUBLICATION",
            )

        # 2. Recency elapsed hours
        elapsed_hours = max(0.0, (now_asof - pub_dt).total_seconds() / 3600.0)
        values["FEAT_RECENCY_ELAPSED_HOURS"] = elapsed_hours
        avail_map["FEAT_RECENCY_ELAPSED_HOURS"] = pub_str

        # 3. Direct issuer / entity matching
        selected_entity_id = (context or {}).get("selected_entity_id")
        event_entities = event_data.get("entities", [])
        if selected_entity_id:
            is_direct = any(
                e.get("entity_id") == selected_entity_id and e.get("predicate", "MENTIONED_IN") in ("ISSUED_BY", "TARGET_OF", "PARTICIPANT_IN")
                for e in event_entities
            )
            values["FEAT_DIRECT_ISSUER_MATCH"] = is_direct
            avail_map["FEAT_DIRECT_ISSUER_MATCH"] = pub_str
        else:
            values["FEAT_DIRECT_ISSUER_MATCH"] = True if event_entities else False
            avail_map["FEAT_DIRECT_ISSUER_MATCH"] = pub_str

        # 4. Independent sources count (with anti-syndication deduplication)
        sources = event_data.get("sources", [])
        # Deduplicate syndicated copies that share the same root article fingerprint or original source id
        unique_fingerprints = set()
        for src in sources:
            src_pub = src.get("published_at", pub_str)
            src_dt = datetime.fromisoformat(src_pub.replace("Z", "+00:00"))
            # If source was published after known_as_of, it cannot be considered
            if src_dt <= now_asof:
                fp = src.get("article_fingerprint") or src.get("source_id") or src.get("name")
                unique_fingerprints.add(fp)

        values["FEAT_INDEPENDENT_SOURCE_COUNT"] = len(unique_fingerprints)
        avail_map["FEAT_INDEPENDENT_SOURCE_COUNT"] = pub_str

        # 5. Primary official filing present
        has_primary = any(
            src.get("source_type") in ("OFFICIAL_REGULATORY", "CENTRAL_BANK_BULLETIN", "OFFICIAL_GOVERNMENT")
            or "EDGAR" in str(src.get("name", ""))
            or "Federal Reserve" in str(src.get("name", ""))
            for src in sources
        )
        values["FEAT_PRIMARY_OFFICIAL_FILING"] = has_primary
        avail_map["FEAT_PRIMARY_OFFICIAL_FILING"] = pub_str

        # 6. Source conflict flag
        has_conflict = bool(event_data.get("has_conflicts", False))
        values["FEAT_SOURCE_CONFLICT_FLAG"] = has_conflict
        avail_map["FEAT_SOURCE_CONFLICT_FLAG"] = pub_str

        # 7. Novelty
        is_novel = event_data.get("is_novel", True)
        values["FEAT_NOVELTY_IS_NEW_EVENT"] = is_novel
        avail_map["FEAT_NOVELTY_IS_NEW_EVENT"] = pub_str

        # 8. Portfolio weight (contextual)
        portfolio_context = (context or {}).get("portfolio_context")
        if portfolio_context:
            holding_weight = portfolio_context.get("holding_weight_pct")
            if holding_weight is not None:
                values["FEAT_PORTFOLIO_WEIGHT"] = float(holding_weight)
                avail_map["FEAT_PORTFOLIO_WEIGHT"] = portfolio_context.get("as_of", known_as_of)
            else:
                missing.append("FEAT_PORTFOLIO_WEIGHT")
        else:
            missing.append("FEAT_PORTFOLIO_WEIGHT")

        # 9. Geographic proximity (contextual)
        proximity_km = event_data.get("proximity_km")
        if proximity_km is not None:
            values["FEAT_PROXIMITY_KM"] = float(proximity_km)
            avail_map["FEAT_PROXIMITY_KM"] = pub_str
        else:
            missing.append("FEAT_PROXIMITY_KM")

        return IntelligenceFeatureSnapshot(
            snapshot_id=snapshot_id,
            subject_id=event_data.get("event_id", "unknown"),
            context_id=(context or {}).get("context_id"),
            feature_values=values,
            feature_available_at=avail_map,
            missing_features=missing,
            known_as_of=known_as_of,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

