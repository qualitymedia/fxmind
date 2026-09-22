"use client";

import { useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { PriceHeader } from "@/components/dashboard/price-header";
import { MainChart } from "@/features/market/chart";
import { MarketContextPanel } from "@/components/dashboard/market-context";
import { H1ContextPanel } from "@/components/dashboard/h1-context";
import { EconomicCalendarPanel } from "@/components/dashboard/economic-calendar";
import { useDashboardData } from "@/lib/useDashboardData";
import { RefreshCw, Wifi, WifiOff } from "lucide-react";

export default function MarketPage() {
  const [timeframe, setTimeframe] = useState("M15");
  const { analysis, candles, loading, error, lastRefresh } = useDashboardData(timeframe);

  const signal = analysis?.signal ?? null;
  const market = analysis?.market ?? null;
  const crossMarket = analysis?.cross_market ?? [];
  const h1Ctx = analysis?.h1_context ?? null;

  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        <Header />

        {/* Live Data Status Bar */}
        <div className="px-6 py-2 flex items-center justify-between border-b border-border bg-card text-xs">
          <div className="flex items-center gap-3">
            {loading ? (
              <span className="flex items-center gap-1.5 text-text-muted">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Loading historical & live candles…
              </span>
            ) : error ? (
              <span className="flex items-center gap-1.5 text-negative font-medium">
                <WifiOff className="w-3.5 h-3.5" />
                Backend connection error — {error}
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-positive font-medium">
                <Wifi className="w-3.5 h-3.5" />
                Live Feed Connected &bull; {candles.length} Candles Loaded
              </span>
            )}
            {lastRefresh && (
              <span className="text-text-muted">
                Last updated: {lastRefresh.toLocaleTimeString()}
              </span>
            )}
          </div>
          {signal?.model_version && (
            <span className="font-mono text-text-secondary">
              Model: {signal.model_version}
            </span>
          )}
        </div>

        <main className="p-6 space-y-6 max-w-[1800px] w-full mx-auto">
          {/* Price Header */}
          <PriceHeader
            symbol="GBP/USD"
            price={market?.current_price}
            change={market?.change}
            changePercent={market?.change_percent}
            bid={market?.bid}
            ask={market?.ask}
            spread={market?.spread}
            timeframe={timeframe}
            onTimeframeChange={setTimeframe}
            session={market?.session}
            high24={market?.high_24h}
            low24={market?.low_24h}
          />

          {/* Chart + Market Context */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <MainChart
                candles={candles}
                timeframe={timeframe}
                tradeSetup={
                  signal?.trade?.status === "ACTIVE"
                    ? {
                        entryLow: signal.trade.entry_low ?? undefined,
                        entryHigh: signal.trade.entry_high ?? undefined,
                        stopLoss: signal.trade.stop_loss ?? undefined,
                        takeProfit: signal.trade.take_profit ?? undefined,
                      }
                    : undefined
                }
              />
            </div>
            <div className="space-y-6">
              <MarketContextPanel items={crossMarket as any} />
              <H1ContextPanel
                bias={h1Ctx?.bias ?? "NEUTRAL"}
                trend={h1Ctx?.trend ?? "—"}
                rsi={h1Ctx?.rsi_h1 ?? 50}
                emaStructure={h1Ctx?.ema_structure ?? "—"}
                atr={h1Ctx?.atr_h1 ?? 0}
                distFromHigh={h1Ctx?.dist_from_high ?? "—"}
              />
            </div>
          </div>

          {/* Economic Calendar */}
          <EconomicCalendarPanel events={analysis?.upcoming_events ?? []} />
        </main>
      </div>
    </div>
  );
}
