"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { createChart, ColorType, IChartApi, ISeriesApi, Time } from "lightweight-charts";
import { Candle } from "@/types/market";
import { fetchApi } from "@/lib/api";
import { TradingViewLiveChart } from "./tradingview-widget";
import { Activity, Sparkles } from "lucide-react";

interface MarketOverview {
  current_price: number;
  bid: number;
  ask: number;
  session: string;
}

interface FinancialChartProps {
  candles?: Candle[];
  timeframe?: string;
  showIndicators?: boolean;
  showAILayers?: boolean;
  tradeSetup?: {
    entryLow?: number;
    entryHigh?: number;
    stopLoss?: number;
    takeProfit?: number;
    isWatchLevel?: boolean;
  };
  volumeProfile?: {
    poc?: number;
    vah?: number;
    val?: number;
  };
}

export function MainChart({
  candles = [],
  timeframe = "M15",
  showIndicators = true,
  showAILayers = true,
  tradeSetup,
  volumeProfile,
}: FinancialChartProps) {
  const [chartMode, setChartMode] = useState<"tradingview" | "ai_overlay">("tradingview");
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const liveTickTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastCandleTimeRef = useRef<number | null>(null);

  const lastVol = candles.length > 0 ? candles[candles.length - 1].tick_volume : null;

  // --- Live tick updater ---
  const startLiveTick = useCallback(() => {
    if (liveTickTimer.current) clearInterval(liveTickTimer.current);

    liveTickTimer.current = setInterval(async () => {
      try {
        const overview = await fetchApi<MarketOverview>("/api/v1/market/GBPUSD");
        const livePrice = overview.current_price;

        if (!candleSeriesRef.current || !lastCandleTimeRef.current) return;

        if (candles.length > 0) {
          const lastC = candles[candles.length - 1];
          candleSeriesRef.current.update({
            time: lastCandleTimeRef.current as Time,
            open: lastC.open,
            high: Math.max(lastC.high, livePrice),
            low: Math.min(lastC.low, livePrice),
            close: livePrice,
          });
        }
      } catch {
        // Silently ignore live tick errors
      }
    }, 15_000);
  }, [candles]);

  // --- Single effect: create chart + load data + draw price lines ---
  useEffect(() => {
    if (!chartContainerRef.current || chartMode !== "ai_overlay") return;

    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
    }

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "#0F172A" },
        textColor: "#94A3B8",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: "#1E293B" },
        horzLines: { color: "#1E293B" },
      },
      crosshair: {
        vertLine: { color: "#475569", style: 2 },
        horzLine: { color: "#475569", style: 2 },
      },
      rightPriceScale: {
        borderColor: "#1E293B",
        autoScale: true,
      },
      timeScale: {
        borderColor: "#1E293B",
        timeVisible: true,
        secondsVisible: false,
      },
      height: 320,
    });

    chartRef.current = chart;

    const candleSeries = chart.addCandlestickSeries({
      upColor: "#10B981",
      downColor: "#EF4444",
      borderUpColor: "#10B981",
      borderDownColor: "#EF4444",
      wickUpColor: "#10B981",
      wickDownColor: "#EF4444",
      priceFormat: {
        type: "price",
        precision: 5,
        minMove: 0.00001,
      },
    });
    candleSeriesRef.current = candleSeries;

    // Load candle data immediately
    if (candles.length > 0) {
      const formatted = candles
        .map((c) => ({
          time: (Math.floor(new Date(c.timestamp).getTime() / 1000)) as Time,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close,
        }))
        .sort((a, b) => (a.time as number) - (b.time as number));

      const seen = new Set<number>();
      const deduplicated = formatted.filter((item) => {
        const t = item.time as number;
        if (seen.has(t)) return false;
        seen.add(t);
        return true;
      });

      if (deduplicated.length > 0) {
        candleSeries.setData(deduplicated);
        lastCandleTimeRef.current = deduplicated[deduplicated.length - 1].time as number;
        chart.timeScale().fitContent();
      }
    }

    // Add native Lightweight Charts price lines for Entry, SL, and TP
    if (showAILayers && tradeSetup) {
      const isWatch = tradeSetup.isWatchLevel;
      const prefix = isWatch ? "WATCH " : "";

      if (tradeSetup.takeProfit != null) {
        candleSeries.createPriceLine({
          price: tradeSetup.takeProfit,
          color: "#10B981",
          lineWidth: 2,
          lineStyle: 2,
          axisLabelVisible: true,
          title: `${prefix}TP ${tradeSetup.takeProfit.toFixed(4)}`,
        });
      }

      if (tradeSetup.entryHigh != null && tradeSetup.entryLow != null) {
        const midEntry = (tradeSetup.entryHigh + tradeSetup.entryLow) / 2.0;
        candleSeries.createPriceLine({
          price: midEntry,
          color: "#3B82F6",
          lineWidth: 1,
          lineStyle: 1,
          axisLabelVisible: true,
          title: `${prefix}ENTRY ${midEntry.toFixed(4)}`,
        });
      } else if (tradeSetup.entryLow != null) {
        candleSeries.createPriceLine({
          price: tradeSetup.entryLow,
          color: "#3B82F6",
          lineWidth: 1,
          lineStyle: 1,
          axisLabelVisible: true,
          title: `${prefix}ENTRY ${tradeSetup.entryLow.toFixed(4)}`,
        });
      }

      if (tradeSetup.stopLoss != null) {
        candleSeries.createPriceLine({
          price: tradeSetup.stopLoss,
          color: "#EF4444",
          lineWidth: 2,
          lineStyle: 2,
          axisLabelVisible: true,
          title: `${prefix}SL ${tradeSetup.stopLoss.toFixed(4)}`,
        });
      }
    }

    // Add Volume Profile POC, VAH, and VAL Price Lines cleanly
    if (showAILayers && volumeProfile) {
      if (volumeProfile.poc != null) {
        candleSeries.createPriceLine({
          price: volumeProfile.poc,
          color: "#F59E0B", // Gold
          lineWidth: 2,
          lineStyle: 0, // Solid
          axisLabelVisible: true,
          title: `POC ${volumeProfile.poc.toFixed(4)}`,
        });
      }

      if (volumeProfile.vah != null) {
        candleSeries.createPriceLine({
          price: volumeProfile.vah,
          color: "#06B6D4", // Cyan
          lineWidth: 1,
          lineStyle: 2, // Dashed
          axisLabelVisible: false,
          title: `VAH ${volumeProfile.vah.toFixed(4)}`,
        });
      }

      if (volumeProfile.val != null) {
        candleSeries.createPriceLine({
          price: volumeProfile.val,
          color: "#8B5CF6", // Purple
          lineWidth: 1,
          lineStyle: 2, // Dashed
          axisLabelVisible: false,
          title: `VAL ${volumeProfile.val.toFixed(4)}`,
        });
      }
    }

    // Responsive resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };
    window.addEventListener("resize", handleResize);

    startLiveTick();

    return () => {
      window.removeEventListener("resize", handleResize);
      if (liveTickTimer.current) clearInterval(liveTickTimer.current);
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
    };
  }, [candles, timeframe, tradeSetup, volumeProfile, showAILayers, chartMode, startLiveTick]);

  return (
    <div className="bg-card border border-border rounded-xl p-2 shadow-card sm:p-3">
      {/* Chart Controls & Mode Switcher */}
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-border text-[10px] sm:text-xs flex-wrap gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center bg-background p-0.5 rounded-lg border border-border">
            <button
              onClick={() => setChartMode("tradingview")}
              className={`flex items-center gap-1 px-2 py-1 text-[10px] sm:text-xs font-semibold rounded-md transition-colors ${
                chartMode === "tradingview"
                  ? "bg-primary text-white shadow-sm"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              TradingView Live Stream
            </button>
            <button
              onClick={() => setChartMode("ai_overlay")}
              className={`flex items-center gap-1 px-2 py-1 text-[10px] sm:text-xs font-semibold rounded-md transition-colors ${
                chartMode === "ai_overlay"
                  ? "bg-primary text-white shadow-sm"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              AI Setup Lines Overlay
            </button>
          </div>

          <span className="text-text-muted text-[11px]">
            {chartMode === "tradingview" ? "FX:GBPUSD Live WebSocket" : `GBP/USD ${timeframe}`}
          </span>
        </div>

        <div className="flex items-center gap-2 text-[11px]">
          {chartMode === "tradingview" ? (
            <span className="px-2 py-0.5 rounded-full bg-positive/10 border border-positive/20 text-positive font-bold flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-positive animate-pulse" />
              Real-Time
            </span>
          ) : (
            <>
              {lastVol != null && (
                <span className="px-2 py-0.5 rounded bg-background border border-border text-text-secondary font-medium">
                  Vol {lastVol.toLocaleString()}
                </span>
              )}
              <span className="px-2 py-0.5 rounded bg-positive/10 border border-positive/20 text-positive font-medium">
                ● Live
              </span>
            </>
          )}
        </div>
      </div>

      {/* Conditional Chart Rendering */}
      {chartMode === "tradingview" ? (
        <TradingViewLiveChart
          symbol="FX:GBPUSD"
          interval={timeframe === "H1" ? "60" : timeframe === "30m" ? "30" : "15"}
          theme="dark"
        />
      ) : (
        <div ref={chartContainerRef} className="w-full relative min-h-[440px]">
          {showAILayers && tradeSetup && tradeSetup.takeProfit != null && (
            <div className="absolute right-16 top-12 z-10 space-y-1 text-[10px] font-bold pointer-events-none">
              {tradeSetup.isWatchLevel ? (
                <div className="bg-amber-500/20 border border-amber-400 text-amber-300 px-3 py-1 rounded shadow-lg flex items-center gap-1">
                  <span>📌 KEY WATCH LEVELS — PENDING TRIGGER</span>
                </div>
              ) : (
                <div className="bg-emerald-500/20 border border-emerald-400 text-emerald-300 px-3 py-1 rounded shadow-lg flex items-center gap-1">
                  <span>⚡ ACTIVE SETUP LINES ON CHART</span>
                </div>
              )}
            </div>
          )}

          {candles.length === 0 && (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-text-muted">
              <div className="text-2xl mb-2 opacity-40">📊</div>
              <p className="text-xs">Waiting for candle data from API…</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
