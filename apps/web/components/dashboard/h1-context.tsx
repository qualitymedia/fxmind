"use client";

interface H1ContextProps {
  bias?: string;
  trend?: string;
  rsi?: number;
  emaStructure?: string;
  atr?: number;
  distFromHigh?: string;
}

export function H1ContextPanel({
  bias = "NEUTRAL",
  trend = "—",
  rsi,
  emaStructure = "—",
  atr,
  distFromHigh = "—",
}: H1ContextProps) {
  const biasColor =
    bias === "BULLISH"
      ? "bg-positive-light text-positive"
      : bias === "BEARISH"
      ? "bg-negative-light text-negative"
      : "bg-background text-text-secondary border border-border";

  const emaColor =
    emaStructure === "Bullish"
      ? "text-positive"
      : emaStructure === "Bearish"
      ? "text-negative"
      : "text-text-primary";

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-card">
      <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
        <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
          H1 Context
        </h2>
        <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${biasColor}`}>
          {bias}
        </span>
      </div>

      <div className="space-y-2.5 text-xs">
        <div className="flex justify-between items-center py-1 border-b border-border/50">
          <span className="text-text-secondary">Trend</span>
          <span className="font-semibold text-text-primary">{trend}</span>
        </div>
        <div className="flex justify-between items-center py-1 border-b border-border/50">
          <span className="text-text-secondary">RSI (H1)</span>
          <span className="font-semibold text-text-primary">
            {rsi != null ? rsi.toFixed(1) : "—"}
          </span>
        </div>
        <div className="flex justify-between items-center py-1 border-b border-border/50">
          <span className="text-text-secondary">EMA Structure</span>
          <span className={`font-semibold ${emaColor}`}>{emaStructure}</span>
        </div>
        <div className="flex justify-between items-center py-1 border-b border-border/50">
          <span className="text-text-secondary">ATR (H1)</span>
          <span className="font-semibold text-text-primary">
            {atr != null && atr > 0 ? atr.toFixed(5) : "—"}
          </span>
        </div>
        <div className="flex justify-between items-center py-1">
          <span className="text-text-secondary">Dist. from 24h High</span>
          <span className="font-semibold text-text-primary">{distFromHigh}</span>
        </div>
      </div>
    </div>
  );
}
