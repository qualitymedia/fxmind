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
    <div className="bg-card/95 border-b border-border px-3 py-2.5 shadow-card sm:px-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2.5 min-w-0 flex-1">
          <div className="flex items-center -space-x-2 shrink-0">
            <div className="w-7 h-7 rounded-full bg-blue-600 text-white text-[10px] font-bold flex items-center justify-center border-2 border-card">
              GB
            </div>
            <div className="w-7 h-7 rounded-full bg-red-600 text-white text-[10px] font-bold flex items-center justify-center border-2 border-card">
              US
            </div>
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-base font-bold font-display text-text-primary leading-tight sm:text-lg">
                {symbol}
              </h1>
              <span className="text-[10px] text-text-secondary">British Pound / US Dollar</span>
            </div>

            <div className="mt-1 flex items-center gap-2 flex-wrap">
              {price != null ? (
                <>
                  <span className="text-2xl font-bold font-display text-text-primary tracking-tight">
                    {price.toFixed(4)}
                  </span>
                  {change != null && changePercent != null && (
                    <span
                      className={`inline-flex items-center text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${
                        isUp
                          ? "bg-positive-light text-positive"
                          : "bg-negative-light text-negative"
                      }`}
                    >
                      {isUp ? (
                        <ArrowUpRight className="w-3 h-3 mr-0.5" />
                      ) : (
                        <ArrowDownRight className="w-3 h-3 mr-0.5" />
                      )}
                      {isUp ? "+" : ""}
                      {change.toFixed(4)} ({isUp ? "+" : ""}
                      {changePercent.toFixed(2)}%)
                    </span>
                  )}
                </>
              ) : (
                <span className="text-text-muted text-sm animate-pulse">Loading…</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between gap-2 sm:justify-end sm:gap-4">
          <div className="min-w-0 flex-1 sm:flex-none">
            <div className="grid grid-cols-3 gap-1.5 text-[10px] sm:gap-2 sm:text-xs">
              <div>
                <span className="text-text-muted block text-[10px]">Bid</span>
                <span className="font-semibold text-text-primary">{bid != null ? bid.toFixed(4) : "—"}</span>
              </div>
              <div>
                <span className="text-text-muted block text-[10px]">Ask</span>
                <span className="font-semibold text-text-primary">{ask != null ? ask.toFixed(4) : "—"}</span>
              </div>
              <div>
                <span className="text-text-muted block text-[10px]">Spread</span>
                <span className="font-semibold text-text-primary">
                  {spread != null ? `${(spread * 10000).toFixed(1)} pip` : "—"}
                </span>
              </div>
            </div>
            {high24 != null && low24 != null && (
              <div className="mt-1 text-[9px] text-text-secondary sm:hidden">
                (24h {low24.toFixed(4)}–{high24.toFixed(4)})
              </div>
            )}
          </div>

          <div className="flex shrink-0 items-center gap-0.5 rounded-lg border border-border bg-background p-0.5 sm:gap-2 sm:p-1">
            {['M15', '30m', 'H1'].map((tf) => (
              <button
                key={tf}
                onClick={() => onTimeframeChange?.(tf)}
                className={`px-2 py-1 text-[9px] font-medium rounded-md transition-colors sm:px-2.5 sm:text-[10px] ${
                  timeframe === tf
                    ? 'bg-primary text-white font-semibold'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          {session && (
            <span
              className={`hidden sm:inline-flex text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                isWeekend
                  ? "bg-amber-50 text-amber-700 border-amber-200"
                  : "bg-positive-light text-positive border-positive/20"
              }`}
            >
              {sessionLabel[session] ?? session}
            </span>
          )}
        </div>
      </div>

      <div className="mt-2 flex items-center justify-between gap-2 flex-wrap">
        {high24 != null && low24 != null && (
          <div className="hidden text-[10px] text-text-secondary sm:block">
            <span className="text-text-muted">24h</span> {low24.toFixed(4)} – {high24.toFixed(4)}
          </div>
        )}
      </div>
    </div>
  );
}
