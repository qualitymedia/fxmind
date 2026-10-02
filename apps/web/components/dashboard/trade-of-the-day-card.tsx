"use client";

import { Award, Target, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface TradeOfTheDayCardProps {
  bias?: "BULLISH" | "BEARISH" | "NEUTRAL" | string;
  confidence?: number;
  direction?: "LONG" | "SHORT" | string | null;
  status?: string;
  entryLow?: number | null;
  entryHigh?: number | null;
  stopLoss?: number | null;
  takeProfit?: number | null;
  riskReward?: number | null;
  session?: string;
  currentPrice?: number | null;
  strategyType?: string | null;
}

export function TradeOfTheDayCard({
  bias = "NEUTRAL",
  confidence = 0.3333,
  direction,
  status = "NO_TRADE",
  entryLow,
  entryHigh,
  stopLoss,
  takeProfit,
  riskReward,
  session = "ACTIVE",
  currentPrice,
  strategyType,
}: TradeOfTheDayCardProps) {
  const isLong = direction === "LONG" || (bias === "BULLISH" && direction !== "SHORT");
  const isShort = direction === "SHORT" || (bias === "BEARISH" && direction !== "LONG");

  // Determine Entry Price midpoint
  const entryPrice =
    entryLow != null && entryHigh != null
      ? (entryLow + entryHigh) / 2.0
      : entryLow ?? entryHigh ?? currentPrice;

  // Calculate dynamic Pips for TP & SL
  const tpPips =
    takeProfit != null && entryPrice != null
      ? Math.abs(takeProfit - entryPrice) * 10000.0
      : null;

  const slPips =
    stopLoss != null && entryPrice != null
      ? Math.abs(entryPrice - stopLoss) * 10000.0
      : null;

  const computedRR =
    riskReward != null
      ? riskReward
      : tpPips != null && slPips != null && slPips > 0
      ? tpPips / slPips
      : 1.8;

  const isActive = status === "ACTIVE";

  return (
    <div className="bg-card border border-primary/30 rounded-xl p-3 shadow-card flex items-center justify-between relative overflow-hidden">
      {/* Top Accent Gradient Line */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary via-amber-500 to-cyan-500" />

      <div className="space-y-1 w-full pr-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Award className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">
              Trade Setup of the Day
            </span>
          </div>

          <span
            className={`text-[9px] font-bold px-1.5 py-0.2 rounded border ${
              isActive
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 animate-pulse"
                : "bg-amber-500/10 text-amber-400 border-amber-500/30"
            }`}
          >
            {isActive ? "● ACTIVE SETUP" : "KEY WATCH"}
          </span>
        </div>

        {/* Action Title & R:R */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            {isLong ? (
              <TrendingUp className="w-4 h-4 text-emerald-400" />
            ) : isShort ? (
              <TrendingDown className="w-4 h-4 text-red-400" />
            ) : (
              <Minus className="w-4 h-4 text-amber-400" />
            )}
            <span className="text-sm font-bold font-display text-text-primary">
              {isLong ? "BUY GBP/USD" : isShort ? "SELL GBP/USD" : "RANGE WATCH"}
            </span>
          </div>

          <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
            R:R 1:{computedRR.toFixed(1)}
          </span>
        </div>

        {/* Level Details & Pips */}
        <div className="text-[11px] font-mono text-text-secondary flex items-center justify-between pt-0.5 border-t border-border/50">
          <span>
            TP:{" "}
            <strong className="text-emerald-400">
              {takeProfit != null ? takeProfit.toFixed(4) : "—"}
            </strong>{" "}
            {tpPips != null && <span className="text-[10px] text-emerald-400/80">(+{tpPips.toFixed(1)}p)</span>}
          </span>

          <span>
            SL:{" "}
            <strong className="text-red-400">
              {stopLoss != null ? stopLoss.toFixed(4) : "—"}
            </strong>{" "}
            {slPips != null && <span className="text-[10px] text-red-400/80">(-{slPips.toFixed(1)}p)</span>}
          </span>
        </div>
      </div>

      <div className="p-2 rounded-lg bg-primary/10 text-primary flex-shrink-0">
        <Target className="w-4 h-4" />
      </div>
    </div>
  );
}
