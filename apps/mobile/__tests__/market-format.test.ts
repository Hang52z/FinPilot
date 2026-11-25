import { linePath, rangeChangePct } from '@/features/market/chart';
import { errorKey, formatChangePct, formatMarketDate, formatPrice } from '@/features/market/format';
import { ApiError } from '@/services/api';

describe('formatChangePct', () => {
  it('shows direction with an arrow and a sign', () => {
    expect(formatChangePct(1.234)).toBe('▲ +1.23%');
    expect(formatChangePct(-3.91)).toBe('▼ −3.91%');
    expect(formatChangePct(0)).toBe('0.00%');
  });
});

describe('formatMarketDate', () => {
  it('keeps the market date regardless of time zone', () => {
    expect(formatMarketDate('2026-11-25', 'en')).toBe('Nov 25, 2026');
  });
});

describe('formatPrice', () => {
  it('formats in the given currency and locale', () => {
    expect(formatPrice('149.3000', 'USD', 'en')).toBe('$149.30');
  });
});

describe('errorKey', () => {
  it('maps backend codes to messages', () => {
    expect(errorKey(new ApiError(404, 'symbol_not_found'))).toBe('errors.symbolNotFound');
    expect(errorKey(new ApiError(503, 'provider_quota_exceeded'))).toBe('errors.quotaExceeded');
    expect(errorKey(new ApiError(0, 'network'))).toBe('errors.serverUnreachable');
    expect(errorKey(new ApiError(500, 'something_new'))).toBe('errors.generic');
    expect(errorKey(new Error('x'))).toBe('errors.generic');
  });
});

describe('linePath', () => {
  const box = { width: 100, height: 50, padding: 5 };

  it('scales values to fill the box, highest value at the top', () => {
    expect(linePath([1, 3, 2], box)).toBe('M0.0,45.0 L50.0,5.0 L100.0,25.0');
  });

  it('draws nothing for fewer than two points or no width', () => {
    expect(linePath([1], box)).toBe('');
    expect(linePath([1, 2], { ...box, width: 0 })).toBe('');
  });

  it('reduces long series to about one point per pixel and keeps the last value', () => {
    const values = Array.from({ length: 1001 }, (_, i) => i);
    const path = linePath(values, box);
    const points = path.split(' ');
    expect(points.length).toBeLessThanOrEqual(102);
    expect(points.at(-1)).toBe('L100.0,5.0');
  });

  it('handles a flat series', () => {
    expect(linePath([2, 2], box)).toBe('M0.0,45.0 L100.0,45.0');
  });
});

describe('rangeChangePct', () => {
  it('compares the last value with the first', () => {
    expect(rangeChangePct([100, 90, 110])).toBeCloseTo(10);
    expect(rangeChangePct([100])).toBeNull();
  });
});
