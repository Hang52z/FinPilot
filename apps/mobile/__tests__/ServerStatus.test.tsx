import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, userEvent, waitFor } from '@testing-library/react-native';

import { ServerStatus } from '@/components/ServerStatus';
import '@/i18n';

async function renderWithClient() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity } },
  });
  await render(
    <QueryClientProvider client={client}>
      <ServerStatus />
    </QueryClientProvider>,
  );
}

function mockFetch(...responses: (Partial<Response> | Error)[]) {
  const fn = jest.fn();
  for (const r of responses) {
    if (r instanceof Error) fn.mockRejectedValueOnce(r);
    else fn.mockResolvedValueOnce(r);
  }
  global.fetch = fn;
  return fn;
}

const healthy = {
  ok: true,
  status: 200,
  json: async () => ({ status: 'ok', database: 'ok', version: '0.1.0' }),
};

describe('ServerStatus', () => {
  it('renders nothing when the server is healthy', async () => {
    const fetch = mockFetch(healthy);
    await renderWithClient();

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    expect(screen.queryByRole('alert')).not.toBeOnTheScreen();
  });

  it('shows an error with retry when the server is unreachable', async () => {
    const fetch = mockFetch(new TypeError('Network request failed'), healthy);
    await renderWithClient();

    expect(await screen.findByText("Can't reach server")).toBeOnTheScreen();

    await userEvent.setup().press(screen.getByRole('button', { name: 'Retry' }));

    await waitFor(() => expect(screen.queryByText("Can't reach server")).not.toBeOnTheScreen());
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it('shows an error when the database is unavailable', async () => {
    mockFetch({
      ok: false,
      status: 503,
      json: async () => ({ status: 'degraded', database: 'unavailable', version: '0.1.0' }),
    });
    await renderWithClient();

    expect(await screen.findByText("Can't reach server")).toBeOnTheScreen();
  });
});
