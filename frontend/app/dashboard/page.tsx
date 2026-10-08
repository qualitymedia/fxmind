"use client";

import { useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { PriceHeader } from "@/components/dashboard/price-header";
import { AIBiasCard } from "@/components/dashboard/ai-bias-card";
import { RegimeCard } from "@/components/dashboard/regime-card";
import { SignalCard } from "@/components/dashboard/signal-card";
import { SetupQualityCard } from "@/components/dashboard/setup-quality-card";
import { VolumeProfileCard } from "@/components/dashboard/volume-profile-card";
import { PaperPortfolioCard } from "@/components/dashboard/paper-portfolio-card";
import { MainChart } from "@/features/market/chart";
import { AIMetricsSidebar } from "@/components/dashboard/ai-metrics-sidebar";
import { useDashboardData } from "@/lib/useDashboardData";
import {
  AlertTriangle,
  RefreshCw,
  Wifi,
  WifiOff,
  Moon,
  ArrowRight,
  Zap,
  BarChart3,
  Terminal,
} from "lucide-react";

export default function DashboardPage() {
  const [timeframe, setTimeframe] = useState("M15");
  const {
    analysis,
    candles,
    signals,
    volumeProfile,
    paperSummary,
    paperPositions,
    tradeHistory,
    loading,
    error,
    lastRefresh,
    refetch,
  } = useDashboardData(timeframe);

  const signal = analysis?.signal ?? null;
  const market = analysis?.market ?? null;

  const isWeekendClosed =
    signal?.market?.session === "WEEKEND_CLOSED" ||
    market?.session === "WEEKEND_CLOSED";

  // Derive quality label from confidence
  const quality =
    signal && signal.confidence >= 0.7
      ? "Very Strong"
      : signal && signal.confidence >= 0.62
      ? "Strong"
      : signal && signal.confidence >= 0.58
      ? "Moderate"
      : "Weak";

  const quickLinks = [
    { label: "Recent Signals", href: "/signals", icon: Zap, count: signals?.length ?? 0 },
    { label: "Performance", href: "/performance", icon: BarChart3 },
    { label: "Activity Audit", href: "/logs", icon: Terminal, badge: "LIVE" },
  ];

  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
        <Header />

        {/* Live Data Status Bar */}
        <div className="px-5 py-1.5 flex items-center justify-between border-b border-border bg-card text-xs">
          <div className="flex items-center gap-3">
            {loading ? (
              <span className="flex items-center gap-1.5 text-text-muted">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Fetching live data…
              </span>
            ) : error ? (
              <span className="flex items-center gap-1.5 text-negative font-medium">
                <WifiOff className="w-3.5 h-3.5" />
                Backend unreachable
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-positive font-medium">
                <Wifi className="w-3.5 h-3.5" />
                Live — polling 15 s
              </span>
            )}
            {lastRefresh && (
              <span className="text-text-muted flex items-center gap-2">
                <span>Updated: {lastRefresh.toLocaleTimeString()}</span>
                <button
                  onClick={() => refetch()}
                  className="px-2 py-0.5 rounded bg-card-secondary hover:bg-border border border-border text-[10px] font-semibold text-text-primary flex items-center gap-1 transition-colors"
                  title="Manual Sync"
                >
                  <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
                  Sync
                </button>
              </span>
            )}
          </div>
          <span className="font-mono text-text-secondary text-[11px]">
            Engine: FXMind Alpha v2
          </span>
        </div>

        {/* Banners */}
        {isWeekendClosed && (
          <div className="mx-5 mt-3 flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-2 text-xs text-amber-300">
            <Moon className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <span>
              <strong>Forex Market Closed (Weekend)</strong> — Live analysis resumes Sunday 22:00 UTC. Historical data shown below.
            </span>
          </div>
        )}

        {error && !loading && (
          <div className="mx-5 mt-3 flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2 text-xs text-red-400">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span><strong>API Error:</strong> {error}</span>
          </div>
        )}

        {/* Main Dashboard Layout */}
        <main className="p-4 md:p-5 space-y-4 max-w-[1800px] w-full mx-auto">
          {/* 1. Price Header */}
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

          {/* 2. Top KPI Row — 3 Core Cards (AI Bias, Regime, Signal Status) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
            <AIBiasCard
              bias={(signal?.bias as any) ?? "NEUTRAL"}
              confidence={signal?.confidence ?? 0.3333}
            />
            <RegimeCard regime={(signal?.regime as any) ?? "RANGING"} />
            <SignalCard
              direction={(signal?.trade?.direction as any) ?? null}
              status={signal?.trade?.status ?? "NO_TRADE"}
              strategyType={(signal?.trade as any)?.strategy_type ?? null}
            />
          </div>

          {/* 3. Main Content: Chart (Left 3 cols) + AI Insight & Setup Quality (Right 1 col) */}
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
            {/* Main Chart */}
            <div className="xl:col-span-3">
              <MainChart
                candles={candles}
                timeframe={timeframe}
                tradeSetup={
                  signal?.trade?.entry_low != null
                    ? {
                        entryLow: signal.trade.entry_low ?? undefined,
                        entryHigh: signal.trade.entry_high ?? undefined,
                        stopLoss: signal.trade.stop_loss ?? undefined,
                        takeProfit: signal.trade.take_profit ?? undefined,
                        isWatchLevel:
                          (signal.trade as any)?.is_watch_level ??
                          signal.trade.status === "NO_TRADE",
                      }
                    : undefined
                }
                volumeProfile={
                  volumeProfile
                    ? {
                        poc: volumeProfile.poc,
                        vah: volumeProfile.vah,
                        val: volumeProfile.val,
                      }
                    : undefined
                }
              />
            </div>

            {/* Right Column Stack: AI Insight (Top) + Setup Quality (Directly Below) */}
            <div className="xl:col-span-1 flex flex-col gap-3">
              {/* AI INSIGHT */}
              <AIMetricsSidebar
                bias={signal?.bias ?? "NEUTRAL"}
                confidence={signal?.confidence ?? 0.33}
                regime={signal?.regime ?? "RANGING"}
                bullProbability={signal?.model?.bull_probability}
                bearProbability={signal?.model?.bear_probability}
                neutralProbability={signal?.model?.neutral_probability}
                patterns={signal?.patterns ?? []}
                reasons={signal?.reasons ?? []}
                tradeStatus={signal?.trade?.status ?? "NO_TRADE"}
                direction={signal?.trade?.direction ?? undefined}
                entryLow={signal?.trade?.entry_low ?? undefined}
                entryHigh={signal?.trade?.entry_high ?? undefined}
                stopLoss={signal?.trade?.stop_loss ?? undefined}
                takeProfit={signal?.trade?.take_profit ?? undefined}
                riskReward={signal?.trade?.risk_reward ?? undefined}
              />

              {/* Setup Quality Card */}
              <SetupQualityCard
                quality={
                  signal?.trade?.status === "ACTIVE" ? quality : "Key Watch Levels"
                }
                riskReward={signal?.trade?.risk_reward ?? null}
                entryLow={signal?.trade?.entry_low ?? undefined}
                entryHigh={signal?.trade?.entry_high ?? undefined}
                stopLoss={signal?.trade?.stop_loss ?? undefined}
                takeProfit={signal?.trade?.take_profit ?? undefined}
              />
            </div>
          </div>

          {/* 4. Institutional Analytics & Live Execution Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <VolumeProfileCard
              volumeProfile={volumeProfile}
              currentPrice={market?.current_price}
            />
            <PaperPortfolioCard
              paperSummary={paperSummary}
              paperPositions={paperPositions}
              tradeHistory={tradeHistory}
            />
          </div>

          {/* 5. Quick Links */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {quickLinks.map((link) => {
              const Icon = link.icon;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className="group flex items-center justify-between bg-card border border-border rounded-xl px-4 py-3 shadow-card hover:border-primary/40 transition-all text-xs"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Icon className="w-4 h-4 text-primary" />
                    </div>
                    <div>
                      <span className="font-semibold text-text-primary block">
                        {link.label}
                      </span>
                      {link.count != null && (
                        <span className="text-[10px] text-text-secondary">
                          {link.count} recent
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5">
                    {link.badge && (
                      <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        {link.badge}
                      </span>
                    )}
                    <ArrowRight className="w-3.5 h-3.5 text-text-muted group-hover:text-primary transition-colors" />
                  </div>
                </Link>
              );
            })}
          </div>
        </main>
      </div>
    </div>
  );
}
