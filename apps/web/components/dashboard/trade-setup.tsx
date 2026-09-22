"use client";

import { Bell } from "lucide-react";

interface TradeSetupProps {
  direction?: "LONG" | "SHORT" | null;
  entryLow?: number | null;
  entryHigh?: number | null;
  stopLoss?: number | null;
  takeProfit?: number | null;
  riskReward?: number | null;
  quality?: string;
  status?: string;
}

export function TradeSetupPanel({
  direction,
  entryLow,
  entryHigh,
  stopLoss,
  takeProfit,
  riskReward,
  quality = "—",
  status = "NO_TRADE",
}: TradeSetupProps) {
  const isNoTrade = !direction || status === "NO_TRADE" || status === "WEEKEND_CLOSED";
  const isLong = direction === "LONG";

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-card">
      <div className="flex items-center justify-between pb-4 border-b border-border mb-4">
        <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
          Trade Setup
        </h2>
        <span
          className={`px-2.5 py-0.5 text-xs font-bold rounded-full ${
            isNoTrade
              ? "bg-background text-text-secondary border border-border"
              : isLong
              ? "bg-positive-light text-positive"
              : "bg-negative-light text-negative"
          }`}
        >
          {isNoTrade ? "NO TRADE" : direction}
        </span>
      </div>

      {isNoTrade ? (
        <div className="py-6 text-center space-y-2">
          <p className="text-xs font-medium text-text-secondary">
            No trade setup currently qualifies.
          </p>
          <p className="text-[11px] text-text-muted">
            Confidence or directional margin below threshold, or market is closed / illiquid.
          </p>
        </div>
      ) : (
        <div className="space-y-3.5 text-xs">
          <div className="flex justify-between items-center py-1 border-b border-border/50">
            <span className="text-text-secondary">Direction</span>
            <span className={`font-bold ${isLong ? "text-positive" : "text-negative"}`}>
              {direction}
            </span>
          </div>

          <div className="flex justify-between items-center py-1 border-b border-border/50">
            <span className="text-text-secondary">Entry Zone</span>
            <span className="font-semibold text-text-primary">
              {entryLow?.toFixed(4) ?? "—"} – {entryHigh?.toFixed(4) ?? "—"}
            </span>
          </div>

          <div className="flex justify-between items-center py-1 border-b border-border/50">
            <span className="text-text-secondary">Stop Loss</span>
            <span className="font-semibold text-negative">
              {stopLoss?.toFixed(4) ?? "—"}
            </span>
          </div>

          <div className="flex justify-between items-center py-1 border-b border-border/50">
            <span className="text-text-secondary">Take Profit</span>
            <span className="font-semibold text-positive">
              {takeProfit?.toFixed(4) ?? "—"}
            </span>
          </div>

          <div className="flex justify-between items-center py-1 border-b border-border/50">
            <span className="text-text-secondary">Risk / Reward</span>
            <span className="font-semibold text-text-primary">
              {riskReward != null ? `1 : ${riskReward.toFixed(1)}` : "—"}
            </span>
          </div>

          <div className="flex justify-between items-center py-1">
            <span className="text-text-secondary">Setup Quality</span>
            <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-positive-light text-positive">
              {quality}
            </span>
          </div>

          {/* CTA — SET ALERT ONLY. This system never executes trades. */}
          <button className="w-full mt-4 bg-primary hover:bg-primary/90 text-white font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors shadow-sm text-xs">
            <Bell className="w-4 h-4" />
            <span>SET ALERT (Analysis Only)</span>
          </button>
        </div>
      )}
    </div>
  );
}
