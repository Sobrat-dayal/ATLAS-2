from enum import StrEnum


class IdentifierCategory(StrEnum):
    FINANCIAL = "financial"
    ORGANIZATION = "organization"
    GEOGRAPHIC = "geographic"
    ECONOMIC = "economic"
    RESEARCH = "research"
    PROVIDER = "provider"


class IdentifierScopePolicy(StrEnum):
    GLOBAL = "global"
    ENTITY = "entity"
    NAMESPACE = "namespace"


class IdentifierNormalizationStrategy(StrEnum):
    UPPERCASE_TRIM = "uppercase_trim"
    LOWERCASE_TRIM = "lowercase_trim"
    COMPACT_UPPERCASE = "compact_uppercase"
    DIGITS_ONLY = "digits_only"
    DOI = "doi"
    ISBN10 = "isbn10"
    ISBN13 = "isbn13"
    PRESERVE_TRIM = "preserve_trim"


class IdentifierSchemeKey(StrEnum):
    TICKER = "ticker"
    FIGI = "figi"
    COMPOSITE_FIGI = "composite_figi"
    SHARE_CLASS_FIGI = "share_class_figi"
    ISIN = "isin"
    CUSIP = "cusip"
    SEDOL = "sedol"
    OCC_OPTION_SYMBOL = "occ_option_symbol"
    EXCHANGE_CONTRACT_CODE = "exchange_contract_code"

    ISO_4217_ALPHA = "iso_4217_alpha"
    ISO_4217_NUMERIC = "iso_4217_numeric"

    CIK = "cik"
    LEI = "lei"

    ISO_3166_ALPHA2 = "iso_3166_alpha2"
    ISO_3166_ALPHA3 = "iso_3166_alpha3"
    ISO_3166_NUMERIC = "iso_3166_numeric"

    IATA_AIRPORT = "iata_airport"
    ICAO_AIRPORT = "icao_airport"
    UNLOCODE = "unlocode"
    MIC = "mic"

    FRED_SERIES = "fred_series"
    WORLD_BANK_INDICATOR = "world_bank_indicator"
    OECD_SERIES = "oecd_series"
    IMF_SERIES = "imf_series"

    DOI = "doi"
    ARXIV = "arxiv"
    OPENALEX = "openalex"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    PUBMED = "pubmed"
    ISBN_10 = "isbn_10"
    ISBN_13 = "isbn_13"
    CROSSREF = "crossref"

    PROVIDER_EXTERNAL_ID = "provider_external_id"
