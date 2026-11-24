import { create } from 'zustand';
import type { UserProfileResponse } from '@/types';

export interface AuthState {
  readonly accessToken: string | null;
  readonly user: UserProfileResponse | null;
  readonly isAuthenticated: boolean;
  readonly countryCode: 'US' | 'IN' | 'GB';
  setSession: (accessToken: string, user?: UserProfileResponse | null) => void;
  setUser: (user: UserProfileResponse | null) => void;
  setCountryCode: (countryCode: 'US' | 'IN' | 'GB') => void;
  clearSession: () => void;
}

/**
 * In-memory authentication store (ADR-004).
 * Access JWT is kept strictly in JS memory (never localStorage) to prevent XSS theft.
 */
export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  isAuthenticated: false,
  countryCode: 'US',
  setSession: (accessToken, user) =>
    set((state) => ({
      accessToken,
      user: user !== undefined ? user : state.user,
      isAuthenticated: true,
    })),
  setUser: (user) =>
    set(() => ({
      user,
      isAuthenticated: user !== null,
    })),
  setCountryCode: (countryCode) => set(() => ({ countryCode })),
  clearSession: () =>
    set(() => ({
      accessToken: null,
      user: null,
      isAuthenticated: false,
    })),
}));
