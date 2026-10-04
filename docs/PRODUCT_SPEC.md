# ATLAS Product Specification

## What is ATLAS?

ATLAS is an **AI-native financial intelligence, markets, research, trading, geospatial intelligence, portfolio analytics, risk, data, and autonomous-agent operating system.**

It is built to feel less like a traditional website and more like a cohesive **financial operating environment**. It synthesizes the most effective interaction patterns from:
- Bloomberg Terminal
- TradingView
- OpenBB
- Google Earth and advanced geospatial platforms
- VS Code
- n8n-style workflow automation
- AI agent operating systems

## Who is it for?

ATLAS is for professionals and advanced users who require a unified, data-dense platform to:
- Monitor global financial markets
- Analyze companies and economics
- Chart securities and visualize physical-world information geographically
- Consume financial news and conduct deep document research
- Manage portfolios, risk, and execute options/trading strategies
- Interact seamlessly with an embedded AI Assistant
- Create and deploy autonomous AI employees and multi-agent workflows
- Connect MCP (Model Context Protocol) servers and external tools
- Run Python/SQL/ATLAS commands in an integrated terminal
- Automate recurring research and manage parts of an autonomous company

## The 20 Top-Level Modules

ATLAS uses a fixed sidebar navigation consisting of the following 20 modules:

1. **Home** - Main operational command center.
2. **Markets** - Global multi-asset market discovery.
3. **Charts** - Professional financial charting.
4. **Watchlists** - Persistent monitoring lists.
5. **Screeners** - Universal market discovery and filtering.
6. **Companies** - Full company intelligence profile.
7. **Economics** - Global macroeconomic and central bank intelligence.
8. **News** - Real-time and historical financial/global news.
9. **Research** - Institutional-style document analysis.
10. **Maps** - Geospatial and God's Eye intelligence system.
11. **Intelligence** - Cross-domain signal and event engine.
12. **Options** - Dedicated derivatives analytics.
13. **Trading** - Execution and order-management.
14. **Portfolios** - Portfolio management and analytics.
15. **Risk** - Portfolio and market-risk analytics.
16. **AI Assistant** - Full ATLAS AI workspace.
17. **Data** - Data management and developer platform.
18. **Saved** - Universal personal knowledge/bookmark layer.
19. **Workspaces** - Configurable terminal environment.
20. **Agents** - Autonomous AI employee and workflow system.

*For deep dives into each module, refer to [MODULES.md](MODULES.md).*

## Core Architectural Concepts

### Global Context System
ATLAS is context-aware. If the user selects an entity (e.g., NVIDIA), the entire application understands this context. Switching to Charts shows NVDA; switching to Maps shows NVIDIA facilities; asking ATLAS AI a question implies NVIDIA as the subject.

### Universal Entity System
The system is built around stable internal identifiers for entities, rather than relying merely on ticker symbols. Entities include Companies, Securities, Options, Countries, Facilities, Pipelines, News Events, Portfolios, Agents, and Workflows.

### Universal Relationship Graph
Entities are connected in a graph. For example: `Company -> owns -> Facility -> located_in -> Country`. This relationship network powers cross-module intelligence spanning Companies, Maps, Risk, Portfolios, and AI.

### Shared Capability Layer
If ATLAS implements a core function (e.g., `get_company()`), this capability will be shared across the UI, AI Assistant, autonomous Agents, Workflow Builder, Terminal, MCP, and external APIs.

## Product Boundaries

Early versions of ATLAS are **not** expected to include:
- Full Bloomberg-scale market data coverage
- Direct global exchange connectivity or HFT infrastructure
- Institutional OMS/EMS from day one
- Unrestricted live trading
- Every global data provider or chart type
- Full compliance infrastructure
- Distributed microservices everywhere by default (ATLAS begins as a modular monolith)
