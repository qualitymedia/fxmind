"use client";

import { useEffect, useState, useCallback } from "react";
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

export interface DashboardData {
  analysis: AnalysisResponse | null;
  candles: CandleData[];
  performance: PerformanceData | null;
  model: ModelData | null;
  signals: SignalRow[];
  loading: boolean;
  error: string | null;
  lastRefresh: Date | null;
  refetch: () => void;
}

const POLL_INTERVAL_MS = 15_000; // refresh every 15 seconds

export function useDashboardData(timeframe: string = "M15"): DashboardData {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [candles, setCandles] = useState<CandleData[]>([]);
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [model, setModel] = useState<ModelData | null>(null);
  const [signals, setSignals] = useState<SignalRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const fetchAll = useCallback(async () => {
    try {
      const [analysisData, candlesData, perfData, modelData, signalsData] = await Promise.allSettled([
        fetchApi<AnalysisResponse>("/api/v1/analysis/GBPUSD"),
        fetchApi<CandleData[]>(`/api/v1/market/GBPUSD/candles?timeframe=${timeframe}&limit=200`),
        fetchApi<PerformanceData>("/api/v1/performance"),
        fetchApi<ModelData>("/api/v1/models/current"),
        fetchApi<SignalRow[]>("/api/v1/signals?limit=10"),
      ]);

      if (analysisData.status === "fulfilled") setAnalysis(analysisData.value);
      if (candlesData.status === "fulfilled") setCandles(candlesData.value);
      if (perfData.status === "fulfilled") setPerformance(perfData.value);
      if (modelData.status === "fulfilled") setModel(modelData.value);
      if (signalsData.status === "fulfilled") setSignals(signalsData.value);

      // Surface first error encountered
      const firstError = [analysisData, candlesData, perfData, modelData].find(
        (r) => r.status === "rejected"
      ) as PromiseRejectedResult | undefined;

      setError(firstError ? (firstError.reason as Error).message : null);
      setLastRefresh(new Date());
    } catch (err: any) {
      setError(err.message ?? "Failed to fetch dashboard data");
    } finally {
      setLoading(false);
    }
  }, [timeframe]);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [fetchAll]);

  return { analysis, candles, performance, model, signals, loading, error, lastRefresh, refetch: fetchAll };
}
