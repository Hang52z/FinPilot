import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

import {
  addToWatchlist,
  getHistory,
  getStock,
  getWatchlist,
  removeFromWatchlist,
  searchSecurities,
  type Range,
} from '@/services/market';

const WATCHLIST = ['watchlist'] as const;

/** Prices are daily closes: they change at most once a day, so cache them for a while. */
const DAILY = 5 * 60 * 1000;

export function useDebounced<T>(value: T, delayMs = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(id);
  }, [value, delayMs]);
  return debounced;
}

export function useSearch(query: string) {
  const q = useDebounced(query.trim());
  return useQuery({
    queryKey: ['search', q.toLowerCase()],
    queryFn: () => searchSecurities(q),
    enabled: q.length > 0,
    staleTime: Infinity,
    select: (data) => data.results,
  });
}

export function useStock(symbol: string) {
  return useQuery({
    queryKey: ['stock', symbol],
    queryFn: () => getStock(symbol),
    staleTime: DAILY,
  });
}

export function useHistory(symbol: string, range: Range) {
  return useQuery({
    queryKey: ['history', symbol, range],
    queryFn: () => getHistory(symbol, range),
    staleTime: DAILY,
    placeholderData: (previous) => previous,
  });
}

export function useWatchlist() {
  return useQuery({ queryKey: WATCHLIST, queryFn: getWatchlist, staleTime: DAILY });
}

export function useWatchlistToggle(symbol: string) {
  const client = useQueryClient();
  const watchlist = useWatchlist();
  const watched = watchlist.data?.items.some((i) => i.symbol === symbol) ?? false;
  const mutation = useMutation({
    mutationFn: () => (watched ? removeFromWatchlist(symbol) : addToWatchlist(symbol)),
    onSettled: () => client.invalidateQueries({ queryKey: WATCHLIST }),
  });
  return { watched, ready: watchlist.isSuccess, toggle: mutation.mutate, mutation };
}
