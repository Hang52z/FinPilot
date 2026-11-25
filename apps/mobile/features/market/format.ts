import type { TranslationKey } from '@/i18n';
import { ApiError } from '@/services/api';

const SOURCES: Record<string, string> = { tiingo: 'Tiingo' };

export const sourceName = (source: string) => SOURCES[source] ?? source;

export function formatPrice(value: string, currency: string, locale: string): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));
}

/** Direction is shown by arrow and sign, never by color alone. */
export function formatChangePct(pct: number): string {
  if (pct === 0) return '0.00%';
  const arrow = pct > 0 ? '▲' : '▼';
  const sign = pct > 0 ? '+' : '−';
  return `${arrow} ${sign}${Math.abs(pct).toFixed(2)}%`;
}

/** Market dates (YYYY-MM-DD) are calendar dates, so format them in UTC to avoid day shifts. */
export function formatMarketDate(date: string, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${date}T00:00:00Z`));
}

const ERROR_KEYS: Record<string, TranslationKey> = {
  symbol_not_found: 'errors.symbolNotFound',
  invalid_symbol: 'errors.symbolNotFound',
  provider_quota_exceeded: 'errors.quotaExceeded',
  provider_unavailable: 'errors.dataUnavailable',
  provider_not_configured: 'errors.dataUnavailable',
  network: 'errors.serverUnreachable',
};

export function errorKey(error: unknown): TranslationKey {
  const code = error instanceof ApiError ? error.code : 'unknown';
  return ERROR_KEYS[code] ?? 'errors.generic';
}
