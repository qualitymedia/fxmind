"use client";

interface PatternItem {
  name: string;
  type: string;
  bias: string;
  icon: string;
}

interface AIAnalysisProps {
  bias?: string;
  reasons?: Array<{
    category: string;
    reason: string;
    sentiment?: string;
  }>;
  patterns?: PatternItem[];
  bullProbability?: number;
  bearProbability?: number;
  neutralProbability?: number;
}

export function AIAnalysisPanel({
  bias = "NEUTRAL",
  reasons = [],
  patterns = [],
  bullProbability,
  bearProbability,
  neutralProbability,
}: AIAnalysisProps) {
  const hasReasons = reasons.length > 0;

  // Fallback: extract pattern items from reasons if patterns prop is empty
  const activePatterns =
    patterns.length > 0
      ? patterns
      : reasons
          .filter((r) => r.category === "Price Action & SMC" || r.category === "Pattern Trigger")
          .map((r) => ({
            name: r.reason,
            type: "SMC_PATTERNS",
            bias: r.sentiment === "SUPPORTIVE" ? bias : "NEUTRAL",
            icon: r.reason.slice(0, 2),
          }));

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-card space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-border">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
            AI Analysis & SMC Triggers
          </h2>
        </div>
        <span className="text-xs text-text-secondary font-medium">
          Bias:{" "}
          <span
            className={
              bias === "BULLISH"
                ? "text-positive font-bold uppercase"
                : bias === "BEARISH"
                ? "text-negative font-bold uppercase"
                : "text-text-muted font-bold uppercase"
            }
          >
            {bias}
          </span>
        </span>
      </div>

      {/* Active SMC & Price Action Pattern Badges */}
      <div>
        <span className="text-[11px] font-bold text-text-secondary uppercase tracking-wider block mb-2">
          Active Price Action & SMC Triggers
        </span>

        {activePatterns.length === 0 ? (
          <div className="p-2.5 rounded-lg bg-background/50 border border-border/60 text-xs text-text-muted flex items-center gap-2">
            <span className="text-sm">🔍</span>
            <span>No active SMC liquidity sweeps or candle patterns on current bar — scanning order flow…</span>
          </div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {activePatterns.map((p, idx) => {
              const isBull = p.bias === "BULLISH";
              const isBear = p.bias === "BEARISH";

              return (
                <div
                  key={idx}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border shadow-sm transition-all ${
                    isBull
                      ? "bg-positive/10 border-positive/30 text-positive"
                      : isBear
                      ? "bg-negative/10 border-negative/30 text-negative"
                      : "bg-primary/10 border-primary/30 text-primary"
                  }`}
                >
                  <span className="text-sm">{p.icon}</span>
                  <span>{p.name}</span>
                  <span className="text-[9px] uppercase px-1 py-0.2 rounded font-mono font-bold bg-card border border-border/40">
                    {p.type}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Probability bars */}
      {bullProbability != null && bearProbability != null && neutralProbability != null && (
        <div className="pt-2 space-y-1.5 border-t border-border/40">
          <span className="text-[11px] font-bold text-text-secondary uppercase tracking-wider block mb-1">
            Ensemble Calibrated Probabilities
          </span>
          <div className="flex items-center gap-2 text-[11px]">
            <span className="w-14 text-text-secondary">Bull</span>
            <div className="flex-1 bg-background rounded-full h-2 border border-border">
              <div
                className="bg-positive h-full rounded-full transition-all"
                style={{ width: `${(bullProbability * 100).toFixed(0)}%` }}
              />
            </div>
            <span className="w-10 text-right font-semibold text-text-primary">
              {(bullProbability * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex items-center gap-2 text-[11px]">
            <span className="w-14 text-text-secondary">Neutral</span>
            <div className="flex-1 bg-background rounded-full h-2 border border-border">
              <div
                className="bg-amber-400 h-full rounded-full transition-all"
                style={{ width: `${(neutralProbability * 100).toFixed(0)}%` }}
              />
            </div>
            <span className="w-10 text-right font-semibold text-text-primary">
              {(neutralProbability * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex items-center gap-2 text-[11px]">
            <span className="w-14 text-text-secondary">Bear</span>
            <div className="flex-1 bg-background rounded-full h-2 border border-border">
              <div
                className="bg-negative h-full rounded-full transition-all"
                style={{ width: `${(bearProbability * 100).toFixed(0)}%` }}
              />
            </div>
            <span className="w-10 text-right font-semibold text-text-primary">
              {(bearProbability * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      )}

      {/* Evidence reasons breakdown */}
      {hasReasons && (
        <div className="pt-2 border-t border-border/40 space-y-2 text-xs">
          <span className="text-[11px] font-bold text-text-secondary uppercase tracking-wider block">
            Signal Evidence Breakdown
          </span>
          <div className="space-y-2">
            {reasons.map((item, idx) => {
              const isSupportive = item.sentiment === "SUPPORTIVE" || item.sentiment === "CLEAR";
              const isOpposing = item.sentiment === "OPPOSING";

              return (
                <div key={idx} className="flex items-start justify-between py-1 border-b border-border/30 last:border-0">
                  <div className="flex items-start gap-2">
                    <span className="font-semibold text-text-primary w-32 flex-shrink-0 leading-tight">
                      {item.category}
                    </span>
                    <span className="text-text-secondary leading-tight">{item.reason}</span>
                  </div>

                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-semibold flex-shrink-0 ml-2 ${
                      isSupportive
                        ? "bg-positive-light text-positive border border-positive/20"
                        : isOpposing
                        ? "bg-negative-light text-negative border border-negative/20"
                        : "bg-background text-text-secondary border border-border"
                    }`}
                  >
                    {item.sentiment || "NEUTRAL"}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
