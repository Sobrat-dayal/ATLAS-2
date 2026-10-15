# ATLAS Cryptocurrency Markets V1 (Stage 60 Architecture)

## Executive Summary

Stage 60 implements **Cryptocurrency Markets V1: Global Crypto Asset Discovery, Exchange-Aware Spot Markets, Digital Asset Intelligence, Real-Time Trading Pairs and Professional Crypto Market Terminal** inside ATLAS Module 2 (`/markets`). It delivers an institutional-grade, exchange-aware discovery, inspection, and observational analytics workspace for digital assets and cryptocurrency spot trading pairs across verified centralized exchanges.

The canonical workspace route is:
```
/markets/crypto
```
integrated directly into the existing Markets application alongside Markets Overview (`/markets`), Equities (`/markets/equities`), ETFs & Funds (`/markets/funds`), and Foreign Exchange (`/markets/fx`).

---

## 1. Architecture Flow

```
ATLAS MARKETS (Module 02)
       │
       ├── Overview (Stage 56)           [/markets]
       ├── Equities (Stage 57)           [/markets/equities]
       ├── ETFs & Funds (Stage 58)       [/markets/funds]
       ├── Foreign Exchange (Stage 59)   [/markets/fx]
       │
       └── Cryptocurrency (Stage 60)     [/markets/crypto]
               │
               ├── MarketsNavigationTabs (Overview, Equities, Funds, FX, Crypto [Active], Bonds [St 61], Futures [St 62])
               ├── CryptoHeader (Search Ctrl+K, Overview, Charts, Research, Refresh)
               ├── CryptoCoverageSummary (Assets, Spot Markets, Venues, Active Quotes)
               ├── CryptoMarketFilters (Search query, Base Asset filter, Quote Asset filter, Exchange/Venue filter, Denomination filter, Reset)
               ├── CryptoSpotMarketTable (High-density tabular crypto spot display with deterministic keyset/offset pagination)
               │     └── CryptoSpotMarketRow (Pair, Exchange, Last Price, Bid, Ask, Spread, 24h Change, 24h Volume, Status, Source, Observed)
               └── CryptoMarketInspector (Deep inspection: Canonical UUID, Orientation explanation, Spot Quote, Level-1 Book, Base Asset specification, Venue identity, Cross-module navigation, Non-executable OTC disclaimer)
                       │
                       ▼
               Crypto REST API (FastAPI)
                       │
          ┌────────────┼────────────────────────┐
          ▼            ▼                        ▼
   CryptoDirectoryService  CryptoMarketReadService   CryptoAssetDirectoryService
          │            │                        │
     PostgreSQL   LiveQuoteService (Stage 41)   Canonical Digital Asset Catalog
                  ClickHouse History (Stage 39) Network & Token Contract Resolver
                  FreshnessClassifier (Stage 44) Decimal Financial Calculation Engine
```

---

## 2. Core Digital Asset & Market Identity Architecture

### A. Digital Asset vs Trading Pair Identity
Cryptocurrency asset identity is separate and decoupled from exchange trading pair identity:
- **Digital Asset Entity**: Represents the underlying crypto asset (e.g. Bitcoin `BTC`, Ethereum `ETH`, Tether `USDT`, USD Coin `USDC`, Wrapped Bitcoin `WBTC`, Solana `SOL`). Identified by deterministic UUID5 under `CRYPTO_ASSET_NAMESPACE`.
- **Spot Trading Pair Instrument**: Represents a specific market listing of a base asset priced in a quote asset on a specific exchange/venue (e.g. `BTC/USD` on Coinbase, `BTC/USDT` on Binance, `BTC/EUR` on Kraken). Identified by deterministic UUID5 under `CRYPTO_INSTRUMENT_NAMESPACE`.

### B. Base and Quote Asset Semantics
For every trading pair formatted in canonical `BASE/QUOTE` notation:
- **Price Meaning**: Units of `QUOTE` asset required for one unit of `BASE` asset.
- **Example**: `BTC/USDT = 67,465.00` mathematically means `1 BTC = 67,465.00 USDT`.
- **Directional Integrity**: `BTC/ETH` and `ETH/BTC` are distinct market instruments with inverse quotation orientation. ATLAS never conflates a direct pair with its reverse or silently flips symbols.

### C. Exchange / Venue Awareness
Spot crypto markets are fragmented across decentralized and centralized venues:
- Observations from Coinbase, Binance, Kraken, and Bitstamp are treated as distinct market series.
- Bid from Exchange A and Ask from Exchange B are never mixed or synthesized into an artificial spread.
- Market symbols on specific exchanges (e.g. `BTC-USD` on Coinbase, `BTCUSDT` on Binance, `XBT/EUR` on Kraken) resolve deterministically to their respective canonical spot instrument UUID.

### D. Fiat vs Stablecoin vs Crypto Quotation Denominations
- **Fiat Quotes**: Pairs quoted in sovereign fiat currencies (e.g. `USD`, `EUR`, `GBP`).
- **Stablecoin Quotes**: Pairs quoted in fiat-referenced digital tokens (e.g. `USDT`, `USDC`). Stablecoins are digital assets, NOT sovereign currencies.
- **No Hardcoded Parity**: ATLAS never assumes `1 USDT = 1.00 USD` or `1 USDC = 1.00 USD`. True observed market prices are preserved without artificial normalization.
- **Crypto Quotes**: Crypto-denominated pairs (e.g. `ETH/BTC`) preserve fractional crypto quotation units (e.g. 6 decimal places).

### E. Native Blockchain Coins vs Contract Tokens
- **Native Coins**: Assets that serve as the base monetary unit or gas asset of an independent layer-1 blockchain (e.g. Bitcoin on `bitcoin`, Ether on `ethereum`, SOL on `solana`, AVAX on `avalanche`, DOGE on `dogecoin`). Native assets do not possess smart contract addresses.
- **Contract Tokens**: Fungible tokens deployed as smart contracts on a host blockchain network (e.g. Tether `USDT` and Chainlink `LINK` as `ERC-20` on `ethereum`). Network identity and contract addresses are explicitly modeled and network-scoped.
- **Wrapped Assets**: Tokenized representations of another cryptocurrency (e.g. `WBTC` as an `ERC-20` contract on Ethereum backed 1:1 by custodial Bitcoin reserves). Wrapped assets are strictly distinguished from their native counterparts.

---

## 3. Financial Semantics, Spread, and Precision Engine

### A. Level-1 Top-of-Book and Trade Prices
- **Last Price**: The most recent confirmed spot trade price observed on the venue feed.
- **Bid**: The highest price a buyer on that venue order book is offering to pay for 1 unit of base asset.
- **Ask**: The lowest price a seller on that venue order book is asking to receive for 1 unit of base asset.
- **Rate Kinds**: Explicitly classified as `SPOT_TRADE`, `BID_ASK_QUOTE`, `INDICATIVE_COMPOSITE`, or `CROSSED_INVALID`.

### B. Decimal-Safe Spread and Midpoint Calculation
When both bid and ask are positive, originating from the same provider observation on the same venue:
$$\text{spread}_{\text{absolute}} = \text{ask} - \text{bid}$$
$$\text{midpoint} = \frac{\text{bid} + \text{ask}}{2}$$
$$\text{spread}_{\text{bps}} = \left(\frac{\text{ask} - \text{bid}}{\text{midpoint}}\right) \times 10{,}000$$

### C. Crossed Market Detection
If an observation reports $\text{bid} > \text{ask}$, the market state is crossed/inconsistent. ATLAS flags the rate kind as `CROSSED_INVALID` and suppresses spread and midpoint calculations (returned as `None`), preventing misleading negative spreads.

### D. Price and Quantity Precision
- High-value assets (e.g. Bitcoin at $67,450.00) use 2 decimal places.
- Mid-value assets (e.g. Chainlink at $14.850) use 3 decimal places.
- Lower-value assets (e.g. Dogecoin at $0.14250) use 5 decimal places.
- Crypto-denominated pairs (e.g. ETH/BTC at 0.052210 BTC) use 6 decimal places.
- Prices are never prematurely rounded to 2 decimals, preventing small token prices from displaying as zero.

### E. 24-Hour Price Change
Rolling 24-hour price change is evaluated against compatible prior observations on the exact same venue, series, and quote asset denomination. Zero-denominator errors are strictly guarded. When historical references are unavailable, the interface displays an honest dash (`—`), never an assumed `0.00%`.

### F. Reported 24-Hour Volume
- **Base Volume**: Total traded quantity expressed in the base asset (e.g. `11,200.50 BTC`).
- **Quote Volume**: Total traded value expressed in the quote asset (e.g. `$755,473,725.00 USD` or `1,916,006,000.00 USDT`).
- Preserves explicit asset units at all times; USDT volume is never relabeled as USD.

### G. Freshness and Provenance
- Reuses Stage 44 freshness monitoring: `FRESH` (< 30s), `DELAYED`, `STALE` (> 300s), `UNKNOWN`.
- Source observation timestamps and platform receipt timestamps are preserved in UTC ISO 8601.

---

## 4. API Architecture & Endpoints

| Method | Path | Summary | Auth & Entitlements |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/markets/crypto` | Paginated spot market directory with search, base/quote/venue/type filters | Authenticated (`AuthPrincipal`) + `atlas.access` |
| `GET` | `/api/v1/markets/crypto/assets` | Directory of canonical digital assets with network/contract metadata | Authenticated (`AuthPrincipal`) + `atlas.access` |
| `GET` | `/api/v1/markets/crypto/filters` | Distinct active filter options derived from configured catalog | Authenticated (`AuthPrincipal`) + `atlas.access` |
| `GET` | `/api/v1/markets/crypto/{id}` | Comprehensive inspection detail for a specific spot market | Authenticated (`AuthPrincipal`) + `atlas.access` |

### Read-Only Invariants
All cryptocurrency read endpoints enforce strict side-effect guarantees:
- PostgreSQL writes: **0**
- Redis writes: **0**
- ClickHouse writes: **0**
- Upstream external provider HTTP requests: **0**
- New ingestion targets created: **0**
- Exchange orders placed: **0**
- Blockchain transactions signed: **0**

---

## 5. UI/UX Workspace Design

The Cryptocurrency Markets workspace follows Bloomberg/OpenBB institutional financial workstation aesthetics:
- **High Information Density**: Tabular financial data with right-aligned monospace numbers, explicit asset units, and clear venue tags.
- **Deep Market Inspector**: Interactive detail sidebar providing quotation orientation, top-of-book breakdown, volume metrics, base asset specification (network, contract address, token standard), and cross-module deep links (`/charts`, `/research`).
- **Responsive Layout**: Fluid CSS grid adapting from 320px mobile to 1920px multi-monitor displays, compatible with Agent Dock and Bottom Taskbar drawers.
- **Strict Design Bans**: Zero purple gradients, zero emojis, zero fake trading activity, zero buy/sell buttons, and zero unverified market capitalization rankings.

---

## 6. Non-Executable Disclosure & Safety Safeguards

The workspace explicitly informs users through in-app disclosures:
> "Indicative spot market observation from identified venue. Not an order execution offer, custody service, or investment advice."

Stage 60 strictly prohibits and does not implement:
- Exchange trading account connectivity or API key input
- Cryptocurrency wallet connectivity (MetaMask, WalletConnect, etc.)
- Private key or seed phrase ingestion
- Blockchain transaction signing or fund transfers
- Perpetual futures, funding rate arbitrage, or leverage/margin management
- Automated algorithmic trading bots or AI buy/sell recommendations

---

## 7. Canonical Roadmap Position & Boundaries

| Stage | Domain | Status in Stage 60 |
| :--- | :--- | :--- |
| **56** | Markets Overview V1 | Preserved |
| **57** | Equities Markets V1 | Preserved |
| **58** | ETFs & Funds Markets V1 | Preserved |
| **59** | FX Markets V1 | Preserved |
| **60** | Cryptocurrency Markets V1 | **Completed (Current Stage)** |
| **61** | Bonds & Fixed-Income Markets V1 | Canonical Next Stage (Not Begun) |
| **62** | Futures & Commodities Markets V1 | Future Stage (Deferred) |
| **63** | Market Movers | Future Stage (Deferred) |
| **64** | Heatmaps | Future Stage (Deferred) |
| **65** | Cross-Asset Analytics | Future Stage (Deferred) |
| **66** | Charts V1 | Future Stage (Deferred) |
