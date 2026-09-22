"use client";

import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface MarketItem {
  symbol: string;
  current_value: number;
  change_percent: number;
  bias?: string;
  correlation_note?: string;
}

interface MarketContextProps {
  items?: MarketItem[];
}

export function MarketContextPanel({ items = [] }: MarketContextProps) {
  // Count bullish vs bearish for alignment meter
  const bullCount = items.filter((i) => i.bias === "BULLISH").length;
  const totalWithBias = items.filter((i) => i.bias != null).length;
  const alignmentPct =
    totalWithBias > 0 ? Math.round((bullCount / totalWithBias) * 100) : 0;

  const symbolDisplay = (sym: string) =>
    sym.replace("USDJPY", "USD/JPY").replace("EURUSD", "EUR/USD")
      .replace("EURGBP", "EUR/GBP").replace("GBPUSD", "GBP/USD");

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-card">
      <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
        <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
          Market Context
        </h2>
        <span className="text-xs text-text-muted">Contextual evidence</span>
      </div>

      {items.length === 0 ? (
        <p className="text-xs text-text-muted py-4 text-center">Loading cross-market data…</p>
      ) : (
        <div className="space-y-3 text-xs">
          {items.map((item) => {
            const isPos = item.change_percent > 0;
            const isNeg = item.change_percent < 0;

            return (
              <div
                key={item.symbol}
                className="flex items-center justify-between py-1 border-b border-border/40 last:border-0"
              >
                <div className="flex items-center gap-3">
                  <span className="font-bold text-text-primary w-20">
                    {symbolDisplay(item.symbol)}
                  </span>
                  <span className="text-text-secondary">
                    {item.current_value.toFixed(item.current_value > 10 ? 2 : 4)}
                  </span>
                  <span
                    className={`inline-flex items-center font-medium ${
                      isPos
                        ? "text-positive"
                        : isNeg
                        ? "text-negative"
                        : "text-text-secondary"
                    }`}
                  >
                    {isPos ? (
                      <ArrowUpRight className="w-3 h-3" />
                    ) : isNeg ? (
                      <ArrowDownRight className="w-3 h-3" />
                    ) : (
                      <Minus className="w-3 h-3" />
                    )}
                    {isPos ? "+" : ""}
                    {item.change_percent.toFixed(2)}%
                  </span>
                </div>

                {item.bias && (
                  <span
                    className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                      item.bias === "BULLISH"
                        ? "bg-positive-light text-positive"
                        : item.bias === "BEARISH"
                        ? "bg-negative-light text-negative"
                        : "bg-background text-text-secondary"
                    }`}
                  >
                    {item.bias}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Cross-market alignment meter */}
      <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-xs">
        <span className="text-text-secondary font-medium">Cross-market alignment</span>
        <div className="flex items-center gap-2">
          <div className="w-24 bg-background rounded-full h-1.5 border border-border">
            <div
              className="bg-positive h-full rounded-full transition-all"
              style={{ width: `${alignmentPct}%` }}
            />
          </div>
          <span className="font-bold text-text-primary">{alignmentPct}%</span>
        </div>
      </div>
    </div>
  );
}
