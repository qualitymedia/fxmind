"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { fetchApi } from "@/lib/api";
import type { AnalysisResponse } from "@/types/signal";

export interface PerformanceData {
  accuracy: number;
  profit_factor: number;
  expectancy: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  win_rate: number;
  trade_count: number;
  average_win: number;
  average_loss: number;
  equity_curve: { index: number; equity: number }[];
}

export interface SignalRow {
  id: number;
  timestamp: string;
  bias: string;
  regime: string;
  status: string;
  direction: string | null;
  strategy_type?: string | null;
  confidence: number;
  entry_low?: number | null;
  entry_high?: number | null;
  stop_loss?: number | null;
  take_profit?: number | null;
}

export interface ModelData {
  version: string;
  model_type: string;
  state: string;
  feature_count: number;
  calibration_method: string;
  training_samples: number;
  validation_samples: number;
  accuracy: number;
  profit_factor: number;
  last_validation: string;
}

export interface CandleData {
  symbol: string;
  timeframe: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  tick_volume: number;
}

export interface VolumeProfileBin {
  price: number;
  volume: number;
  percentage: number;
  is_poc: boolean;
  is_value_area: boolean;
}

export interface VolumeProfileData {
  poc: number;
  vah: number;
  val: number;
  total_volume: number;
  value_area_volume: number;
  price_position: "ABOVE_VAH" | "INSIDE_VA" | "BELOW_VAL" | string;
  dist_to_poc_pips: number;
  bins: VolumeProfileBin[];
  symbol?: string;
}

export interface PaperPosition {
  id?: number;
  position_id?: string;
  signal_id?: number;
  symbol: string;
  direction: "BUY" | "SELL" | "LONG" | "SHORT" | string;
  entry_price: number;
  current_price: number;
  stop_loss: number;
  take_profit: number;
  size?: number;
  pnl_pips?: number;
  unrealized_pnl_pips?: number;
  pnl_usd?: number;
  realized_pnl?: number;
  status: "OPEN" | "CLOSED" | "TARGET_HIT" | "STOP_HIT" | "EXPIRED" | string;
  strategy_type?: string;
  opened_at: string;
  closed_at?: string;
  close_reason?: string;
  trade_mode?: string;
  is_scrap_trade?: boolean;
}

export interface PaperSummaryData {
  total_trades: number;
  open_trades: number;
  win_rate: number;
  profit_factor: number;
  total_pnl_pips: number;
  current_equity: number;
  closed_positions: PaperPosition[];
}

export interface TradeHistoryEntry {
  position_id: string;
  signal_id: number;
  symbol: string;
  direction: string;
  strategy_type: string | null;
  entry_price: number;
  stop_loss: number | null;
  take_profit: number | null;
  risk_reward: number | null;
  opened_at: string | null;
  closed_at: string | null;
  status: string; // TARGET_HIT | STOP_HIT | EXPIRED
  pnl_pips: number;
  realized_pnl: number;
  model_confidence: number;
  regime: string | null;
  session: string | null;
  trade_mode?: string;
  is_scrap_trade?: boolean;
}

export interface DashboardData {
  analysis: AnalysisResponse | null;
  candles: CandleData[];
  performance: PerformanceData | null;
  model: ModelData | null;
  signals: SignalRow[];
  volumeProfile: VolumeProfileData | null;
  paperSummary: PaperSummaryData | null;
  paperPositions: PaperPosition[];
  tradeHistory: TradeHistoryEntry[];
  loading: boolean;
  refreshing: boolean;
  error: string | null;
  lastRefresh: Date | null;
  refetch: () => void;
}

type DashboardSnapshot = Omit<
  DashboardData,
  "loading" | "refreshing" | "error" | "lastRefresh" | "refetch"
>;

interface DashboardCacheEntry {
  snapshot: DashboardSnapshot;
  lastRefresh: string;
}

const POLL_INTERVAL_MS = 30_000;
const CACHE_FRESH_MS = 30_000;
const dashboardCache = new Map<string, DashboardCacheEntry>();

const emptySnapshot = (): DashboardSnapshot => ({
  analysis: null,
  candles: [],
  performance: null,
  model: null,
  signals: [],
  volumeProfile: null,
  paperSummary: null,
  paperPositions: [],
  tradeHistory: [],
});

function isUnavailableAnalysis(analysis: AnalysisResponse | null): boolean {
  return Boolean(
    analysis?.signal?.reasons?.some((reason) =>
      reason.reason?.toLowerCase().includes("ai analysis model is unavailable")
    )
  );
}

function readCache(timeframe: string): {
  snapshot: DashboardSnapshot;
  lastRefresh: Date | null;
} {
  const key = `fxmind:dashboard:v1:${timeframe}`;
  let entry = dashboardCache.get(key);

  if (!entry && typeof window !== "undefined") {
    try {
      const stored = window.sessionStorage.getItem(key);
      if (stored) {
        const parsed = JSON.parse(stored) as DashboardCacheEntry;
        if (
          parsed.lastRefresh &&
          Number.isFinite(new Date(parsed.lastRefresh).getTime()) &&
          parsed.snapshot
        ) {
          entry = parsed;
          dashboardCache.set(key, entry);
        }
      }
    } catch {
      try {
        window.sessionStorage.removeItem(key);
      } catch {
        return { snapshot: emptySnapshot(), lastRefresh: null };
      }
    }
  }

  if (!entry) {
    return { snapshot: emptySnapshot(), lastRefresh: null };
  }

  return {
    snapshot: {
      ...emptySnapshot(),
      ...entry.snapshot,
      analysis: isUnavailableAnalysis(entry.snapshot.analysis)
        ? null
        : entry.snapshot.analysis,
    },
    lastRefresh: new Date(entry.lastRefresh),
  };
}

function writeCache(
  timeframe: string,
  snapshot: DashboardSnapshot,
  lastRefresh: Date
): void {
  const key = `fxmind:dashboard:v1:${timeframe}`;
  const entry = { snapshot, lastRefresh: lastRefresh.toISOString() };
  dashboardCache.set(key, entry);
  try {
    window.sessionStorage.setItem(key, JSON.stringify(entry));
  } catch {
    // Storage may be unavailable or full; in-memory caching still works.
  }
}

export function useDashboardData(timeframe: string = "M15"): DashboardData {
  const [snapshot, setSnapshot] = useState(emptySnapshot);
  const snapshotRef = useRef(snapshot);
  const [snapshotTimeframe, setSnapshotTimeframe] = useState<string | null>(null);
  const lastRefreshRef = useRef<Date | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const fetchAll = useCallback(async (force = false) => {
    const previousRefresh = lastRefreshRef.current;
    if (
      !force &&
      previousRefresh &&
      Date.now() - previousRefresh.getTime() < CACHE_FRESH_MS
    ) {
      setLoading(false);
      return;
    }

    setRefreshing(true);
    try {
      const updateOnSuccess = <T,>(
        request: Promise<T>,
        update: (current: DashboardSnapshot, value: T) => DashboardSnapshot
      ) =>
        request.then((value) => {
          const nextSnapshot = update(snapshotRef.current, value);
          snapshotRef.current = nextSnapshot;
          setSnapshot(nextSnapshot);
          return value;
        });

      const [
        analysisData,
        candlesData,
        perfData,
        modelData,
        signalsData,
        vpData,
        paperSumData,
        paperPosData,
        tradeHistoryData,
      ] = await Promise.allSettled([
        updateOnSuccess(
          fetchApi<AnalysisResponse>("/api/v1/analysis/GBPUSD"),
          (current, value) =>
            isUnavailableAnalysis(value) && current.analysis
              ? current
              : { ...current, analysis: value }
        ),
        updateOnSuccess(
          fetchApi<CandleData[]>(`/api/v1/market/GBPUSD/candles?timeframe=${timeframe}&limit=200`),
          (current, value) => ({ ...current, candles: value })
        ),
        updateOnSuccess(
          fetchApi<PerformanceData>("/api/v1/performance"),
          (current, value) => ({ ...current, performance: value })
        ),
        updateOnSuccess(
          fetchApi<ModelData>("/api/v1/models/current"),
          (current, value) => ({ ...current, model: value })
        ),
        updateOnSuccess(
          fetchApi<SignalRow[]>("/api/v1/signals?limit=10"),
          (current, value) => ({ ...current, signals: value })
        ),
        updateOnSuccess(
          fetchApi<VolumeProfileData>("/api/v1/market/GBPUSD/volume-profile"),
          (current, value) => ({ ...current, volumeProfile: value })
        ),
        updateOnSuccess(
          fetchApi<PaperSummaryData>("/api/v1/paper-trading/summary"),
          (current, value) => ({ ...current, paperSummary: value })
        ),
        updateOnSuccess(
          fetchApi<PaperPosition[]>("/api/v1/paper-trading/positions"),
          (current, value) => ({ ...current, paperPositions: value })
        ),
        updateOnSuccess(
          fetchApi<TradeHistoryEntry[]>("/api/v1/paper-trading/history?limit=30"),
          (current, value) => ({ ...current, tradeHistory: value })
        ),
      ]);

      // Surface first error encountered
      const firstError = [analysisData, candlesData, perfData, modelData].find(
        (r) => r.status === "rejected"
      ) as PromiseRejectedResult | undefined;

      setError(
        firstError
          ? firstError.reason instanceof Error
            ? firstError.reason.message
            : String(firstError.reason)
          : null
      );
      const refreshedAt = new Date();
      lastRefreshRef.current = refreshedAt;
      setLastRefresh(refreshedAt);
      writeCache(timeframe, snapshotRef.current, refreshedAt);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch dashboard data");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [timeframe]);

  useEffect(() => {
    const cached = readCache(timeframe);
    snapshotRef.current = cached.snapshot;
    setSnapshotTimeframe(timeframe);
    lastRefreshRef.current = cached.lastRefresh;
    setSnapshot(cached.snapshot);
    setLastRefresh(cached.lastRefresh);
    setLoading(cached.lastRefresh === null);
  }, [timeframe]);

  useEffect(() => {
    void fetchAll();
    const id = setInterval(fetchAll, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [fetchAll]);

  return {
    ...(snapshotTimeframe === timeframe ? snapshot : emptySnapshot()),
    loading,
    refreshing,
    error,
    lastRefresh,
    refetch: () => fetchAll(true),
  };
}
