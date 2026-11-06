"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  Zap,
  TrendingUp,
  AlertTriangle,
  Play,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  Server,
  Lock,
  DollarSign,
  PlusCircle,
  FileText,
  Sliders,
  Activity,
  Layers,
} from "lucide-react";
import { BacktestingLab } from "./backtesting/BacktestingLab";
import {
  listPaperAccounts,
  createPaperAccount,
  submitPaperOrder,
  listPaperOrders,
  cancelPaperOrder,
  listPaperPositions,
  activatePaperKillSwitch,
} from "@/lib/trading/paper/api";
import type { PaperAccount, PaperOrder, PaperPosition } from "@/lib/trading/paper/types";
import {
  listBrokerProviders,
  listBrokerConnections,
  createBrokerConnection,
  verifyBrokerConnection,
  previewBrokerOrder,
  submitBrokerOrder,
  type SandboxBrokerProvider,
  type SandboxBrokerConnection,
} from "@/lib/trading/brokers/api";

export function TradingCockpit() {
  const [activeTab, setActiveTab] = useState<"PAPER" | "BROKERS" | "BACKTEST">("PAPER");

  // Paper Trading State
  const [accounts, setAccounts] = useState<PaperAccount[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string>("");
  const [orders, setOrders] = useState<PaperOrder[]>([]);
  const [positions, setPositions] = useState<PaperPosition[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // New Paper Account Form
  const [newAccName, setNewAccName] = useState("");
  const [newAccCash, setNewAccCash] = useState(100000);
  const [showNewAccModal, setShowNewAccModal] = useState(false);

  // Order Ticket Form
  const [symbol, setSymbol] = useState("NVDA");
  const [side, setSide] = useState<"BUY" | "SELL">("BUY");
  const [orderType, setOrderType] = useState("MARKET");
  const [quantity, setQuantity] = useState(10);
  const [limitPrice, setLimitPrice] = useState<number | undefined>(undefined);
  const [stopPrice, setStopPrice] = useState<number | undefined>(undefined);
  const [orderSubmitting, setOrderSubmitting] = useState(false);

  // Kill Switch
  const [showKillSwitchModal, setShowKillSwitchModal] = useState(false);
  const [killSwitchReason, setKillSwitchReason] = useState("");

  // Broker Sandbox State
  const [providers, setProviders] = useState<SandboxBrokerProvider[]>([]);
  const [connections, setConnections] = useState<SandboxBrokerConnection[]>([]);
  const [selectedProviderId, setSelectedProviderId] = useState("ALPACA_PAPER");
  const [brokerSecret, setBrokerSecret] = useState("");
  const [verifyingConnId, setVerifyingConnId] = useState<string | null>(null);

  // Fetch Paper Accounts on mount
  useEffect(() => {
    loadAccounts();
    loadBrokers();
  }, []);

  // When selected account changes, load orders and positions
  useEffect(() => {
    if (selectedAccountId) {
      loadAccountData(selectedAccountId);
    }
  }, [selectedAccountId]);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const accs = await listPaperAccounts();
      setAccounts(accs);
      if (accs.length > 0 && !selectedAccountId) {
        setSelectedAccountId(accs[0].account_id);
      }
    } catch (err: any) {
      console.error("Failed to load paper accounts:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadBrokers = async () => {
    try {
      const [p, c] = await Promise.all([listBrokerProviders(), listBrokerConnections()]);
      setProviders(p);
      setConnections(c);
    } catch (err: any) {
      console.error("Failed to load broker data:", err);
    }
  };

  const loadAccountData = async (accId: string) => {
    try {
      const [ords, poss] = await Promise.all([
        listPaperOrders(accId),
        listPaperPositions(accId),
      ]);
      setOrders(ords);
      setPositions(poss);
    } catch (err: any) {
      console.error("Failed to load orders/positions:", err);
    }
  };

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAccName.trim()) return;
    try {
      setLoading(true);
      const acc = await createPaperAccount({
        name: newAccName.trim(),
        initial_cash: Number(newAccCash),
        currency: "USD",
      });
      setAccounts((prev) => [acc, ...prev]);
      setSelectedAccountId(acc.account_id);
      setShowNewAccModal(false);
      setNewAccName("");
    } catch (err: any) {
      setError(err.message || "Failed to create account.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAccountId) return;
    try {
      setOrderSubmitting(true);
      setError(null);
      await submitPaperOrder(selectedAccountId, {
        symbol: symbol.toUpperCase(),
        side,
        order_type: orderType,
        quantity: Number(quantity),
        limit_price: limitPrice ? Number(limitPrice) : undefined,
        stop_price: stopPrice ? Number(stopPrice) : undefined,
      });
      await loadAccountData(selectedAccountId);
      await loadAccounts();
    } catch (err: any) {
      setError(err.message || "Failed to submit paper order.");
    } finally {
      setOrderSubmitting(false);
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    if (!selectedAccountId) return;
    try {
      await cancelPaperOrder(selectedAccountId, orderId);
      await loadAccountData(selectedAccountId);
    } catch (err: any) {
      setError(err.message || "Failed to cancel order.");
    }
  };

  const handleKillSwitch = async () => {
    if (!selectedAccountId || !killSwitchReason.trim()) return;
    try {
      await activatePaperKillSwitch(selectedAccountId, killSwitchReason.trim());
      setShowKillSwitchModal(false);
      setKillSwitchReason("");
      await loadAccounts();
    } catch (err: any) {
      setError(err.message || "Failed to activate kill switch.");
    }
  };

  const handleCreateBrokerConnection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!brokerSecret.trim()) return;
    try {
      setLoading(true);
      await createBrokerConnection({
        provider_id: selectedProviderId,
        secret: brokerSecret.trim(),
        account_id: `sandbox-${selectedProviderId.toLowerCase()}`,
      });
      setBrokerSecret("");
      await loadBrokers();
    } catch (err: any) {
      setError(err.message || "Failed to create sandbox connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyBroker = async (connId: string) => {
    try {
      setVerifyingConnId(connId);
      await verifyBrokerConnection(connId);
      await loadBrokers();
    } catch (err: any) {
      setError(err.message || "Verification failed.");
    } finally {
      setVerifyingConnId(null);
    }
  };

  const currentAccount = accounts.find((a) => a.account_id === selectedAccountId);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 space-y-6">
      {/* Top Banner: Absolute Financial Safety Firewall */}
      <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
          <div>
            <p className="text-xs font-semibold text-amber-300 uppercase tracking-wider">
              Financial Safety Firewall Enforced · Stage 144 / 145 / 150
            </p>
            <p className="text-xs text-neutral-400 mt-0.5">
              Strictly simulated paper trading & isolated sandbox broker environments. Zero live capital risk. Live broker connections are categorically blocked.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            FIREWALL ACTIVE
          </span>
        </div>
      </div>

      {/* Main Cockpit Header & Tabs */}
      <div className="flex flex-wrap items-center justify-between pb-4 border-b border-neutral-800 gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <Activity className="w-5 h-5 text-indigo-400" />
            <h1 className="text-xl font-bold tracking-tight">ATLAS Unified Trading Cockpit</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">
              Stage 143 · 144 · 145
            </span>
          </div>
          <p className="text-xs text-neutral-400 mt-1">
            Backtesting Lab, Simulated Order Execution, Virtual Portfolios, and Sandbox Broker Gateways
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center bg-neutral-900 border border-neutral-800 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab("PAPER")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeTab === "PAPER"
                ? "bg-neutral-800 text-white shadow-sm"
                : "text-neutral-400 hover:text-neutral-200"
            }`}
          >
            <Wallet className="w-3.5 h-3.5 text-emerald-400" />
            Paper Trading Terminal
          </button>
          <button
            onClick={() => setActiveTab("BROKERS")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeTab === "BROKERS"
                ? "bg-neutral-800 text-white shadow-sm"
                : "text-neutral-400 hover:text-neutral-200"
            }`}
          >
            <Server className="w-3.5 h-3.5 text-cyan-400" />
            Broker Sandbox Hub
          </button>
          <button
            onClick={() => setActiveTab("BACKTEST")}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              activeTab === "BACKTEST"
                ? "bg-neutral-800 text-white shadow-sm"
                : "text-neutral-400 hover:text-neutral-200"
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-amber-400" />
            Backtesting Lab (Nautilus)
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs p-3 rounded-lg flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-rose-400 hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* TAB 1: PAPER TRADING TERMINAL */}
      {activeTab === "PAPER" && (
        <div className="space-y-6">
          {/* Account Selector & Metric Tiles */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Account Card */}
            <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl flex flex-col justify-between">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-neutral-400">Virtual Paper Account</span>
                <button
                  onClick={() => setShowNewAccModal(true)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  New
                </button>
              </div>
              <select
                value={selectedAccountId}
                onChange={(e) => setSelectedAccountId(e.target.value)}
                className="bg-neutral-950 border border-neutral-800 text-sm text-neutral-100 rounded-lg p-2 focus:ring-1 focus:ring-indigo-500 outline-none"
              >
                {accounts.map((a) => (
                  <option key={a.account_id} value={a.account_id}>
                    {a.name || "Default Account"} ({a.currency || "USD"})
                  </option>
                ))}
              </select>
              {currentAccount?.kill_switch_active && (
                <div className="mt-2 text-xs font-bold text-rose-400 flex items-center gap-1 bg-rose-500/10 border border-rose-500/20 px-2 py-1 rounded">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  KILL SWITCH ACTIVE
                </div>
              )}
            </div>

            {/* Cash Balance */}
            <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl">
              <span className="text-xs text-neutral-400">Cash Balance</span>
              <p className="text-xl font-bold font-mono text-neutral-100 mt-1">
                ${(currentAccount?.cash ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </p>
              <span className="text-xs text-neutral-500 mt-1 block">
                Virtual simulated liquidity
              </span>
            </div>

            {/* Account Equity */}
            <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl">
              <span className="text-xs text-neutral-400">Total Account Equity</span>
              <p className="text-xl font-bold font-mono text-neutral-100 mt-1">
                ${(currentAccount?.portfolio_value ?? currentAccount?.cash ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </p>
              <div className="flex items-center gap-1 text-xs mt-1 text-emerald-400">
                <ArrowUpRight className="w-3.5 h-3.5" />
                <span>Realized PnL: ${(currentAccount?.realized_pnl ?? 0).toFixed(2)}</span>
              </div>
            </div>

            {/* Buying Power & Kill Switch Button */}
            <div className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl flex flex-col justify-between">
              <div>
                <span className="text-xs text-neutral-400">Simulated Buying Power</span>
                <p className="text-xl font-bold font-mono text-neutral-100 mt-1">
                  ${(currentAccount?.buying_power ?? currentAccount?.cash ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </p>
              </div>
              <button
                onClick={() => setShowKillSwitchModal(true)}
                disabled={currentAccount?.kill_switch_active}
                className="mt-2 text-xs bg-rose-600/20 text-rose-300 border border-rose-600/30 hover:bg-rose-600/30 p-1.5 rounded-lg flex items-center justify-center gap-1.5 font-medium transition-colors disabled:opacity-50"
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                Emergency Kill Switch
              </button>
            </div>
          </div>

          {/* Center Work Area: Order Ticket & Positions/Orders */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 1 Col: Simulated Order Ticket */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
                <h2 className="text-sm font-semibold flex items-center gap-2">
                  <Play className="w-4 h-4 text-emerald-400" />
                  Order Ticket (Simulated)
                </h2>
                <span className="text-xs font-mono text-neutral-500">PAPER ONLY</span>
              </div>

              <form onSubmit={handleSubmitOrder} className="space-y-3">
                {/* Buy / Sell Toggle */}
                <div className="grid grid-cols-2 gap-2 bg-neutral-950 p-1 rounded-lg border border-neutral-800">
                  <button
                    type="button"
                    onClick={() => setSide("BUY")}
                    className={`py-1.5 rounded text-xs font-bold transition-colors ${
                      side === "BUY"
                        ? "bg-emerald-600 text-white"
                        : "text-neutral-400 hover:text-white"
                    }`}
                  >
                    BUY
                  </button>
                  <button
                    type="button"
                    onClick={() => setSide("SELL")}
                    className={`py-1.5 rounded text-xs font-bold transition-colors ${
                      side === "SELL"
                        ? "bg-rose-600 text-white"
                        : "text-neutral-400 hover:text-white"
                    }`}
                  >
                    SELL
                  </button>
                </div>

                {/* Symbol */}
                <div>
                  <label className="text-xs text-neutral-400 block mb-1">Asset Symbol</label>
                  <input
                    type="text"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-sm text-neutral-100 font-mono focus:border-indigo-500 outline-none uppercase"
                    placeholder="e.g. NVDA, AAPL, MSFT"
                    required
                  />
                </div>

                {/* Order Type & Quantity */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-neutral-400 block mb-1">Order Type</label>
                    <select
                      value={orderType}
                      onChange={(e) => setOrderType(e.target.value)}
                      className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-xs text-neutral-100 outline-none"
                    >
                      <option value="MARKET">Market</option>
                      <option value="LIMIT">Limit</option>
                      <option value="STOP">Stop</option>
                      <option value="STOP_LIMIT">Stop Limit</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-neutral-400 block mb-1">Quantity</label>
                    <input
                      type="number"
                      step="any"
                      min="0.001"
                      value={quantity}
                      onChange={(e) => setQuantity(Number(e.target.value))}
                      className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-xs text-neutral-100 font-mono outline-none"
                      required
                    />
                  </div>
                </div>

                {/* Limit Price (if limit) */}
                {orderType.includes("LIMIT") && (
                  <div>
                    <label className="text-xs text-neutral-400 block mb-1">Limit Price ($)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={limitPrice || ""}
                      onChange={(e) => setLimitPrice(Number(e.target.value))}
                      className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-xs text-neutral-100 font-mono outline-none"
                      placeholder="0.00"
                      required
                    />
                  </div>
                )}

                {/* Stop Price (if stop) */}
                {orderType.includes("STOP") && (
                  <div>
                    <label className="text-xs text-neutral-400 block mb-1">Stop Price ($)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={stopPrice || ""}
                      onChange={(e) => setStopPrice(Number(e.target.value))}
                      className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-xs text-neutral-100 font-mono outline-none"
                      placeholder="0.00"
                      required
                    />
                  </div>
                )}

                <button
                  type="submit"
                  disabled={orderSubmitting || currentAccount?.kill_switch_active}
                  className={`w-full py-2.5 rounded-lg text-xs font-bold text-white transition-colors shadow-sm disabled:opacity-50 ${
                    side === "BUY"
                      ? "bg-emerald-600 hover:bg-emerald-500"
                      : "bg-rose-600 hover:bg-rose-500"
                  }`}
                >
                  {orderSubmitting ? "Routing Simulated Order..." : `Submit Paper ${side} Order`}
                </button>
              </form>
            </div>

            {/* Right 2 Cols: Positions & Orders Tables */}
            <div className="lg:col-span-2 space-y-5">
              {/* Virtual Positions Table */}
              <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5">
                <div className="flex items-center justify-between pb-3 border-b border-neutral-800 mb-3">
                  <h2 className="text-sm font-semibold flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-indigo-400" />
                    Open Paper Positions ({positions.length})
                  </h2>
                  <button
                    onClick={() => selectedAccountId && loadAccountData(selectedAccountId)}
                    className="text-neutral-400 hover:text-neutral-200 text-xs flex items-center gap-1"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    Refresh
                  </button>
                </div>

                {positions.length === 0 ? (
                  <div className="text-center py-8 text-neutral-500 text-xs">
                    No active simulated positions in this account. Submit a paper order to open a position.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="text-neutral-400 uppercase tracking-wider font-mono border-b border-neutral-800">
                        <tr>
                          <th className="py-2">Symbol</th>
                          <th className="py-2">Qty</th>
                          <th className="py-2">Avg Cost</th>
                          <th className="py-2">Current</th>
                          <th className="py-2">Market Value</th>
                          <th className="py-2">Unrealized PnL</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-neutral-800/60 font-mono">
                        {positions.map((p) => {
                          const pnl = p.unrealized_pnl || 0;
                          return (
                            <tr key={p.position_id || p.symbol} className="hover:bg-neutral-800/30">
                              <td className="py-2.5 font-bold text-neutral-100">{p.symbol}</td>
                              <td className="py-2.5">{p.quantity}</td>
                              <td className="py-2.5">${(p.avg_cost || 0).toFixed(2)}</td>
                              <td className="py-2.5">${(p.current_price || 0).toFixed(2)}</td>
                              <td className="py-2.5">${(p.market_value || 0).toFixed(2)}</td>
                              <td
                                className={`py-2.5 font-semibold ${
                                  pnl >= 0 ? "text-emerald-400" : "text-rose-400"
                                }`}
                              >
                                {pnl >= 0 ? "+" : ""}${pnl.toFixed(2)}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Simulated Orders Table */}
              <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5">
                <div className="flex items-center justify-between pb-3 border-b border-neutral-800 mb-3">
                  <h2 className="text-sm font-semibold flex items-center gap-2">
                    <FileText className="w-4 h-4 text-cyan-400" />
                    Orders History & Execution Log ({orders.length})
                  </h2>
                </div>

                {orders.length === 0 ? (
                  <div className="text-center py-8 text-neutral-500 text-xs">
                    No orders submitted yet.
                  </div>
                ) : (
                  <div className="overflow-x-auto max-h-60 overflow-y-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="text-neutral-400 uppercase tracking-wider font-mono border-b border-neutral-800 sticky top-0 bg-neutral-900">
                        <tr>
                          <th className="py-2">Symbol</th>
                          <th className="py-2">Side</th>
                          <th className="py-2">Type</th>
                          <th className="py-2">Qty</th>
                          <th className="py-2">Status</th>
                          <th className="py-2">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-neutral-800/60 font-mono">
                        {orders.map((o) => (
                          <tr key={o.order_id} className="hover:bg-neutral-800/30">
                            <td className="py-2 font-bold">{o.symbol}</td>
                            <td className="py-2">
                              <span
                                className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                  o.side === "BUY"
                                    ? "bg-emerald-500/10 text-emerald-400"
                                    : "bg-rose-500/10 text-rose-400"
                                }`}
                              >
                                {o.side}
                              </span>
                            </td>
                            <td className="py-2">{o.order_type}</td>
                            <td className="py-2">{o.quantity}</td>
                            <td className="py-2">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                                  o.status === "FILLED"
                                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                    : o.status === "OPEN"
                                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                    : "bg-neutral-800 text-neutral-400"
                                }`}
                              >
                                {o.status}
                              </span>
                            </td>
                            <td className="py-2">
                              {o.status === "OPEN" && (
                                <button
                                  onClick={() => handleCancelOrder(o.order_id)}
                                  className="text-rose-400 hover:text-rose-300 underline text-[11px]"
                                >
                                  Cancel
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: BROKER SANDBOX HUB */}
      {activeTab === "BROKERS" && (
        <div className="space-y-6">
          {/* Supported Providers Cards */}
          <div>
            <h2 className="text-sm font-semibold mb-3">Supported Sandbox Broker Providers</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {providers.map((p) => (
                <div
                  key={p.provider_id}
                  className="bg-neutral-900 border border-neutral-800 p-4 rounded-xl space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-neutral-100">{p.display_name}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                      SANDBOX
                    </span>
                  </div>
                  <p className="text-xs text-neutral-400 font-mono">Host: {p.execution_host}</p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {p.capabilities.supports_order_submit && (
                      <span className="text-[10px] bg-neutral-800 text-neutral-300 px-2 py-0.5 rounded">
                        Order Submit
                      </span>
                    )}
                    {p.capabilities.supports_order_preview && (
                      <span className="text-[10px] bg-neutral-800 text-neutral-300 px-2 py-0.5 rounded">
                        Order Preview
                      </span>
                    )}
                    {p.capabilities.supports_order_modify && (
                      <span className="text-[10px] bg-neutral-800 text-neutral-300 px-2 py-0.5 rounded">
                        Order Modify
                      </span>
                    )}
                    {p.capabilities.supports_order_cancel && (
                      <span className="text-[10px] bg-neutral-800 text-neutral-300 px-2 py-0.5 rounded">
                        Order Cancel
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Connect & Connections Management */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Create Connection Form */}
            <div className="bg-neutral-900 border border-neutral-800 p-5 rounded-xl space-y-4">
              <h2 className="text-sm font-semibold flex items-center gap-2">
                <Lock className="w-4 h-4 text-cyan-400" />
                Register Sandbox Connection
              </h2>
              <p className="text-xs text-neutral-400">
                Credentials are encrypted in-memory with Fernet tokens and restricted to verified sandbox hosts.
              </p>

              <form onSubmit={handleCreateBrokerConnection} className="space-y-3">
                <div>
                  <label className="text-xs text-neutral-400 block mb-1">Provider</label>
                  <select
                    value={selectedProviderId}
                    onChange={(e) => setSelectedProviderId(e.target.value)}
                    className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-xs text-neutral-100 outline-none"
                  >
                    {providers.map((p) => (
                      <option key={p.provider_id} value={p.provider_id}>
                        {p.display_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs text-neutral-400 block mb-1">Sandbox API Secret / Token</label>
                  <input
                    type="password"
                    value={brokerSecret}
                    onChange={(e) => setBrokerSecret(e.target.value)}
                    placeholder="sandbox-key-secret-..."
                    className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-xs text-neutral-100 font-mono outline-none"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 rounded-lg text-xs font-bold text-white transition-colors"
                >
                  Register Sandbox Connection
                </button>
              </form>
            </div>

            {/* Active Connections List */}
            <div className="lg:col-span-2 bg-neutral-900 border border-neutral-800 p-5 rounded-xl">
              <div className="flex items-center justify-between pb-3 border-b border-neutral-800 mb-3">
                <h2 className="text-sm font-semibold flex items-center gap-2">
                  <Server className="w-4 h-4 text-emerald-400" />
                  Configured Sandbox Connections ({connections.length})
                </h2>
                <button
                  onClick={loadBrokers}
                  className="text-xs text-neutral-400 hover:text-neutral-200 flex items-center gap-1"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Refresh
                </button>
              </div>

              {connections.length === 0 ? (
                <div className="text-center py-8 text-neutral-500 text-xs">
                  No sandbox broker connections configured yet.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="text-neutral-400 uppercase tracking-wider font-mono border-b border-neutral-800">
                      <tr>
                        <th className="py-2">Provider</th>
                        <th className="py-2">Environment</th>
                        <th className="py-2">Status</th>
                        <th className="py-2">Last Verified</th>
                        <th className="py-2">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-800/60 font-mono">
                      {connections.map((c) => (
                        <tr key={c.connection_id} className="hover:bg-neutral-800/30">
                          <td className="py-2.5 font-bold">{c.provider_id}</td>
                          <td className="py-2.5 text-neutral-400">{c.environment}</td>
                          <td className="py-2.5">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                                c.status === "VERIFIED_WITH_MOCK" || c.status === "CONNECTED"
                                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                  : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                              }`}
                            >
                              {c.status}
                            </span>
                          </td>
                          <td className="py-2.5 text-neutral-400">
                            {c.last_verified_at
                              ? new Date(c.last_verified_at).toLocaleTimeString()
                              : "Never"}
                          </td>
                          <td className="py-2.5">
                            <button
                              onClick={() => handleVerifyBroker(c.connection_id)}
                              disabled={verifyingConnId === c.connection_id}
                              className="text-xs text-cyan-400 hover:text-cyan-300 underline disabled:opacity-50"
                            >
                              {verifyingConnId === c.connection_id ? "Testing..." : "Verify"}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: NAUTILUSTRADER BACKTESTING LAB */}
      {activeTab === "BACKTEST" && (
        <div className="border border-neutral-800 rounded-xl overflow-hidden">
          <BacktestingLab />
        </div>
      )}

      {/* Modal: Create Paper Account */}
      {showNewAccModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-base font-bold">Create Virtual Paper Account</h3>
            <form onSubmit={handleCreateAccount} className="space-y-3">
              <div>
                <label className="text-xs text-neutral-400 block mb-1">Account Label</label>
                <input
                  type="text"
                  value={newAccName}
                  onChange={(e) => setNewAccName(e.target.value)}
                  placeholder="e.g. Quantitative Macro Sandbox"
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-sm text-neutral-100 outline-none"
                  required
                />
              </div>
              <div>
                <label className="text-xs text-neutral-400 block mb-1">Initial Virtual Cash ($)</label>
                <input
                  type="number"
                  value={newAccCash}
                  onChange={(e) => setNewAccCash(Number(e.target.value))}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-sm text-neutral-100 font-mono outline-none"
                  min="1"
                  required
                />
              </div>
              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowNewAccModal(false)}
                  className="px-3 py-1.5 text-xs text-neutral-400 hover:text-neutral-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-xs font-bold text-white"
                >
                  Create Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Kill Switch Confirmation */}
      {showKillSwitchModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-neutral-900 border border-rose-500/30 rounded-xl p-6 max-w-md w-full space-y-4">
            <div className="flex items-center gap-3 text-rose-400">
              <ShieldAlert className="w-6 h-6" />
              <h3 className="text-base font-bold">Activate Emergency Kill Switch</h3>
            </div>
            <p className="text-xs text-neutral-400">
              Activating the kill switch immediately halts all simulated order submissions and disables automated strategy trading on this account.
            </p>
            <div>
              <label className="text-xs text-neutral-400 block mb-1">Reason for Emergency Stop</label>
              <input
                type="text"
                value={killSwitchReason}
                onChange={(e) => setKillSwitchReason(e.target.value)}
                placeholder="e.g. Risk threshold breached / testing failover"
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-2 text-xs text-neutral-100 outline-none"
                required
              />
            </div>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowKillSwitchModal(false)}
                className="px-3 py-1.5 text-xs text-neutral-400 hover:text-neutral-200"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleKillSwitch}
                disabled={!killSwitchReason.trim()}
                className="px-4 py-1.5 bg-rose-600 hover:bg-rose-500 rounded-lg text-xs font-bold text-white disabled:opacity-50"
              >
                Confirm Emergency Stop
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
