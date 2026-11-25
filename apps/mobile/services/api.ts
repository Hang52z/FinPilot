const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly body: unknown,
  ) {
    super(`API request failed with status ${status}`);
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}/api/v1${path}`, {
    headers: { Accept: 'application/json' },
  });
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, body);
  return body as T;
}

export type Health = {
  status: 'ok' | 'degraded';
  database: 'ok' | 'unavailable';
  version: string;
};

export const getHealth = () => apiGet<Health>('/health');
