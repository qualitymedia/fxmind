"use client";

interface PatternItem {
  name: string;
  type: string;
  bias: string;
}

interface AIMetricsSidebarProps {
  bias?: string;
  confidence?: number;
  regime?: string;
  bullProbability?: number;
  bearProbability?: number;
  neutralProbability?: number;
  patterns?: PatternItem[];
  reasons?: Array<{
    category: string;
    reason: string;
    sentiment?: string;
  }>;
  tradeStatus?: string;
  direction?: string;
  entryLow?: number;
  entryHigh?: number;
  stopLoss?: number;
  takeProfit?: number;
  riskReward?: number;
}

function CircularGauge({
  value,
  label,
  color,
  size = 52,
}: {
  value: number;
  label: string;
  color: string;
  size?: number;
}) {
  const pct = Math.min(Math.max(value * 100, 0), 100);
  const radius = (size - 6) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (pct / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-0.5">
      <div className="relative flex items-center justify-center">
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#E2E8F0"
            strokeWidth={3.5}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={3.5}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-500 ease-out"
          />
        </svg>
        <span className="absolute text-xs font-bold font-display text-text-primary">
          {pct.toFixed(0)}%
        </span>
      </div>
      <span className="text-[9px] font-bold text-text-secondary uppercase tracking-tight">
        {label}
      </span>
    </div>
  );
}

export function AIMetricsSidebar({
  bias,
  confidence,
  regime,
  bullProbability,
  bearProbability,
  neutralProbability,
  patterns = [],
  reasons = [],
  tradeStatus = "NO_TRADE",
  direction,
  entryLow,
  entryHigh,
  stopLoss,
  takeProfit,
  riskReward,
}: AIMetricsSidebarProps) {
  const biasColor =
    bias === "BULLISH"
      ? "text-positive"
      : bias === "BEARISH"
      ? "text-negative"
      : "text-text-muted";
  const confidencePercent =
    confidence !== undefined ? (confidence * 100).toFixed(0) : null;

  const statusColor =
    tradeStatus === "ACTIVE"
      ? "bg-positive/10 text-positive border-positive/30"
      : "bg-background text-text-muted border-border";

  const activePatterns =
    patterns.length > 0
      ? patterns
      : reasons
          .filter(
            (r) =>
              r.category === "Price Action & SMC" ||
              r.category === "Pattern Trigger"
          )
          .map((r) => ({
            name: r.reason,
            type: "SMC",
            bias: r.sentiment === "SUPPORTIVE" ? bias : "NEUTRAL",
          }));

  return (
    <div className="bg-card border border-border rounded-xl shadow-card flex flex-col overflow-hidden">
      <div className="px-3 py-2 border-b border-border flex items-center justify-between bg-card-secondary/40">
        <h3 className="text-xs font-bold font-display text-text-primary uppercase tracking-wider">
          MODEL INSIGHT
        </h3>
        <span className={`text-xs font-bold uppercase ${biasColor}`}>
          {bias ?? "NO DATA"}
        </span>
      </div>

      <div className="p-3 space-y-3">
        <div className="flex items-center justify-between">
          <span
            className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold border ${statusColor}`}
          >
            {tradeStatus === "ACTIVE" ? `${direction ?? ""} ACTIVE` : "NO TRADE"}
          </span>
          <span className="text-[10px] text-text-muted font-mono">{regime ?? "—"}</span>
        </div>

        {bullProbability != null &&
          bearProbability != null &&
          neutralProbability != null && (
            <div className="bg-background/40 p-2 rounded-lg border border-border/50">
              <span className="text-[9px] font-bold text-text-secondary uppercase tracking-wider block mb-1.5 text-center">
                Model Probabilities
              </span>
              <div className="flex items-center justify-around">
                <CircularGauge
                  value={bullProbability}
                  label="Bull"
                  color="#10B981"
                  size={52}
                />
                <CircularGauge
                  value={neutralProbability}
                  label="Neutral"
                  color="#f59e0b"
                  size={52}
                />
                <CircularGauge
                  value={bearProbability}
                  label="Bear"
                  color="#EF4444"
                  size={52}
                />
              </div>
            </div>
          )}

        {/* Active Patterns */}
        {activePatterns.length > 0 && (
          <div>
            <span className="text-[9px] font-bold text-text-secondary uppercase tracking-wider block mb-1">
              Active Patterns
            </span>
            <div className="flex flex-wrap gap-1">
              {activePatterns.slice(0, 3).map((p, idx) => {
                const isBull = p.bias === "BULLISH";
                const isBear = p.bias === "BEARISH";
                return (
                  <span
                    key={idx}
                    className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-semibold border ${
                      isBull
                        ? "bg-positive/10 border-positive/30 text-positive"
                        : isBear
                        ? "bg-negative/10 border-negative/30 text-negative"
                        : "bg-primary/10 border-primary/30 text-primary"
                    }`}
                  >
                    <span>{p.name}</span>
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Signal Evidence (Truncated to avoid wasting space) */}
        {reasons.length > 0 && (
          <div>
            <span className="text-[9px] font-bold text-text-secondary uppercase tracking-wider block mb-1">
              Signal Evidence
            </span>
            <div className="space-y-1">
              {reasons.slice(0, 3).map((item, idx) => {
                const isSupportive =
                  item.sentiment === "SUPPORTIVE" || item.sentiment === "CLEAR";
                const isOpposing = item.sentiment === "OPPOSING";
                return (
                  <div
                    key={idx}
                    className="flex items-center justify-between gap-1 text-[9px]"
                  >
                    <span className="text-text-secondary truncate max-w-[170px]" title={item.reason}>
                      {item.reason}
                    </span>
                    <span
                      className={`px-1 py-0.2 rounded text-[8px] font-bold flex-shrink-0 uppercase ${
                        isSupportive
                          ? "bg-positive/10 text-positive"
                          : isOpposing
                          ? "bg-negative/10 text-negative"
                          : "bg-background text-text-muted"
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

        {/* Confidence Meter */}
        {confidence !== undefined && (
        <div>
          <div className="flex justify-between text-[9px] text-text-muted mb-0.5">
            <span className="font-semibold uppercase">Confidence</span>
            <span className="font-bold text-text-primary font-mono">
              {confidencePercent}%
            </span>
          </div>
          <div className="w-full bg-background rounded-full h-1.5 border border-border overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                confidence >= 0.65
                  ? "bg-positive"
                  : confidence >= 0.5
                  ? "bg-amber-400"
                  : "bg-negative"
              }`}
              style={{ width: `${(confidence * 100).toFixed(0)}%` }}
            />
          </div>
        </div>
        )}
      </div>
    </div>
  );
}
