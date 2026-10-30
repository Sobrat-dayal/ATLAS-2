/**
 * Minimal Allowlisted Route Descriptors for Stage 124 Context-Light Awareness.
 * Strictly respects Stage 124 boundaries: no deep DOM inspection, no panel scraping.
 */

import { RouteContext } from "./types";

export const CANONICAL_ROUTES_MAP: Record<string, RouteContext> = {
  "/home": {
    route: "/home",
    module_name: "Executive Overview",
    summary: "Institutional dashboard, macro headlines, and portfolio summaries.",
  },
  "/markets": {
    route: "/markets",
    module_name: "Markets Monitor",
    summary: "Real-time cross-asset equities, FX, fixed income, crypto, and futures.",
  },
  "/charts": {
    route: "/charts",
    module_name: "Interactive Charts",
    summary: "Institutional multi-panel technical analysis and market replay.",
  },
  "/watchlists": {
    route: "/watchlists",
    module_name: "Watchlists",
    summary: "Multi-asset custom instrument monitoring and real-time tracking.",
  },
  "/screeners": {
    route: "/screeners",
    module_name: "Screeners",
    summary: "Quantitative multi-factor security screening and filtering engine.",
  },
  "/companies": {
    route: "/companies",
    module_name: "Companies",
    summary: "Corporate fundamentals, financial statements, SEC filings, and ownership.",
  },
  "/economics": {
    route: "/economics",
    module_name: "Economics",
    summary: "Global macroeconomic indicators, central banks, and yield curves.",
  },
  "/news": {
    route: "/news",
    module_name: "News Intelligence",
    summary: "Real-time curated financial newswires, sentiment analysis, and clustering.",
  },
  "/research": {
    route: "/research",
    module_name: "Research Library",
    summary: "Institutional reports, quantitative papers, and analyst research notes.",
  },
  "/maps": {
    route: "/maps",
    module_name: "Geopolitical & Supply Maps",
    summary: "Global supply chain mapping, trade flows, and geopolitical exposure.",
  },
  "/intelligence": {
    route: "/intelligence",
    module_name: "Intelligence Signals",
    summary: "AI-driven market anomalies, institutional flow signals, and insider activity.",
  },
  "/options": {
    route: "/options",
    module_name: "Options Analytics",
    summary: "Options chains, volatility surfaces, Greeks, and implied skew modeling.",
  },
  "/trading": {
    route: "/trading",
    module_name: "Trading Blotter",
    summary: "Order lifecycle, routing execution blotters, and fill allocations.",
  },
  "/portfolios": {
    route: "/portfolios",
    module_name: "Portfolios",
    summary: "Multi-asset portfolio accounting, attribution, and benchmark tracking.",
  },
  "/risk": {
    route: "/risk",
    module_name: "Risk Engine",
    summary: "Factor risk models, Value-at-Risk, stress tests, and scenario simulations.",
  },
  "/ai": {
    route: "/ai",
    module_name: "AI Workspace",
    summary: "Dedicated institutional AI workspace and quantitative conversation hub.",
  },
  "/data": {
    route: "/data",
    module_name: "Data Platform",
    summary: "Master data catalog, schema governance, and provider status.",
  },
  "/saved": {
    route: "/saved",
    module_name: "Saved Library",
    summary: "Universal persistent library for workspaces, screeners, and notebooks.",
  },
  "/workspaces": {
    route: "/workspaces",
    module_name: "Workspaces",
    summary: "Institutional multi-window analytical desks and linked widget workspaces.",
  },
  "/agents": {
    route: "/agents",
    module_name: "Autonomous Agents",
    summary: "Quantitative research workflows, agent execution, and MCP tools.",
  },
};

/**
 * Resolves pathname to the nearest canonical route descriptor.
 */
export function getRouteContext(pathname: string): RouteContext {
  if (!pathname || pathname === "/") {
    return CANONICAL_ROUTES_MAP["/home"];
  }

  // Exact match
  if (CANONICAL_ROUTES_MAP[pathname]) {
    return CANONICAL_ROUTES_MAP[pathname];
  }

  // Prefix match (e.g. /markets/equities -> /markets, /companies/AAPL -> /companies)
  for (const [route, context] of Object.entries(CANONICAL_ROUTES_MAP)) {
    if (pathname.startsWith(route)) {
      return context;
    }
  }

  return {
    route: pathname,
    module_name: "ATLAS Operating System",
    summary: "Institutional financial intelligence platform workspace.",
  };
}

