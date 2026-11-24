import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { axe } from 'vitest-axe';
import { AppRoutes } from '@/App';
import { apiFetch, ApiClientError } from '@/services/apiClient';
import { useAuthStore } from '@/stores/authStore';

describe('Milestone 07: Frontend Core Shell, Routing & Silent Auth Refresh', () => {
  beforeEach(() => {
    useAuthStore.getState().clearSession();
    vi.restoreAllMocks();
  });

  it('redirects unauthenticated users from protected /dashboard to /login and passes axe', async () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AppRoutes />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /Sign In to HeartXAI 2.0/i })).toBeInTheDocument();
    expect(screen.getByText(/SYNTHETIC DATA ONLY/i)).toBeInTheDocument();
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('renders authenticated shell navigation, skip link, and emergency banner cleanly', async () => {
    useAuthStore.getState().setSession('mock-jwt', {
      id: 'usr-1',
      email: 'patient.demo@example.com',
      full_name: 'Synthetic Patient Alpha',
      role: 'PATIENT',
      country_code: 'US',
      clinician_status: null,
      created_at: new Date().toISOString(),
    });

    const { container } = render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AppRoutes />
      </MemoryRouter>
    );

    expect(
      screen.getByRole('heading', { name: /Cardiovascular Health Workspace/i })
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Skip to main content/i })).toBeInTheDocument();
    expect(screen.getByText(/Medical Emergency\? Call Local EMS/i)).toBeInTheDocument();

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('silently refreshes access JWT once on 401 and retries original API request', async () => {
    useAuthStore.getState().setSession('expired-jwt');
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: 'Expired token' }), { status: 401 })
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ access_token: 'fresh-jwt', token_type: 'bearer', expires_in: 900 }),
          { status: 200 }
        )
      )
      .mockResolvedValueOnce(new Response(JSON.stringify({ ok: true }), { status: 200 }));

    vi.stubGlobal('fetch', fetchMock);

    const data = await apiFetch<{ ok: boolean }>('/assessments');
    expect(data.ok).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(useAuthStore.getState().accessToken).toBe('fresh-jwt');
  });

  it('breaks infinite refresh loop and clears session if silent refresh fails', async () => {
    useAuthStore.getState().setSession('expired-jwt');
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Expired' }), { status: 401 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: 'Refresh revoked' }), { status: 401 })
      );

    vi.stubGlobal('fetch', fetchMock);

    await expect(apiFetch('/assessments')).rejects.toBeInstanceOf(ApiClientError);
    await waitFor(() => {
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
      expect(useAuthStore.getState().accessToken).toBeNull();
    });
  });
});
