const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

/** A failed request. `code` is the backend's machine code (`{"error": "<code>"}`), or `network`. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
  ) {
    super(`API request failed: ${status} ${code}`);
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}/api/v1${path}`, {
      method,
      headers: {
        Accept: 'application/json',
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, 'network');
  }
  const data: unknown = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const code =
      data && typeof data === 'object' && 'error' in data ? String(data.error) : 'unknown';
    throw new ApiError(response.status, code);
  }
  return data as T;
}

export const apiGet = <T>(path: string) => request<T>('GET', path);
export const apiPost = <T>(path: string, body: unknown) => request<T>('POST', path, body);
export const apiDelete = (path: string) => request<null>('DELETE', path);

export type Health = {
  status: 'ok' | 'degraded';
  database: 'ok' | 'unavailable';
  version: string;
};

export const getHealth = () => apiGet<Health>('/health');
