"use client";

import { ArrowUpRight, ArrowDownRight, Slash, Zap, Clock, TrendingUp } from "lucide-react";

interface SignalCardProps {
  direction?: "LONG" | "SHORT" | null;
  status?: string;
  strategyType?: string | null;
}

const STRATEGY_LABELS: Record<string, { label: string; color: string }> = {
  VP_POC_RETEST_BOUNCE: { label: "VP-POC Retest", color: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
  VP_VALUE_AREA_ROTATION: { label: "Value Area 80%", color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20" },
  TREND_FOLLOWING: { label: "Trend Follow", color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
  MEAN_REVERSION: { label: "Mean Reversion", color: "text-purple-400 bg-purple-500/10 border-purple-500/20" },
  TRAILING_LIMIT_ENTRY: { label: "Trailing Limit", color: "text-blue-400 bg-blue-500/10 border-blue-500/20" },
};

export function SignalCard({ direction = "LONG", status = "ACTIVE", strategyType }: SignalCardProps) {
  const isLong = direction === "LONG";
  const isShort = direction === "SHORT";
  const isNoTrade = !direction || status === "NO_TRADE";
  const isActive = status === "ACTIVE";

  const Icon = isLong ? ArrowUpRight : isShort ? ArrowDownRight : Slash;
  const text = isNoTrade ? "NO TRADE" : direction;
  const colorClass = isLong ? "text-positive" : isShort ? "text-negative" : "text-text-secondary";

  const stratInfo = strategyType ? STRATEGY_LABELS[strategyType] : null;

  return (
    <div className="bg-card border border-border rounded-xl p-3 shadow-card flex items-center justify-between">
      <div className="min-w-0 flex-1">
        <span className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">
          Signal Status
        </span>
        <div className="flex items-center gap-2 mt-0.5">
          <span className={`text-base font-bold font-display ${colorClass}`}>
            {text}
          </span>
          {isActive && (
            <span className="w-1.5 h-1.5 rounded-full bg-positive animate-pulse flex-shrink-0" />
          )}
        </div>
        {stratInfo ? (
          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border mt-1 inline-block ${stratInfo.color}`}>
            {stratInfo.label}
          </span>
        ) : (
          <span className="text-[10px] text-text-secondary block">
            {isNoTrade ? "Gates Active" : "Setup Active"}
          </span>
        )}
      </div>

      <div className={`p-2 rounded-lg flex-shrink-0 ml-2 ${isLong ? "bg-positive-light text-positive" : isShort ? "bg-negative-light text-negative" : "bg-background text-text-secondary"}`}>
        <Icon className="w-4 h-4" />
      </div>
    </div>
  );
}
