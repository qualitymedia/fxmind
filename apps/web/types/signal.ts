export interface TradeSetup {
  status: 'ACTIVE' | 'NO_TRADE' | 'TARGET_HIT' | 'STOP_HIT' | 'EXPIRED' | 'INVALIDATED';
  direction: 'LONG' | 'SHORT' | null;
  entry_low: number | null;
  entry_high: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  risk_reward: number | null;
}

export interface ModelProbabilities {
  bull_probability: number;
  bear_probability: number;
  neutral_probability: number;
}

export interface SignalReason {
  category: string;
  reason: string;
  value?: string;
  sentiment?: 'SUPPORTIVE' | 'NEUTRAL' | 'OPPOSING' | 'CLEAR';
}

export interface Signal {
  id: number;
  symbol: string;
  timestamp: string;
  timeframe: string;
  bias: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidence: number;
  regime: 'TRENDING' | 'RANGING' | 'HIGH_VOLATILITY' | 'ILLIQUID';
  trade: TradeSetup;
  model: ModelProbabilities;
  market: {
    atr14?: number;
    spread?: number;
    session?: string;
  };
  filters: {
    news_clear: boolean;
    liquidity_ok: boolean;
    spread_ok: boolean;
  };
  reasons: SignalReason[];
  patterns?: Array<{
    name: string;
    type: string;
    bias: string;
    icon: string;
  }>;
  model_version: string;
  outcome?: string;
}

export interface AnalysisResponse {
  signal: Signal;
  market: any;
  cross_market: CrossMarketItem[];
  h1_context?: any;
  upcoming_events?: any[];
  data_freshness: string;
  last_updated: string;
}
