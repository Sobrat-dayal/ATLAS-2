import { AtlasModuleId } from "./atlas-modules";

export type SectionSettingType = "boolean" | "select" | "number" | "slider" | "text" | "foundation";

export interface SectionSettingDefinition {
  id: string;
  label: string;
  description?: string;
  type: SectionSettingType;
  defaultValue?: unknown;
  options?: readonly { label: string; value: unknown }[];
  keywords?: string[];
  availability?: "active" | "foundation" | "unavailable";
  requiresFeature?: string;
  min?: number;
  max?: number;
  step?: number;
}

export interface SectionSettingsGroup {
  id: string;
  label: string;
  settings: SectionSettingDefinition[];
}

export interface AtlasSectionSettingsDefinition {
  moduleId: AtlasModuleId;
  title: string;
  description: string;
  storageNamespace: string;
  version: number;
  groups: SectionSettingsGroup[];
}

// Helper to define settings quickly
const defineModuleSettings = (def: AtlasSectionSettingsDefinition) => def;

export const SECTION_SETTINGS_REGISTRY: Record<AtlasModuleId, AtlasSectionSettingsDefinition> = {
  home: defineModuleSettings({
    moduleId: "home",
    title: "Home Settings",
    description: "Configure how Home displays and behaves.",
    storageNamespace: "atlas.section-settings.home.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "home.layoutMode",
            label: "Default Home layout mode",
            type: "select",
            defaultValue: "standard",
            options: [
              { label: "Standard", value: "standard" },
              { label: "Dense", value: "dense" }
            ],
            availability: "active"
          },
          {
            id: "home.restoreScroll",
            label: "Restore last scroll position",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "marketSummary",
        label: "Market Summary",
        settings: [
          {
            id: "home.showMarketSummary",
            label: "Show market summary",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "home.showTickerStrip",
            label: "Show ticker strip",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "home.defaultMarketRegion",
            label: "Default market region",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "sections",
        label: "Home Sections",
        settings: [
          {
            id: "home.showNews",
            label: "Show News",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "home.showEconomics",
            label: "Show Economics",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "home.showWatchlist",
            label: "Show Watchlist",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "home.showAgentActivity",
            label: "Show Agent Activity",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "home.showTasks",
            label: "Show Tasks",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "home.showIntelligence",
            label: "Show Intelligence",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "display",
        label: "Display",
        settings: [
          {
            id: "home.compactCards",
            label: "Compact cards",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "home.showMiniSparklines",
            label: "Show mini sparklines",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      }
    ]
  }),

  markets: defineModuleSettings({
    moduleId: "markets",
    title: "Markets Settings",
    description: "Configure how Markets displays and behaves.",
    storageNamespace: "atlas.section-settings.markets.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "markets.defaultAssetClass",
            label: "Default asset class",
            type: "select",
            defaultValue: "overview",
            options: [
              { label: "Overview", value: "overview" },
              { label: "Equities", value: "equities" },
              { label: "ETFs", value: "etfs" },
              { label: "FX", value: "fx" },
              { label: "Crypto", value: "crypto" },
              { label: "Bonds", value: "bonds" },
              { label: "Futures", value: "futures" },
              { label: "Commodities", value: "commodities" }
            ],
            availability: "active"
          },
          {
            id: "markets.defaultRegion",
            label: "Default region",
            type: "select",
            defaultValue: "global",
            options: [
              { label: "Global", value: "global" },
              { label: "United States", value: "us" },
              { label: "Europe", value: "europe" },
              { label: "Asia", value: "asia" },
              { label: "India", value: "india" }
            ],
            availability: "active"
          },
          {
            id: "markets.defaultSession",
            label: "Default market session",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "display",
        label: "Display",
        settings: [
          {
            id: "markets.showSparklines",
            label: "Show sparklines",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "markets.showPercentageChange",
            label: "Show percentage change",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "markets.showAbsoluteChange",
            label: "Show absolute change",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "markets.showMarketStatus",
            label: "Show market status",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "tables",
        label: "Tables",
        settings: [
          {
            id: "markets.rowDensity",
            label: "Row density",
            type: "select",
            defaultValue: "default",
            options: [
              { label: "Compact", value: "compact" },
              { label: "Default", value: "default" },
              { label: "Comfortable", value: "comfortable" }
            ],
            availability: "active"
          },
          {
            id: "markets.defaultSort",
            label: "Default sort",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "markets.stickyHeaders",
            label: "Sticky headers",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "markets.highlightMovers",
            label: "Highlight movers",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "data",
        label: "Data",
        settings: [
          {
            id: "markets.showDelayedStatus",
            label: "Show delayed/live status",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "markets.extendedHours",
            label: "Extended hours",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "markets.preferredProvider",
            label: "Preferred provider",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "heatmaps",
        label: "Heatmaps",
        settings: [
          {
            id: "markets.heatmapDefaultGrouping",
            label: "Default grouping",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "markets.heatmapShowLabels",
            label: "Show labels",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      }
    ]
  }),

  charts: defineModuleSettings({
    moduleId: "charts",
    title: "Charts Settings",
    description: "Configure how Charts displays and behaves.",
    storageNamespace: "atlas.section-settings.charts.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "charts.defaultTimeframe",
            label: "Default timeframe",
            type: "select",
            defaultValue: "1D",
            options: [
              { label: "1 Minute", value: "1m" },
              { label: "5 Minutes", value: "5m" },
              { label: "15 Minutes", value: "15m" },
              { label: "1 Hour", value: "1H" },
              { label: "1 Day", value: "1D" },
              { label: "1 Week", value: "1W" },
              { label: "1 Month", value: "1M" }
            ],
            availability: "active"
          },
          {
            id: "charts.defaultChartType",
            label: "Default chart type",
            type: "select",
            defaultValue: "candles",
            options: [
              { label: "Candles", value: "candles" },
              { label: "Line", value: "line" },
              { label: "Area", value: "area" },
              { label: "Bars", value: "bars" }
            ],
            availability: "active"
          },
          {
            id: "charts.autoSaveLayouts",
            label: "Auto-save layouts",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "appearance",
        label: "Appearance",
        settings: [
          {
            id: "charts.grid",
            label: "Grid",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "charts.crosshair",
            label: "Crosshair",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "charts.priceLine",
            label: "Price line",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "charts.sessionBreaks",
            label: "Session breaks",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "charts.watermarkSymbol",
            label: "Watermark symbol",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "charts.upDownColors",
            label: "Up/down colors",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "candles",
        label: "Candles",
        settings: [
          {
            id: "charts.candleBody",
            label: "Body",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "charts.candleWick",
            label: "Wick",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "charts.candleBorders",
            label: "Borders",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "scales",
        label: "Scales",
        settings: [
          {
            id: "charts.priceScale",
            label: "Price scale",
            type: "select",
            defaultValue: "right",
            options: [
              { label: "Right", value: "right" },
              { label: "Left", value: "left" }
            ],
            availability: "active"
          },
          {
            id: "charts.percentageScale",
            label: "Percentage scale",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "charts.logScale",
            label: "Log scale",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "indicators",
        label: "Indicators",
        settings: [
          {
            id: "charts.defaultIndicatorBehavior",
            label: "Default indicator behavior",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "drawingTools",
        label: "Drawing Tools",
        settings: [
          {
            id: "charts.magnetMode",
            label: "Magnet mode",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "charts.persistDrawings",
            label: "Persist drawings",
            description: "Preserve chart drawings between sessions. Available after drawing tools are implemented.",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "data",
        label: "Data",
        settings: [
          {
            id: "charts.extendedHours",
            label: "Extended hours",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "charts.adjustedPrices",
            label: "Adjusted prices",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  watchlists: defineModuleSettings({
    moduleId: "watchlists",
    title: "Watchlists Settings",
    description: "Configure how Watchlists displays and behaves.",
    storageNamespace: "atlas.section-settings.watchlists.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "watchlists.defaultWatchlist",
            label: "Default watchlist",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "watchlists.openInInspector",
            label: "Open selected item in inspector",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "display",
        label: "Display",
        settings: [
          {
            id: "watchlists.rowDensity",
            label: "Row density",
            type: "select",
            defaultValue: "default",
            options: [
              { label: "Compact", value: "compact" },
              { label: "Default", value: "default" },
              { label: "Comfortable", value: "comfortable" }
            ],
            availability: "active"
          },
          {
            id: "watchlists.showSparklines",
            label: "Show sparklines",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "watchlists.flashPriceChanges",
            label: "Flash price changes",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "watchlists.showLogos",
            label: "Show logos",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "watchlists.showTags",
            label: "Show tags",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "columns",
        label: "Columns",
        settings: [
          {
            id: "watchlists.defaultVisibleColumns",
            label: "Default visible columns",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "updates",
        label: "Updates",
        settings: [
          {
            id: "watchlists.refreshBehavior",
            label: "Refresh behavior",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "alerts",
        label: "Alerts",
        settings: [
          {
            id: "watchlists.alertIndicatorVisibility",
            label: "Alert indicator visibility",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  screeners: defineModuleSettings({
    moduleId: "screeners",
    title: "Screeners Settings",
    description: "Configure how Screeners displays and behaves.",
    storageNamespace: "atlas.section-settings.screeners.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "screeners.defaultUniverse",
            label: "Default screener universe",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "screeners.defaultRegion",
            label: "Default region",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "screeners.resultsPerPage",
            label: "Results per page",
            type: "select",
            defaultValue: 50,
            options: [
              { label: "25", value: 25 },
              { label: "50", value: 50 },
              { label: "100", value: 100 }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "results",
        label: "Results",
        settings: [
          {
            id: "screeners.rowDensity",
            label: "Row density",
            type: "select",
            defaultValue: "default",
            options: [
              { label: "Compact", value: "compact" },
              { label: "Default", value: "default" },
              { label: "Comfortable", value: "comfortable" }
            ],
            availability: "active"
          },
          {
            id: "screeners.stickyHeaders",
            label: "Sticky headers",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "screeners.autoRunFilters",
            label: "Auto-run filters",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "display",
        label: "Display",
        settings: [
          {
            id: "screeners.showMiniCharts",
            label: "Show mini charts",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "screeners.showTags",
            label: "Show tags",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "ranking",
        label: "Ranking",
        settings: [
          {
            id: "screeners.defaultSort",
            label: "Default sort",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "screeners.rankingDirection",
            label: "Ranking direction",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "naturalLanguage",
        label: "Natural Language",
        settings: [
          {
            id: "screeners.nlScreener",
            label: "NL screener",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  companies: defineModuleSettings({
    moduleId: "companies",
    title: "Companies Settings",
    description: "Configure how Companies displays and behaves.",
    storageNamespace: "atlas.section-settings.companies.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "companies.defaultCompanyTab",
            label: "Default company tab",
            type: "select",
            defaultValue: "overview",
            options: [
              { label: "Overview", value: "overview" },
              { label: "Financials", value: "financials" },
              { label: "News", value: "news" },
              { label: "Filings", value: "filings" },
              { label: "Peers", value: "peers" }
            ],
            availability: "active"
          },
          {
            id: "companies.openInInspector",
            label: "Open company in inspector/full page",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "financials",
        label: "Financials",
        settings: [
          {
            id: "companies.annualQuarterlyDefault",
            label: "Annual / Quarterly default",
            type: "select",
            defaultValue: "annual",
            options: [
              { label: "Annual", value: "annual" },
              { label: "Quarterly", value: "quarterly" }
            ],
            availability: "active"
          },
          {
            id: "companies.currencyDisplay",
            label: "Currency display",
            type: "select",
            defaultValue: "reported",
            options: [
              { label: "As Reported", value: "reported" },
              { label: "USD Converted", value: "usd" }
            ],
            availability: "active"
          },
          {
            id: "companies.units",
            label: "Units",
            type: "select",
            defaultValue: "millions",
            options: [
              { label: "Raw", value: "raw" },
              { label: "Thousands", value: "thousands" },
              { label: "Millions", value: "millions" },
              { label: "Billions", value: "billions" }
            ],
            availability: "active"
          },
          {
            id: "companies.numberPrecision",
            label: "Number precision",
            type: "select",
            defaultValue: 2,
            options: [
              { label: "0 decimals", value: 0 },
              { label: "1 decimal", value: 1 },
              { label: "2 decimals", value: 2 }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "valuation",
        label: "Valuation",
        settings: [
          {
            id: "companies.preferredMultiples",
            label: "Preferred multiples",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "charts",
        label: "Charts",
        settings: [
          {
            id: "companies.defaultPriceTimeframe",
            label: "Default company price timeframe",
            type: "select",
            defaultValue: "1Y",
            options: [
              { label: "1 Month", value: "1M" },
              { label: "3 Months", value: "3M" },
              { label: "1 Year", value: "1Y" },
              { label: "5 Years", value: "5Y" },
              { label: "Max", value: "MAX" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "news",
        label: "News",
        settings: [
          {
            id: "companies.showCompanyNewsPanel",
            label: "Show company news panel",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "filings",
        label: "Filings",
        settings: [
          {
            id: "companies.defaultFilingType",
            label: "Default filing type",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "peers",
        label: "Peers",
        settings: [
          {
            id: "companies.showPeerComparison",
            label: "Show peer comparison",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      }
    ]
  }),

  economics: defineModuleSettings({
    moduleId: "economics",
    title: "Economics Settings",
    description: "Configure how Economics displays and behaves.",
    storageNamespace: "atlas.section-settings.economics.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "economics.defaultCountry",
            label: "Default country",
            type: "select",
            defaultValue: "us",
            options: [
              { label: "United States", value: "us" },
              { label: "Eurozone", value: "eurozone" },
              { label: "China", value: "china" },
              { label: "Japan", value: "japan" },
              { label: "UK", value: "uk" }
            ],
            availability: "active"
          },
          {
            id: "economics.defaultMacroRegion",
            label: "Default macro region",
            type: "select",
            defaultValue: "global",
            options: [
              { label: "Global", value: "global" },
              { label: "Americas", value: "americas" },
              { label: "EMEA", value: "emea" },
              { label: "APAC", value: "apac" }
            ],
            availability: "active"
          },
          {
            id: "economics.defaultTimeRange",
            label: "Default time range",
            type: "select",
            defaultValue: "10Y",
            options: [
              { label: "1 Year", value: "1Y" },
              { label: "5 Years", value: "5Y" },
              { label: "10 Years", value: "10Y" },
              { label: "Max", value: "MAX" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "charts",
        label: "Charts",
        settings: [
          {
            id: "economics.lineBarDefault",
            label: "Line / bar default",
            type: "select",
            defaultValue: "line",
            options: [
              { label: "Line", value: "line" },
              { label: "Bar", value: "bar" }
            ],
            availability: "active"
          },
          {
            id: "economics.showRecessionBands",
            label: "Show recession bands",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "calendar",
        label: "Calendar",
        settings: [
          {
            id: "economics.showImportance",
            label: "Show importance",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "economics.defaultEventImportanceThreshold",
            label: "Default event importance threshold",
            type: "select",
            defaultValue: "medium",
            options: [
              { label: "All", value: "low" },
              { label: "Medium & High", value: "medium" },
              { label: "High Only", value: "high" }
            ],
            availability: "active"
          },
          {
            id: "economics.showForecasts",
            label: "Show forecasts",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "economics.showPreviousValues",
            label: "Show previous values",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "rates",
        label: "Rates",
        settings: [
          {
            id: "economics.defaultCentralBank",
            label: "Default central bank",
            type: "select",
            defaultValue: "fed",
            options: [
              { label: "Federal Reserve (Fed)", value: "fed" },
              { label: "European Central Bank (ECB)", value: "ecb" },
              { label: "Bank of England (BoE)", value: "boe" },
              { label: "Bank of Japan (BoJ)", value: "boj" }
            ],
            availability: "active"
          },
          {
            id: "economics.yieldCurveMaturityDisplay",
            label: "Yield curve maturity display",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "data",
        label: "Data",
        settings: [
          {
            id: "economics.seasonalAdjustment",
            label: "Seasonal adjustment preference",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  news: defineModuleSettings({
    moduleId: "news",
    title: "News Settings",
    description: "Configure how News displays and behaves.",
    storageNamespace: "atlas.section-settings.news.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "news.defaultCategory",
            label: "Default news category",
            type: "select",
            defaultValue: "all",
            options: [
              { label: "All", value: "all" },
              { label: "Markets", value: "markets" },
              { label: "Companies", value: "companies" },
              { label: "Economics", value: "economics" },
              { label: "Geopolitics", value: "geopolitics" }
            ],
            availability: "active"
          },
          {
            id: "news.defaultRegion",
            label: "Default region",
            type: "select",
            defaultValue: "global",
            options: [
              { label: "Global", value: "global" },
              { label: "US", value: "us" },
              { label: "Europe", value: "europe" },
              { label: "Asia", value: "asia" }
            ],
            availability: "active"
          },
          {
            id: "news.defaultLanguage",
            label: "Default language",
            type: "select",
            defaultValue: "en",
            options: [
              { label: "English", value: "en" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "display",
        label: "Display",
        settings: [
          {
            id: "news.compactHeadlines",
            label: "Compact headlines",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "news.showThumbnails",
            label: "Show thumbnails",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "news.showSource",
            label: "Show source",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "news.showTimestamps",
            label: "Show timestamps",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "intelligence",
        label: "Intelligence",
        settings: [
          {
            id: "news.showSentiment",
            label: "Show sentiment",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "news.showImportanceScore",
            label: "Show importance score",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "news.showEntityTags",
            label: "Show entity tags",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "news.showAiSummary",
            label: "Show AI summary",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "storyClustering",
        label: "Story Clustering",
        settings: [
          {
            id: "news.groupRelatedStories",
            label: "Group related stories",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "filters",
        label: "Filters",
        settings: [
          {
            id: "news.hideDuplicates",
            label: "Hide duplicates",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "news.portfolioOnlyMode",
            label: "Portfolio-only mode",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "alerts",
        label: "Alerts",
        settings: [
          {
            id: "news.breakingNewsAlert",
            label: "Breaking-news alert",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  research: defineModuleSettings({
    moduleId: "research",
    title: "Research Settings",
    description: "Configure how Research displays and behaves.",
    storageNamespace: "atlas.section-settings.research.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "research.defaultView",
            label: "Default research view",
            type: "select",
            defaultValue: "library",
            options: [
              { label: "Library", value: "library" },
              { label: "Recent", value: "recent" },
              { label: "Favorites", value: "favorites" }
            ],
            availability: "active"
          },
          {
            id: "research.defaultDocumentSort",
            label: "Default document sort",
            type: "select",
            defaultValue: "newest",
            options: [
              { label: "Newest first", value: "newest" },
              { label: "Oldest first", value: "oldest" },
              { label: "Title A-Z", value: "title" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "documentViewer",
        label: "Document Viewer",
        settings: [
          {
            id: "research.readingWidth",
            label: "Reading width",
            type: "select",
            defaultValue: "normal",
            options: [
              { label: "Narrow", value: "narrow" },
              { label: "Normal", value: "normal" },
              { label: "Wide", value: "wide" },
              { label: "Full", value: "full" }
            ],
            availability: "active"
          },
          {
            id: "research.fontSize",
            label: "Font size",
            type: "select",
            defaultValue: "medium",
            options: [
              { label: "Small", value: "small" },
              { label: "Medium", value: "medium" },
              { label: "Large", value: "large" }
            ],
            availability: "active"
          },
          {
            id: "research.showMetadataPanel",
            label: "Show metadata panel",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "research.showCitationsPanel",
            label: "Show citations panel",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "library",
        label: "Library",
        settings: [
          {
            id: "research.rowDensity",
            label: "Row density",
            type: "select",
            defaultValue: "default",
            options: [
              { label: "Compact", value: "compact" },
              { label: "Default", value: "default" },
              { label: "Comfortable", value: "comfortable" }
            ],
            availability: "active"
          },
          {
            id: "research.showTags",
            label: "Show tags",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "research.showSource",
            label: "Show source",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "research.showDate",
            label: "Show date",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "aiResearch",
        label: "AI Research",
        settings: [
          {
            id: "research.autoCitations",
            label: "Auto-citations",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "research.multiDocumentContext",
            label: "Multi-document context",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "notes",
        label: "Notes",
        settings: [
          {
            id: "research.autoSaveNotes",
            label: "Auto-save notes",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "semanticSearch",
        label: "Semantic Search",
        settings: [
          {
            id: "research.resultCount",
            label: "Result count",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  maps: defineModuleSettings({
    moduleId: "maps",
    title: "Maps Settings",
    description: "Configure how Maps displays and behaves.",
    storageNamespace: "atlas.section-settings.maps.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "maps.defaultMapMode",
            label: "Default map mode",
            type: "select",
            defaultValue: "standard",
            options: [
              { label: "Standard", value: "standard" },
              { label: "Dark", value: "dark" },
              { label: "Light", value: "light" }
            ],
            availability: "active"
          },
          {
            id: "maps.default2d3dView",
            label: "Default 2D/3D view",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "maps.restoreCameraPosition",
            label: "Restore last camera position",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "basemap",
        label: "Basemap",
        settings: [
          {
            id: "maps.satellite",
            label: "Satellite",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "maps.terrain",
            label: "Terrain",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "labels",
        label: "Labels",
        settings: [
          {
            id: "maps.placeLabels",
            label: "Place labels",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "maps.countryLabels",
            label: "Country labels",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "maps.facilityLabels",
            label: "Facility labels",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "performance",
        label: "Performance",
        settings: [
          {
            id: "maps.detailLevel",
            label: "Detail level",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "maps.maxVisibleEntities",
            label: "Max visible entities",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "maps.clusterEntities",
            label: "Cluster entities",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "layers",
        label: "Layers",
        settings: [
          {
            id: "maps.rememberActiveLayers",
            label: "Remember active layers",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "maps.defaultLayerGroup",
            label: "Default layer group",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "interactions",
        label: "Interactions",
        settings: [
          {
            id: "maps.hoverDetails",
            label: "Hover details",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "maps.clickInspector",
            label: "Click inspector",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "maps.showCoordinates",
            label: "Show coordinates",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          }
        ]
      },
      {
        id: "visualization",
        label: "Visualization",
        settings: [
          {
            id: "maps.trails",
            label: "Trails",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "maps.heatmaps",
            label: "Heatmaps",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "maps.h3Overlay",
            label: "H3 overlay",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "godsEye",
        label: "God's Eye",
        settings: [
          {
            id: "maps.timeline",
            label: "Timeline",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "maps.liveEvents",
            label: "Live events",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  intelligence: defineModuleSettings({
    moduleId: "intelligence",
    title: "Intelligence Settings",
    description: "Configure how Intelligence displays and behaves.",
    storageNamespace: "atlas.section-settings.intelligence.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "intelligence.defaultView",
            label: "Default intelligence view",
            type: "select",
            defaultValue: "feed",
            options: [
              { label: "Feed", value: "feed" },
              { label: "Map", value: "map" },
              { label: "Graph", value: "graph" }
            ],
            availability: "active"
          },
          {
            id: "intelligence.defaultTimeHorizon",
            label: "Default time horizon",
            type: "select",
            defaultValue: "24h",
            options: [
              { label: "1 Hour", value: "1h" },
              { label: "12 Hours", value: "12h" },
              { label: "24 Hours", value: "24h" },
              { label: "7 Days", value: "7d" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "signals",
        label: "Signals",
        settings: [
          {
            id: "intelligence.minimumConfidence",
            label: "Minimum confidence",
            type: "select",
            defaultValue: "medium",
            options: [
              { label: "Low", value: "low" },
              { label: "Medium", value: "medium" },
              { label: "High", value: "high" }
            ],
            availability: "active"
          },
          {
            id: "intelligence.minimumSeverity",
            label: "Minimum severity",
            type: "select",
            defaultValue: "info",
            options: [
              { label: "Info", value: "info" },
              { label: "Low", value: "low" },
              { label: "Medium", value: "medium" },
              { label: "High", value: "high" },
              { label: "Critical", value: "critical" }
            ],
            availability: "active"
          },
          {
            id: "intelligence.showLowConfidenceSignals",
            label: "Show low-confidence signals",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          }
        ]
      },
      {
        id: "events",
        label: "Events",
        settings: [
          {
            id: "intelligence.eventCategories",
            label: "Event categories",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "intelligence.geographicFiltering",
            label: "Geographic filtering",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "scoring",
        label: "Scoring",
        settings: [
          {
            id: "intelligence.showConfidence",
            label: "Show confidence",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "intelligence.showSeverity",
            label: "Show severity",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "intelligence.showPortfolioRelevance",
            label: "Show portfolio relevance",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "feed",
        label: "Feed",
        settings: [
          {
            id: "intelligence.compactMode",
            label: "Compact mode",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "intelligence.groupSimilarEvents",
            label: "Group similar events",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "map",
        label: "Map",
        settings: [
          {
            id: "intelligence.autoOpenImportantEvents",
            label: "Auto-open important geographic events",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "ai",
        label: "AI",
        settings: [
          {
            id: "intelligence.aiExplanation",
            label: "AI explanation",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  options: defineModuleSettings({
    moduleId: "options",
    title: "Options Settings",
    description: "Configure how Options displays and behaves.",
    storageNamespace: "atlas.section-settings.options.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "options.defaultExpiration",
            label: "Default expiration",
            type: "select",
            defaultValue: "near",
            options: [
              { label: "Nearest", value: "near" },
              { label: "Next month", value: "next-month" }
            ],
            availability: "active"
          },
          {
            id: "options.defaultStrikesAroundSpot",
            label: "Default strikes around spot",
            type: "select",
            defaultValue: 10,
            options: [
              { label: "5", value: 5 },
              { label: "10", value: 10 },
              { label: "20", value: 20 },
              { label: "All", value: 100 }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "chain",
        label: "Chain",
        settings: [
          {
            id: "options.callsPutsLayout",
            label: "Calls/puts layout",
            type: "select",
            defaultValue: "side-by-side",
            options: [
              { label: "Side-by-side", value: "side-by-side" },
              { label: "Stacked", value: "stacked" }
            ],
            availability: "active"
          },
          {
            id: "options.showIv",
            label: "Show IV",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "options.showGreeks",
            label: "Show Greeks",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "options.showVolume",
            label: "Show volume",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "options.showOpenInterest",
            label: "Show open interest",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "greeks",
        label: "Greeks",
        settings: [
          {
            id: "options.delta",
            label: "Delta",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "options.gamma",
            label: "Gamma",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "options.theta",
            label: "Theta",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "options.vega",
            label: "Vega",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "options.rho",
            label: "Rho",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          }
        ]
      },
      {
        id: "volatility",
        label: "Volatility",
        settings: [
          {
            id: "options.defaultIvView",
            label: "Default IV view",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "strategies",
        label: "Strategies",
        settings: [
          {
            id: "options.defaultStrategyView",
            label: "Default strategy view",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "pricing",
        label: "Pricing",
        settings: [
          {
            id: "options.pricingModel",
            label: "Pricing model",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "risk",
        label: "Risk",
        settings: [
          {
            id: "options.showPayoffAtExpiration",
            label: "Show payoff at expiration",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  trading: defineModuleSettings({
    moduleId: "trading",
    title: "Trading Settings",
    description: "Configure how Trading displays and behaves.",
    storageNamespace: "atlas.section-settings.trading.v1",
    version: 1,
    groups: [
      {
        id: "display",
        label: "Display",
        settings: [
          {
            id: "trading.defaultMode",
            label: "Default mode",
            type: "select",
            defaultValue: "paper",
            options: [
              { label: "Paper", value: "paper" }
            ],
            availability: "active"
          },
          {
            id: "trading.showEstimatedValue",
            label: "Show estimated value",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "trading.showFees",
            label: "Show fees",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "trading.chartTrading",
            label: "Chart trading",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "orderDefaults",
        label: "Order Defaults",
        settings: [
          {
            id: "trading.defaultOrderType",
            label: "Default order type",
            type: "select",
            defaultValue: "limit",
            options: [
              { label: "Limit", value: "limit" },
              { label: "Market", value: "market" },
              { label: "Stop", value: "stop" }
            ],
            availability: "active"
          },
          {
            id: "trading.defaultDuration",
            label: "Default duration",
            type: "select",
            defaultValue: "day",
            options: [
              { label: "Day", value: "day" },
              { label: "GTC", value: "gtc" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "confirmation",
        label: "Confirmation",
        settings: [
          {
            id: "trading.confirmBeforeSubmit",
            label: "Confirm before order submission",
            description: "Safety policy requirement.",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "trading.confirmBeforeCancelAll",
            label: "Confirm before cancel-all",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "liveTrading",
        label: "Live Trading Foundation",
        settings: [
          {
            id: "trading.liveTrading",
            label: "Live trading",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  portfolios: defineModuleSettings({
    moduleId: "portfolios",
    title: "Portfolios Settings",
    description: "Configure how Portfolios displays and behaves.",
    storageNamespace: "atlas.section-settings.portfolios.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "portfolios.defaultPortfolio",
            label: "Default portfolio",
            type: "select",
            defaultValue: "all",
            options: [
              { label: "All Accounts", value: "all" }
            ],
            availability: "active"
          },
          {
            id: "portfolios.defaultBenchmark",
            label: "Default benchmark",
            type: "select",
            defaultValue: "spy",
            options: [
              { label: "S&P 500 (SPY)", value: "spy" },
              { label: "Nasdaq 100 (QQQ)", value: "qqq" },
              { label: "MSCI World", value: "urth" }
            ],
            availability: "active"
          },
          {
            id: "portfolios.baseCurrency",
            label: "Base currency",
            type: "select",
            defaultValue: "usd",
            options: [
              { label: "USD", value: "usd" },
              { label: "EUR", value: "eur" },
              { label: "GBP", value: "gbp" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "performance",
        label: "Performance",
        settings: [
          {
            id: "portfolios.defaultPeriod",
            label: "Default period",
            type: "select",
            defaultValue: "ytd",
            options: [
              { label: "1 Month", value: "1m" },
              { label: "3 Months", value: "3m" },
              { label: "YTD", value: "ytd" },
              { label: "1 Year", value: "1y" },
              { label: "All Time", value: "all" }
            ],
            availability: "active"
          },
          {
            id: "portfolios.annualizedReturns",
            label: "Annualized returns",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "portfolios.includeDividends",
            label: "Include dividends",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "holdings",
        label: "Holdings",
        settings: [
          {
            id: "portfolios.rowDensity",
            label: "Row density",
            type: "select",
            defaultValue: "default",
            options: [
              { label: "Compact", value: "compact" },
              { label: "Default", value: "default" },
              { label: "Comfortable", value: "comfortable" }
            ],
            availability: "active"
          },
          {
            id: "portfolios.showUnrealizedPl",
            label: "Show unrealized P&L",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "portfolios.showDailyPl",
            label: "Show daily P&L",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "portfolios.showAllocation",
            label: "Show allocation",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "allocation",
        label: "Allocation",
        settings: [
          {
            id: "portfolios.defaultGrouping",
            label: "Default grouping",
            type: "select",
            defaultValue: "assetClass",
            options: [
              { label: "Asset Class", value: "assetClass" },
              { label: "Sector", value: "sector" },
              { label: "Country", value: "country" },
              { label: "Currency", value: "currency" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "charts",
        label: "Charts",
        settings: [
          {
            id: "portfolios.defaultPerformanceChart",
            label: "Default performance chart",
            type: "select",
            defaultValue: "cumulative",
            options: [
              { label: "Cumulative", value: "cumulative" },
              { label: "Daily Return", value: "daily" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "transactions",
        label: "Transactions",
        settings: [
          {
            id: "portfolios.defaultTransactionView",
            label: "Default transaction view",
            type: "select",
            defaultValue: "list",
            options: [
              { label: "List", value: "list" },
              { label: "Summary", value: "summary" }
            ],
            availability: "active"
          }
        ]
      }
    ]
  }),

  risk: defineModuleSettings({
    moduleId: "risk",
    title: "Risk Settings",
    description: "Configure how Risk displays and behaves.",
    storageNamespace: "atlas.section-settings.risk.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "risk.defaultPortfolio",
            label: "Default portfolio",
            type: "select",
            defaultValue: "all",
            options: [
              { label: "All Accounts", value: "all" }
            ],
            availability: "active"
          },
          {
            id: "risk.defaultRiskHorizon",
            label: "Default risk horizon",
            type: "select",
            defaultValue: "1y",
            options: [
              { label: "1 Month", value: "1m" },
              { label: "3 Months", value: "3m" },
              { label: "1 Year", value: "1y" },
              { label: "3 Years", value: "3y" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "metrics",
        label: "Metrics",
        settings: [
          {
            id: "risk.showVolatility",
            label: "Show volatility",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "risk.showBeta",
            label: "Show beta",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "risk.showSharpe",
            label: "Show Sharpe",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "risk.showDrawdown",
            label: "Show drawdown",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "var",
        label: "VaR",
        settings: [
          {
            id: "risk.confidenceLevel",
            label: "Confidence level",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "risk.horizon",
            label: "Horizon",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "risk.method",
            label: "Method",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "stress",
        label: "Stress",
        settings: [
          {
            id: "risk.defaultScenario",
            label: "Default scenario",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "concentration",
        label: "Concentration",
        settings: [
          {
            id: "risk.threshold",
            label: "Threshold",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "colors",
        label: "Risk Colors",
        settings: [
          {
            id: "risk.useStandardAtlasScale",
            label: "Use standard ATLAS risk scale",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      }
    ]
  }),

  ai: defineModuleSettings({
    moduleId: "ai",
    title: "AI Assistant Settings",
    description: "Configure how AI Assistant displays and behaves.",
    storageNamespace: "atlas.section-settings.ai.v1",
    version: 1,
    groups: [
      {
        id: "workspace",
        label: "Workspace",
        settings: [
          {
            id: "ai.showContextPanel",
            label: "Show context panel",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "ai.showSourcesPanel",
            label: "Show sources panel",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "ai.showToolActivity",
            label: "Show tool activity",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "ai.showArtifacts",
            label: "Show artifacts",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "conversation",
        label: "Conversation",
        settings: [
          {
            id: "ai.enterToSend",
            label: "Enter to send",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "ai.showTimestamps",
            label: "Show timestamps",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "ai.collapseToolTraces",
            label: "Collapse tool traces",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "research",
        label: "Research",
        settings: [
          {
            id: "ai.showCitationsByDefault",
            label: "Show citations by default",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "ai.openGeneratedTablesInline",
            label: "Open generated tables inline",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "context",
        label: "Context",
        settings: [
          {
            id: "ai.autoIncludeCurrentEntity",
            label: "Automatically include current entity",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "ai.autoIncludeCurrentWorkspace",
            label: "Automatically include current workspace",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  data: defineModuleSettings({
    moduleId: "data",
    title: "Data Settings",
    description: "Configure how Data displays and behaves.",
    storageNamespace: "atlas.section-settings.data.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "data.defaultDataView",
            label: "Default Data view",
            type: "select",
            defaultValue: "catalog",
            options: [
              { label: "Catalog", value: "catalog" },
              { label: "Queries", value: "queries" },
              { label: "Connections", value: "connections" }
            ],
            availability: "active"
          },
          {
            id: "data.defaultDatasetPreviewRows",
            label: "Default dataset preview rows",
            type: "select",
            defaultValue: 100,
            options: [
              { label: "10", value: 10 },
              { label: "100", value: 100 },
              { label: "1000", value: 1000 }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "tables",
        label: "Tables",
        settings: [
          {
            id: "data.rowDensity",
            label: "Row density",
            type: "select",
            defaultValue: "compact",
            options: [
              { label: "Compact", value: "compact" },
              { label: "Default", value: "default" },
              { label: "Comfortable", value: "comfortable" }
            ],
            availability: "active"
          },
          {
            id: "data.stickyHeaders",
            label: "Sticky headers",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "data.showDataTypes",
            label: "Show data types",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "queryStudio",
        label: "Query Studio",
        settings: [
          {
            id: "data.defaultLanguage",
            label: "Default language",
            type: "select",
            defaultValue: "sql",
            options: [
              { label: "SQL", value: "sql" },
              { label: "Python", value: "python" }
            ],
            availability: "active"
          },
          {
            id: "data.autoRunQuery",
            label: "Auto-run query",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          }
        ]
      },
      {
        id: "schema",
        label: "Schema",
        settings: [
          {
            id: "data.showNullable",
            label: "Show nullable",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "data.showKeys",
            label: "Show keys",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "data.showDescriptions",
            label: "Show descriptions",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "exports",
        label: "Exports",
        settings: [
          {
            id: "data.defaultFormat",
            label: "Default format",
            type: "select",
            defaultValue: "csv",
            options: [
              { label: "CSV", value: "csv" },
              { label: "JSON", value: "json" },
              { label: "Parquet", value: "parquet" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "provenance",
        label: "Provenance",
        settings: [
          {
            id: "data.showSourceMetadata",
            label: "Show source metadata",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "data.showRetrievalTimestamps",
            label: "Show retrieval timestamps",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          }
        ]
      }
    ]
  }),

  saved: defineModuleSettings({
    moduleId: "saved",
    title: "Saved Settings",
    description: "Configure how Saved displays and behaves.",
    storageNamespace: "atlas.section-settings.saved.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "saved.defaultView",
            label: "Default Saved view",
            type: "select",
            defaultValue: "all",
            options: [
              { label: "All Items", value: "all" },
              { label: "Collections", value: "collections" },
              { label: "Recent", value: "recent" }
            ],
            availability: "active"
          },
          {
            id: "saved.defaultSort",
            label: "Default sort",
            type: "select",
            defaultValue: "newest",
            options: [
              { label: "Newest first", value: "newest" },
              { label: "Oldest first", value: "oldest" },
              { label: "Alphabetical", value: "alpha" }
            ],
            availability: "active"
          },
          {
            id: "saved.defaultCollection",
            label: "Default collection",
            type: "select",
            defaultValue: "inbox",
            options: [
              { label: "Inbox", value: "inbox" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "display",
        label: "Display",
        settings: [
          {
            id: "saved.compactList",
            label: "Compact list",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "saved.showPreviewPanel",
            label: "Show preview panel",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "saved.showTags",
            label: "Show tags",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "saved.showMetadata",
            label: "Show metadata",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "behavior",
        label: "Behavior",
        settings: [
          {
            id: "saved.openInCurrentWorkspace",
            label: "Open saved item in current workspace",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "saved.askBeforeRemovingPinned",
            label: "Ask before removing pinned item",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "types",
        label: "Types",
        settings: [
          {
            id: "saved.showHideCategories",
            label: "Show/hide categories",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  workspaces: defineModuleSettings({
    moduleId: "workspaces",
    title: "Workspaces Settings",
    description: "Configure how Workspaces displays and behaves.",
    storageNamespace: "atlas.section-settings.workspaces.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "workspaces.defaultWorkspace",
            label: "Default workspace",
            type: "select",
            defaultValue: "default",
            options: [
              { label: "Default", value: "default" }
            ],
            availability: "active"
          },
          {
            id: "workspaces.restoreLastWorkspace",
            label: "Restore last workspace",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "workspaces.openWorkspaceOnLaunch",
            label: "Open workspace on launch",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "layout",
        label: "Layout",
        settings: [
          {
            id: "workspaces.showGridGuides",
            label: "Show grid guides",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "workspaces.snapPanels",
            label: "Snap panels",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "workspaces.defaultGap",
            label: "Default gap",
            type: "select",
            defaultValue: 8,
            options: [
              { label: "0px", value: 0 },
              { label: "4px", value: 4 },
              { label: "8px", value: 8 },
              { label: "16px", value: 16 }
            ],
            availability: "active"
          },
          {
            id: "workspaces.preservePanelSizes",
            label: "Preserve panel sizes",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "behavior",
        label: "Behavior",
        settings: [
          {
            id: "workspaces.confirmWorkspaceDelete",
            label: "Confirm workspace delete",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "workspaces.autoSaveLayouts",
            label: "Auto-save layouts",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "display",
        label: "Display",
        settings: [
          {
            id: "workspaces.showWorkspacePreviews",
            label: "Show workspace previews",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "workspaces.showTemplateDescriptions",
            label: "Show template descriptions",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "background",
        label: "Background",
        settings: [
          {
            id: "workspaces.useGlobalBackground",
            label: "Use Global",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "workspaces.workspaceOverride",
            label: "Workspace override",
            type: "foundation",
            availability: "foundation"
          }
        ]
      }
    ]
  }),

  agents: defineModuleSettings({
    moduleId: "agents",
    title: "Agents Settings",
    description: "Configure how Agents displays and behaves.",
    storageNamespace: "atlas.section-settings.agents.v1",
    version: 1,
    groups: [
      {
        id: "general",
        label: "General",
        settings: [
          {
            id: "agents.defaultView",
            label: "Default Agents view",
            type: "select",
            defaultValue: "fleet",
            options: [
              { label: "Fleet", value: "fleet" },
              { label: "Tasks", value: "tasks" },
              { label: "Workflows", value: "workflows" }
            ],
            availability: "active"
          },
          {
            id: "agents.showDisabledAgents",
            label: "Show disabled agents",
            type: "boolean",
            defaultValue: false,
            availability: "active"
          },
          {
            id: "agents.showStatusIndicators",
            label: "Show status indicators",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "tables",
        label: "Tables",
        settings: [
          {
            id: "agents.showCost",
            label: "Show cost",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "agents.showModel",
            label: "Show model",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "agents.showAutonomy",
            label: "Show autonomy",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "agents.showLastRun",
            label: "Show last run",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      },
      {
        id: "workflowStudio",
        label: "Workflow Studio",
        settings: [
          {
            id: "agents.showGrid",
            label: "Show grid",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "agents.snapNodes",
            label: "Snap nodes",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "agents.showMinimap",
            label: "Show minimap",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "agents.showNodeIds",
            label: "Show node IDs",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "runs",
        label: "Runs",
        settings: [
          {
            id: "agents.autoOpenFailedRuns",
            label: "Auto-open failed runs",
            type: "foundation",
            availability: "foundation"
          },
          {
            id: "agents.showToolCalls",
            label: "Show tool calls",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "logs",
        label: "Logs",
        settings: [
          {
            id: "agents.defaultLogLevel",
            label: "Default log level",
            type: "foundation",
            availability: "foundation"
          }
        ]
      },
      {
        id: "costs",
        label: "Costs",
        settings: [
          {
            id: "agents.showEstimatedCost",
            label: "Show estimated cost",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "agents.defaultPeriod",
            label: "Default period",
            type: "select",
            defaultValue: "this-month",
            options: [
              { label: "Today", value: "today" },
              { label: "This Week", value: "this-week" },
              { label: "This Month", value: "this-month" },
              { label: "All Time", value: "all" }
            ],
            availability: "active"
          }
        ]
      },
      {
        id: "safety",
        label: "Safety",
        settings: [
          {
            id: "agents.showApprovalQueue",
            label: "Show approval queue",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          },
          {
            id: "agents.highlightExternalActions",
            label: "Highlight external actions",
            type: "boolean",
            defaultValue: true,
            availability: "active"
          }
        ]
      }
    ]
  })
};
