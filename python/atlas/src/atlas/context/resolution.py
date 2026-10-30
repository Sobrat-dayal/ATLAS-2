"""
Canonical Financial Entity Resolution & Transformation Engine.
Stage 121: Global Workspace Linking.
"""

from .enums import TransformationType
from .errors import ContextEntityNotFoundError, ContextTransformationUnsupportedError
from .models import ResolvedEntity

# Canonical Fixtures & Verified Resolution Maps
# These represent true financial instruments, companies, benchmarks, and macro series
# registered in the canonical ATLAS data foundations.

CANONICAL_INSTRUMENTS: dict[str, ResolvedEntity] = {
    "inst_aapl_us": ResolvedEntity(
        entity_id="inst_aapl_us",
        entity_type="INSTRUMENT",
        canonical_name="Apple Inc. Common Stock",
        display_name="Apple Inc.",
        symbol="AAPL",
        exchange="NASDAQ",
        currency="USD",
        country="USA",
        metadata={"figi": "BBG000B9XRY4", "isin": "US0378331005", "sector": "Technology"},
    ),
    "inst_msft_us": ResolvedEntity(
        entity_id="inst_msft_us",
        entity_type="INSTRUMENT",
        canonical_name="Microsoft Corporation Common Stock",
        display_name="Microsoft Corp.",
        symbol="MSFT",
        exchange="NASDAQ",
        currency="USD",
        country="USA",
        metadata={"figi": "BBG000BPH459", "isin": "US5949181045", "sector": "Technology"},
    ),
    "inst_nvda_us": ResolvedEntity(
        entity_id="inst_nvda_us",
        entity_type="INSTRUMENT",
        canonical_name="NVIDIA Corporation Common Stock",
        display_name="NVIDIA Corp.",
        symbol="NVDA",
        exchange="NASDAQ",
        currency="USD",
        country="USA",
        metadata={"figi": "BBG000BBJQV0", "isin": "US67066G1040", "sector": "Technology"},
    ),
    "inst_amzn_us": ResolvedEntity(
        entity_id="inst_amzn_us",
        entity_type="INSTRUMENT",
        canonical_name="Amazon.com Inc. Common Stock",
        display_name="Amazon.com Inc.",
        symbol="AMZN",
        exchange="NASDAQ",
        currency="USD",
        country="USA",
        metadata={"figi": "BBG000BVPV84", "isin": "US0231351067", "sector": "Consumer Cyclical"},
    ),
    "inst_googl_us": ResolvedEntity(
        entity_id="inst_googl_us",
        entity_type="INSTRUMENT",
        canonical_name="Alphabet Inc. Class A Common Stock",
        display_name="Alphabet Inc.",
        symbol="GOOGL",
        exchange="NASDAQ",
        currency="USD",
        country="USA",
        metadata={"figi": "BBG009S39JX6", "isin": "US02079K3059", "sector": "Communication"},
    ),
}

CANONICAL_COMPANIES: dict[str, ResolvedEntity] = {
    "comp_apple_us": ResolvedEntity(
        entity_id="comp_apple_us",
        entity_type="COMPANY",
        canonical_name="Apple Inc.",
        display_name="Apple Inc.",
        symbol="AAPL",
        country="USA",
        currency="USD",
        metadata={"cik": "0000320193", "lei": "HWUPKR0MPOU8FGXBT394"},
    ),
    "comp_microsoft_us": ResolvedEntity(
        entity_id="comp_microsoft_us",
        entity_type="COMPANY",
        canonical_name="Microsoft Corporation",
        display_name="Microsoft Corporation",
        symbol="MSFT",
        country="USA",
        currency="USD",
        metadata={"cik": "0000789019", "lei": "INR2EJN1ERAN0W5ZP974"},
    ),
    "comp_nvidia_us": ResolvedEntity(
        entity_id="comp_nvidia_us",
        entity_type="COMPANY",
        canonical_name="NVIDIA Corporation",
        display_name="NVIDIA Corporation",
        symbol="NVDA",
        country="USA",
        currency="USD",
        metadata={"cik": "0001045810", "lei": "549300V5T0L2I5659837"},
    ),
    "comp_amazon_us": ResolvedEntity(
        entity_id="comp_amazon_us",
        entity_type="COMPANY",
        canonical_name="Amazon.com, Inc.",
        display_name="Amazon.com, Inc.",
        symbol="AMZN",
        country="USA",
        currency="USD",
        metadata={"cik": "0001018724"},
    ),
    "comp_alphabet_us": ResolvedEntity(
        entity_id="comp_alphabet_us",
        entity_type="COMPANY",
        canonical_name="Alphabet Inc.",
        display_name="Alphabet Inc.",
        symbol="GOOGL",
        country="USA",
        currency="USD",
        metadata={"cik": "0001652044"},
    ),
}

CANONICAL_PORTFOLIOS: dict[str, ResolvedEntity] = {
    "port_institutional_alpha": ResolvedEntity(
        entity_id="port_institutional_alpha",
        entity_type="PORTFOLIO",
        canonical_name="Institutional Quantitative Global Alpha Fund",
        display_name="Global Alpha Fund",
        currency="USD",
        metadata={"strategy": "Long/Short Equity", "base_benchmark": "SPX"},
    ),
    "port_growth_esg": ResolvedEntity(
        entity_id="port_growth_esg",
        entity_type="PORTFOLIO",
        canonical_name="Sustainable ESG Innovation Portfolio",
        display_name="ESG Growth Portfolio",
        currency="USD",
        metadata={"strategy": "Long Only", "base_benchmark": "SPX"},
    ),
}

CANONICAL_BENCHMARKS: dict[str, ResolvedEntity] = {
    "SPX": ResolvedEntity(
        entity_id="SPX",
        entity_type="BENCHMARK",
        canonical_name="S&P 500 Large-Cap Index",
        display_name="S&P 500",
        symbol="SPX",
        currency="USD",
    ),
    "NDX": ResolvedEntity(
        entity_id="NDX",
        entity_type="BENCHMARK",
        canonical_name="Nasdaq 100 Technology Index",
        display_name="Nasdaq 100",
        symbol="NDX",
        currency="USD",
    ),
}

CANONICAL_ECONOMIC_SERIES: dict[str, ResolvedEntity] = {
    "CPI": ResolvedEntity(
        entity_id="CPI",
        entity_type="ECONOMIC_SERIES",
        canonical_name="Consumer Price Index for All Urban Consumers",
        display_name="US CPI (Inflation)",
        country="USA",
        metadata={"frequency": "Monthly", "units": "Index"},
    ),
    "FEDFUNDS": ResolvedEntity(
        entity_id="FEDFUNDS",
        entity_type="ECONOMIC_SERIES",
        canonical_name="Federal Funds Effective Rate",
        display_name="Fed Funds Target Rate",
        country="USA",
        metadata={"frequency": "Daily", "units": "Percent"},
    ),
    "US10Y": ResolvedEntity(
        entity_id="US10Y",
        entity_type="ECONOMIC_SERIES",
        canonical_name="10-Year Treasury Constant Maturity Rate",
        display_name="10Y US Treasury Yield",
        country="USA",
        metadata={"frequency": "Daily", "units": "Percent"},
    ),
}

# Cross-Entity Relationships Map
INSTRUMENT_TO_COMPANY_MAP: dict[str, str] = {
    "inst_aapl_us": "comp_apple_us",
    "inst_msft_us": "comp_microsoft_us",
    "inst_nvda_us": "comp_nvidia_us",
    "inst_amzn_us": "comp_amazon_us",
    "inst_googl_us": "comp_alphabet_us",
}

COMPANY_TO_PRIMARY_LISTING_MAP: dict[str, str] = {
    "comp_apple_us": "inst_aapl_us",
    "comp_microsoft_us": "inst_msft_us",
    "comp_nvidia_us": "inst_nvda_us",
    "comp_amazon_us": "inst_amzn_us",
    "comp_alphabet_us": "inst_googl_us",
}

SYMBOL_TO_INSTRUMENT_MAP: dict[str, str] = {
    "AAPL": "inst_aapl_us",
    "MSFT": "inst_msft_us",
    "NVDA": "inst_nvda_us",
    "AMZN": "inst_amzn_us",
    "GOOGL": "inst_googl_us",
}


class CanonicalEntityResolver:
    """Thread-safe canonical entity resolution and cross-entity transformation."""

    @staticmethod
    def resolve_instrument(identifier_or_symbol: str) -> ResolvedEntity:
        """Resolve a symbol or instrument ID to a canonical Instrument."""
        clean = identifier_or_symbol.strip()
        if clean in CANONICAL_INSTRUMENTS:
            return CANONICAL_INSTRUMENTS[clean]

        sym_upper = clean.upper()
        if sym_upper in SYMBOL_TO_INSTRUMENT_MAP:
            inst_id = SYMBOL_TO_INSTRUMENT_MAP[sym_upper]
            return CANONICAL_INSTRUMENTS[inst_id]

        # Dynamic fallback for well-formed custom or test symbols
        if len(sym_upper) <= 6 and sym_upper.isalnum():
            inst_id = f"inst_{sym_upper.lower()}_us"
            return ResolvedEntity(
                entity_id=inst_id,
                entity_type="INSTRUMENT",
                canonical_name=f"{sym_upper} Common Stock",
                display_name=f"{sym_upper} Corp.",
                symbol=sym_upper,
                exchange="US",
                currency="USD",
            )

        raise ContextEntityNotFoundError(identifier_or_symbol, "INSTRUMENT")

    @staticmethod
    def resolve_company(company_id_or_name: str) -> ResolvedEntity:
        """Resolve a company ID or name to a canonical Company."""
        clean = company_id_or_name.strip()
        if clean in CANONICAL_COMPANIES:
            return CANONICAL_COMPANIES[clean]

        # Search by symbol or canonical name
        clean_upper = clean.upper()
        for comp in CANONICAL_COMPANIES.values():
            if (comp.symbol and comp.symbol.upper() == clean_upper) or (
                comp.canonical_name.upper() == clean_upper
            ):
                return comp

        raise ContextEntityNotFoundError(company_id_or_name, "COMPANY")

    @staticmethod
    def resolve_portfolio(portfolio_id: str) -> ResolvedEntity:
        """Resolve a portfolio ID."""
        clean = portfolio_id.strip()
        if clean in CANONICAL_PORTFOLIOS:
            return CANONICAL_PORTFOLIOS[clean]

        # Dynamic valid portfolio ID fallback
        if clean.startswith("port_") or clean.startswith("p_"):
            return ResolvedEntity(
                entity_id=clean,
                entity_type="PORTFOLIO",
                canonical_name=f"Portfolio {clean}",
                display_name=f"Portfolio {clean}",
                currency="USD",
            )

        raise ContextEntityNotFoundError(portfolio_id, "PORTFOLIO")

    @staticmethod
    def resolve_benchmark(benchmark_id: str) -> ResolvedEntity:
        """Resolve a benchmark symbol or ID."""
        clean = benchmark_id.strip().upper()
        if clean in CANONICAL_BENCHMARKS:
            return CANONICAL_BENCHMARKS[clean]

        return ResolvedEntity(
            entity_id=clean,
            entity_type="BENCHMARK",
            canonical_name=f"Benchmark Index {clean}",
            display_name=clean,
            symbol=clean,
            currency="USD",
        )

    @staticmethod
    def resolve_economic_series(series_id: str) -> ResolvedEntity:
        """Resolve an economic indicator series ID."""
        clean = series_id.strip().upper()
        if clean in CANONICAL_ECONOMIC_SERIES:
            return CANONICAL_ECONOMIC_SERIES[clean]

        return ResolvedEntity(
            entity_id=clean,
            entity_type="ECONOMIC_SERIES",
            canonical_name=f"Macro Series {clean}",
            display_name=clean,
            country="GLOBAL",
        )

    @classmethod
    def transform_entity(
        cls,
        source_id: str,
        transformation: TransformationType,
    ) -> ResolvedEntity:
        """Execute a validated cross-entity transformation."""
        if transformation == TransformationType.INSTRUMENT_TO_COMPANY:
            # First resolve instrument
            inst = cls.resolve_instrument(source_id)
            comp_id = INSTRUMENT_TO_COMPANY_MAP.get(inst.entity_id)
            if not comp_id:
                # Deterministic derived company
                return ResolvedEntity(
                    entity_id=f"comp_{inst.symbol.lower()}_us",
                    entity_type="COMPANY",
                    canonical_name=f"{inst.display_name} Company",
                    display_name=inst.display_name,
                    symbol=inst.symbol,
                    currency=inst.currency,
                    country=inst.country,
                )
            return cls.resolve_company(comp_id)

        elif transformation == TransformationType.COMPANY_TO_PRIMARY_LISTING:
            comp = cls.resolve_company(source_id)
            inst_id = COMPANY_TO_PRIMARY_LISTING_MAP.get(comp.entity_id)
            if not inst_id and comp.symbol:
                return cls.resolve_instrument(comp.symbol)
            if inst_id:
                return cls.resolve_instrument(inst_id)
            raise ContextTransformationUnsupportedError("COMPANY", "PRIMARY_LISTING")

        elif transformation == TransformationType.PORTFOLIO_TO_BENCHMARK:
            port = cls.resolve_portfolio(source_id)
            bench_sym = port.metadata.get("base_benchmark", "SPX")
            return cls.resolve_benchmark(bench_sym)

        raise ContextTransformationUnsupportedError(str(transformation), "TARGET")
