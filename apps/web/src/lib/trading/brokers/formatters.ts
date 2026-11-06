/**
 * ATLAS Stage 145: Broker Abstraction formatters.
 */

import type { BrokerAuthMethod, BrokerConnection, BrokerProvider, ConnectionStatus } from "./types";

export function formatConnectionStatus(status: ConnectionStatus): string {
  switch (status) {
    case "CONNECTED": return "Connected";
    case "DISCONNECTED": return "Disconnected";
    case "ERROR": return "Error";
    case "PENDING": return "Pending";
    case "RATE_LIMITED": return "Rate Limited";
    default: return status;
  }
}

export function statusColor(status: ConnectionStatus): string {
  switch (status) {
    case "CONNECTED": return "text-green-400";
    case "DISCONNECTED": return "text-gray-500";
    case "ERROR": return "text-red-400";
    case "PENDING": return "text-yellow-400";
    case "RATE_LIMITED": return "text-orange-400";
    default: return "text-gray-400";
  }
}

export function formatAuthMethod(method: BrokerAuthMethod): string {
  switch (method) {
    case "API_KEY": return "API Key";
    case "OAUTH2": return "OAuth 2.0";
    case "CLIENT_CREDENTIALS": return "Client Credentials";
    default: return method;
  }
}

export function formatProviderBadge(provider: BrokerProvider): string {
  return provider.is_sandbox ? "[SANDBOX]" : "[LIVE]";
}

export function isSandboxProvider(provider: BrokerProvider): boolean {
  return provider.is_sandbox;
}

export function maskApiKey(key: string): string {
  if (!key || key.length < 8) return "••••••••";
  return key.slice(0, 4) + "••••••••" + key.slice(-4);
}

export function connectionAge(connection: BrokerConnection): string {
  try {
    const created = new Date(connection.created_at);
    const diff = Date.now() - created.getTime();
    const days = Math.floor(diff / 86400000);
    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    return `${days}d ago`;
  } catch {
    return "—";
  }
}
