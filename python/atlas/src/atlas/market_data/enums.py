from enum import Enum


class MarketDataTimeliness(str, Enum):
    """
    Indicates how fresh the market data observation is represented to be.
    """

    REAL_TIME = "real_time"
    DELAYED = "delayed"
    END_OF_DAY = "end_of_day"
    HISTORICAL = "historical"
    UNKNOWN = "unknown"


class MarketDataTimestampSource(str, Enum):
    """
    Indicates the origin of the timestamp for the market data observation.
    """

    EXCHANGE = "exchange"
    PROVIDER = "provider"
    RETRIEVAL = "retrieval"
    DERIVED = "derived"


class MarketSession(str, Enum):
    """
    Indicates the trading session in which the market data was observed.
    """

    PRE_MARKET = "pre_market"
    REGULAR = "regular"
    POST_MARKET = "post_market"
    OVERNIGHT = "overnight"
    CONTINUOUS = "continuous"
    UNKNOWN = "unknown"


class TradeSide(str, Enum):
    """
    Indicates the aggressor side of a trade, if known.
    """

    BUY = "buy"
    SELL = "sell"
    UNKNOWN = "unknown"


class PriceAdjustment(str, Enum):
    """
    Indicates the adjustment semantics for historical pricing data.
    """

    RAW = "raw"
    SPLIT_ADJUSTED = "split_adjusted"
    TOTAL_RETURN = "total_return"


class BarInterval(str, Enum):
    """
    Canonical intervals for OHLCV bars.
    Provider-specific interval strings must be mapped to these.
    """

    ONE_SECOND = "1s"
    FIVE_SECONDS = "5s"
    FIFTEEN_SECONDS = "15s"
    THIRTY_SECONDS = "30s"
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1mo"


class MarketDataOperation(str, Enum):
    """
    Canonical market data operations that can be implemented by providers.
    """

    QUOTE = "quote"
    HISTORICAL_BARS = "historical_bars"
    TRADES = "trades"
    ORDER_BOOK = "order_book"
    SNAPSHOT = "snapshot"
    LIVE_QUOTE_STREAM = "live_quote_stream"
