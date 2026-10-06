export interface Candle {
  symbol: string;
  timeframe: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  tick_volume: number;
}

export interface MarketOverview {
  symbol: string;
  current_price: number;
  bid: number;
  ask: number;
  spread: number;
  change: number;
  change_percent: number;
  high_24h: number;
  low_24h: number;
  session: string;
  is_live: boolean;
  last_updated: string;
  timeframe: string;
}

export interface CrossMarketItem {
  symbol: string;
  current_value: number;
  change_percent: number;
  bias?: string;
  correlation_note?: string;
}
