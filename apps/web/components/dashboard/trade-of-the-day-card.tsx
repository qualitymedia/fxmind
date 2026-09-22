"use client";

import { Award, Target } from "lucide-react";

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
}

export function TradeOfTheDayCard({
  bias = "BEARISH",
  confidence = 0.99,
  direction,
  status = "NO_TRADE",
  entryLow,
  entryHigh,
  stopLoss,
  takeProfit,
  riskReward,
  session = "ASIAN",
  currentPrice = 1.3513,
}: TradeOfTheDayCardProps) {
  const isLong = direction === "LONG" || (bias === "BULLISH" && direction !== "SHORT");
  const isShort = direction === "SHORT" || bias === "BEARISH";

  // Use dynamic market price as anchor rather than static legacy numbers
  const anchorPrice = currentPrice ?? 1.3513;
  const computedTP = takeProfit ?? (isLong ? anchorPrice + 0.0050 : anchorPrice - 0.0050);
  const computedRR = riskReward ?? 2.0;

  return (
    <div className="bg-card border border-primary/30 rounded-xl p-3 shadow-card flex items-center justify-between relative overflow-hidden">
      {/* Accent Line */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary via-amber-500 to-cyan-500" />

      <div className="space-y-0.5">
        <div className="flex items-center gap-1">
          <Award className="w-3.5 h-3.5 text-primary" />
          <span className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">
            Trade of the Day
          </span>
          <span className="ml-1 text-[8px] font-bold px-1 py-0.2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
            {status === "ACTIVE" ? "ACTIVE" : "GATES ACTIVE"}
          </span>
        </div>

        <div className="text-base font-bold font-display text-text-primary flex items-center gap-1.5">
          <span>{isLong ? "BUY GBP/USD" : isShort ? "SELL GBP/USD" : "RANGE WATCH"}</span>
          <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            R:R 1:{computedRR.toFixed(1)}
          </span>
        </div>

        <span className="text-[10px] text-text-secondary block font-mono">
          TP: {computedTP.toFixed(4)} | {session} Session
        </span>
      </div>

      <div className="p-2 rounded-lg bg-primary/10 text-primary">
        <Target className="w-4 h-4" />
      </div>
    </div>
  );
}
