"use client";

interface ModelInfoProps {
  version?: string;
  type?: string;
  trainingPeriod?: string;
  featureCount?: number;
  calibration?: string;
  lastValidation?: string;
  accuracy?: number;
  dataSource?: string;
}

export function ModelInfoPanel({
  version,
  type,
  trainingPeriod,
  featureCount,
  calibration,
  lastValidation,
  accuracy,
  dataSource,
}: ModelInfoProps) {
  const row = (label: string, value: React.ReactNode) => (
    <div className="flex justify-between items-center py-1 border-b border-border/50 last:border-0">
      <span className="text-text-secondary">{label}</span>
      <span className="font-semibold text-text-primary text-right max-w-[55%] truncate">
        {value ?? "—"}
      </span>
    </div>
  );

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-card">
      <div className="flex items-center justify-between pb-3 border-b border-border mb-4">
        <h2 className="text-sm font-bold font-display text-text-primary uppercase tracking-wider">
          Model Info
        </h2>
        <span className="text-xs font-medium px-2 py-0.5 rounded bg-positive-light text-positive">
          PRODUCTION
        </span>
      </div>

      <div className="space-y-2.5 text-xs">
        {row("Version", <span className="font-mono">{version ?? "—"}</span>)}
        {row("Model Type", type)}
        {row("Data Source",
          <span className="text-positive font-semibold">
            {dataSource ?? "Yahoo Finance (Authentic)"}
          </span>
        )}
        {row("Training Bars", trainingPeriod)}
        {row("Feature Count", featureCount != null ? `${featureCount} features` : undefined)}
        {row("Calibration", calibration)}
        {accuracy != null &&
          row(
            "OOS Accuracy",
            <span className="text-primary font-bold">{(accuracy * 100).toFixed(1)}%</span>
          )}
        {row(
          "Last Validated",
          lastValidation
            ? new Date(lastValidation).toLocaleDateString("en-GB", {
                year: "numeric",
                month: "short",
                day: "numeric",
              })
            : undefined
        )}
      </div>

      <p className="mt-4 text-[10px] text-text-muted leading-relaxed border-t border-border pt-3">
        This is an <strong>analysis-only</strong> system. Model output is probabilistic and must
        never be treated as financial advice. No trades are executed automatically.
      </p>
    </div>
  );
}
