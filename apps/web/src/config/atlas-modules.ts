import {
  LayoutDashboard,
  LineChart,
  CandlestickChart,
  List,
  Search,
  Building2,
  TrendingUp,
  Newspaper,
  BookOpen,
  Map,
  Globe,
  Activity,
  ArrowLeftRight,
  Briefcase,
  ShieldAlert,
  Sparkles,
  Database,
  Bookmark,
  PanelsTopLeft,
  Bot
} from "lucide-react";

export type AtlasModuleId =
  | "home"
  | "markets"
  | "charts"
  | "watchlists"
  | "screeners"
  | "companies"
  | "economics"
  | "news"
  | "research"
  | "maps"
  | "intelligence"
  | "options"
  | "trading"
  | "portfolios"
  | "risk"
  | "ai"
  | "data"
  | "saved"
  | "workspaces"
  | "agents";

export interface AtlasModuleDefinition {
  id: AtlasModuleId;
  label: string;
  route: string;
  icon: any; // LucideIcon type simplified
  description: string;
  order: number;
  availability: "active" | "foundation" | "coming-soon";
  layoutMode: "standard" | "dense" | "fullBleed";
  settingsNamespace: string;
  aliases?: string[];
  legacyRoutes?: string[];
}

export const ATLAS_MODULES: Record<AtlasModuleId, AtlasModuleDefinition> = {
  home: {
    id: "home",
    label: "Home",
    route: "/home",
    icon: LayoutDashboard,
    description: "Command center for markets, portfolios, intelligence, agents, tasks and navigation.",
    order: 1,
    availability: "active",
    layoutMode: "dense",
    settingsNamespace: "settings.home",
  },
  markets: {
    id: "markets",
    label: "Markets",
    route: "/markets",
    icon: LineChart,
    description: "Global multi-asset market discovery, monitoring, movers, breadth and heatmaps.",
    order: 2,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.markets",
    aliases: ["markets", "market", "mkt", "mkts"],
  },
  charts: {
    id: "charts",
    label: "Charts",
    route: "/charts",
    icon: CandlestickChart,
    description: "Professional financial charting, indicators, drawings, layouts and replay.",
    order: 3,
    availability: "foundation",
    layoutMode: "fullBleed",
    settingsNamespace: "settings.charts",
    aliases: ["chart", "charts", "ch"],
  },
  watchlists: {
    id: "watchlists",
    label: "Watchlists",
    route: "/watchlists",
    icon: List,
    description: "Persistent monitoring lists with pricing, events, signals, news and alerts.",
    order: 4,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.watchlists",
    aliases: ["watchlist", "watchlists", "wl"],
  },
  screeners: {
    id: "screeners",
    label: "Screeners",
    route: "/screeners",
    icon: Search,
    description: "Multi-asset discovery using fundamental, technical, quantitative and custom filters.",
    order: 5,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.screeners",
    aliases: ["screen", "screener", "screeners", "scr"],
    legacyRoutes: ["/screener"],
  },
  companies: {
    id: "companies",
    label: "Companies",
    route: "/companies",
    icon: Building2,
    description: "Company intelligence covering fundamentals, financials, ownership, filings, peers and supply chains.",
    order: 6,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.companies",
    aliases: ["company", "companies", "co"],
  },
  economics: {
    id: "economics",
    label: "Economics",
    route: "/economics",
    icon: TrendingUp,
    description: "Macroeconomic indicators, central banks, rates, countries and economic events.",
    order: 7,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.economics",
    aliases: ["economics", "economy", "macro", "eco"],
    legacyRoutes: ["/economy"],
  },
  news: {
    id: "news",
    label: "News",
    route: "/news",
    icon: Newspaper,
    description: "Real-time financial, economic, corporate and geopolitical news intelligence.",
    order: 8,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.news",
    aliases: ["news", "nw"],
  },
  research: {
    id: "research",
    label: "Research",
    route: "/research",
    icon: BookOpen,
    description: "Filings, transcripts, reports, papers, notes and AI-assisted document research.",
    order: 9,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.research",
    aliases: ["research", "res"],
  },
  maps: {
    id: "maps",
    label: "Maps",
    route: "/maps",
    icon: Map,
    description: "Geospatial markets, infrastructure, logistics, supply chains and God's Eye intelligence.",
    order: 10,
    availability: "foundation",
    layoutMode: "fullBleed",
    settingsNamespace: "settings.maps",
    aliases: ["map", "maps", "geo"],
    legacyRoutes: ["/map"],
  },
  intelligence: {
    id: "intelligence",
    label: "Intelligence",
    route: "/intelligence",
    icon: Globe,
    description: "Cross-domain signals, events, anomalies, exposures, narratives and prioritized intelligence.",
    order: 11,
    availability: "foundation",
    layoutMode: "fullBleed",
    settingsNamespace: "settings.intelligence",
    aliases: ["intelligence", "intel"],
  },
  options: {
    id: "options",
    label: "Options",
    route: "/options",
    icon: Activity,
    description: "Options chains, volatility, Greeks, strategy analysis and derivatives intelligence.",
    order: 12,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.options",
    aliases: ["options", "opt"],
  },
  trading: {
    id: "trading",
    label: "Trading",
    route: "/trading",
    icon: ArrowLeftRight,
    description: "Paper/live execution, orders, positions, broker connectivity and execution workflows.",
    order: 13,
    availability: "foundation",
    layoutMode: "fullBleed",
    settingsNamespace: "settings.trading",
    aliases: ["trading", "trade", "trd"],
  },
  portfolios: {
    id: "portfolios",
    label: "Portfolios",
    route: "/portfolios",
    icon: Briefcase,
    description: "Holdings, transactions, performance, allocation, attribution and optimization.",
    order: 14,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.portfolios",
    aliases: ["portfolio", "portfolios", "port"],
    legacyRoutes: ["/portfolio"],
  },
  risk: {
    id: "risk",
    label: "Risk",
    route: "/risk",
    icon: ShieldAlert,
    description: "Market, portfolio, factor, credit, liquidity and scenario risk analytics.",
    order: 15,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.risk",
    aliases: ["risk"],
    legacyRoutes: ["/analytics"],
  },
  ai: {
    id: "ai",
    label: "AI Assistant",
    route: "/ai",
    icon: Sparkles,
    description: "Full ATLAS AI workspace for research, analysis, tools, artifacts and multi-step workflows.",
    order: 16,
    availability: "foundation",
    layoutMode: "fullBleed",
    settingsNamespace: "settings.ai",
    aliases: ["ai", "assistant"],
  },
  data: {
    id: "data",
    label: "Data",
    route: "/data",
    icon: Database,
    description: "Datasets, providers, schemas, queries, connectors, APIs and data-quality management.",
    order: 17,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.data",
    aliases: ["data"],
  },
  saved: {
    id: "saved",
    label: "Saved",
    route: "/saved",
    icon: Bookmark,
    description: "Universal library for saved assets, research, charts, screens, maps, notes and workflows.",
    order: 18,
    availability: "foundation",
    layoutMode: "dense",
    settingsNamespace: "settings.saved",
    aliases: ["saved", "save"],
  },
  workspaces: {
    id: "workspaces",
    label: "Workspaces",
    route: "/workspaces",
    icon: PanelsTopLeft,
    description: "Configurable multi-panel terminal environments with linked context and reusable layouts.",
    order: 19,
    availability: "foundation",
    layoutMode: "fullBleed",
    settingsNamespace: "settings.workspaces",
    aliases: ["workspace", "workspaces", "ws"],
  },
  agents: {
    id: "agents",
    label: "Agents",
    route: "/agents",
    icon: Bot,
    description: "Autonomous AI employees, teams, tasks, workflows, MCP tools and visual automation.",
    order: 20,
    availability: "foundation",
    layoutMode: "fullBleed",
    settingsNamespace: "settings.agents",
    aliases: ["agent", "agents"],
  },
};

// Sorted array for rendering
export const ATLAS_MODULES_LIST = Object.values(ATLAS_MODULES).sort((a, b) => a.order - b.order);

/**
 * Robust active-route matching
 * @param pathname Current browser pathname
 * @returns Active module definition or undefined
 */
export function getActiveAtlasModule(pathname: string): AtlasModuleDefinition | undefined {
  if (pathname === "/") return ATLAS_MODULES.home;
  
  // Find longest matching route
  const matches = ATLAS_MODULES_LIST.filter(m => 
    pathname === m.route || pathname.startsWith(m.route + "/")
  );
  
  if (matches.length > 0) {
    // Sort by length descending to get the most specific match
    return matches.sort((a, b) => b.route.length - a.route.length)[0];
  }

  // Check legacy routes fallback just in case redirect hasn't run yet on client
  for (const module of ATLAS_MODULES_LIST) {
    if (module.legacyRoutes?.some(legacy => pathname === legacy || pathname.startsWith(legacy + "/"))) {
      return module;
    }
  }

  return undefined;
}
