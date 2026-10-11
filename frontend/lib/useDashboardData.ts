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
  const [volumeProfile, setVolumeProfile] = useState<VolumeProfileData | null>(null);
  const [paperSummary, setPaperSummary] = useState<PaperSummaryData | null>(null);
  const [paperPositions, setPaperPositions] = useState<PaperPosition[]>([]);
  const [tradeHistory, setTradeHistory] = useState<TradeHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const fetchAll = useCallback(async () => {
    try {
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
        fetchApi<AnalysisResponse>("/api/v1/analysis/GBPUSD"),
        fetchApi<CandleData[]>(`/api/v1/market/GBPUSD/candles?timeframe=${timeframe}&limit=200`),
        fetchApi<PerformanceData>("/api/v1/performance"),
        fetchApi<ModelData>("/api/v1/models/current"),
        fetchApi<SignalRow[]>("/api/v1/signals?limit=10"),
        fetchApi<VolumeProfileData>("/api/v1/market/GBPUSD/volume-profile"),
        fetchApi<PaperSummaryData>("/api/v1/paper-trading/summary"),
        fetchApi<PaperPosition[]>("/api/v1/paper-trading/positions"),
        fetchApi<TradeHistoryEntry[]>("/api/v1/paper-trading/history?limit=30"),
      ]);

      if (analysisData.status === "fulfilled") setAnalysis(analysisData.value);
      if (candlesData.status === "fulfilled") setCandles(candlesData.value);
      if (perfData.status === "fulfilled") setPerformance(perfData.value);
      if (modelData.status === "fulfilled") setModel(modelData.value);
      if (signalsData.status === "fulfilled") setSignals(signalsData.value);
      if (vpData.status === "fulfilled") setVolumeProfile(vpData.value);
      if (paperSumData.status === "fulfilled") setPaperSummary(paperSumData.value);
      if (paperPosData.status === "fulfilled") setPaperPositions(paperPosData.value);
      if (tradeHistoryData.status === "fulfilled") setTradeHistory(tradeHistoryData.value);

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

  return {
    analysis,
    candles,
    performance,
    model,
    signals,
    volumeProfile,
    paperSummary,
    paperPositions,
    tradeHistory,
    loading,
    error,
    lastRefresh,
    refetch: fetchAll,
  };
}

