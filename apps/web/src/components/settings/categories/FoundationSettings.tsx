"use client";

import React from "react";
import { SettingsCategory } from "@/config/settings-registry";
import { SettingsGroup, SettingsRow, SettingsFoundationState } from "../SettingsControls";
import { Shield, Key, EyeOff, Plug, Database, Activity, Landmark, ArrowLeftRight, Terminal, User, Bell, Network, Bot, Cpu, Cable, CreditCard } from "lucide-react";

export function FoundationSettings({ category }: { category: SettingsCategory }) {
  // We can render some mock settings based on the category to show foundation structure
  
  const getMockSettings = () => {
    switch (category.id) {
      case "account":
        return [
          { label: "Profile Information", desc: "Manage your display name and avatar." },
          { label: "Connected Accounts", desc: "Link external authentication providers." },
          { label: "Organization", desc: "Your primary ATLAS organization." }
        ];
      case "security":
        return [
          { label: "Password", desc: "Change your account password." },
          { label: "Two-Factor Authentication", desc: "Add an extra layer of security." },
          { label: "Active Sessions", desc: "Manage your currently logged in devices." }
        ];
      case "privacy":
        return [
          { label: "Telemetry", desc: "Allow ATLAS to collect usage data." },
          { label: "AI Data Handling", desc: "Preferences for how your data is used in models." },
          { label: "History Retention", desc: "How long to keep activity logs." }
        ];
      case "notifications":
        return [
          { label: "In-App Alerts", desc: "Receive notifications within the application." },
          { label: "Push Notifications", desc: "Receive notifications on your device." },
          { label: "Email Summaries", desc: "Daily or weekly activity reports." }
        ];
      case "apiKeys":
        return [
          { label: "Secure Vault", desc: "Store credentials for external services." },
          { label: "Provider Keys", desc: "Manage individual API keys." }
        ];
      case "brokers":
        return [
          { label: "Connected Brokers", desc: "Link brokerage accounts for trading." },
          { label: "Sandbox Mode", desc: "Use paper trading credentials." }
        ];
      case "trading":
        return [
          { label: "Default Order Type", desc: "Limit, Market, or Stop." },
          { label: "Risk Confirmation", desc: "Require confirmation for all trades." }
        ];
      case "models":
        return [
          { label: "Connected Providers", desc: "Link Anthropic, OpenAI, or others." },
          { label: "Local Models", desc: "Configure local LLM execution." }
        ];
      case "ai":
        return [
          { label: "Default Assistant", desc: "Select the primary AI agent." },
          { label: "Tool Access", desc: "Allow AI to execute actions." }
        ];
      case "agents":
        return [
          { label: "Default Autonomy", desc: "Approval required vs autonomous." },
          { label: "Concurrency", desc: "Maximum simultaneous agent tasks." }
        ];
      case "mcp":
        return [
          { label: "Connected Servers", desc: "Manage Model Context Protocol connections." },
          { label: "Tool Permissions", desc: "Control which tools are exposed to agents." }
        ];
      case "dataProviders":
        return [
          { label: "Financial Data", desc: "Select default fundamental data source." },
          { label: "News Feed", desc: "Configure news aggregation sources." }
        ];
      case "marketData":
        return [
          { label: "Real-time Provider", desc: "Primary source for live quotes." },
          { label: "Delayed Data", desc: "Fallback policy when real-time is unavailable." }
        ];
      case "integrations":
        return [
          { label: "GitHub", desc: "Connect repositories." },
          { label: "Slack / Discord", desc: "Configure webhooks." }
        ];
      case "terminal":
        return [
          { label: "Default Shell", desc: "Bash, Zsh, or PowerShell." },
          { label: "Python Environment", desc: "Configure default virtualenv." }
        ];
      case "billing":
        return [
          { label: "Subscription Plan", desc: "Your current ATLAS tier." },
          { label: "Payment Method", desc: "Manage credit cards." },
          { label: "API Usage", desc: "Monitor metered costs." }
        ];
      default:
        return [
          { label: "Configuration", desc: "Settings for this feature." }
        ];
    }
  };

  const Icon = category.icon;
  const mockSettings = getMockSettings();

  return (
    <div className="space-y-6">
      <div className="p-6 border border-atlas-border-default bg-atlas-surface-1 rounded-md text-center flex flex-col items-center">
        <Icon className="h-10 w-10 text-atlas-text-muted mb-4 opacity-50" />
        <h3 className="text-lg font-medium text-atlas-text-primary mb-2">
          {category.label} Configuration
        </h3>
        <p className="text-atlas-text-muted max-w-md text-sm">
          This section is a structural foundation. {category.label} infrastructure will be implemented in a future stage.
        </p>
      </div>

      <SettingsGroup>
        {mockSettings.map((setting, idx) => (
          <SettingsRow 
            key={idx} 
            label={setting.label} 
            description={setting.desc}
          >
            <SettingsFoundationState />
          </SettingsRow>
        ))}
      </SettingsGroup>
    </div>
  );
}
