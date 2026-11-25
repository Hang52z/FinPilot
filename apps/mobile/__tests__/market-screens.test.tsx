import { userEvent } from '@testing-library/react-native';
import { renderRouter, screen, waitFor } from 'expo-router/testing-library';

import i18n from '@/i18n';
import { healthy, mockApi, nvda } from '@/test-utils/mockApi';

const stock = {
  ...nvda,
  exchange: 'NASDAQ',
  description: null,
  currency: 'USD',
  source: 'tiingo',
  fetched_at: '2026-11-25T23:32:49Z',
};
const history = {
  symbol: 'NVDA',
  range: '1Y',
  source: 'tiingo',
  as_of: '2026-11-25',
  fetched_at: '2026-11-25T23:32:49Z',
  bars: [
    {
      date: '2026-11-24',
      open: '1',
      high: '1',
      low: '1',
      close: '155.38',
      adj_close: '155.38',
      volume: 1,
    },
    {
      date: '2026-11-25',
      open: '1',
      high: '1',
      low: '1',
      close: '149.30',
      adj_close: '149.30',
      volume: 1,
    },
  ],
};

beforeEach(async () => {
  await i18n.changeLanguage('en');
});

it('shows watchlist rows with price, signed change and data source', async () => {
  mockApi({
    'GET /health': healthy,
    'GET /watchlist': { items: [nvda], source: 'tiingo', fetched_at: null },
  });
  await renderRouter('./app');

  expect(await screen.findByText('NVDA')).toBeOnTheScreen();
  expect(screen.getByText('$149.30')).toBeOnTheScreen();
  expect(screen.getByText('▼ −3.91%')).toBeOnTheScreen();
  expect(screen.getByText('Daily close · Nov 25, 2026 · Tiingo')).toBeOnTheScreen();
});

it('offers search when the watchlist is empty', async () => {
  mockApi({
    'GET /health': healthy,
    'GET /watchlist': { items: [], source: 'tiingo', fetched_at: null },
  });
  await renderRouter('./app');

  await userEvent.setup().press(await screen.findByRole('button', { name: 'Search' }));

  expect(await screen.findByLabelText('Search')).toBeOnTheScreen();
});

it('shows a translated error when market data is unavailable', async () => {
  mockApi({
    'GET /health': healthy,
    'GET /watchlist': () => ({ status: 503, body: { error: 'provider_quota_exceeded' } }),
  });
  await renderRouter('./app');

  // The app retries once before showing the error.
  expect(
    await screen.findByText('Data limit reached. Try again later.', {}, { timeout: 5000 }),
  ).toBeOnTheScreen();
});

it('searches after typing and opens the result', async () => {
  const calls = mockApi({
    'GET /health': healthy,
    'GET /watchlist': { items: [], source: 'tiingo', fetched_at: null },
    'GET /market/search': {
      results: [
        { symbol: 'NVDA', name: 'NVIDIA Corp', asset_type: 'stock' },
        { symbol: 'NVDX', name: 'T-REX 2X LONG NVIDIA', asset_type: 'etf' },
      ],
    },
    'GET /market/stocks/NVDA': stock,
    'GET /market/stocks/NVDA/history': history,
  });
  await renderRouter('./app', { initialUrl: '/research' });
  const user = userEvent.setup();

  await user.type(screen.getByLabelText('Search'), 'nvidia');

  expect(await screen.findByText('NVIDIA Corp')).toBeOnTheScreen();
  expect(screen.getByText('ETF')).toBeOnTheScreen();
  expect(calls.filter((c) => c.startsWith('GET /market/search'))).toEqual([
    'GET /market/search?q=nvidia',
  ]);

  await user.press(screen.getByText('NVIDIA Corp'));
  expect(await screen.findByText('$149.30')).toBeOnTheScreen();
});

it('shows stock detail and toggles the watchlist', async () => {
  let watched = false;
  const calls = mockApi({
    'GET /health': healthy,
    'GET /watchlist': () => ({
      body: { items: watched ? [nvda] : [], source: 'tiingo', fetched_at: null },
    }),
    'POST /watchlist': ({ body }) => {
      watched = (body as { symbol: string }).symbol === 'NVDA';
      return { status: 201, body: nvda };
    },
    'GET /market/stocks/NVDA': stock,
    'GET /market/stocks/NVDA/history': history,
  });
  await renderRouter('./app', { initialUrl: '/stock/NVDA' });

  expect(await screen.findByText('$149.30')).toBeOnTheScreen();
  expect(screen.getByText('Daily close · Nov 25, 2026 · Tiingo')).toBeOnTheScreen();
  expect(screen.getByRole('image', { name: /NVDA 1Y ▼ −3\.91%/ })).toBeOnTheScreen();

  const user = userEvent.setup();
  await user.press(await screen.findByRole('button', { name: 'Add to watchlist' }));

  expect(await screen.findByRole('button', { name: 'Remove from watchlist' })).toBeOnTheScreen();
  expect(calls).toContain('POST /watchlist');

  await user.press(screen.getByRole('tab', { name: '5Y' }));
  await waitFor(() => expect(calls).toContain('GET /market/stocks/NVDA/history?range=5Y'));
});

it('shows symbol not found', async () => {
  mockApi({
    'GET /health': healthy,
    'GET /watchlist': { items: [], source: 'tiingo', fetched_at: null },
    'GET /market/stocks/ZZZZ': () => ({ status: 404, body: { error: 'symbol_not_found' } }),
    'GET /market/stocks/ZZZZ/history': () => ({ status: 404, body: { error: 'symbol_not_found' } }),
  });
  await renderRouter('./app', { initialUrl: '/stock/ZZZZ' });

  expect(await screen.findByText('Symbol not found', {}, { timeout: 5000 })).toBeOnTheScreen();
});
