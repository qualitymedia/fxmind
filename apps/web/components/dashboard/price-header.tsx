"use client";

import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface PriceHeaderProps {
  symbol?: string;
  price?: number;
  change?: number;
  changePercent?: number;
  bid?: number;
  ask?: number;
  spread?: number;
  timeframe?: string;
  session?: string;
  high24?: number;
  low24?: number;
  onTimeframeChange?: (tf: string) => void;
}

export function PriceHeader({
  symbol = "GBP/USD",
  price,
  change,
  changePercent,
  bid,
  ask,
  spread,
  timeframe = "M15",
  session,
  high24,
  low24,
  onTimeframeChange,
}: PriceHeaderProps) {
  const isUp = (change ?? 0) >= 0;
  const isWeekend = session === "WEEKEND_CLOSED";

  const sessionLabel: Record<string, string> = {
    LONDON_NY_OVERLAP: "London/NY Overlap",
    LONDON: "London Session",
    NEW_YORK: "New York Session",
    ASIAN: "Asian Session",
    WEEKEND_CLOSED: "Market Closed",
  };

  return (
    <div className="bg-card border border-border rounded-xl p-4 shadow-card flex flex-wrap items-center justify-between gap-4">
      {/* Symbol & Flags */}
      <div className="flex items-center gap-4">
        <div className="flex items-center -space-x-2">
          <div className="w-7 h-7 rounded-full bg-blue-600 text-white text-[10px] font-bold flex items-center justify-center border-2 border-card">
            GB
          </div>
          <div className="w-7 h-7 rounded-full bg-red-600 text-white text-[10px] font-bold flex items-center justify-center border-2 border-card">
            US
          </div>
        </div>
        <div>
          <h1 className="text-lg font-bold font-display text-text-primary leading-tight">
            {symbol}
          </h1>
          <span className="text-xs text-text-secondary leading-tight block">
            British Pound / US Dollar
          </span>
        </div>

        {/* Current Price & Change */}
        {price != null ? (
          <div className="ml-6 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-display text-text-primary tracking-tight">
              {price.toFixed(4)}
            </span>
            {change != null && changePercent != null && (
              <span
                className={`inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full ${
                  isUp
                    ? "bg-positive-light text-positive"
                    : "bg-negative-light text-negative"
                }`}
              >
                {isUp ? (
                  <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
                ) : (
                  <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
                )}
                {isUp ? "+" : ""}
                {change.toFixed(4)} ({isUp ? "+" : ""}
                {changePercent.toFixed(2)}%)
              </span>
            )}
          </div>
        ) : (
          <div className="ml-6">
            <span className="text-text-muted text-sm animate-pulse">Loading…</span>
          </div>
        )}
      </div>

      {/* Right side — bid/ask/spread + session + 24h range + timeframe */}
      <div className="flex items-center gap-6 flex-wrap">
        {/* Bid / Ask / Spread */}
        <div className="flex items-center gap-6 text-xs">
          <div>
            <span className="text-text-muted block text-[11px]">Bid</span>
            <span className="font-semibold text-text-primary">
              {bid != null ? bid.toFixed(4) : "—"}
            </span>
          </div>
          <div>
            <span className="text-text-muted block text-[11px]">Ask</span>
            <span className="font-semibold text-text-primary">
              {ask != null ? ask.toFixed(4) : "—"}
            </span>
          </div>
          <div>
            <span className="text-text-muted block text-[11px]">Spread</span>
            <span className="font-semibold text-text-primary">
              {spread != null ? `${(spread * 10000).toFixed(1)} pip` : "—"}
            </span>
          </div>
          {high24 != null && low24 != null && (
            <div>
              <span className="text-text-muted block text-[11px]">24h Range</span>
              <span className="font-semibold text-text-primary text-[11px]">
                {low24.toFixed(4)} – {high24.toFixed(4)}
              </span>
            </div>
          )}
        </div>

        {/* Session Badge */}
        {session && (
          <span
            className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${
              isWeekend
                ? "bg-amber-50 text-amber-700 border-amber-200"
                : "bg-positive-light text-positive border-positive/20"
            }`}
          >
            {sessionLabel[session] ?? session}
          </span>
        )}

        {/* Timeframe Selector */}
        <div className="flex items-center gap-1 bg-background p-1 rounded-lg border border-border">
          {["M15", "30m", "H1"].map((tf) => (
            <button
              key={tf}
              onClick={() => onTimeframeChange?.(tf)}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                timeframe === tf
                  ? "bg-primary text-white font-semibold"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
