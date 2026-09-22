"use client";

interface EquityPoint {
  index: number;
  equity: number;
}

interface PerformanceSummaryProps {
  profitFactor?: number;
  sharpeRatio?: number;
  maxDrawdown?: string;
  winRate?: string;
  expectancy?: number;
  tradeCount?: number;
  accuracy?: number;
  equityCurve?: EquityPoint[];
}

export function PerformanceSummaryPanel({
  profitFactor,
  sharpeRatio,
  maxDrawdown,
  winRate,
  expectancy,
  tradeCount,
  accuracy,
  equityCurve = [],
}: PerformanceSummaryProps) {
  const fmt = (v?: number, dp = 2) => (v != null ? v.toFixed(dp) : "—");
  const pnlPositive = (profitFactor ?? 0) >= 1.0;

  // Build sparkline heights from the real equity curve
  const sparkHeights = (() => {
    if (equityCurve.length < 2) return [] as number[];
    const equities = equityCurve.map((p) => p.equity);
    const min = Math.min(...equities);
    const max = Math.max(...equities);
    const range = max - min || 1;
    return equities.map((e) => Math.round(((e - min) / range) * 85) + 10);
  })();

  const curveLabel =
    equityCurve.length >= 2
      ? `Trade 1 – ${equityCurve[equityCurve.length - 1].index}`
      : "Walk-Forward Test";

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-card">
      <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
        <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
          Performance{" "}
          <span className="text-text-muted font-normal text-xs">(Walk-Forward)</span>
        </h2>
        <span className="text-xs text-text-muted font-medium">Yahoo Finance data</span>
      </div>

      {/* Grid Metrics — real values from API */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-background p-2.5 rounded-lg border border-border">
          <span className="text-[11px] text-text-secondary block">Profit Factor</span>
          <span
            className={`text-base font-bold font-display mt-0.5 block ${
              pnlPositive ? "text-positive" : "text-negative"
            }`}
          >
            {fmt(profitFactor)}
          </span>
        </div>

        <div className="bg-background p-2.5 rounded-lg border border-border">
          <span className="text-[11px] text-text-secondary block">Sharpe</span>
          <span className="text-base font-bold font-display text-text-primary mt-0.5 block">
            {fmt(sharpeRatio)}
          </span>
        </div>

        <div className="bg-background p-2.5 rounded-lg border border-border">
          <span className="text-[11px] text-text-secondary block">Max DD</span>
          <span className="text-base font-bold font-display text-negative mt-0.5 block">
            {maxDrawdown ?? "—"}
          </span>
        </div>

        <div className="bg-background p-2.5 rounded-lg border border-border">
          <span className="text-[11px] text-text-secondary block">Win Rate</span>
          <span className="text-base font-bold font-display text-positive mt-0.5 block">
            {winRate ?? "—"}
          </span>
        </div>

        <div className="bg-background p-2.5 rounded-lg border border-border">
          <span className="text-[11px] text-text-secondary block">Expectancy</span>
          <span className="text-base font-bold font-display text-text-primary mt-0.5 block">
            {expectancy != null ? `${expectancy.toFixed(2)} pip` : "—"}
          </span>
        </div>

        <div className="bg-background p-2.5 rounded-lg border border-border">
          <span className="text-[11px] text-text-secondary block">Trades</span>
          <span className="text-base font-bold font-display text-text-primary mt-0.5 block">
            {tradeCount?.toLocaleString() ?? "—"}
          </span>
        </div>
      </div>

      {/* Model Accuracy row */}
      {accuracy != null && (
        <div className="flex items-center justify-between text-xs mb-3 px-1">
          <span className="text-text-secondary">Model OOS Accuracy</span>
          <span className="font-bold text-primary">{(accuracy * 100).toFixed(1)}%</span>
        </div>
      )}

      {/* Equity Curve Sparkline — derived from real trade stats */}
      <div className="pt-2 border-t border-border">
        <div className="flex justify-between text-[11px] text-text-secondary mb-1">
          <span>Equity Curve</span>
          <span className="text-positive font-semibold">{curveLabel}</span>
        </div>
        <div className="h-10 w-full bg-background rounded border border-border flex items-end p-1 gap-0.5">
          {sparkHeights.length > 0 ? (
            sparkHeights.map((h, i) => (
              <div
                key={i}
                className="flex-1 bg-positive/75 rounded-t transition-all"
                style={{ height: `${h}%` }}
              />
            ))
          ) : (
            <div className="flex-1 flex items-center justify-center text-[10px] text-text-muted">
              Loading curve…
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
