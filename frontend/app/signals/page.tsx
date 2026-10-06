"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { useDashboardData } from "@/lib/useDashboardData";
import {
  Zap,
  Clock,
  Filter,
  Search,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  ShieldCheck,
  BarChart2,
} from "lucide-react";
import { TradeCountdown } from "@/components/dashboard/paper-portfolio-card";

export default function SignalsPage() {
  const { analysis, signals, tradeHistory, loading, lastRefresh } = useDashboardData("M15");
  const signal = analysis?.signal ?? null;

  const [biasFilter, setBiasFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Combine live signals and trade history into a rich list
  const combinedHistory = tradeHistory.map((t) => ({
    id: t.signal_id,
    timestamp: t.opened_at || t.closed_at || new Date().toISOString(),
    symbol: t.symbol,
    bias: t.direction === "LONG" ? "BULLISH" : "BEARISH",
    direction: t.direction,
    confidence: t.model_confidence || 0.65,
    status: t.status,
    entry: t.entry_price,
    stop_loss: t.stop_loss,
    take_profit: t.take_profit,
    pnl_pips: t.pnl_pips,
    realized_pnl: t.realized_pnl,
    regime: t.regime || "TRENDING",
  }));

  const filteredHistory = combinedHistory.filter((item) => {
    if (biasFilter !== "ALL" && item.bias !== biasFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchSymbol = item.symbol.toLowerCase().includes(q);
      const matchStatus = item.status.toLowerCase().includes(q);
      const matchBias = item.bias.toLowerCase().includes(q);
      if (!matchSymbol && !matchStatus && !matchBias) return false;
    }
    return true;
  });

  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="p-6 space-y-6 max-w-[1800px] w-full mx-auto">
          {/* Header Banner */}
          <div className="flex items-center justify-between pb-4 border-b border-border flex-wrap gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Zap className="w-6 h-6 text-primary animate-pulse" />
                <h1 className="text-xl font-bold font-display text-text-primary uppercase tracking-wider">
                  AI Signal Intelligence Hub
                </h1>
              </div>
              <p className="text-xs text-text-secondary mt-1">
                Real-time quantitative signal feed, institutional entry/exit levels, and trade resolution log.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-xs px-3 py-1 rounded-full bg-primary/10 text-primary font-mono font-semibold border border-primary/20">
                FXMind Alpha Engine
              </span>
              <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-mono font-semibold border border-emerald-500/20 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                LIVE AI ENGINE ACTIVE
              </span>
            </div>
          </div>

          {/* Current Live Signal Card */}
          <div className="bg-card border border-border rounded-xl p-5 shadow-card relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-text-secondary uppercase tracking-wider">
                  Live Engine Signal Evaluation (GBP/USD M15)
                </span>
              </div>
              <span className="text-[11px] text-text-muted flex items-center gap-1 font-mono">
                <Clock className="w-3.5 h-3.5" />
                {lastRefresh ? `Evaluated ${lastRefresh.toLocaleTimeString()}` : "Evaluating..."}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-background/60 p-3 rounded-lg border border-border">
                <span className="text-[11px] text-text-secondary block">AI Market Bias</span>
                <div className="flex items-center gap-1.5 mt-1">
                  {signal?.bias === "BULLISH" && <ArrowUpRight className="w-5 h-5 text-emerald-400" />}
                  {signal?.bias === "BEARISH" && <ArrowDownRight className="w-5 h-5 text-red-400" />}
                  <span
                    className={`text-lg font-bold font-mono ${
                      signal?.bias === "BULLISH"
                        ? "text-emerald-400"
                        : signal?.bias === "BEARISH"
                        ? "text-red-400"
                        : "text-text-primary"
                    }`}
                  >
                    {signal?.bias ?? "NEUTRAL"}
                  </span>
                </div>
              </div>

              <div className="bg-background/60 p-3 rounded-lg border border-border">
                <span className="text-[11px] text-text-secondary block">Calibrated Confidence</span>
                <span className="text-lg font-bold font-mono text-text-primary block mt-1">
                  {signal?.confidence != null ? `${(signal.confidence * 100).toFixed(1)}%` : "50.0%"}
                </span>
              </div>

              <div className="bg-background/60 p-3 rounded-lg border border-border">
                <span className="text-[11px] text-text-secondary block">Market Regime</span>
                <span className="text-lg font-bold font-mono text-text-primary block mt-1">
                  {signal?.regime ?? "RANGING"}
                </span>
              </div>

              <div className="bg-background/60 p-3 rounded-lg border border-border">
                <span className="text-[11px] text-text-secondary block">Execution Status</span>
                <div className="flex items-center gap-2 mt-1">
                  <span
                    className={`inline-block px-2.5 py-1 rounded text-xs font-bold font-mono ${
                      signal?.trade?.status === "ACTIVE"
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-background text-text-muted border border-border"
                    }`}
                  >
                    {signal?.trade?.status ?? "NO_TRADE"}
                  </span>
                  {signal?.trade?.status === "ACTIVE" && (
                    <TradeCountdown openedAt={lastRefresh ? lastRefresh.toISOString() : new Date().toISOString()} durationHours={6} />
                  )}
                </div>
              </div>
            </div>

            {/* Active Trade Levels */}
            {signal?.trade?.status === "ACTIVE" && (
              <div className="mt-4 pt-4 border-t border-border grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono bg-emerald-500/5 p-3 rounded-lg border border-emerald-500/20">
                <div>
                  <span className="text-text-secondary block">Entry Range</span>
                  <span className="text-text-primary font-bold text-sm">
                    {signal.trade.entry_low?.toFixed(5)} – {signal.trade.entry_high?.toFixed(5)}
                  </span>
                </div>
                <div>
                  <span className="text-text-secondary block">Stop Loss</span>
                  <span className="text-red-400 font-bold text-sm">{signal.trade.stop_loss?.toFixed(5)}</span>
                </div>
                <div>
                  <span className="text-text-secondary block">Take Profit</span>
                  <span className="text-emerald-400 font-bold text-sm">{signal.trade.take_profit?.toFixed(5)}</span>
                </div>
                <div>
                  <span className="text-text-secondary block">Risk/Reward</span>
                  <span className="text-text-primary font-bold text-sm">1:{signal.trade.risk_reward?.toFixed(2)}</span>
                </div>
              </div>
            )}

            {/* Key Decision Drivers */}
            {signal?.reasons && signal.reasons.length > 0 && (
              <div className="mt-4 pt-4 border-t border-border">
                <span className="text-xs font-bold text-text-secondary uppercase tracking-wider block mb-2">
                  Primary Confluence Drivers
                </span>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {signal.reasons.map((r: any, idx: number) => {
                    const reasonText = typeof r === "string" ? r : r.reason ?? r.category ?? JSON.stringify(r);
                    const sentiment = typeof r === "object" ? r.sentiment : null;
                    const category = typeof r === "object" ? r.category : null;
                    const isSupportive = sentiment === "SUPPORTIVE" || sentiment === "CLEAR";
                    const isOpposing = sentiment === "OPPOSING";

                    return (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-2 rounded bg-background border border-border text-xs"
                      >
                        <div className="flex items-center gap-2 text-text-secondary truncate pr-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                          {category && (
                            <span className="font-semibold text-text-primary font-mono">{category}:</span>
                          )}
                          <span className="truncate">{reasonText}</span>
                        </div>
                        {sentiment && (
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono flex-shrink-0 ${
                              isSupportive
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : isOpposing
                                ? "bg-red-500/10 text-red-400 border border-red-500/20"
                                : "bg-background text-text-secondary border border-border"
                            }`}
                          >
                            {sentiment}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Historical Signal Stream Table */}
          <div className="bg-card border border-border rounded-xl p-5 shadow-card space-y-4">
            <div className="flex items-center justify-between flex-wrap gap-3">
              <div>
                <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
                  Historical Signal Log & Trade Resolution Feed
                </h2>
                <p className="text-xs text-text-secondary mt-0.5">
                  Complete history of evaluated signals and closed paper trades.
                </p>
              </div>

              {/* Controls */}
              <div className="flex items-center gap-2 flex-wrap">
                {/* Search */}
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-text-muted absolute left-2.5 top-2.5" />
                  <input
                    type="text"
                    placeholder="Search signals..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-8 pr-3 py-1.5 bg-background border border-border rounded-lg text-xs font-mono focus:outline-none focus:border-primary w-44"
                  />
                </div>

                {/* Bias Filter */}
                <div className="flex items-center bg-background border border-border rounded-lg p-0.5 text-xs font-mono">
                  {["ALL", "BULLISH", "BEARISH"].map((b) => (
                    <button
                      key={b}
                      onClick={() => setBiasFilter(b)}
                      className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                        biasFilter === b
                          ? "bg-card text-text-primary border border-border"
                          : "text-text-muted hover:text-text-primary"
                      }`}
                    >
                      {b}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-background border-b border-border text-text-secondary uppercase text-[10px] font-bold">
                  <tr>
                    <th className="p-3">Signal ID</th>
                    <th className="p-3">Time</th>
                    <th className="p-3">Pair</th>
                    <th className="p-3">Bias</th>
                    <th className="p-3">Confidence</th>
                    <th className="p-3">Entry Price</th>
                    <th className="p-3">Take Profit</th>
                    <th className="p-3">Stop Loss</th>
                    <th className="p-3">Outcome Status</th>
                    <th className="p-3 text-right">PnL (Pips)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/60">
                  {filteredHistory.length === 0 ? (
                    <tr>
                      <td colSpan={10} className="p-6 text-center text-text-muted text-xs font-sans">
                        No signal records matching criteria. Trades and signals appear here automatically as they occur.
                      </td>
                    </tr>
                  ) : (
                    filteredHistory.map((item, idx) => {
                      const isLong = item.bias === "BULLISH";
                      const isPositive = (item.pnl_pips ?? 0) >= 0;
                      return (
                        <tr key={idx} className="hover:bg-background/50 transition-colors">
                          <td className="p-3 font-semibold text-text-primary">#{item.id}</td>
                          <td className="p-3 text-text-muted text-[11px]">
                            {new Date(item.timestamp).toLocaleString(undefined, {
                              month: "short",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </td>
                          <td className="p-3 font-bold">{item.symbol}</td>
                          <td className="p-3">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                isLong
                                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                                  : "bg-red-500/15 text-red-400 border border-red-500/20"
                              }`}
                            >
                              {item.bias}
                            </span>
                          </td>
                          <td className="p-3 font-semibold text-text-primary">
                            {(item.confidence * 100).toFixed(1)}%
                          </td>
                          <td className="p-3 font-semibold text-text-primary">
                            {item.entry ? item.entry.toFixed(5) : "—"}
                          </td>
                          <td className="p-3 text-emerald-400">
                            {item.take_profit ? item.take_profit.toFixed(5) : "—"}
                          </td>
                          <td className="p-3 text-red-400">
                            {item.stop_loss ? item.stop_loss.toFixed(5) : "—"}
                          </td>
                          <td className="p-3">
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                item.status === "TARGET_HIT"
                                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                  : item.status === "STOP_HIT"
                                  ? "bg-red-500/10 text-red-400 border-red-500/20"
                                  : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                              }`}
                            >
                              {item.status}
                            </span>
                          </td>
                          <td
                            className={`p-3 text-right font-bold ${
                              isPositive ? "text-emerald-400" : "text-red-400"
                            }`}
                          >
                            {isPositive ? "+" : ""}
                            {item.pnl_pips != null ? item.pnl_pips.toFixed(1) : "0.0"}p
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
