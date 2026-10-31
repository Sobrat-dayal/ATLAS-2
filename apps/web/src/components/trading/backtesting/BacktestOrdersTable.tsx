"use client";

import React, { useState } from "react";
import { OrderRecord } from "@/lib/trading/backtesting/types";
import { ShieldAlert, CheckCircle2, Clock, XCircle, AlertCircle } from "lucide-react";

interface BacktestOrdersTableProps {
  orders: OrderRecord[];
}

export function BacktestOrdersTable({ orders }: BacktestOrdersTableProps) {
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  const filteredOrders = orders.filter((ord) => {
    if (statusFilter === "ALL") return true;
    return ord.status === statusFilter;
  });

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 text-neutral-200">
      <div className="flex flex-wrap items-center justify-between pb-4 border-b border-neutral-800 gap-3 mb-4">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-neutral-100">
            Order Lifecycle Audit & Pre-Trade Risk
          </h3>
          <p className="text-xs text-neutral-400 mt-0.5">
            Full order matching state machine audit, including pre-trade risk rejections
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-1.5 bg-neutral-950 border border-neutral-800 rounded-lg p-0.5 text-xs">
          {["ALL", "FILLED", "PARTIALLY_FILLED", "REJECTED"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-2.5 py-1 rounded transition-colors ${
                statusFilter === st
                  ? "bg-neutral-800 text-neutral-100 font-semibold"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              {st.replace(/_/g, " ")}
            </button>
          ))}
        </div>
      </div>

      {filteredOrders.length === 0 ? (
        <div className="text-center py-10 text-neutral-500 text-xs">
          No orders matching status &quot;{statusFilter}&quot;.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-neutral-800 text-neutral-400 uppercase tracking-wider text-[10px]">
                <th className="pb-2.5 font-medium">Order ID</th>
                <th className="pb-2.5 font-medium">Side</th>
                <th className="pb-2.5 font-medium">Type</th>
                <th className="pb-2.5 font-medium text-right">Qty</th>
                <th className="pb-2.5 font-medium">Status</th>
                <th className="pb-2.5 font-medium">Submitted</th>
                <th className="pb-2.5 font-medium">Completed</th>
                <th className="pb-2.5 font-medium">Risk / Execution Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-800/60 font-mono text-[11px]">
              {filteredOrders.map((ord) => {
                const isRejected = ord.status === "REJECTED";
                const isFilled = ord.status === "FILLED";
                const isPartial = ord.status === "PARTIALLY_FILLED";

                return (
                  <tr
                    key={ord.order_id}
                    className={`hover:bg-neutral-800/30 transition-colors ${
                      isRejected ? "bg-rose-950/20" : ""
                    }`}
                  >
                    <td className="py-2.5 text-neutral-300 font-sans font-medium">
                      {ord.order_id}
                    </td>
                    <td className="py-2.5">
                      <span
                        className={`font-semibold ${
                          ord.order_side === "BUY" ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {ord.order_side}
                      </span>
                    </td>
                    <td className="py-2.5 text-neutral-400 font-sans">{ord.order_type}</td>
                    <td className="py-2.5 text-right text-neutral-300">{ord.quantity}</td>
                    <td className="py-2.5">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-sans font-semibold inline-flex items-center gap-1 ${
                          isFilled
                            ? "bg-emerald-950 text-emerald-300 border border-emerald-800/60"
                            : isPartial
                            ? "bg-amber-950 text-amber-300 border border-amber-800/60"
                            : isRejected
                            ? "bg-rose-950 text-rose-300 border border-rose-800/60"
                            : "bg-neutral-800 text-neutral-300"
                        }`}
                      >
                        {isFilled && <CheckCircle2 className="w-3 h-3" />}
                        {isRejected && <XCircle className="w-3 h-3" />}
                        {isPartial && <Clock className="w-3 h-3" />}
                        {ord.status}
                      </span>
                    </td>
                    <td className="py-2.5 text-neutral-400 text-[10px]">{ord.submitted_at}</td>
                    <td className="py-2.5 text-neutral-400 text-[10px]">
                      {ord.completed_at || "—"}
                    </td>
                    <td className="py-2.5 text-neutral-400 font-sans">
                      {ord.rejection_reason ? (
                        <span className="text-rose-400 font-medium flex items-center gap-1 text-[11px]">
                          <AlertCircle className="w-3 h-3" />
                          {ord.rejection_reason}
                        </span>
                      ) : (
                        <span className="text-neutral-500 text-[11px]">Normal Execution</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

