import { apiDelete, apiGet, apiPost } from './api';

/** Decimal values arrive as strings to keep precision; convert only for display and charts. */
export type LastClose = {
  date: string;
  close: string;
  change: string | null;
  change_pct: string | null;
};

export type SearchResult = { symbol: string; name: string; asset_type: 'stock' | 'etf' | null };

export type Stock = {
  symbol: string;
  name: string;
  exchange: string | null;
  description: string | null;
  currency: string;
  last_close: LastClose | null;
  source: string;
  fetched_at: string | null;
};

export const RANGES = ['1M', '3M', '6M', '1Y', '5Y'] as const;
export type Range = (typeof RANGES)[number];

export type Bar = {
  date: string;
  open: string;
  high: string;
  low: string;
  close: string;
  adj_close: string;
  volume: number;
};

export type History = {
  symbol: string;
  range: Range | 'MAX';
  bars: Bar[];
  source: string;
  as_of: string | null;
  fetched_at: string | null;
};

export type WatchlistItem = { symbol: string; name: string; last_close: LastClose | null };
export type Watchlist = { items: WatchlistItem[]; source: string; fetched_at: string | null };

const path = (symbol: string) => encodeURIComponent(symbol);

export const searchSecurities = (q: string) =>
  apiGet<{ results: SearchResult[] }>(`/market/search?q=${encodeURIComponent(q)}`);
export const getStock = (symbol: string) => apiGet<Stock>(`/market/stocks/${path(symbol)}`);
export const getHistory = (symbol: string, range: Range) =>
  apiGet<History>(`/market/stocks/${path(symbol)}/history?range=${range}`);
export const getWatchlist = () => apiGet<Watchlist>('/watchlist');
export const addToWatchlist = (symbol: string) => apiPost<WatchlistItem>('/watchlist', { symbol });
export const removeFromWatchlist = (symbol: string) => apiDelete(`/watchlist/${path(symbol)}`);
