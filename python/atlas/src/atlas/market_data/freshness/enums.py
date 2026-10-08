from enum import Enum

class MarketDataFreshnessStatus(str, Enum):
    UNAVAILABLE = "unavailable"
    FRESH = "fresh"
    AGING = "aging"
    STALE = "stale"

class MarketDataFreshnessReason(str, Enum):
    NO_QUOTE = "no_quote"
    
    SOURCE_TIME_WITHIN_FRESH_THRESHOLD = "source_time_within_fresh_threshold"
    SOURCE_TIME_BETWEEN_THRESHOLDS = "source_time_between_thresholds"
    SOURCE_TIME_EXCEEDS_STALE_THRESHOLD = "source_time_exceeds_stale_threshold"
    
    RECEIVE_TIME_WITHIN_FRESH_THRESHOLD = "receive_time_within_fresh_threshold"
    RECEIVE_TIME_BETWEEN_THRESHOLDS = "receive_time_between_thresholds"
    RECEIVE_TIME_EXCEEDS_STALE_THRESHOLD = "receive_time_exceeds_stale_threshold"
    
    SOURCE_TIMESTAMP_UNAVAILABLE = "source_timestamp_unavailable"
    TARGET_DISABLED = "target_disabled"
    LIVE_TARGET_UNAVAILABLE = "live_target_unavailable"
    
    SOURCE_TIMESTAMP_IN_FUTURE = "source_timestamp_in_future"

class MarketDataFreshnessAgeBasis(str, Enum):
    SOURCE_TIME_PREFERRED = "source_time_preferred"
    RECEIVE_TIME_ONLY = "receive_time_only"

class MarketDataSourceTimestampFallback(str, Enum):
    USE_RECEIVED_AT = "use_received_at"
    MARK_UNAVAILABLE = "mark_unavailable"
