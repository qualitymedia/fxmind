"use client";

import { useState, useEffect } from "react";
import { PaperSummaryData, PaperPosition, TradeHistoryEntry } from "@/lib/useDashboardData";
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  Target,
  Clock,
  CheckCircle2,
  History,
  XCircle,
  Timer,
  Hourglass,
} from "lucide-react";

interface PaperPortfolioCardProps {
  paperSummary: PaperSummaryData | null;
  paperPositions: PaperPosition[];
  tradeHistory?: TradeHistoryEntry[];
}

function OutcomeIcon({ status }: { status: string }) {
  if (status === "TARGET_HIT")
    return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />;
  if (status === "STOP_HIT")
    return <XCircle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />;
  return <Timer className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />;
}

function outcomeLabel(status: string) {
  if (status === "TARGET_HIT") return "TP HIT";
  if (status === "STOP_HIT") return "SL HIT";
  if (status === "EXPIRED") return "EXPIRED";
  return status;
}

function outcomeBadgeClass(status: string) {
  if (status === "TARGET_HIT")
    return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
  if (status === "STOP_HIT") return "bg-red-500/10 text-red-400 border-red-500/20";
  return "bg-amber-500/10 text-amber-400 border-amber-500/20";
}

// ── Live Trade Countdown Component ────────────────────────────────────────────

export function TradeCountdown({ openedAt, durationHours = 6 }: { openedAt: string; durationHours?: number }) {
  const [timeLeft, setTimeLeft] = useState<{ hours: number; minutes: number; seconds: number; isExpired: boolean }>({
    hours: 0,
    minutes: 0,
    seconds: 0,
    isExpired: false,
  });

  useEffect(() => {
    function update() {
      const openTime = new Date(openedAt).getTime();
      const expireTime = openTime + durationHours * 3600 * 1000;
      const now = Date.now();
      const diff = expireTime - now;

      if (diff <= 0) {
        setTimeLeft({ hours: 0, minutes: 0, seconds: 0, isExpired: true });
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setTimeLeft({ hours, minutes, seconds, isExpired: false });
    }

    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, [openedAt, durationHours]);

  if (timeLeft.isExpired) {
    return (
      <span className="text-[10px] font-mono font-bold text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">
        EXPIRING
      </span>
    );
  }

  return (
    <div className="inline-flex items-center gap-1 font-mono text-[10px] font-bold text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20 shadow-sm">
      <Hourglass className="w-2.5 h-2.5 text-amber-400 animate-pulse" />
      <span>
        {String(timeLeft.hours).padStart(2, "0")}:{String(timeLeft.minutes).padStart(2, "0")}:{String(timeLeft.seconds).padStart(2, "0")}
      </span>
      <span className="text-[9px] text-amber-300/70 font-sans">left</span>
    </div>
  );
}

export function PaperPortfolioCard({
  paperSummary,
  paperPositions,
  tradeHistory = [],
}: PaperPortfolioCardProps) {
  // Derive PnL from trade history
  const historyPnlPips = tradeHistory.reduce((s, t) => s + (t.pnl_pips ?? 0), 0);
  const historyPnlUsd = tradeHistory.reduce((s, t) => s + (t.realized_pnl ?? (t.pnl_pips ?? 0) * 0.50), 0);

  const totalPnlPips = paperSummary?.total_pnl_pips ?? 0.0;
  const displayPnlPips = totalPnlPips !== 0 ? totalPnlPips : historyPnlPips;

  // Re-base strictly onto $100.00 initial capital
  let rawEquity = paperSummary?.current_equity ?? 100.0;
  if (rawEquity > 500) {
    rawEquity = 100.0 + historyPnlUsd;
  }
  const equity = rawEquity;

  const winRate = paperSummary?.win_rate ?? 0.0;
  const openCount = paperPositions.length;
  const hasHistory = tradeHistory.length > 0;

  const historyWins = tradeHistory.filter((t) => (t.pnl_pips ?? 0) > 0).length;
  const displayWinRate =
    winRate !== 0
      ? winRate
      : tradeHistory.length > 0
      ? historyWins / tradeHistory.length
      : 0;

  return (
    <div className="bg-card border border-border rounded-xl p-4 shadow-card hover:border-primary/30 transition-all flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
            <Wallet className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-text-muted block leading-none">
              Paper Trading ($100 Capital)
            </span>
            <span className="text-xs font-semibold text-text-primary">
              Simulated Execution Portfolio
            </span>
          </div>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border bg-emerald-500/10 text-emerald-400 border-emerald-500/30 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          {openCount > 0 ? `${openCount} ACTIVE` : "STANDBY"}
        </span>
      </div>

      {/* Equity & Stats Grid */}
      <div className="grid grid-cols-3 gap-2 p-3 rounded-lg bg-background border border-border/80 text-center">
        <div>
          <span className="text-[10px] text-text-muted block">Equity</span>
          <span className="text-sm font-bold font-mono text-text-primary mt-0.5 block">
            ${equity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>
        <div>
          <span className="text-[10px] text-text-muted block">Total PnL</span>
          <span
            className={`text-sm font-bold font-mono mt-0.5 block ${
              displayPnlPips >= 0 ? "text-emerald-400" : "text-red-400"
            }`}
          >
            {displayPnlPips >= 0 ? "+" : ""}
            {displayPnlPips.toFixed(1)}p (${historyPnlUsd >= 0 ? "+" : ""}{historyPnlUsd.toFixed(2)})
          </span>
        </div>
        <div>
          <span className="text-[10px] text-text-muted block">Win Rate</span>
          <span className="text-sm font-bold font-mono text-text-primary mt-0.5 block">
            {(displayWinRate * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Open Positions */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] uppercase font-bold tracking-wider text-text-muted block">
            Active Positions ({openCount})
          </span>
          <span className="text-[10px] text-text-muted font-mono">Live Multi-Trade Tracking</span>
        </div>

        {openCount === 0 ? (
          <div className="p-3 bg-background/50 border border-border rounded-lg text-center text-text-muted text-xs">
            <Clock className="w-4 h-4 mx-auto mb-1 opacity-50" />
            <span>Awaiting next confirmed &ge;78% confidence setup…</span>
          </div>
        ) : (
          <div className="space-y-2">
            {paperPositions.map((pos, idx) => {
              const isBuy = pos.direction === "BUY" || pos.direction === "LONG";
              const pnlPips = Number(pos.pnl_pips ?? pos.unrealized_pnl_pips ?? 0);
              const lotSize = (pos as any).lot_size ?? 0.05;
              const pnlUsd = (pos as any).unrealized_pnl_usd ?? (pnlPips * lotSize * 10.0);

              return (
                <div
                  key={pos.id ?? pos.position_id ?? idx}
                  className="p-3 rounded-lg bg-background border border-border flex flex-col gap-2 shadow-sm"
                >
                  <div className="flex items-center justify-between flex-wrap gap-1.5">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                          isBuy
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                            : "bg-red-500/20 text-red-400 border border-red-500/30"
                        }`}
                      >
                        {pos.direction} {pos.symbol}
                      </span>
                      <span className="text-[10px] font-bold font-mono px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
                        {lotSize} Lots
                      </span>
                    </div>

                    {/* Live Countdown Timer */}
                    <TradeCountdown openedAt={pos.opened_at} durationHours={6} />

                    <span
                      className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                        pnlPips >= 0
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-red-500/10 text-red-400 border border-red-500/20"
                      }`}
                    >
                      {pnlPips >= 0 ? "+" : ""}
                      {pnlPips.toFixed(1)}p ({pnlUsd >= 0 ? "+" : ""}${Number(pnlUsd).toFixed(2)})
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-1 text-[11px] font-mono bg-card-secondary/40 p-1.5 rounded border border-border/50 text-center">
                    <div>
                      <span className="text-[9px] text-text-muted block">ENTRY</span>
                      <span className="font-semibold text-text-primary">
                        {Number(pos.entry_price).toFixed(5)}
                      </span>
                    </div>
                    <div>
                      <span className="text-[9px] text-text-muted block">STOP LOSS</span>
                      <span className="font-semibold text-red-400">
                        {Number(pos.stop_loss).toFixed(5)}
                      </span>
                    </div>
                    <div>
                      <span className="text-[9px] text-text-muted block">TAKE PROFIT</span>
                      <span className="font-semibold text-emerald-400">
                        {Number(pos.take_profit).toFixed(5)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Trade History — DB-backed, survives restarts */}
      <div>
        <div className="flex items-center gap-1.5 mb-1.5">
          <History className="w-3.5 h-3.5 text-text-muted" />
          <span className="text-[10px] uppercase font-bold tracking-wider text-text-muted">
            Closed Trade History ({tradeHistory.length})
          </span>
        </div>

        {!hasHistory ? (
          <div className="p-3 bg-background/50 border border-border rounded-lg text-center text-text-muted text-xs">
            No closed trades yet — history is recorded here when trades resolve.
          </div>
        ) : (
          <div className="space-y-1.5 max-h-64 overflow-y-auto pr-0.5">
            {tradeHistory.map((t, i) => {
              const isLong = t.direction === "LONG";
              const closedDate = t.closed_at
                ? new Date(t.closed_at).toLocaleString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })
                : "—";
              return (
                <div
                  key={t.position_id ?? i}
                  className="flex items-center gap-2 p-2.5 rounded-lg bg-background border border-border/60 text-xs"
                >
                  <OutcomeIcon status={t.status} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded font-mono ${
                          isLong
                            ? "bg-emerald-500/15 text-emerald-400"
                            : "bg-red-500/15 text-red-400"
                        }`}
                      >
                        {isLong ? "LONG" : "SHORT"}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${outcomeBadgeClass(t.status)}`}
                      >
                        {outcomeLabel(t.status)}
                      </span>
                      <span className="text-text-muted text-[10px] ml-auto">{closedDate}</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] font-mono mt-1 text-text-secondary">
                      <span>
                        @ {Number(t.entry_price).toFixed(5)} &rarr;{" "}
                        <strong className={t.pnl_pips >= 0 ? "text-emerald-400" : "text-red-400"}>
                          {t.pnl_pips >= 0 ? "+" : ""}{Number(t.pnl_pips).toFixed(1)}p (${Number(t.realized_pnl ?? 0).toFixed(2)})
                        </strong>
                      </span>
                      {t.session && <span className="text-[10px] text-text-muted">{t.session}</span>}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
