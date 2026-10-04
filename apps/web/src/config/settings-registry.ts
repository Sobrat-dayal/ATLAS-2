import {
  SlidersHorizontal,
  Palette,
  User,
  Shield,
  EyeOff,
  Bell,
  Bot,
  Cpu,
  Network,
  Plug,
  Key,
  Database,
  Activity,
  ArrowLeftRight,
  Landmark,
  HardDrive,
  Cable,
  Code2,
  Terminal,
  Keyboard,
  Accessibility,
  CreditCard,
  Settings2,
  LucideIcon
} from "lucide-react";

export type SettingsAvailability = "active" | "foundation" | "unavailable";
export type SettingsCategoryId =
  | "general"
  | "appearance"
  | "account"
  | "security"
  | "privacy"
  | "notifications"
  | "ai"
  | "models"
  | "agents"
  | "mcp"
  | "apiKeys"
  | "dataProviders"
  | "marketData"
  | "trading"
  | "brokers"
  | "storage"
  | "integrations"
  | "developer"
  | "terminal"
  | "keyboard"
  | "accessibility"
  | "billing"
  | "advanced";

export interface SettingsCategory {
  id: SettingsCategoryId;
  label: string;
  route: string;
  icon: LucideIcon;
  description: string;
  keywords: string[];
  availability: SettingsAvailability;
  order: number;
}

export const SETTINGS_CATEGORIES: SettingsCategory[] = [
  {
    id: "general",
    label: "General",
    route: "/settings/general",
    icon: SlidersHorizontal,
    description: "Startup, application behavior, language, and global preferences.",
    keywords: ["startup", "behavior", "language", "time", "date", "reset"],
    availability: "active",
    order: 10,
  },
  {
    id: "appearance",
    label: "Appearance",
    route: "/settings/appearance",
    icon: Palette,
    description: "Control ATLAS theme, density, accent and background.",
    keywords: ["theme", "dark", "light", "density", "compact", "accent", "color", "background", "wallpaper"],
    availability: "active",
    order: 20,
  },
  {
    id: "account",
    label: "Account",
    route: "/settings/account",
    icon: User,
    description: "Manage your ATLAS profile and connected accounts.",
    keywords: ["profile", "email", "name", "organization", "delete"],
    availability: "foundation",
    order: 30,
  },
  {
    id: "security",
    label: "Security",
    route: "/settings/security",
    icon: Shield,
    description: "Password, MFA, and active sessions.",
    keywords: ["password", "mfa", "2fa", "sessions", "trusted", "api access"],
    availability: "foundation",
    order: 40,
  },
  {
    id: "privacy",
    label: "Privacy",
    route: "/settings/privacy",
    icon: EyeOff,
    description: "Telemetry, personalization, and data handling preferences.",
    keywords: ["telemetry", "ai data", "history", "retention"],
    availability: "foundation",
    order: 50,
  },
  {
    id: "notifications",
    label: "Notifications",
    route: "/settings/notifications",
    icon: Bell,
    description: "Configure in-app, push, email, and agent notifications.",
    keywords: ["alerts", "push", "email", "telegram", "market alerts", "news"],
    availability: "foundation",
    order: 60,
  },
  {
    id: "ai",
    label: "AI",
    route: "/settings/ai",
    icon: Bot,
    description: "Global AI configuration, defaults, and capabilities.",
    keywords: ["assistant", "reasoning", "tools", "web access", "citations"],
    availability: "foundation",
    order: 70,
  },
  {
    id: "models",
    label: "Models",
    route: "/settings/models",
    icon: Cpu,
    description: "Manage model providers, fallback routing, and costs.",
    keywords: ["provider", "local", "api", "context window"],
    availability: "foundation",
    order: 80,
  },
  {
    id: "agents",
    label: "Agents",
    route: "/settings/agents",
    icon: Network,
    description: "Agent autonomy, concurrency, and global execution defaults.",
    keywords: ["autonomy", "budget", "concurrency", "memory", "sandboxing"],
    availability: "foundation",
    order: 90,
  },
  {
    id: "mcp",
    label: "MCP",
    route: "/settings/mcp",
    icon: Plug,
    description: "Manage Model Context Protocol servers and tool access.",
    keywords: ["mcp", "servers", "tools", "transport"],
    availability: "foundation",
    order: 100,
  },
  {
    id: "apiKeys",
    label: "API Keys",
    route: "/settings/api-keys",
    icon: Key,
    description: "Secure vault for your external service credentials.",
    keywords: ["keys", "credentials", "secrets", "vault"],
    availability: "foundation",
    order: 110,
  },
  {
    id: "dataProviders",
    label: "Data Providers",
    route: "/settings/data-providers",
    icon: Database,
    description: "Configure sources for fundamentals, economics, and news.",
    keywords: ["financial data", "economics", "news", "alternative data"],
    availability: "foundation",
    order: 120,
  },
  {
    id: "marketData",
    label: "Market Data",
    route: "/settings/market-data",
    icon: Activity,
    description: "Default providers, delays, and exchange preferences.",
    keywords: ["real-time", "historical", "delayed", "extended hours"],
    availability: "foundation",
    order: 130,
  },
  {
    id: "trading",
    label: "Trading",
    route: "/settings/trading",
    icon: ArrowLeftRight,
    description: "Order confirmations, default order types, and risk checks.",
    keywords: ["paper", "confirmation", "limit", "risk"],
    availability: "foundation",
    order: 140,
  },
  {
    id: "brokers",
    label: "Brokers",
    route: "/settings/brokers",
    icon: Landmark,
    description: "Connected brokerages, live/sandbox modes, and permissions.",
    keywords: ["connected", "accounts", "sandbox", "health"],
    availability: "foundation",
    order: 150,
  },
  {
    id: "storage",
    label: "Storage",
    route: "/settings/storage",
    icon: HardDrive,
    description: "Manage local assets, caching, and data retention.",
    keywords: ["local", "background assets", "cache", "clear"],
    availability: "active", // partially active due to background local clear
    order: 160,
  },
  {
    id: "integrations",
    label: "Integrations",
    route: "/settings/integrations",
    icon: Cable,
    description: "Connections to GitHub, Drive, Discord, and other services.",
    keywords: ["github", "slack", "discord", "webhook"],
    availability: "foundation",
    order: 170,
  },
  {
    id: "developer",
    label: "Developer",
    route: "/settings/developer",
    icon: Code2,
    description: "Debug overlays, feature flags, and experimental tools.",
    keywords: ["debug", "experimental", "flags", "performance", "version"],
    availability: "active",
    order: 180,
  },
  {
    id: "terminal",
    label: "Terminal",
    route: "/settings/terminal",
    icon: Terminal,
    description: "Global terminal fonts, scrollback, and environment defaults.",
    keywords: ["font", "scrollback", "copy", "shell"],
    availability: "foundation",
    order: 190,
  },
  {
    id: "keyboard",
    label: "Keyboard",
    route: "/settings/keyboard",
    icon: Keyboard,
    description: "Keyboard shortcut discovery and management.",
    keywords: ["shortcuts", "hotkeys", "remapping", "command palette"],
    availability: "active",
    order: 200,
  },
  {
    id: "accessibility",
    label: "Accessibility",
    route: "/settings/accessibility",
    icon: Accessibility,
    description: "Reduced motion, high contrast, and focus indicators.",
    keywords: ["motion", "contrast", "vision", "focus"],
    availability: "active",
    order: 210,
  },
  {
    id: "billing",
    label: "Billing",
    route: "/settings/billing",
    icon: CreditCard,
    description: "Your ATLAS plan, usage limits, and invoices.",
    keywords: ["plan", "usage", "invoices", "payment", "costs"],
    availability: "foundation",
    order: 220,
  },
  {
    id: "advanced",
    label: "Advanced",
    route: "/settings/advanced",
    icon: Settings2,
    description: "Cache behavior, diagnostic tools, and deep resets.",
    keywords: ["reset", "diagnostics", "cache"],
    availability: "active",
    order: 230,
  }
];

export function getSettingsCategory(idOrRoute: string): SettingsCategory | undefined {
  return SETTINGS_CATEGORIES.find(c => c.id === idOrRoute || c.route === idOrRoute || c.route === `/settings/${idOrRoute}`);
}
