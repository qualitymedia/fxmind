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
  Moon,
  ArrowRight,
  Zap,
  BarChart3,
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
    refreshing,
    error,
    lastRefresh,
  } = useDashboardData(timeframe);

  const signal = analysis?.signal ?? null;
  const market = analysis?.market ?? null;
  const modelUnavailable = Boolean(
    signal?.reasons?.some((reason) =>
      reason.reason.toLowerCase().includes("ai analysis model is unavailable")
    )
  );

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
    { label: "Signals", href: "/signals", icon: Zap },
    { label: "Performance", href: "/performance", icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-[#eef3f7] md:bg-background text-text-primary">
      <div className="mx-auto w-full md:max-w-none">
        <div className="md:flex md:min-h-screen">
          <Sidebar />

          <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden md:rounded-none">
            <Header />

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
        {modelUnavailable && (
          <div className="mx-5 mt-3 flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-2 text-xs text-amber-300">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>The analysis model is unavailable. Bias probabilities are hidden until predictions are available.</span>
          </div>
        )}
        {lastRefresh && (
          <div className="px-3 pt-3 text-right text-[10px] text-text-muted">
            {refreshing ? "Updating market data…" : "Updated"}{" "}
            {!refreshing && lastRefresh.toLocaleTimeString()}
          </div>
        )}

        {/* Main Dashboard Layout */}
        <main className="p-2.5 sm:p-4 md:p-5 space-y-3 md:space-y-4 max-w-[1800px] w-full mx-auto">
          <div className="md:rounded-none md:shadow-none md:border-0 md:bg-transparent md:p-0">
            <div className="rounded-[1.5rem] border border-border/70 bg-[#f6f8fb] shadow-[0_10px_25px_rgba(15,23,42,0.06)] overflow-hidden">
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
            </div>
          </div>

          {/* 2. Top KPI Row — 4 Core Cards (AI Bias, Regime, Signal Status, Setup Quality) */}
          <div className="grid grid-cols-2 gap-2.5 md:grid-cols-4 md:gap-3.5">
            <AIBiasCard
              bias={modelUnavailable ? undefined : signal?.bias}
              confidence={modelUnavailable ? undefined : signal?.confidence}
              loading={loading && !signal}
              modelUnavailable={modelUnavailable}
            />
            <RegimeCard
              regime={modelUnavailable ? undefined : signal?.regime}
            />
            <SignalCard
              direction={signal?.trade?.direction ?? null}
              status={signal?.trade?.status ?? "NO_TRADE"}
              strategyType={(signal?.trade as any)?.strategy_type ?? null}
              loading={loading && !signal}
            />
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
                bias={modelUnavailable ? "UNAVAILABLE" : signal?.bias}
                confidence={modelUnavailable ? undefined : signal?.confidence}
                regime={modelUnavailable ? undefined : signal?.regime}
                bullProbability={modelUnavailable ? undefined : signal?.model?.bull_probability}
                bearProbability={modelUnavailable ? undefined : signal?.model?.bear_probability}
                neutralProbability={modelUnavailable ? undefined : signal?.model?.neutral_probability}
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

            </div>
          </div>

          {/* Analytics and paper-trading row */}
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
                  className="group flex items-center justify-between bg-card border border-border rounded-xl px-4 py-2.5 shadow-card hover:border-primary/40 transition-all text-xs"
                >
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Icon className="w-3.5 h-3.5 text-primary" />
                    </div>
                    <span className="font-semibold text-text-primary">{link.label}</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-text-muted group-hover:text-primary transition-colors" />
                </Link>
              );
            })}
          </div>
        </main>
          </div>
        </div>
      </div>
    </div>
  );
}
