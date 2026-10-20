import React from "react";
import { WifiOff, RefreshCw } from "lucide-react";
import { RealtimeConnectionState } from "@/lib/realtime/types";

interface WatchlistConnectionStatusProps {
  connectionState: RealtimeConnectionState;
  onReconnect?: () => void;
}

export function WatchlistConnectionStatus({
  connectionState,
  onReconnect,
}: WatchlistConnectionStatusProps) {
  let dotColor = "bg-zinc-500";
  let label = "Disconnected";
  let isConnecting = false;

  switch (connectionState) {
    case "CONNECTED":
      dotColor = "bg-emerald-400";
      label = "Connected";
      break;
    case "CONNECTING":
      dotColor = "bg-amber-400";
      label = "Connecting...";
      isConnecting = true;
      break;
    case "RECONNECTING":
      dotColor = "bg-amber-400";
      label = "Reconnecting...";
      isConnecting = true;
      break;
    case "ERROR":
      dotColor = "bg-rose-400";
      label = "Connection Error";
      break;
    case "DISCONNECTED":
    default:
      dotColor = "bg-zinc-500";
      label = "Disconnected";
      break;
  }

  return (
    <div
      className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-zinc-900 border border-zinc-800 text-[11px] text-zinc-300 select-none"
      title={`Market Data WebSocket: ${label}`}
      role="status"
      aria-live="polite"
    >
      {isConnecting ? (
        <RefreshCw className="w-3 h-3 text-amber-400 animate-spin" aria-hidden="true" />
      ) : connectionState === "CONNECTED" ? (
        <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} aria-hidden="true" />
      ) : (
        <WifiOff className="w-3 h-3 text-zinc-500" aria-hidden="true" />
      )}
      <span className="font-mono text-[10px] text-zinc-400">{label}</span>

      {(connectionState === "DISCONNECTED" || connectionState === "ERROR") && onReconnect && (
        <button
          type="button"
          onClick={onReconnect}
          className="ml-1 text-[10px] text-sky-400 hover:text-sky-300 underline underline-offset-2"
          title="Reconnect to live market data"
        >
          Retry
        </button>
      )}
    </div>
  );
}
