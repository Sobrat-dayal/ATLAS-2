import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  formatConnectionStatus,
  statusColor,
  formatAuthMethod,
  formatProviderBadge,
  isSandboxProvider,
  maskApiKey,
} from "../formatters.js";
import type { BrokerProvider } from "../types.js";

const sandboxProvider: BrokerProvider = {
  provider_id: "alpaca_paper",
  display_name: "Alpaca Paper Trading",
  description: "Alpaca sandbox",
  auth_method: "API_KEY",
  sandbox_base_url: "https://paper-api.alpaca.markets",
  is_sandbox: true,
  logo_key: "alpaca",
  capabilities: {
    supports_market_orders: true,
    supports_limit_orders: true,
    supports_stop_orders: true,
    supports_options: false,
    supports_streaming: true,
    supports_fractional: true,
    base_currency: "USD",
    asset_classes: ["EQUITY"],
  },
};

describe("broker formatters", () => {
  it("formatConnectionStatus returns readable string for CONNECTED", () => {
    assert.equal(formatConnectionStatus("CONNECTED"), "Connected");
  });

  it("formatConnectionStatus handles ERROR", () => {
    assert.equal(formatConnectionStatus("ERROR"), "Error");
  });

  it("statusColor returns green for CONNECTED", () => {
    assert.ok(statusColor("CONNECTED").includes("green"));
  });

  it("statusColor returns red for ERROR", () => {
    assert.ok(statusColor("ERROR").includes("red"));
  });

  it("formatAuthMethod returns API Key for API_KEY", () => {
    assert.equal(formatAuthMethod("API_KEY"), "API Key");
  });

  it("formatProviderBadge returns [SANDBOX] for sandbox provider", () => {
    assert.equal(formatProviderBadge(sandboxProvider), "[SANDBOX]");
  });

  it("isSandboxProvider returns true for sandbox provider", () => {
    assert.equal(isSandboxProvider(sandboxProvider), true);
  });

  it("maskApiKey masks the middle portion", () => {
    const masked = maskApiKey("ABCDEFGH1234");
    assert.ok(masked.includes("••••••••"));
    assert.ok(masked.startsWith("ABCD"));
    assert.ok(masked.endsWith("1234"));
  });

  it("maskApiKey handles short keys", () => {
    const masked = maskApiKey("short");
    assert.equal(masked, "••••••••");
  });
});
