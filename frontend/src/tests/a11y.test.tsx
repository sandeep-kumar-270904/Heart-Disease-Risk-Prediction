import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { axe } from 'vitest-axe';
import { AppRoutes } from '@/App';
import { useAuthStore } from '@/stores/authStore';

const ALL_ROUTES = [
  '/login',
  '/register',
  '/dashboard',
  '/intake',
  '/directory',
  '/doctor',
  '/admin',
] as const;

describe('Milestone 19: Whole-Application WCAG 2.2 AA Route Accessibility Audit', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response(JSON.stringify([]), { status: 200 }))
    );
  });

  it.each(ALL_ROUTES)('route %s passes automated axe-core WCAG audit with zero violations', async (route) => {
    if (route === '/login' || route === '/register') {
      useAuthStore.getState().clearSession();
    } else {
      useAuthStore.getState().setSession('mock-jwt', {
        id: 'usr-a11y',
        email: 'a11y.demo@example.com',
        full_name: 'A11y Audit User',
        role: route === '/admin' ? 'ADMINISTRATOR' : route === '/doctor' ? 'CLINICIAN' : 'PATIENT',
        country_code: 'US',
        clinician_status: null,
        created_at: new Date().toISOString(),
      });
    }

    const { container } = render(
      <MemoryRouter initialEntries={[route]}>
        <AppRoutes />
      </MemoryRouter>
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
