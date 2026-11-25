type Handler = (init: { method: string; body: unknown }) => { status?: number; body?: unknown };

/** Routes `fetch` calls by "METHOD /path" (path after /api/v1, without query) to handlers. */
export function mockApi(routes: Record<string, Handler | object>) {
  const calls: string[] = [];
  global.fetch = jest.fn(async (url: string, init?: RequestInit) => {
    const method = init?.method ?? 'GET';
    const full = String(url).split('/api/v1')[1];
    const path = full.split('?')[0];
    calls.push(`${method} ${full}`);
    const route = routes[`${method} ${path}`];
    if (route === undefined) throw new TypeError(`Network request failed: ${method} ${path}`);
    const body = init?.body ? JSON.parse(String(init.body)) : undefined;
    const result =
      typeof route === 'function' ? (route as Handler)({ method, body }) : { body: route };
    const status = result.status ?? 200;
    return {
      ok: status < 400,
      status,
      json: async () => result.body ?? null,
    } as Response;
  }) as jest.Mock;
  return calls;
}

export const healthy = { status: 'ok', database: 'ok', version: '0.1.0' };

export const nvda = {
  symbol: 'NVDA',
  name: 'NVIDIA Corp',
  last_close: { date: '2026-11-25', close: '149.3000', change: '-6.0800', change_pct: '-3.91' },
};
