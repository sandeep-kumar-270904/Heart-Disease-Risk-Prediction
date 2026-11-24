import { useAuthStore } from '@/stores/authStore';
import type { TokenResponse } from '@/types';

const API_BASE_URL =
  (import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_BASE_URL ??
  '/api/v1';

let refreshPromise: Promise<string | null> | null = null;

export class ApiClientError extends Error {
  public readonly status: number;
  public readonly payload: unknown;

  constructor(status: number, message: string, payload?: unknown) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.payload = payload;
  }
}

async function attemptSilentRefresh(): Promise<string | null> {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        useAuthStore.getState().clearSession();
        return null;
      }
      const data = (await response.json()) as TokenResponse;
      useAuthStore.getState().setSession(data.access_token);
      return data.access_token;
    } catch {
      useAuthStore.getState().clearSession();
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  _retried = false
): Promise<T> {
  const { accessToken, countryCode } = useAuthStore.getState();
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type') && options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  headers.set('X-HeartXAI-Country', countryCode);
  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers,
  });

  if (response.status === 401 && !_retried && !path.startsWith('/auth/refresh')) {
    const newToken = await attemptSilentRefresh();
    if (newToken) {
      return apiFetch<T>(path, options, true);
    }
  }

  if (!response.ok) {
    let errorBody: unknown = null;
    let message = `Request failed with status ${response.status}`;
    try {
      errorBody = await response.json();
      if (
        typeof errorBody === 'object' &&
        errorBody !== null &&
        'detail' in errorBody &&
        typeof (errorBody as { detail: unknown }).detail === 'string'
      ) {
        message = (errorBody as { detail: string }).detail;
      }
    } catch {
      // Non-JSON error body
    }
    throw new ApiClientError(response.status, message, errorBody);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
